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
                    "min": 10,
                },
            ],
        }
    )
    return collection, collection["name"]


async def test_create(superuser_client: PocketBase):
    collection, _ = await create_collection(superuser_client)
    assert collection["type"] == "base"


async def test_update(superuser_client: PocketBase):
    collection, _ = await create_collection(superuser_client)
    new_name = uuid4().hex
    c2 = await superuser_client.collections.update(
        collection["id"],
        {
            "name": new_name,
            "fields": [
                {
                    "name": "title",
                    "type": "text",
                    "required": True,
                    "min": 10,
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


async def test_delete(superuser_client: PocketBase):
    collection, _ = await create_collection(superuser_client)
    await superuser_client.collections.delete(collection["id"])
    with pytest.raises(PocketBaseError) as exc:
        await superuser_client.collections.delete(collection["id"])
    assert exc.value.status == 404  # double already deleted


async def test_delete_nonexisting_exception(superuser_client: PocketBase):
    with pytest.raises(PocketBaseError) as exc:
        await superuser_client.collections.delete(uuid4().hex)
    assert exc.value.status == 404  # delete nonexisting


async def test_get_nonexisting_exception(superuser_client: PocketBase):
    with pytest.raises(PocketBaseError) as exc:
        await superuser_client.collections.get_one(uuid4().hex)
    assert exc.value.status == 404


async def test_import_collection(superuser_client: PocketBase):
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
    await superuser_client.collections.import_collections(data)


async def test_truncate(superuser_client: PocketBase):
    _, name = await create_collection(superuser_client)
    await superuser_client.collection(name).create({"title": "a" * 12})
    assert (await superuser_client.collection(name).get_list())["totalItems"] == 1
    await superuser_client.collections.truncate(name)
    assert (await superuser_client.collection(name).get_list())["totalItems"] == 0


async def test_get_scaffolds(superuser_client: PocketBase):
    scaffolds = await superuser_client.collections.get_scaffolds()
    assert {"base", "auth", "view"} <= set(scaffolds)
    assert scaffolds["auth"]["type"] == "auth"


async def test_get_all_oauth2_providers(superuser_client: PocketBase):
    providers = await superuser_client.collections.get_all_oauth2_providers()
    names = {p["name"] for p in providers}
    assert "google" in names
    assert all(p["displayName"] and p["logo"] for p in providers)


async def test_dry_run_view_query(superuser_client: PocketBase):
    _, name = await create_collection(superuser_client)
    await superuser_client.collection(name).create({"title": "a" * 12})
    result = await superuser_client.collections.dry_run_view_query(f"SELECT id, title FROM `{name}`")
    assert {f["name"] for f in result["fields"]} == {"id", "title"}
    assert result["sample"][0]["title"] == "a" * 12


async def test_dry_run_view_query_invalid(superuser_client: PocketBase):
    with pytest.raises(PocketBaseError) as exc:
        await superuser_client.collections.dry_run_view_query("SELECT nonsense FROM nowhere")
    assert exc.value.status == 400
