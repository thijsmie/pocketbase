from typing import cast

from pocketbase.models.dtos import Collection, CollectionModel
from pocketbase.models.options import CommonOptions, SendOptions
from pocketbase.services.crud import CrudService
from pocketbase.utils.types import BodyField


class CollectionService(CrudService[CollectionModel]):
    """Service for managing collection schemas and metadata.

    This service allows you to create, read, update, and delete collection schemas,
    as well as import/export collection configurations.
    """

    __base_sub_path__ = "/api/collections"

    async def import_collections(
        self, collections: list[Collection], delete_missing: bool = False, options: CommonOptions | None = None
    ) -> None:
        """Import multiple collections, optionally replacing existing ones.

        Args:
            collections: List of collection definitions to import
            delete_missing: Whether to delete collections not present in the import
            options: Additional request parameters

        Example:
            ```python
            collections_to_import = [
                {
                    'name': 'posts',
                    'type': 'base',
                    'fields': [
                        {'name': 'title', 'type': 'text', 'required': True},
                        {'name': 'content', 'type': 'editor'}
                    ]
                }
            ]
            await pb.collections.import_collections(collections_to_import)
            ```
        """
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
