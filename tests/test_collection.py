from uuid import uuid4

import pytest

from pocketbase import PocketBase
from pocketbase.models.dtos import Collection
from pocketbase.models.errors import PocketBaseError


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
                    "options": {
                        "min": 10,
                    },
                },
            ],
        }
    )
    return collection, collection["name"]


async def test_create(admin_client: PocketBase):
    collection, _ = await create_collection(admin_client)
    assert collection["type"] == "base"


async def test_update(admin_client: PocketBase):
    collection, _ = await create_collection(admin_client)
    new_name = uuid4().hex
    c2 = await admin_client.collections.update(
        collection["id"],
        {
            "name": new_name,
            "fields": [
                {
                    "name": "title",
                    "type": "text",
                    "required": True,
                    "options": {
                        "min": 10,
                    },
                },
                {
                    "name": "status",
                    "type": "bool",
                },
            ],
        },
    )
    assert c2["name"] != collection["name"]
    assert c2["name"] == new_name


async def test_delete(admin_client: PocketBase):
    collection, _ = await create_collection(admin_client)
    await admin_client.collections.delete(collection["id"])
    with pytest.raises(PocketBaseError) as exc:
        await admin_client.collections.delete(collection["id"])
    assert exc.value.status == 404  # double already deleted


async def test_delete_nonexisting_exception(admin_client: PocketBase):
    with pytest.raises(PocketBaseError) as exc:
        await admin_client.collections.delete(uuid4().hex)
    assert exc.value.status == 404  # delete nonexisting


async def test_get_nonexisting_exception(admin_client: PocketBase):
    with pytest.raises(PocketBaseError) as exc:
        await admin_client.collections.get_one(uuid4().hex)
    assert exc.value.status == 404


async def test_import_collection(admin_client: PocketBase):
    data = [
        {
            "name": uuid4().hex,
            "fields": [
                {
                    "name": "status",
                    "type": "bool",
                },
            ],
        },
        {
            "name": uuid4().hex,
            "fields": [
                {
                    "name": "title",
                    "type": "text",
                },
            ],
        },
    ]
    await admin_client.collections.import_collections(data)
