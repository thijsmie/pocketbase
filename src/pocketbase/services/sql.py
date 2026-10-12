from pocketbase.models.dtos import SQLResult
from pocketbase.models.options import CommonOptions, SendOptions
from pocketbase.services.base import Service


class SQLService(Service):
    __base_sub_path__ = "/api/sql"

    async def run(self, query: str, options: CommonOptions | None = None) -> SQLResult:
        """Executes a raw SQL query. Superusers only (requires PocketBase v0.39+)."""
        send_options: SendOptions = {"method": "POST", "body": {"query": query}}

        if options:
            send_options.update(options)

        return await self._send("", send_options)  # type: ignore
