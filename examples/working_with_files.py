from pocketbase import PocketBase, PocketbaseError, FileUpload


CONNECTION_URL = "http://localhost:8123"
ADMIN_EMAIL = "test@example.com"
ADMIN_PASSWORD = "test"


async def working_with_files():
    # Instantiate the PocketBase connector
    pb = PocketBase("http://localhost:8123")

    # Authenticate as an admin
    await pb.admin.auth.with_password(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)

    # Create a collection
    try:
        await pb.collections.create(
            {
                "name": "working_with_files",
                "type": "base",
                "schema": [
                    {
                        "name": "name",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "file",
                        "type": "file",
                        "required": True,
                    },
                ],
            }
        )
    except PocketbaseError:
        # Collection probably exists
        pass
    
    # Get the collection instance we can work with
    collection = pb.collection("working_with_files")

    # Upload a file
    # Note that FileUpload takes _tuples_, this is because you can have 
    # fields that take multiple files. They are structed as:
    #   tuple(filename, content) or tuple(filename, content, mimetype)
    # Content can be anything file-like such as bytes, a string, a file descriptor from
    # open() or any io stream object. It uses httpx under the hood.
    record = await collection.create(
        params={
            "name": "important_data.txt",
            "file": FileUpload(("important_data.txt", b"The answer to life, the universe and everything is 42."))
        }
    )

    # Download a file
    # Note: the filename here crucially is not what you originally used
    #       but whatever PocketBase decided to call it for storage. You
    #       can always find it back inside the database record.
    file = await pb.files.download_file(
        collection=record['collectionName'],
        record_id=record['id'],
        filename=record['file'] 
    )

    print(file)

    # Update the file
    updated = await collection.update(
        record_id=record['id'],
        params={'file': FileUpload(("important_question.txt", b"But what is the question?"))}
    )

    print(updated)

    # Clean up after ourselves
    await collection.delete(record_id=record['id'])



if __name__ == "__main__":
    import asyncio
    asyncio.run(working_with_files())
