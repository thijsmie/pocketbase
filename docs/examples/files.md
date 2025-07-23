# Working with Files

This example demonstrates file upload, download, and management using pocketbase-async.

## Prerequisites

Make sure you have a PocketBase instance running locally on port 8123 with a superuser account (see [Hello World Example](hello-world.md) for setup instructions).

## Code Example

```python
--8<-- "examples/working_with_files.py"
```

## What This Example Does

1. **Collection Setup**: Creates a collection with both text and file fields
2. **File Upload**: Demonstrates how to upload files using the `FileUpload` helper
3. **File Download**: Shows how to download files from records
4. **File Update**: Updates an existing file attachment
5. **Cleanup**: Removes the test record

## Key Concepts

### FileUpload Helper

The `FileUpload` class is a convenience wrapper for file uploads. It accepts tuples in the format:

- `(filename, content)` - Basic file upload
- `(filename, content, mimetype)` - File upload with explicit MIME type

The `content` can be:
- Bytes (`b"content"`)
- String (`"content"`)
- File descriptor from `open()`
- Any IO stream object

### File Storage

When files are uploaded to PocketBase:
- PocketBase generates unique filenames for storage
- The original filename is not preserved in the file system
- Use the filename from the record data when downloading

### File URLs

You can also generate URLs for files without downloading them:

```python
# Get file URL
url = pb.files.get_url(
    collection="working_with_files",
    record_id=record["id"], 
    filename=record["file"]
)
print(f"File URL: {url}")
```

## Running the Example

```bash
# Install dependencies
pip install pocketbase-async

# Run the example
python examples/working_with_files.py
```

## Expected Output

```
b'The answer to life, the universe and everything is 42.'
{'id': 'RECORD_ID', 'collectionId': 'COLLECTION_ID', 'collectionName': 'working_with_files', 'name': 'important_data.txt', 'file': 'new_filename.txt', 'created': '2023-01-01 12:00:00.000Z', 'updated': '2023-01-01 12:00:01.000Z'}
```

## Advanced File Operations

### Multiple Files

For fields that accept multiple files:

```python
record = await collection.create(params={
    "name": "Multiple files example",
    "files": [  # Note: field must be configured to accept multiple files
        FileUpload(("file1.txt", b"Content 1")),
        FileUpload(("file2.txt", b"Content 2")),
    ]
})
```

### File Thumbnails

For image files, you can request thumbnails:

```python
# Download thumbnail (100x100 pixels)
thumbnail = await pb.files.download_file(
    collection="images",
    record_id=record["id"],
    filename=record["image"],
    options={"thumb": "100x100"}
)
```

### Protected Files

For accessing protected files, you may need a file token:

```python
# Get file access token
token = await pb.files.get_token()

# Use token in requests or URLs as needed
```
