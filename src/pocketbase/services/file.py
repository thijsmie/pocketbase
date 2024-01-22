from urllib.parse import quote

from pocketbase.models.options import CommonOptions, FileOptions, SendOptions
from pocketbase.services.base import Service


class FileService(Service):
    __base_sub_path__ = "/api/files"

    def get_url(self, collection: str, record_id: str, filename: str) -> str:
        return self._build_url(f"/{quote(collection)}/{quote(record_id)}/{filename}")

    async def download_file(
        self, collection: str, record_id: str, filename: str, options: FileOptions | None = None
    ) -> bytes:
        url = f"/{quote(collection)}/{quote(record_id)}/{filename}"
        send_options: SendOptions = {"method": "GET", "params": {"download": True}}
        if options and "params" in options:
            send_options["params"].update(options["params"])

        if options and "headers" in options:
            send_options["headers"] = options["headers"]

        if options and "thumb" in options:
            send_options["params"]["thumb"] = options["thumb"]

        return (await self._send_raw(url, send_options)).content

    async def get_token(self, options: CommonOptions | None = None) -> str:
        send_options: SendOptions = {"method": "POST"}

        if options:
            send_options.update(options)

        return (await self._send("/token", send_options))["token"]  # type: ignore
