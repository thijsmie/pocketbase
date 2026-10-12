from typing import cast
from urllib.parse import quote

from pocketbase.models.dtos import Collection, CollectionModel, ConfigurableOAuth2Provider, DryRunViewResult
from pocketbase.models.options import CommonOptions, SendOptions
from pocketbase.services.crud import CrudService
from pocketbase.utils.types import BodyField


class CollectionService(CrudService[CollectionModel]):
    __base_sub_path__ = "/api/collections"

    async def import_collections(
        self, collections: list[Collection], delete_missing: bool = False, options: CommonOptions | None = None
    ) -> None:
        send_options: SendOptions = {
            "method": "PUT",
            "body": {
                "collections": cast(BodyField, collections),
                "deleteMissing": delete_missing,
            },
        }

        if options:
            send_options.update(options)

        await self._send_noreturn("/import", send_options)

    async def truncate(self, collection_id_or_name: str, options: CommonOptions | None = None) -> None:
        """Deletes all records of the specified collection."""
        send_options: SendOptions = {"method": "DELETE"}

        if options:
            send_options.update(options)

        await self._send_noreturn(f"/{quote(collection_id_or_name)}/truncate", send_options)

    async def get_scaffolds(self, options: CommonOptions | None = None) -> dict[str, CollectionModel]:
        """Returns a type indexed map with scaffolded collection models populated with their default values."""
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        return await self._send("/meta/scaffolds", send_options)  # type: ignore

    async def get_all_oauth2_providers(self, options: CommonOptions | None = None) -> list[ConfigurableOAuth2Provider]:
        """Returns a list with all configurable OAuth2 providers (requires PocketBase v0.37+)."""
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        return await self._send("/meta/oauth2-providers", send_options)  # type: ignore

    async def dry_run_view_query(self, query: str, options: CommonOptions | None = None) -> DryRunViewResult:
        """Executes a view query and returns its fields and a sample of records (requires PocketBase v0.37+)."""
        send_options: SendOptions = {"method": "POST", "body": {"query": query}}

        if options:
            send_options.update(options)

        return await self._send("/meta/dry-run-view", send_options)  # type: ignore
