from typing import cast

from pocketbase.models.dtos import Collection, CollectionModel
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
