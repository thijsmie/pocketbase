from pocketbase.models.dtos import HealthCheckResponse
from pocketbase.models.options import CommonOptions, SendOptions
from pocketbase.services.base import Service


class HealthService(Service):
    """Service for checking the health status of the PocketBase instance.

    This service provides methods to check if the PocketBase server is running
    and responding correctly.
    """

    __base_sub_path__ = "/api/health"

    async def check(self, options: CommonOptions | None = None) -> HealthCheckResponse:
        """Check the health status of the PocketBase instance.

        Args:
            options: Additional request parameters

        Returns:
            HealthCheckResponse containing the health status information

        Example:
            ```python
            health = await pb.health.check()
            print(f"Status: {health['status']}")
            ```
        """
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        return await self._send("", send_options)  # type: ignore
