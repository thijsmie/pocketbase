from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pocketbase.models.errors import PocketBaseError
from pocketbase.models.options import CommonOptions, SendOptions
from pocketbase.services.base import Service
from pocketbase.utils.types import BodyDict

if TYPE_CHECKING:
    from pocketbase.client import PocketBase, PocketBaseInners


class SettingsService(Service):
    __base_sub_path__: str = "/api/settings"

    def __init__(self, pocketbase: PocketBase, inners: PocketBaseInners) -> None:
        super().__init__(pocketbase, inners)

    async def get_all(self, options: CommonOptions | None = None) -> dict[str, Any]:
        """Fetch all available app settings."""
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        return await self._send("", send_options)  # type: ignore

    async def update(
        self,
        body: BodyDict | None = None,
        options: CommonOptions | None = None,
    ) -> dict[str, Any]:
        """Bulk updates app settings."""
        send_options: SendOptions = {"method": "PATCH"}

        if body:
            send_options["body"] = body

        if options:
            send_options.update(options)

        return await self._send("", send_options)  # type: ignore

    async def test_s3(self, options: CommonOptions | None = None) -> bool:
        """Performs a S3 storage connection test."""
        send_options: SendOptions = {"method": "POST"}

        if options:
            send_options.update(options)

        await self._send("/test/s3", send_options)
        return True

    async def test_email(
        self,
        to_email: str,
        email_template: str,
        options: CommonOptions | None = None,
    ) -> bool:
        """
        Sends a test email.

        The possible `email_template` values are:
        - verification
        - password-reset
        - email-change
        """
        body: BodyDict = {"email": to_email, "template": email_template}
        send_options: SendOptions = {"method": "POST", "body": body}

        if options:
            send_options.update(options)

        await self._send("/test/email", send_options)
        return True

    async def generate_apple_client_secret(
        self,
        client_id: str,
        team_id: str,
        key_id: str,
        private_key: str,
        duration: int,
        options: CommonOptions | None = None,
    ) -> str:
        """Generates a new Apple client secret."""
        body: BodyDict = {
            "clientId": client_id,
            "teamId": team_id,
            "keyId": key_id,
            "privateKey": private_key,
            "duration": duration,
        }
        send_options: SendOptions = {"method": "POST", "body": body}

        if options:
            send_options.update(options)

        response = await self._send("/apple/generate-client-secret", send_options)

        if isinstance(response, dict) and "secret" in response and isinstance(response["secret"], str):
            return response["secret"]
        else:
            raise PocketBaseError(
                "/apple/generate-client-secret",
                500,
                "Failed to generate Apple client secret or unexpected response format.",
            )
