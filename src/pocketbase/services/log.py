from urllib.parse import quote

from pocketbase.models.dtos import HourlyStats, ListResult, LogModel
from pocketbase.models.options import CommonOptions, ListOptions, LogStatsOptions, SendOptions
from pocketbase.services.base import Service


class LogService(Service):
    __base_sub_path__ = "/api/logs"

    async def get_list(
        self, page: int = 1, per_page: int = 30, options: ListOptions | None = None
    ) -> ListResult[LogModel]:
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        send_options["params"] = send_options.get("params", {})
        send_options["params"]["page"] = page
        send_options["params"]["perPage"] = per_page

        if options and "filter" in options:
            send_options["params"]["filter"] = options["filter"]

        return await self._send("", send_options)  # type: ignore

    async def get_one(self, record_id: str, options: CommonOptions | None = None) -> LogModel:
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        return await self._send(f"/{quote(record_id)}", send_options)  # type: ignore

    async def get_stats(self, options: LogStatsOptions | None = None) -> list[HourlyStats]:
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

            if "filter" in options:
                send_options["params"] = send_options.get("params", {})
                send_options["params"]["filter"] = options["filter"]

        return await self._send("/stats", send_options)  # type: ignore
