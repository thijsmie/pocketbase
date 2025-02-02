from random import getrandbits
from uuid import uuid4

from pocketbase import FileUpload, PocketBase


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


async def test_create_three_file_record(superuser_client: PocketBase):
    coll = await create_file_collection(superuser_client)
    col = superuser_client.collection(coll["id"])
    name1 = uuid4().hex
    name2 = uuid4().hex
    name3 = uuid4().hex
    acontent = uuid4().hex
    bcontent = getrandbits(1024 * 8).to_bytes(1024, "little")
    ccontent = uuid4().hex
    record = await col.create(
        {
            "title": uuid4().hex,
            "image": FileUpload(
                (name1 + ".txt", acontent, "text/plain"),
                (name2 + ".txt", bcontent, "application/octet-stream"),
                (name3 + ".txt", ccontent, "text/plain"),
            ),
        }
    )
    assert len(record["image"]) == 3
    for fn in record["image"]:
        if fn.startswith(name2):
            break

    rel = await col.get_one(record["id"])
    assert len(rel["image"]) == 3

    rcontent = await superuser_client.files.download_file(coll["id"], rel["id"], fn)
    assert rcontent == bcontent


async def test_remove_file_from_record(superuser_client: PocketBase):
    coll = await create_file_collection(superuser_client)
    col = superuser_client.collection(coll["id"])
    record = await col.create({"title": "bla", "image": FileUpload(("a.png", b"jajaj"), ("b.png", b"jbjbj"))})

    # delete some of the files from record but keep the file named "filename"
    get_record = await col.update(record["id"], {"image": [record["image"][0]]})
    assert record["image"] != get_record["image"]
    assert len(get_record["image"]) == 1


async def test_create_one_file_record(superuser_client: PocketBase):
    coll = await create_file_collection(superuser_client)
    col = superuser_client.collection(coll["id"])
    name1 = uuid4().hex
    acontent = uuid4().hex
    record = await col.create(
        {
            "title": uuid4().hex,
            "image": FileUpload((name1 + ".txt", acontent, "text/plain")),
        }
    )
    assert len(record["image"]) == 1
    for fn in record["image"]:
        assert fn.startswith(name1)

    rel = await col.get_one(record["id"])
    assert len(rel["image"]) == 1

    r = await superuser_client.files.download_file(rel["collectionName"], rel["id"], rel["image"][0])
    assert r.decode("utf-8") == acontent


async def test_create_without_file_record2(superuser_client: PocketBase):
    coll = await create_file_collection(superuser_client)
    col = superuser_client.collection(coll["id"])
    record = await col.create(
        {
            "title": uuid4().hex,
            "image": None,
        }
    )
    assert len(record["image"]) == 0

    rel = await col.get_one(record["id"])
    assert len(rel["image"]) == 0
