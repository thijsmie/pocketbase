from collections.abc import AsyncGenerator
from random import getrandbits
from uuid import uuid4

import pytest

from pocketbase import FileUpload, PocketBase, PocketBaseError
from pocketbase.models.dtos import CollectionModel


@pytest.fixture
async def collection(superuser_client: PocketBase) -> CollectionModel:
    return await superuser_client.collections.create(
        {
            "name": uuid4().hex,
            "type": "base",
            "fields": [
                {"name": "title", "type": "text", "required": True},
                {"name": "data", "type": "json", "required": False},
            ],
        }
    )


async def create_file_collection(superuser_client: PocketBase) -> CollectionModel:
    return await superuser_client.collections.create(
        {
            "name": uuid4().hex,
            "type": "base",
            "fields": [
                {"name": "title", "type": "text", "required": True},
                {
                    "name": "image",
                    "type": "file",
                    "required": False,
                    "maxSelect": 3,
                    "maxSize": 5242880,
                    "mimeTypes": ["application/octet-stream", "text/plain"],
                },
            ],
        }
    )


async def set_batch_enabled(superuser_client: PocketBase, enabled: bool) -> None:
    await superuser_client.settings.update(
        body={"batch": {"enabled": enabled, "maxRequests": 50, "timeout": 3, "maxBodySize": 0}}
    )


@pytest.fixture
async def batch_api(superuser_client: PocketBase) -> AsyncGenerator[None, None]:
    await set_batch_enabled(superuser_client, True)
    yield
    await set_batch_enabled(superuser_client, False)


async def test_batch_api_disabled(superuser_client: PocketBase, collection: CollectionModel):
    await set_batch_enabled(superuser_client, False)
    with pytest.raises(PocketBaseError) as exc:
        async with superuser_client.batched() as batch:
            batch.collection(collection["id"]).create({"title": uuid4().hex})
    assert exc.value.status == 403

    assert await superuser_client.collection(collection["id"]).get_full_list() == []


async def test_create_records(superuser_client: PocketBase, collection: CollectionModel, batch_api):
    titles = [uuid4().hex for _ in range(10)]
    async with superuser_client.batched() as batch:
        col = batch.collection(collection["id"])
        for title in titles:
            col.create({"title": title, "data": {"nested": [1, 2, 3]}})

    assert [r["status"] for r in batch.results] == [200] * 10
    assert [r["body"]["title"] for r in batch.results] == titles
    records = await superuser_client.collection(collection["id"]).get_full_list()
    assert sorted(r["title"] for r in records) == sorted(titles)
    assert all(r["data"] == {"nested": [1, 2, 3]} for r in records)


async def test_upsert_update_delete(superuser_client: PocketBase, collection: CollectionModel, batch_api):
    col = superuser_client.collection(collection["id"])
    existing = await col.create({"title": uuid4().hex})
    to_delete = await col.create({"title": uuid4().hex})
    new_id = uuid4().hex[:15]

    async with superuser_client.batched() as batch:
        sub = batch.collection(collection["id"])
        sub.update(existing["id"], {"title": "updated"})
        sub.upsert({"id": new_id, "title": "upserted"})
        sub.delete(to_delete["id"])

    assert [r["status"] for r in batch.results] == [200, 200, 204]
    assert (await col.get_one(existing["id"]))["title"] == "updated"
    assert (await col.get_one(new_id))["title"] == "upserted"
    with pytest.raises(PocketBaseError) as exc:
        await col.get_one(to_delete["id"])
    assert exc.value.status == 404


async def test_failed_request_rolls_back(superuser_client: PocketBase, collection: CollectionModel, batch_api):
    with pytest.raises(PocketBaseError) as exc:
        async with superuser_client.batched() as batch:
            sub = batch.collection(collection["id"])
            sub.create({"title": uuid4().hex})
            sub.create({})  # title is required
    assert exc.value.status == 400

    assert await superuser_client.collection(collection["id"]).get_full_list() == []
    with pytest.raises(RuntimeError):
        async with batch:
            pass


async def test_exception_in_block_sends_nothing(superuser_client: PocketBase, collection: CollectionModel, batch_api):
    with pytest.raises(ZeroDivisionError):
        async with superuser_client.batched() as batch:
            batch.collection(collection["id"]).create({"title": uuid4().hex})
            _ = 1 / 0

    assert await superuser_client.collection(collection["id"]).get_full_list() == []
    with pytest.raises(RuntimeError):
        _ = batch.results


async def test_empty_batch(superuser_client: PocketBase):
    async with superuser_client.batched() as batch:
        pass
    assert batch.results == []


async def test_batch_scope_is_enforced(superuser_client: PocketBase, collection: CollectionModel, batch_api):
    batch = superuser_client.batched()
    with pytest.raises(RuntimeError):
        batch.collection(collection["id"]).create({"title": uuid4().hex})
    with pytest.raises(RuntimeError):
        _ = batch.results

    async with batch:
        sub = batch.collection(collection["id"])
        sub.create({"title": uuid4().hex})

    with pytest.raises(RuntimeError):
        sub.create({"title": uuid4().hex})
    with pytest.raises(RuntimeError):
        async with batch:
            pass
    assert len(batch.results) == 1


async def test_batches_are_independent(superuser_client: PocketBase, collection: CollectionModel, batch_api):
    async with superuser_client.batched() as first, superuser_client.batched() as second:
        first.collection(collection["id"]).create({"title": "first"})
        second.collection(collection["id"]).create({"title": "second"})

    assert [r["body"]["title"] for r in first.results] == ["first"]
    assert [r["body"]["title"] for r in second.results] == ["second"]


async def test_batch_with_files(superuser_client: PocketBase, batch_api):
    coll = await create_file_collection(superuser_client)
    name = uuid4().hex
    acontent = uuid4().hex
    bcontent = getrandbits(1024 * 8).to_bytes(1024, "little")

    async with superuser_client.batched() as batch:
        col = batch.collection(coll["id"])
        col.create(
            {
                "title": uuid4().hex,
                "image": FileUpload(
                    (name + "a.txt", acontent, "text/plain"),
                    (name + "b.txt", bcontent, "application/octet-stream"),
                ),
            }
        )
        col.create({"title": uuid4().hex, "image": FileUpload((name + "c.txt", acontent, "text/plain"))})

    first, second = (r["body"] for r in batch.results)
    assert len(first["image"]) == 2
    assert len(second["image"]) == 1
    binary = next(fn for fn in first["image"] if fn.startswith(name + "b"))
    assert await superuser_client.files.download_file(coll["id"], first["id"], binary) == bcontent
