from contextlib import suppress
from uuid import uuid4

from pocketbase import PocketBase
from pocketbase.models.dtos import Collection
from pocketbase.models.errors import PocketBaseNotFoundError


async def create_collection(client: PocketBase) -> tuple[Collection, str]:
    collection = await client.collections.create(
        {
            "name": uuid4().hex,
            "type": "base",
            "fields": [
                {
                    "name": "title",
                    "type": "text",
                    "required": True,
                    "min": 10,
                },
            ],
        }
    )
    return collection, collection["name"]


async def test_github_issue_21(superuser_client: PocketBase):
    _, name = await create_collection(superuser_client)
    collection = superuser_client.collection(name)
    params = {}

    await collection.get_full_list({"params": params})

    with suppress(PocketBaseNotFoundError):
        await collection.get_one("bla", {"params": params})

    with suppress(PocketBaseNotFoundError):
        await collection.get_first({"filter": 'id="bla"', "params": params})

    assert params == {}
