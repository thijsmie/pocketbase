from pocketbase import PocketBase, PocketBaseError


CONNECTION_URL = "http://localhost:8123"
ADMIN_EMAIL = "test@example.com"
ADMIN_PASSWORD = "test"


async def hello_world():
    # Instantiate the PocketBase connector
    pb = PocketBase("http://localhost:8123")

    # Authenticate as an admin
    await pb.admin.auth.with_password(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)

    # Create a collection to store records in
    # It is a base collection (not "view" or "auth") with one column "content"
    # and it will have the regular "id", "created" and "updated" columns.
    try:
        await pb.collections.create(
            {
                "name": "hello_world",
                "type": "base",
                "schema": [
                    {
                        "name": "content",
                        "type": "text",
                        "required": True,
                    },
                ],
            }
        )
    except PocketBaseError:
        # You probably ran this example before, and the collection already exists!
        # No problem, we'll continue as normal :)
        pass
    
    # Get the collection instance we can work with
    collection = pb.collection("hello_world")

    # Add a new record.
    await collection.create(params={"content": "Hello, World!"})

    # All the different ways to get records
    first = await collection.get_first()
    list_records = await collection.get_list(page=1, per_page=10)
    all_records = await collection.get_full_list()
    one = await collection.get_one(record_id=first['id'])

    print(one)

    # Update a record
    updated = await collection.update(
        record_id=one['id'],
        params={'contents': "Good to see you again!"}
    )

    print(updated)

    # Delete a record
    await collection.delete(
        record_id=one['id']
    )



if __name__ == "__main__":
    import asyncio
    asyncio.run(hello_world())
