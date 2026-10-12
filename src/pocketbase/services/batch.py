import json
from types import TracebackType
from typing import TYPE_CHECKING, Any, Literal, TypedDict, cast
from urllib.parse import quote, urlencode

from pocketbase.models.errors import PocketBaseError
from pocketbase.models.options import CommonOptions, SendOptions
from pocketbase.services.base import Service
from pocketbase.utils.types import BodyDict, JsonType, SendableFiles, transform

if TYPE_CHECKING:
    from pocketbase.client import PocketBase, PocketBaseInners


class BatchRequest(TypedDict, total=False):
    url: str
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    headers: dict[str, str]
    body: BodyDict


class BatchRequestResult(TypedDict):
    status: int
    body: JsonType


class BatchService(Service):
    """
    Collects record operations and sends them as a single transactional `/api/batch` call.

    Use it as an async context manager; the queued operations are sent when the block exits
    without an exception, and the per-request results are available on `results` afterwards.
    If any operation fails, none are applied. The batch API must be enabled in the PocketBase
    settings, and a batch may not hold more operations than its `maxRequests` setting allows.

        async with pb.batched() as batch:
            batch.collection("posts").create({"title": "Hello"})
            batch.collection("posts").delete("RECORD_ID")
        batch.results[0]["body"]["title"]
    """

    __base_sub_path__: str = "/api/batch"

    def __init__(
        self, pocketbase: "PocketBase", inners: "PocketBaseInners", options: CommonOptions | None = None
    ) -> None:
        super().__init__(pocketbase, inners)
        self._options = options
        self._requests: list[BatchRequest] = []
        self._subs: dict[str, SubBatchService] = {}
        self._open = False
        self._used = False
        self._results: list[BatchRequestResult] | None = None

    async def __aenter__(self) -> "BatchService":
        if self._used:
            raise RuntimeError("A batch can only be used once, create a new one with PocketBase.batched()")
        self._open = self._used = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._open = False
        try:
            # On an exception nothing has been sent yet, so dropping the queue leaves the database untouched.
            if exc_type is None:
                self._results = await self._send_batch() if self._requests else []
        finally:
            self._requests.clear()

    @property
    def results(self) -> list[BatchRequestResult]:
        """The result of each queued request, in order. Available once the `async with` block has exited."""
        if self._results is None:
            raise RuntimeError("Batch results are only available after the `async with` block has exited")
        return self._results

    def collection(self, id_or_name: str) -> "SubBatchService":
        """Queue record operations on the given collection."""
        if id_or_name not in self._subs:
            self._subs[id_or_name] = SubBatchService(self, id_or_name)
        return self._subs[id_or_name]

    def _submit_request(self, request: BatchRequest) -> None:
        if not self._open:
            raise RuntimeError("Batch operations can only be queued inside an `async with pb.batched()` block")
        self._requests.append(request)

    async def _send_batch(self) -> list[BatchRequestResult]:
        requests: list[JsonType] = []
        files: SendableFiles = []

        for idx, req in enumerate(self._requests):
            body, request_files = transform(req["body"])
            request: dict[str, JsonType] = {"method": req["method"], "url": req["url"], "body": body}
            if "headers" in req:
                request["headers"] = req["headers"]  # type: ignore[assignment]
            requests.append(request)
            files.extend((f"requests.{idx}.{key}", file) for key, file in request_files)  # type: ignore[misc]

        send_options: SendOptions = {"method": "POST"}
        if self._options:
            send_options.update(self._options)

        if files:
            # Files can only be sent as multipart/form-data, which carries the JSON part in `@jsonPayload`.
            send_options["body"] = {"@jsonPayload": json.dumps({"requests": requests})}
            send_options["files"] = files
        else:
            send_options["body"] = {"requests": requests}

        response = await self._send("", send_options)
        if not isinstance(response, list):
            raise PocketBaseError(self._build_url(""), 200, "PocketBase returned an unexpected batch response")

        items = cast(list[dict[str, Any]], response)
        return [{"status": item["status"], "body": item.get("body")} for item in items]


class SubBatchService:
    """Queues record operations on one collection into its parent batch."""

    def __init__(self, batch: BatchService, collection: str) -> None:
        self._batch = batch
        self._collection = collection

    def _records_url(self, record_id: str | None = None) -> str:
        url = f"/api/collections/{quote(self._collection)}/records"
        return f"{url}/{quote(record_id)}" if record_id is not None else url

    def _submit(
        self,
        method: Literal["POST", "PUT", "PATCH", "DELETE"],
        url: str,
        body: BodyDict,
        options: CommonOptions | None,
    ) -> None:
        if options and options.get("params"):
            url = f"{url}?{urlencode(options['params'])}"
        request: BatchRequest = {"method": method, "url": url, "body": body}
        if options and "headers" in options:
            request["headers"] = options["headers"]
        self._batch._submit_request(request)

    def create(self, params: BodyDict, options: CommonOptions | None = None) -> None:
        self._submit("POST", self._records_url(), params, options)

    def upsert(self, params: BodyDict, options: CommonOptions | None = None) -> None:
        """Update the record whose `id` is in `params`, or create it if it does not exist."""
        self._submit("PUT", self._records_url(), params, options)

    def update(self, record_id: str, params: BodyDict, options: CommonOptions | None = None) -> None:
        self._submit("PATCH", self._records_url(record_id), params, options)

    def delete(self, record_id: str, options: CommonOptions | None = None) -> None:
        self._submit("DELETE", self._records_url(record_id), {}, options)
