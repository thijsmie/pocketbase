from urllib.parse import quote

from pocketbase.models.dtos import HourlyStats, ListResult, LogModel
from pocketbase.models.options import CommonOptions, ListOptions, LogStatsOptions, SendOptions
from pocketbase.services.base import Service


class LogService(Service):
    """Service for accessing application logs and statistics.

    This service provides methods to retrieve application logs and log statistics
    from the PocketBase instance.
    """

    __base_sub_path__ = "/api/logs"

    async def get_list(
        self, page: int = 1, per_page: int = 30, options: ListOptions | None = None
    ) -> ListResult[LogModel]:
        """Retrieve a paginated list of log entries.

        Args:
            page: Page number (1-based, defaults to 1)
            per_page: Number of log entries per page (defaults to 30)
            options: Additional options like filters and sorting

        Returns:
            ListResult containing log entries and pagination info

        Example:
            ```python
            logs = await pb.logs.get_list(page=1, per_page=50)
            for log in logs['items']:
                print(f"{log['created']}: {log['message']}")
            ```
        """
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        send_options["params"] = send_options.get("params", {})
        send_options["params"]["page"] = page
        send_options["params"]["perPage"] = per_page

        if options and "filter" in options:
            send_options["params"]["filter"] = options["filter"]

        if options and "sort" in options:
            send_options["params"]["sort"] = options["sort"]

        return await self._send("", send_options)  # type: ignore

    async def get_one(self, record_id: str, options: CommonOptions | None = None) -> LogModel:
        """Retrieve a specific log entry by its ID.

        Args:
            record_id: The unique identifier of the log entry
            options: Additional request parameters

        Returns:
            The log entry with the specified ID

        Example:
            ```python
            log = await pb.logs.get_one('LOG_ENTRY_ID')
            print(f"Log message: {log['message']}")
            ```
        """
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        return await self._send(f"/{quote(record_id)}", send_options)  # type: ignore

    async def get_stats(self, options: LogStatsOptions | None = None) -> list[HourlyStats]:
        """Get hourly statistics for log entries.

        Args:
            options: Options including filters for the statistics

        Returns:
            List of hourly statistics showing log activity

        Example:
            ```python
            stats = await pb.logs.get_stats()
            for stat in stats:
                print(f"Hour {stat['hour']}: {stat['total']} entries")
            ```
        """
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

            if "filter" in options:
                send_options["params"] = send_options.get("params", {}).copy()
                send_options["params"]["filter"] = options["filter"]

        return await self._send("/stats", send_options)  # type: ignore
