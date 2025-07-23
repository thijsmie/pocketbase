# Hello World Example

This example demonstrates the basic usage of pocketbase-async, including authentication, collection management, and CRUD operations.

## Prerequisites

Make sure you have a PocketBase instance running:

```bash
# Download PocketBase (adjust URL for your OS)
wget https://github.com/pocketbase/pocketbase/releases/download/v0.20.0/pocketbase_0.20.0_linux_amd64.zip
unzip pocketbase_0.20.0_linux_amd64.zip

# Run PocketBase
./pocketbase serve --http=127.0.0.1:8123

# In another terminal, create a superuser
./pocketbase superuser create test@example.com test
```

## Code Example

```python
--8<-- "examples/hello_world.py"
```

## What This Example Does

1. **Initialize the Client**: Creates a PocketBase client instance pointing to your local server
2. **Authenticate**: Logs in as a superuser using email and password
3. **Create Collection**: Programmatically creates a new collection with a text field
4. **CRUD Operations**: Demonstrates all basic operations:
   - **Create**: Adds a new record
   - **Read**: Retrieves records using different methods (`get_first`, `get_list`, `get_full_list`, `get_one`)
   - **Update**: Modifies an existing record
   - **Delete**: Removes a record

## Key Features Demonstrated

- **Error Handling**: Uses try/catch to handle cases where the collection already exists
- **Multiple Read Methods**: Shows different ways to fetch records based on your needs
- **Async/Await**: Proper use of async/await throughout the application

## Running the Example

```bash
# Install dependencies
pip install pocketbase-async

# Run the example
python examples/hello_world.py
```

## Expected Output

```
{'id': 'RECORD_ID', 'collectionId': 'COLLECTION_ID', 'collectionName': 'hello_world', 'content': 'Hello, World!', 'created': '2023-01-01 12:00:00.000Z', 'updated': '2023-01-01 12:00:00.000Z'}
{'id': 'RECORD_ID', 'collectionId': 'COLLECTION_ID', 'collectionName': 'hello_world', 'content': 'Good to see you again!', 'created': '2023-01-01 12:00:00.000Z', 'updated': '2023-01-01 12:00:01.000Z'}
```
