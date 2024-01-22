from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, cast
from urllib.parse import quote

from pocketbase.models.dtos import AuthMethods, AuthResult, ExternalAuthModel, Oauth2Payload, Record
from pocketbase.models.options import CommonOptions, SendOptions
from pocketbase.services.base import Service
from pocketbase.services.crud import CrudService
from pocketbase.services.realtime import Callback
from pocketbase.utils.types import BodyDict

if TYPE_CHECKING:
    from pocketbase.client import PocketBase, PocketBaseInners


class RecordService(CrudService[Record]):
    __base_sub_path__: str

    def __init__(self, pocketbase: "PocketBase", inners: "PocketBaseInners", collection: str) -> None:
        super().__init__(pocketbase, inners)
        self._collection = collection
        self.__base_sub_path__ = f"/api/collections/{quote(collection)}/records"
        self._auth = RecordAuthService(pocketbase, inners, collection)

    @property
    def auth(self) -> "RecordAuthService":
        return self._auth

    async def subscribe(
        self, callback: Callback, record_id: str | None = None, options: CommonOptions | None = None
    ) -> Callable[[], Awaitable[None]]:
        if record_id:
            return await self._pb.realtime.subscribe(f"{self._collection}/{record_id}", callback, options)
        else:
            return await self._pb.realtime.subscribe(self._collection, callback, options)


class RecordAuthService(Service):
    def __init__(self, pocketbase: "PocketBase", inners: "PocketBaseInners", collection: str) -> None:
        super().__init__(pocketbase, inners)
        self.__base_sub_path__ = f"/api/collections/{quote(collection)}"

    async def methods(self, options: CommonOptions | None = None) -> AuthMethods:
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        result: AuthMethods = await self._send("/auth-methods", send_options)  # type: ignore
        result["usernamePassword"] = result.get("usernamePassword", False)
        result["emailPassword"] = result.get("emailPassword", False)
        result["authProviders"] = result.get("authProviders", [])
        return result

    async def with_password(
        self, username_or_email: str, password: str, options: CommonOptions | None = None
    ) -> AuthResult:
        send_options: SendOptions = {"method": "POST", "body": {"identity": username_or_email, "password": password}}

        if options:
            send_options.update(options)

        result: AuthResult = await self._send("/auth-with-password", send_options)  # type: ignore
        self._in.auth.set_user(result)
        return result

    async def with_OAuth2(self, payload: Oauth2Payload, options: CommonOptions | None = None) -> AuthResult:
        send_options: SendOptions = {"method": "POST", "body": cast(BodyDict, payload)}

        if options:
            send_options.update(options)

        result: AuthResult = await self._send("/auth-with-oauth2", send_options)  # type: ignore
        self._in.auth.set_user(result)
        return result

    async def refresh(self, options: CommonOptions | None = None) -> AuthResult:
        send_options: SendOptions = {"method": "POST"}

        if options:
            send_options.update(options)

        self._in.auth.set_is_refreshing(True)
        result: AuthResult = await self._send("/auth-refresh", send_options)  # type: ignore
        self._in.auth.set_is_refreshing(False)
        self._in.auth.set_user(result)
        return result

    async def list_external_auths(
        self, record_id: str, options: CommonOptions | None = None
    ) -> list[ExternalAuthModel]:
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        return await self._send(f"/records/{quote(record_id)}/external-auths", send_options)  # type: ignore

    async def unlink_external_auth(self, record_id: str, provider: str, options: CommonOptions | None = None) -> None:
        send_options: SendOptions = {"method": "DELETE"}

        if options:
            send_options.update(options)

        await self._send_noreturn(f"/records/{quote(record_id)}/external-auths/{quote(provider)}", send_options)
