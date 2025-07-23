# Basic Usage

This guide covers the fundamental concepts and patterns you'll use when working with PocketBase Async.

## Client Initialization

The `PocketBase` class is your main entry point:

```python
from pocketbase import PocketBase

# Basic initialization
pb = PocketBase('http://localhost:8090')

# You can also use environment variables
import os
pb = PocketBase(os.getenv('POCKETBASE_URL', 'http://localhost:8090'))
```

## Working with Collections

Collections are the core of PocketBase. Each collection represents a table in your database:

```python
# Get a collection service
users = pb.collection('users')
posts = pb.collection('posts')
```

## Filtering and Querying

PocketBase supports powerful filtering using a simple syntax:

```python
# Basic filtering
published_posts = await posts.get_full_list({
    'filter': 'published = true'
})

# Multiple conditions
recent_posts = await posts.get_full_list({
    'filter': 'published = true && created >= "2024-01-01"'
})

# Text search
search_results = await posts.get_full_list({
    'filter': 'title ~ "python"'  # Contains "python"
})

# Complex queries with relationships
user_posts = await posts.get_full_list({
    'filter': 'author.email = "user@example.com"'
})
```

### Filter Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equal | `status = "active"` |
| `!=` | Not equal | `status != "deleted"` |
| `>` | Greater than | `views > 100` |
| `>=` | Greater than or equal | `created >= "2024-01-01"` |
| `<` | Less than | `price < 50` |
| `<=` | Less than or equal | `discount <= 0.2` |
| `~` | Contains (case-insensitive) | `title ~ "python"` |
| `!~` | Does not contain | `content !~ "spam"` |
| `?=` | Any/some (for arrays) | `tags ?= "python"` |

## Sorting

Control the order of your results:

```python
# Single field sorting
posts = await posts.get_full_list({
    'sort': '-created'  # Descending by created date
})

# Multiple field sorting
posts = await posts.get_full_list({
    'sort': '-published,title'  # Published desc, then title asc
})
```

Use `-` prefix for descending order, no prefix for ascending.

## Pagination

Handle large datasets efficiently:

```python
# Get paginated results
page_1 = await posts.get_list(page=1, per_page=20)

print(f"Total items: {page_1['totalItems']}")
print(f"Total pages: {page_1['totalPages']}")
print(f"Current page: {page_1['page']}")

# Process all items across pages
page = 1
while True:
    result = await posts.get_list(
        page=page,
        per_page=50,
        options={'filter': 'published = true'}
    )
    
    # Process items
    for post in result['items']:
        print(post['title'])
    
    # Check if we're done
    if page >= result['totalPages']:
        break
    page += 1

# Or use get_full_list for automatic pagination
all_posts = await posts.get_full_list({
    'filter': 'published = true'
})
```

## Expanding Relations

Load related records in a single request:

```python
# Load posts with author information
posts_with_authors = await posts.get_full_list({
    'expand': 'author'
})

for post in posts_with_authors:
    author = post['expand']['author']
    print(f"'{post['title']}' by {author['name']}")

# Multiple expansions
posts_full = await posts.get_full_list({
    'expand': 'author,category,tags'
})

# Nested expansions
comments_full = await comments.get_full_list({
    'expand': 'post.author'
})
```

## Creating Records

```python
# Simple record creation
new_post = await posts.create({
    'title': 'My Blog Post',
    'content': 'This is the content...',
    'published': False
})

# With file upload
from pocketbase import FileUpload

with open('image.jpg', 'rb') as f:
    new_post = await posts.create({
        'title': 'Post with Image',
        'content': 'Check out this image!',
        'featured_image': FileUpload('image.jpg', f.read(), 'image/jpeg')
    })

# With relations
new_comment = await comments.create({
    'content': 'Great post!',
    'post': new_post['id'],  # Reference to post
    'author': current_user['id']
})
```

## Updating Records

```python
# Partial update
updated_post = await posts.update(post_id, {
    'title': 'Updated Title'
})

# Full replacement (careful!)
updated_post = await posts.update(post_id, {
    'title': 'New Title',
    'content': 'Completely new content',
    'published': True
})

# Update with file
with open('new_image.jpg', 'rb') as f:
    updated_post = await posts.update(post_id, {
        'featured_image': FileUpload('new_image.jpg', f.read(), 'image/jpeg')
    })
```

## Deleting Records

```python
# Delete a single record
await posts.delete(post_id)

# Bulk delete using filters (careful!)
# Note: PocketBase doesn't support bulk delete directly,
# you need to fetch and delete individually
posts_to_delete = await posts.get_full_list({
    'filter': 'published = false && created < "2023-01-01"'
})

for post in posts_to_delete:
    await posts.delete(post['id'])
```

## Error Handling

Always handle potential errors:

```python
from pocketbase import PocketBaseError

try:
    record = await posts.get_one('invalid-id')
except PocketBaseError as e:
    if e.status == 404:
        print("Record not found")
    elif e.status == 403:
        print("Access denied")
    else:
        print(f"Error {e.status}: {e.data}")
```

## Using Request Options

Most methods accept an `options` parameter for additional control:

```python
# Custom headers
record = await posts.get_one(post_id, {
    'headers': {
        'X-Custom-Header': 'value'
    }
})

# Query parameters
records = await posts.get_full_list({
    'params': {
        'custom_param': 'value'
    },
    'filter': 'published = true'
})
```

## Working with Files

```python
# Download a file
file_bytes = await pb.files.download_file(
    'posts',      # collection
    post_id,      # record id
    'image.jpg'   # filename
)

# Save to disk
with open('downloaded_image.jpg', 'wb') as f:
    f.write(file_bytes)

# Get file URL
file_url = pb.files.get_url('posts', post_id, 'image.jpg')
print(f"File available at: {file_url}")

# Get thumbnail
thumbnail_bytes = await pb.files.download_file(
    'posts', post_id, 'image.jpg',
    options={'thumb': '200x200'}
)
```

## Best Practices

### 1. Use Connection Reuse
```python
# Good: Reuse the same client instance
pb = PocketBase('http://localhost:8090')

async def get_posts():
    return await pb.collection('posts').get_full_list()

async def get_users():
    return await pb.collection('users').get_full_list()

# Avoid: Creating new clients for each request
```

### 2. Handle Authentication State
```python
# Check if authenticated
auth_store = pb._inners.auth
if auth_store.is_valid():
    current_user = auth_store.model
    print(f"Logged in as: {current_user['email']}")
else:
    print("Not authenticated")
```

### 3. Use Type Hints
```python
from typing import Dict, List, Any

async def get_published_posts() -> List[Dict[str, Any]]:
    return await pb.collection('posts').get_full_list({
        'filter': 'published = true'
    })
```

### 4. Environment Configuration
```python
import os
from pocketbase import PocketBase

# Use environment variables for configuration
POCKETBASE_URL = os.getenv('POCKETBASE_URL', 'http://localhost:8090')
pb = PocketBase(POCKETBASE_URL)
```

## Next Steps

- **[Authentication](../api/authentication.md)** - Learn about user authentication
- **[Real-time Updates](../api/realtime.md)** - Subscribe to live data changes
- **[File Management](../api/files.md)** - Work with file uploads and downloads
- **[Examples](../examples/hello-world.md)** - See complete examples
