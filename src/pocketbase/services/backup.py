from typing import TypeAlias, TypedDict, cast
from urllib.parse import quote

from httpx._types import FileTypes

from pocketbase.models.errors import PocketBaseError
from pocketbase.models.options import CommonOptions, SendOptions
from pocketbase.services.base import Service

ZipFileName: TypeAlias = str


class BackupFileInfo(TypedDict):
    key: ZipFileName
    size: int
    modified: str


class BackupService(Service):
    __base_sub_path__ = "/api/backups"

    async def get_full_list(self, options: CommonOptions | None = None) -> list[BackupFileInfo]:
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        backups = await self._send("", send_options)
        return cast(list[BackupFileInfo], backups)

    async def create(self, key: ZipFileName | None = None, options: CommonOptions | None = None) -> None:
        send_options: SendOptions = {"method": "POST", "body": {}}

        if key:
            send_options["body"]["name"] = key

        if options:
            send_options.update(options)

        await self._send_noreturn("", send_options)

    async def upload(self, file: FileTypes, options: CommonOptions | None = None) -> None:
        send_options: SendOptions = {
            "method": "POST",
            "files": [("file", file)],
        }

        if options:
            send_options.update(options)

        await self._send_noreturn("/upload", send_options)

    async def delete(self, key: ZipFileName, options: CommonOptions | None = None) -> None:
        send_options: SendOptions = {"method": "DELETE"}

        if options:
            send_options.update(options)

        await self._send_noreturn(f"/{quote(key)}", send_options)

    async def download(self, key: ZipFileName, options: CommonOptions | None = None) -> bytes:
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        send_options["params"] = send_options.get("params", {})
        send_options["params"]["token"] = await self._pb.files.get_token()

        response = await self._send_raw(f"/{quote(key)}", send_options)

        if not 200 >= response.status_code < 300:
            raise PocketBaseError(url=str(response.url), status=response.status_code, data=response.json())

        return response.content

    async def restore(self, key: ZipFileName, options: CommonOptions | None = None) -> None:
        send_options: SendOptions = {"method": "POST"}

        if options:
            send_options.update(options)

        await self._send_noreturn(f"/{quote(key)}/restore", send_options)

    async def get_download_url(self, key: ZipFileName) -> str:
        admin_token = await self._pb.files.get_token()
        return self._build_url(f"{quote(key)}?token={quote(admin_token)}")
