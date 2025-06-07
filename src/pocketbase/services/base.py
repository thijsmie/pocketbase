import json
from typing import TYPE_CHECKING

from httpx import Request, Response

from pocketbase.models.errors import PocketBaseError
from pocketbase.models.options import SendOptions
from pocketbase.utils.types import JsonType, SendableFiles, transform

if TYPE_CHECKING:
    from pocketbase.client import PocketBase, PocketBaseInners


class Service:
    __base_sub_path__: str

    def __init__(self, pocketbase: "PocketBase", inners: "PocketBaseInners") -> None:
        self._pb = pocketbase
        self._in = inners

    async def _send_raw(self, path: str, options: SendOptions) -> Response:
        request = self._init_send(path, options)
        await self._in.auth.authorize(request)

        if self._pb.before_send != self._pb.__class__.before_send:
            request = (await self._pb.before_send(request)) or request

        response = await self._in.client.send(request)

        if self._pb.after_send != self._pb.__class__.after_send:
            response = (await self._pb.after_send(response)) or response

        return response

    async def _send(self, path: str, options: SendOptions) -> JsonType:
        response = await self._send_raw(path, options)
        PocketBaseError.raise_for_status(response)

        try:
            return response.json()
        except ValueError as e:
            raise PocketBaseError(str(response.url), response.status_code, "PocketBase returned invalid JSON") from e

    async def _send_noreturn(self, path: str, options: SendOptions) -> None:
        response = await self._send_raw(path, options)
        PocketBaseError.raise_for_status(response)

    def _init_send(self, path: str, options: SendOptions) -> Request:
        headers = self._pb.headers()

        if options.get("headers"):
            headers.update(options["headers"])

        headers["accept"] = "application/json"

        body = options.get("body")
        data: dict[str, JsonType] | None = None
        files: SendableFiles | None = options.get("files")
        if body and files is None:
            data, files = transform(body)
            if not files:
                files = None
                data = None
            else:
                body = None
        elif body and files is not None:
            data, sfiles = transform(body)
            files.extend(sfiles)

        # convert the casted data back to str (happens inside transform)
        for key, value in (data or {}).items():
            if isinstance(value, dict | list):
                data[key] = json.dumps(value)  # type: ignore

        return self._in.client.build_request(
            url=self._build_url(path),
            method=options.get("method", "GET"),
            json=body,
            data=data,  # on multipart with files we have to send it via data
            files=files,  # type: ignore
            params=options.get("params"),
            headers=headers,
        )

    def _build_url(self, path: str) -> str:
        return f"{self.__base_sub_path__}{path}"
