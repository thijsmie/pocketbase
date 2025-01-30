from typing import TYPE_CHECKING, cast

from pocketbase.models.dtos import AdminAuthResult, AdminModel
from pocketbase.models.options import CommonOptions, SendOptions
from pocketbase.services.base import Service
from pocketbase.services.crud import CrudService
from pocketbase.utils.types import BodyDict

if TYPE_CHECKING:
    from pocketbase.client import PocketBase, PocketBaseInners


class AdminService(CrudService[AdminModel]):
    __base_sub_path__ = "/api/collections/_superusers/records"

    def __init__(self, pocketbase: "PocketBase", inners: "PocketBaseInners") -> None:
        super().__init__(pocketbase, inners)
        self._auth = AdminAuthService(pocketbase, inners)

    async def update(self, record_id: str, params: BodyDict, options: CommonOptions | None = None) -> AdminModel:
        item = await super().update(record_id, params, options)

        if self._in.auth.admin_id == item["id"]:
            self._in.auth.set_admin(item)

        return cast(AdminModel, item)

    async def delete(self, record_id: str, options: CommonOptions | None = None) -> None:
        await super().delete(record_id, options)

        if self._in.auth.admin_id == record_id:
            self._in.auth.clean()

    @property
    def auth(self) -> "AdminAuthService":
        return self._auth


class AdminAuthService(Service):
    __base_sub_path__ = "/api/collections/_superusers"

    async def with_password(self, email: str, password: str, options: CommonOptions | None = None) -> AdminAuthResult:
        send_options: SendOptions = {"method": "POST", "body": {"identity": email, "password": password}}

        if options:
            send_options.update(options)

        result: AdminAuthResult = await self._send("/auth-with-password", send_options)  # type: ignore
        self._in.auth.set_admin(result["record"], token=result["token"])
        return result

    async def refresh(self, options: CommonOptions | None = None) -> AdminAuthResult:
        send_options: SendOptions = {"method": "POST"}

        if options:
            send_options.update(options)

        self._in.auth.set_is_refreshing(True)
        result: AdminAuthResult = await self._send("/auth-refresh", send_options)  # type: ignore
        self._in.auth.set_is_refreshing(False)
        self._in.auth.set_admin(result["record"], token=result["token"])
        return result
