# Files

File management for uploading, downloading, and serving files.

## FileService

::: pocketbase.services.file.FileService
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### File URLs

```python
from pocketbase import PocketBase

pb = PocketBase('http://localhost:8090')

# Generate file URL
file_url = pb.files.get_url('posts', 'RECORD_ID', 'image.jpg')
print(f"File URL: {file_url}")
# Output: http://localhost:8090/api/files/posts/RECORD_ID/image.jpg

# Thumbnail URL (if thumbnails are enabled)
thumb_url = pb.files.get_url('posts', 'RECORD_ID', 'image.jpg') + '?thumb=200x200'
```

### Downloading Files

```python
# Download original file
file_content = await pb.files.download_file(
    'posts',        # collection
    'RECORD_ID',    # record ID
    'image.jpg'     # filename
)

# Save to disk
with open('downloaded_image.jpg', 'wb') as f:
    f.write(file_content)

# Download thumbnail
thumbnail = await pb.files.download_file(
    'posts', 'RECORD_ID', 'image.jpg',
    options={'thumb': '200x200'}
)

with open('thumbnail.jpg', 'wb') as f:
    f.write(thumbnail)
```

### File Tokens

For protected files that require authentication:

```python
# Get a file token
token = await pb.files.get_token()

# Use token in URL
protected_url = f"{pb.files.get_url('private_docs', 'RECORD_ID', 'document.pdf')}?token={token}"
```

## File Upload

Files are uploaded as part of record creation/updates:

```python
from pocketbase import FileUpload

# Single file upload
with open('image.jpg', 'rb') as f:
    record = await pb.collection('posts').create({
        'title': 'Post with Image',
        'image': FileUpload('image.jpg', f.read(), 'image/jpeg')
    })

# Multiple files
with open('image1.jpg', 'rb') as f1, open('image2.png', 'rb') as f2:
    record = await pb.collection('gallery').create({
        'title': 'Photo Gallery',
        'images': [
            FileUpload('image1.jpg', f1.read(), 'image/jpeg'),
            FileUpload('image2.png', f2.read(), 'image/png')
        ]
    })

# Update with new file
with open('updated_image.jpg', 'rb') as f:
    updated_record = await pb.collection('posts').update('RECORD_ID', {
        'image': FileUpload('updated_image.jpg', f.read(), 'image/jpeg')
    })
```

## File Field Configuration

When creating collections with file fields:

```python
file_field = {
    'name': 'attachments',
    'type': 'file',
    'options': {
        'maxSelect': 5,          # Maximum number of files
        'maxSize': 10485760,     # 10MB per file
        'mimeTypes': [           # Allowed file types
            'image/jpeg',
            'image/png',
            'image/webp',
            'application/pdf',
            'text/plain'
        ],
        'thumbs': [              # Auto-generate thumbnails for images
            '100x100',
            '300x300',
            '800x600'
        ]
    }
}

collection_data = {
    'name': 'documents',
    'type': 'base',
    'fields': [file_field]
}

await pb.collections.create(collection_data)
```

## Working with Different File Types

### Images

```python
# Image with thumbnail generation
image_field = {
    'name': 'photos',
    'type': 'file',
    'options': {
        'maxSelect': 10,
        'maxSize': 5242880,  # 5MB
        'mimeTypes': ['image/jpeg', 'image/png', 'image/webp'],
        'thumbs': ['100x100', '300x300', '800x600']
    }
}

# Upload and get thumbnail
with open('photo.jpg', 'rb') as f:
    record = await pb.collection('photos').create({
        'title': 'My Photo',
        'photo': FileUpload('photo.jpg', f.read(), 'image/jpeg')
    })

# Download different sizes
original = await pb.files.download_file('photos', record['id'], 'photo.jpg')
small_thumb = await pb.files.download_file(
    'photos', record['id'], 'photo.jpg',
    options={'thumb': '100x100'}
)
large_thumb = await pb.files.download_file(
    'photos', record['id'], 'photo.jpg',
    options={'thumb': '800x600'}
)
```

### Documents

```python
# Document upload
document_field = {
    'name': 'files',
    'type': 'file',
    'options': {
        'maxSelect': 5,
        'maxSize': 52428800,  # 50MB
        'mimeTypes': [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ]
    }
}

# Upload documents
with open('document.pdf', 'rb') as f:
    record = await pb.collection('documents').create({
        'title': 'Important Document',
        'file': FileUpload('document.pdf', f.read(), 'application/pdf')
    })
```

### Audio/Video

```python
media_field = {
    'name': 'media',
    'type': 'file',
    'options': {
        'maxSelect': 1,
        'maxSize': 104857600,  # 100MB
        'mimeTypes': [
            'video/mp4',
            'video/webm',
            'audio/mpeg',
            'audio/wav'
        ]
    }
}
```

