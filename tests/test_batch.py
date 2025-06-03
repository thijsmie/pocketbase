from random import getrandbits
from uuid import uuid4

import pytest

from pocketbase import FileUpload, PocketBase, PocketBaseError
from pocketbase.models.dtos import CollectionModel


@pytest.fixture
async def collection(superuser_client: PocketBase) -> CollectionModel:
    schema = [
        {"name": "created", "onCreate": True, "onUpdate": False, "type": "autodate"},
        {"name": "updated", "onCreate": True, "onUpdate": True, "type": "autodate"},
        {
            "name": "title",
            "type": "text",
            "required": True,
        },
    ]
    coll = await superuser_client.collections.create(
        {
            "name": uuid4().hex,
            "type": "base",
            "fields": schema,
        }
    )
    schema.append(
        {
            "name": "rel",
            "type": "relation",
            "required": False,
            "collectionId": coll["id"],
            "cascadeDelete": False,
            "maxSelect": 1,
        },
    )
    schema.append(
        {
            "name": "multirel",
            "type": "relation",
            "required": False,
            "collectionId": coll["id"],
            "cascadeDelete": False,
            "maxSelect": 5,
        },
    )
    return await superuser_client.collections.update(coll["id"], {"fields": schema})


async def create_file_collection(superuser_client: PocketBase):
    schema = [
        {
            "name": "title",
            "type": "text",
            "required": True,
        },
        {
            "name": "image",
            "type": "file",
            "required": False,
            "maxSelect": 3,
            "maxSize": 5242880,
            "mimeTypes": [
                "application/octet-stream",
                "text/plain",
            ],
        },
    ]

    return await superuser_client.collections.create(
        {
            "name": uuid4().hex,
            "type": "base",
            "fields": schema,
        }
    )


@pytest.fixture
async def activate_batch_api(superuser_client: PocketBase):
    await superuser_client.settings.update(
        body={
            "batch": {"enabled": True, "maxRequests": 50, "timeout": 3, "maxBodySize": 0},
        }
    )


async def test_create_record_batch_without_batch_api(superuser_client: PocketBase, collection: CollectionModel):
    bname = uuid4().hex
    bname_2 = uuid4().hex
    async with superuser_client.batched() as batch:
        col = batch.collection(collection["id"])
        col.create(
            {
                "title": bname,
            }
        )
        col.create(
            {
                "title": bname_2,
            }
        )

        with pytest.raises(PocketBaseError) as exc:
            _ = await batch.send()
            assert exc.value.status == 403  # batch API is not enabled


async def test_create_record_batch(superuser_client: PocketBase, collection: CollectionModel, activate_batch_api):
    bname = uuid4().hex
    bname_2 = uuid4().hex
    col_id = collection["id"]
    async with superuser_client.batched() as batch:
        col = batch.collection(col_id)
        col.create(
            {
                "title": bname,
            }
        )
        col.create(
            {
                "title": bname_2,
            }
        )

        result = await batch.send()

    assert len(result) == 2
    assert result[0]["body"]["title"] == bname
    col = superuser_client.collection(collection["id"])
    assert result[0]["body"] == await col.get_first()


async def test_create_multiple_record_batch(
    superuser_client: PocketBase, collection: CollectionModel, activate_batch_api
):
    col_unbatched = superuser_client.collection(collection["id"])
    async with superuser_client.batched() as batch:
        col_id = collection["id"]
        col = batch.collection(col_id)

        for _ in range(10):
            col.create(
                {
                    "title": uuid4().hex,
                }
            )

        await batch.send()

    # expansion

    rel = await col_unbatched.get_full_list()

    assert len(rel) == 10


async def test_create_update_delete_batch(
    superuser_client: PocketBase, collection: CollectionModel, activate_batch_api
):
    col_unbatched = superuser_client.collection(collection["id"])

    async with superuser_client.batched() as batch:
        col_id = collection["id"]
        col = batch.collection(col_id)

        # create
        record = await col_unbatched.create(
            {
                "title": uuid4().hex,
            }
        )
        # update
        col.update(record["id"], {"title": "updated"})
        # delete
        col.delete(record["id"])

        result = await batch.send()

    assert len(result) == 2
    assert result[0]["body"]["title"] == "updated"
    assert result[1]["status"] == 204  # delete should return 204 No Content

    with pytest.raises(PocketBaseError) as exc:
        _ = await col_unbatched.get_one(record["id"])
        assert exc.value.status == 404  # record should be deleted


async def test_batch_with_files(superuser_client: PocketBase, activate_batch_api):
    coll = await create_file_collection(superuser_client)
    col_id = coll["id"]
    col_unbatched = superuser_client.collection(coll["id"])
    name1 = uuid4().hex
    name2 = uuid4().hex
    name3 = uuid4().hex
    acontent = uuid4().hex
    bcontent = getrandbits(1024 * 8).to_bytes(1024, "little")
    ccontent = uuid4().hex

    async with superuser_client.batched() as batch:
        col = batch.collection(col_id)
        col.create(
            {
                "title": uuid4().hex,
                "image": FileUpload(
                    (name1 + ".txt", acontent, "text/plain"),
                    (name2 + ".txt", bcontent, "application/octet-stream"),
                    (name3 + ".txt", ccontent, "text/plain"),
                ),
            }
        )
        col.create({"title": uuid4().hex, "image": FileUpload((name1 + ".txt", acontent, "text/plain"))})
        result = await batch.send()
    assert len(result) == 2
    assert len(result[0]["body"]["image"]) == 3
    for fn in result[0]["body"]["image"]:
        if fn.startswith(name2):
            break
    rel = await col_unbatched.get_one(result[0]["body"]["id"])
    assert len(rel["image"]) == 3


async def test_batch_iteration(superuser_client: PocketBase, collection: CollectionModel, activate_batch_api):
    col_unbatched = superuser_client.collection(collection["id"])
    col_id = collection["id"]

    # create 10 records
    async with superuser_client.batched() as batch:
        col = batch.collection(col_id)
        for i in range(10):
            col.create(
                {
                    "title": f"record {i}",
                }
            )
        await batch.send()

    async with superuser_client.batched() as batch:
        col = batch.collection(col_id)

        # create 10 more records
        for i in range(10, 20):
            col.create(
                {
                    "title": f"record {i}",
                }
            )
        await batch.send()

    # iterate over all records
    items = await col_unbatched.get_full_list()

    assert len(items) == 20
