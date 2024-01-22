from pocketbase.models.dtos import HealthCheckResponse
from pocketbase.models.options import CommonOptions, SendOptions
from pocketbase.services.base import Service


class HealthService(Service):
    __base_sub_path__ = "/api/health"

    async def check(self, options: CommonOptions | None = None) -> HealthCheckResponse:
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        return await self._send("", send_options)  # type: ignore
