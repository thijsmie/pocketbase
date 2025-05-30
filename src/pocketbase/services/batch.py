import json
from typing import TYPE_CHECKING, Literal, TypedDict
from urllib.parse import quote

from pocketbase.models.options import CommonOptions, SendOptions
from pocketbase.services.base import Service
from pocketbase.utils.types import BodyDict, JsonType, SendableFiles, transform

if TYPE_CHECKING:
    from pocketbase.client import PocketBase, PocketBaseInners


class BatchRequest(TypedDict, total=False):
    url: str
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    headers: dict[str, str] | None
    body: BodyDict
    # files: SendableFiles | None
    # are treated seperately in the `send` method


class BatchRequestResult(TypedDict, total=False):
    status: int
    body: BodyDict


class BatchService(Service):
    __base_sub_path__: str = "/api/batch"
    """
    Service for batching multiple PocketBase API requests into a single `/api/batch` call.
    """

    def __init__(self, pocketbase: "PocketBase", inners: "PocketBaseInners") -> None:
        super().__init__(pocketbase, inners)
        self._requests: list[BatchRequest] = []
        self._subs: dict[str, SubBatchService] = {}

    def collection(self, collection_name: str) -> "SubBatchService":
        """
        Begin building a batch for the given collection.

        Returns a `SubBatchService` to queue CRUD operations.
        """
        if collection_name not in self._subs:
            self._subs[collection_name] = SubBatchService(
                self._requests,
                collection_name,
            )
        return self._subs[collection_name]

    async def send(self, options: CommonOptions | None = None) -> list[BatchRequestResult]:
        send_opts: SendOptions = {
            "method": "POST",
        }

        if options:
            send_opts.update(options)

        # building the request body
        json_data = []
        all_files: SendableFiles = []

        for idx, req in enumerate(self._requests):
            body_transformed, files = transform(req.get("body", {}))
            json_data.append(
                {
                    "method": req["method"],
                    "url": req["url"],
                    "headers": req.get("headers"),
                    "body": body_transformed,
                }
            )
            if files:
                for key, file in files:  # type: ignore
                    updated_key = f"requests.{idx}.{key}"
                    all_files.append((updated_key, file))

        send_opts["body"] = {"@jsonPayload": json.dumps({"requests": json_data})}
        if len(all_files) == 0:
            # add dummy files to trigger multipart encoding
            # easiest way to trigger multipart/form-data encoding
            # this key will be ignored by PocketBase
            # https://github.com/pocketbase/js-sdk/blob/b17fd45624a86d69b56163da6e8a519f533a1f22/src/services/BatchService.ts#L71
            all_files.append(("dummy.txt", b"mamaistdiebeste"))
        send_opts["files"] = all_files

        result_request: list[JsonType] = await self._send("", send_opts)  #  type: ignore
        result = []
        for item in result_request:
            result_item: BatchRequestResult = {
                "status": item["status"],  #  type: ignore
                "body": item.get("body", {}),  #  type: ignore
            }
            result.append(result_item)
        return result


class SubBatchService:
    """
    Helper to queue CRUD ops for a specific collection into the batch.
    """

    def __init__(self, requests: list[BatchRequest], collection: str) -> None:
        self._requests = requests
        self._collection = collection

    def create(self, params: BodyDict, options: CommonOptions | None = None) -> None:
        req: BatchRequest = {
            "method": "POST",
            "url": f"/api/collections/{quote(self._collection)}/records",
            "body": params,
            "headers": options.get("headers", None) if options else None,
        }
        self._requests.append(req)

    def update(self, record_id: str, params: BodyDict, options: CommonOptions | None = None) -> None:
        req: BatchRequest = {
            "method": "PATCH",
            "url": (f"/api/collections/{quote(self._collection)}/records/{quote(record_id)}"),
            "body": params,
            "headers": options.get("headers", None) if options else None,
        }
        self._requests.append(req)

    def delete(self, record_id: str, options: CommonOptions | None = None) -> None:
        req: BatchRequest = {
            "method": "DELETE",
            "url": (f"/api/collections/{quote(self._collection)}/records/{quote(record_id)}"),
            "body": {},
            "headers": options.get("headers", None) if options else None,
        }
        self._requests.append(req)
