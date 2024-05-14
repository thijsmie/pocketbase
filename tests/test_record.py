from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pocketbase import PocketBase, PocketbaseError
from pocketbase.models.dtos import CollectionModel


@pytest.fixture
async def collection(admin_client: PocketBase) -> CollectionModel:
    schema = [
        {
            "name": "title",
            "type": "text",
            "required": True,
        },
    ]
    coll = await admin_client.collections.create(
        {
            "name": uuid4().hex,
            "type": "base",
            "schema": schema,
        }
    )
    schema.append(
        {
            "name": "rel",
            "type": "relation",
            "required": False,
            "options": {
                "collectionId": coll["id"],
                "cascadeDelete": False,
                "maxSelect": 1,
            },
        },
    )
    schema.append(
        {
            "name": "multirel",
            "type": "relation",
            "required": False,
            "options": {
                "collectionId": coll["id"],
                "cascadeDelete": False,
                "maxSelect": 5,
            },
        },
    )
    return await admin_client.collections.update(coll["id"], {"schema": schema})


async def test_create_record(admin_client: PocketBase, collection: CollectionModel):
    bname = uuid4().hex
    col = admin_client.collection(collection["id"])
    record = await col.create(
        {
            "title": bname,
        }
    )
    assert record["title"] == bname
    assert record == await col.get_first()


async def test_create_multiple_record(admin_client: PocketBase, collection: CollectionModel):
    records = []
    col = admin_client.collection(collection["id"])

    for _ in range(10):
        records.append(
            (
                await col.create(
                    {
                        "title": uuid4().hex,
                        "rel": records[-1] if records else None,
                    }
                )
            )["id"]
        )

    # expansion

    rel = await col.get_one(records[-1], {"params": {"expand": "rel.rel.rel.rel.rel.rel"}})

    for i, r in enumerate(reversed(records)):
        assert rel["id"] == r
        if i > 5:
            break
        rel = rel["expand"]["rel"]


async def test_create_multi_relation_record(admin_client: PocketBase, collection: CollectionModel):
    records = []
    col = admin_client.collection(collection["id"])

    for _ in range(5):
        records.append(
            (
                await admin_client.collection(collection["id"]).create(
                    {
                        "title": uuid4().hex,
                        "multirel": records if records else [],
                    }
                )
            )["id"]
        )

    # expansion

    rel = await col.get_one(records[-1], {"params": {"expand": "multirel.multirel.multirel.multirel"}})

    for i, r in enumerate(reversed(records)):
        assert rel["id"] == r
        if i >= 4:
            break
        assert len(rel["expand"]["multirel"]) == len(records) - i - 1
        rel = rel["expand"]["multirel"][-1]


async def test_get_record(admin_client: PocketBase, collection: CollectionModel):
    bname = uuid4().hex
    col = admin_client.collection(collection["id"])
    record = await col.create(
        {
            "title": bname,
        }
    )
    first = await col.get_first()
    byid = await col.get_one(record["id"])
    full_list = await col.get_full_list()
    partial_list = await col.get_list()
    assert record == first == byid == full_list[0] == partial_list["items"][0]
    assert record["title"] == bname


async def test_get_filter(admin_client: PocketBase, collection: CollectionModel):
    col = admin_client.collection(collection["id"])
    record_a = await col.create(
        {
            "title": "a",
        }
    )
    record_b = await col.create(
        {
            "title": "b",
        }
    )

    assert record_a == await col.get_first({"filter": 'title = "a"'})
    assert record_b == await col.get_first({"filter": 'title = "b"'})
    assert [record_a] == await col.get_full_list({"filter": 'title = "a"'})
    assert [record_b] == await col.get_full_list({"filter": 'title = "b"'})
    assert [record_a] == (await col.get_list(options={"filter": 'title = "a"'}))["items"]
    assert [record_b] == (await col.get_list(options={"filter": 'title = "b"'}))["items"]


async def test_get_sorted(admin_client: PocketBase, collection: CollectionModel):
    col = admin_client.collection(collection["id"])
    record_a = await col.create(
        {
            "title": "a",
        }
    )
    record_c = await col.create(
        {
            "title": "c",
        }
    )
    record_b = await col.create(
        {
            "title": "b",
        }
    )

    falling = await col.get_list(options={"sort": "-title"})
    rising = await col.get_list(options={"sort": "+title"})
    assert [record_a, record_b, record_c] == rising["items"]
    assert [record_c, record_b, record_a] == falling["items"]


async def test_update(admin_client: PocketBase, collection: CollectionModel):
    col = admin_client.collection(collection["id"])
    record = await col.create({"title": "a"})
    updated = await col.update(record["id"], {"title": "b"})
    assert record != updated
    assert updated["updated"] > updated["created"]
    assert updated["created"] == record["created"]


async def test_delete(admin_client: PocketBase, collection: CollectionModel):
    col = admin_client.collection(collection["id"])
    record = await col.create({"title": "a"})
    await col.delete(record["id"])
    # deleting already deleted record should give 404
    with pytest.raises(PocketbaseError) as exc:
        await col.delete(record["id"])
    assert exc.value.status == 404


async def test_get_one(admin_client: PocketBase, collection: CollectionModel):
    col = admin_client.collection(collection["id"])
    with pytest.raises(PocketbaseError) as exc:
        await col.get_one("blblblbllb")
    assert exc.value.status == 404


async def test_datetime(admin_client: PocketBase):
    await admin_client.collections.create(
        {
            "name": "datetime",
            "type": "base",
            "schema": [
                {
                    "name": "when",
                    "type": "date",
                    "required": True,
                },
            ],
        }
    )
    await admin_client.collection("datetime").create({"when": datetime.now()})
    await admin_client.collection("datetime").create({"when": datetime.now(tz=UTC)})
