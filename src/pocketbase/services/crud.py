from typing import Generic, TypeVar, cast
from urllib.parse import quote

from pocketbase.models.dtos import ListResult
from pocketbase.models.errors import PocketbaseError
from pocketbase.models.options import CommonOptions, FirstOptions, FullListOptions, ListOptions, SendOptions
from pocketbase.services.base import Service
from pocketbase.utils.types import BodyDict

_T = TypeVar("_T")


class CrudService(Service, Generic[_T]):
    async def get_list(
        self,
        page: int = 1,
        per_page: int = 30,
        options: ListOptions | SendOptions | None = None,
    ) -> ListResult[_T]:
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        send_options["params"] = send_options.get("params", {})
        send_options["params"]["page"] = page
        send_options["params"]["perPage"] = per_page

        if options and "filter" in options:
            send_options["params"]["filter"] = options["filter"]  # type: ignore

        if options and "sort" in options:
            send_options["params"]["sort"] = options["sort"]  # type: ignore

        return await self._send("", send_options)  # type: ignore

    async def get_full_list(self, options: FullListOptions | None = None) -> list[_T]:
        list_options: ListOptions = {}
        if options and "batch" in options:
            batch = options["batch"]
            del options["batch"]
        else:
            batch = 500

        if options:
            list_options.update(options)

        list_options["params"] = list_options.get("params", {})
        list_options["params"]["skipTotal"] = 1

        page = 1
        items: list[_T] = []
        result = None

        while result is None or len(result["items"]) == batch:
            result = await self.get_list(page, batch, list_options)
            items.extend(result["items"])
            page += 1

        return items

    async def get_first(self, options: FirstOptions | None = None) -> _T:
        list_options: ListOptions = cast(ListOptions, options) or {}
        list_options["params"] = list_options.get("params", {})
        list_options["params"]["skipTotal"] = 1
        result = await self.get_list(1, 1, list_options)
        if not result["items"]:
            raise PocketbaseError(
                url=self._build_url(""),
                status=404,
                data={"code": 404, "message": "The requested resource wasn't found.", "data": {}},
            )
        return result["items"][0]

    async def get_one(self, record_id: str, options: CommonOptions | None = None) -> _T:
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        return await self._send(f"/{quote(record_id)}", send_options)  # type: ignore

    async def create(self, params: BodyDict, options: CommonOptions | None = None) -> _T:
        if "password" in params and "passwordConfirm" not in params:
            params["passwordConfirm"] = params["password"]

        send_options: SendOptions = {"method": "POST", "body": params}

        if options:
            send_options.update(options)

        return await self._send("", send_options)  # type: ignore

    async def update(self, record_id: str, params: BodyDict, options: CommonOptions | None = None) -> _T:
        send_options: SendOptions = {"method": "PATCH", "body": params}

        if options:
            send_options.update(options)

        return await self._send(f"/{quote(record_id)}", send_options)  # type: ignore

    async def delete(self, record_id: str, options: CommonOptions | None = None) -> None:
        send_options: SendOptions = {"method": "DELETE"}

        if options:
            send_options.update(options)

        await self._send_noreturn(f"/{quote(record_id)}", send_options)