## File Management Patterns

### File Validation Before Upload

```python
import mimetypes
import os

def validate_file(file_path: str, max_size: int, allowed_types: list[str]) -> bool:
    # Check file size
    if os.path.getsize(file_path) > max_size:
        return False
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type not in allowed_types:
        return False
    
    return True

# Use validation
if validate_file('image.jpg', 5242880, ['image/jpeg', 'image/png']):
    with open('image.jpg', 'rb') as f:
        record = await pb.collection('posts').create({
            'title': 'Validated Upload',
            'image': FileUpload('image.jpg', f.read(), 'image/jpeg')
        })
```

### Batch File Operations

```python
async def upload_multiple_files(collection: str, files: list[str]):
    """Upload multiple files to records"""
    records = []
    
    for file_path in files:
        filename = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        with open(file_path, 'rb') as f:
            record = await pb.collection(collection).create({
                'filename': filename,
                'file': FileUpload(filename, f.read(), mime_type or 'application/octet-stream')
            })
            records.append(record)
    
    return records

# Upload multiple files
file_list = ['doc1.pdf', 'doc2.pdf', 'image.jpg']
uploaded_records = await upload_multiple_files('files', file_list)
```

### File Cleanup

```python
async def cleanup_old_files():
    """Remove old file records and their files"""
    from datetime import datetime, timedelta
    
    # Get records older than 30 days
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
    old_files = await pb.collection('temp_files').get_full_list({
        'filter': f'created < "{thirty_days_ago}"'
    })
    
    # Delete records (files are automatically deleted)
    for record in old_files:
        await pb.collection('temp_files').delete(record['id'])
    
    print(f"Cleaned up {len(old_files)} old files")
```

### Image Processing

```python
from PIL import Image
import io

async def upload_with_processing(image_path: str):
    """Upload image with client-side processing"""
    
    # Process image
    with Image.open(image_path) as img:
        # Resize if too large
        if img.width > 1920 or img.height > 1080:
            img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
        
        # Convert to JPEG and compress
        output = io.BytesIO()
        img.convert('RGB').save(output, format='JPEG', quality=85, optimize=True)
        processed_data = output.getvalue()
    
    # Upload processed image
    record = await pb.collection('photos').create({
        'title': 'Processed Image',
        'image': FileUpload('processed.jpg', processed_data, 'image/jpeg')
    })
    
    return record
```

## File Access Control

### Protected Files

```python
# Create collection with protected files
protected_collection = await pb.collections.create({
    'name': 'private_docs',
    'type': 'base',
    'listRule': '@request.auth.id != ""',  # Authenticated users only
    'viewRule': 'owner = @request.auth.id',  # Only file owner
    'fields': [
        {
            'name': 'title',
            'type': 'text',
            'required': True
        },
        {
            'name': 'file',
            'type': 'file',
            'options': {
                'maxSelect': 1,
                'maxSize': 10485760
            }
        },
        {
            'name': 'owner',
            'type': 'relation',
            'required': True,
            'options': {
                'collectionId': 'users_collection_id'
            }
        }
    ]
})

# Access protected file
token = await pb.files.get_token()
protected_url = f"{pb.files.get_url('private_docs', 'RECORD_ID', 'secret.pdf')}?token={token}"
```

## Error Handling

```python
from pocketbase import PocketBaseError

try:
    file_content = await pb.files.download_file('posts', 'invalid_id', 'file.jpg')
except PocketBaseError as e:
    if e.status == 404:
        print("File not found")
    elif e.status == 403:
        print("Access denied to file")
    else:
        print(f"Error downloading file: {e}")

try:
    token = await pb.files.get_token()
except PocketBaseError as e:
    if e.status == 401:
        print("Authentication required for file token")
    else:
        print(f"Error getting file token: {e}")
```

## Best Practices

### 1. File Size Limits
```python
# Set appropriate limits based on your server capacity
'maxSize': 5242880,  # 5MB for images
'maxSize': 52428800,  # 50MB for documents
```

### 2. MIME Type Restrictions
```python
# Be specific about allowed file types for security
'mimeTypes': [
    'image/jpeg',
    'image/png',
    'image/webp'  # Don't allow generic 'image/*'
]
```

### 3. Thumbnail Generation
```python
# Generate multiple thumbnail sizes for responsive design
'thumbs': ['150x150', '300x300', '600x400', '1200x800']
```

### 4. File Organization
```python
# Use descriptive field names and organize by purpose
{
    'name': 'featured_image',  # Not just 'image'
    'name': 'gallery_photos',  # Not just 'photos'
    'name': 'supporting_documents'  # Not just 'files'
}
```
