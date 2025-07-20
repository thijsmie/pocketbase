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
        {
            "name": "test_json",
            "type": "json",
            "required": False,
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


async def test_create_file_record_and_dict(superuser_client: PocketBase):
    """Test that files and JSON dict/list data can be uploaded together.

    This tests the issue fixed in PR #27 where FileUpload combined with
    dict/list data doesn't work correctly because the multipart transform
    doesn't properly handle JSON serialization.
    """
    coll = await create_file_collection(superuser_client)
    col = superuser_client.collection(coll["id"])
    name1 = uuid4().hex
    name2 = uuid4().hex
    name3 = uuid4().hex
    acontent = uuid4().hex
    bcontent = getrandbits(1024 * 8).to_bytes(1024, "little")
    ccontent = uuid4().hex

    # Test data with complex dict/list structures
    test_json_data = {
        "key1": "value1",
        "key2": "value2",
        "key3": [1, 2, 3],
        "nested": {"inner_key": "inner_value", "inner_list": ["a", "b", "c"]},
    }

    record = await col.create(
        {
            "title": uuid4().hex,
            "image": FileUpload(
                (name1 + ".txt", acontent, "text/plain"),
                (name2 + ".txt", bcontent, "application/octet-stream"),
                (name3 + ".txt", ccontent, "text/plain"),
            ),
            "test_json": test_json_data,
        }
    )

    # Verify the record was created with both files and JSON data
    assert len(record["image"]) == 3
    assert record["test_json"] == test_json_data

    # Find the binary file for testing
    for fn in record["image"]:
        if fn.startswith(name2):
            binary_filename = fn
            break

    # Verify we can retrieve the record and its data
    rel = await col.get_one(record["id"])
    assert len(rel["image"]) == 3
    assert rel["test_json"] == test_json_data

    # Verify file download still works
    rcontent = await superuser_client.files.download_file(coll["id"], rel["id"], binary_filename)
    assert rcontent == bcontent


async def test_create_file_record_and_list(superuser_client: PocketBase):
    """Test that files and JSON list data can be uploaded together."""
    coll = await create_file_collection(superuser_client)
    col = superuser_client.collection(coll["id"])
    name = uuid4().hex
    content = uuid4().hex

    # Test data with list
    test_list_data = [1, 2, "three", {"nested": "object"}, [5, 6]]

    record = await col.create(
        {
            "title": uuid4().hex,
            "image": FileUpload((name + ".txt", content, "text/plain")),
            "test_json": test_list_data,
        }
    )

    # Verify the record was created with both file and JSON list data
    assert len(record["image"]) == 1
    assert record["test_json"] == test_list_data

    # Verify we can retrieve the record and its data
    rel = await col.get_one(record["id"])
    assert len(rel["image"]) == 1
    assert rel["test_json"] == test_list_data


async def test_create_file_record_and_empty_collections(superuser_client: PocketBase):
    """Test that files with empty dict/list data work correctly."""
    coll = await create_file_collection(superuser_client)
    col = superuser_client.collection(coll["id"])
    name = uuid4().hex
    content = uuid4().hex

    record = await col.create(
        {
            "title": uuid4().hex,
            "image": FileUpload((name + ".txt", content, "text/plain")),
            "test_json": {},  # Empty dict
        }
    )

    assert len(record["image"]) == 1
    assert record["test_json"] == {}

    # Test with empty list
    record2 = await col.create(
        {
            "title": uuid4().hex,
            "image": FileUpload((name + "2.txt", content, "text/plain")),
            "test_json": [],  # Empty list
        }
    )

    assert len(record2["image"]) == 1
    assert record2["test_json"] == []


async def test_create_record_dict_without_files(superuser_client: PocketBase):
    """Test that dict/list data works without files (should not trigger the fix)."""
    coll = await create_file_collection(superuser_client)
    col = superuser_client.collection(coll["id"])

    # Test data with complex dict/list structures but no files
    test_json_data = {
        "key1": "value1",
        "key2": "value2",
        "key3": [1, 2, 3],
        "nested": {"inner_key": "inner_value", "inner_list": ["a", "b", "c"]},
    }

    record = await col.create(
        {
            "title": uuid4().hex,
            "test_json": test_json_data,
        }
    )

    # Verify the record was created with JSON data (no files)
    assert len(record["image"]) == 0
    assert record["test_json"] == test_json_data

    # Verify we can retrieve the record and its data
    rel = await col.get_one(record["id"])
    assert len(rel["image"]) == 0
    assert rel["test_json"] == test_json_data


async def test_create_file_record_with_non_serializable_data(superuser_client: PocketBase):
    """Test error handling when dict/list contains non-serializable data."""
    import pytest

    coll = await create_file_collection(superuser_client)
    col = superuser_client.collection(coll["id"])
    name = uuid4().hex
    content = uuid4().hex

    # Create a non-serializable object
    class NonSerializable:
        pass

    # Test data with non-serializable object
    non_serializable_data = {"key1": "value1", "key2": NonSerializable()}

    with pytest.raises(ValueError, match="Failed to serialize field 'test_json' to JSON"):
        await col.create(
            {
                "title": uuid4().hex,
                "image": FileUpload((name + ".txt", content, "text/plain")),
                "test_json": non_serializable_data,
            }
        )
