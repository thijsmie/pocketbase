# Records

Record operations for managing data in your PocketBase collections.

## RecordService

::: pocketbase.services.record.RecordService
    options:
      show_root_heading: true
      show_source: false

## CRUD Operations

All RecordService instances inherit from CrudService, providing standard database operations:

::: pocketbase.services.crud.CrudService
    options:
      show_root_heading: true
      show_source: false
      members:
        - get_list
        - get_full_list
        - get_first
        - get_one
        - create
        - update
        - delete

## Usage Examples

### Basic CRUD Operations

```python
from pocketbase import PocketBase

pb = PocketBase('http://localhost:8090')
posts = pb.collection('posts')

# Create a record
new_post = await posts.create({
    'title': 'My Blog Post',
    'content': 'This is the content of my blog post.',
    'published': True
})

# Read records
all_posts = await posts.get_full_list()
published_posts = await posts.get_full_list({
    'filter': 'published = true'
})

# Get a specific record
post = await posts.get_one(new_post['id'])

# Update a record
updated_post = await posts.update(new_post['id'], {
    'title': 'Updated Blog Post Title'
})

# Delete a record
await posts.delete(new_post['id'])
```

### Advanced Querying

```python
# Pagination
page_result = await posts.get_list(
    page=1, 
    per_page=20,
    options={
        'filter': 'published = true',
        'sort': '-created'
    }
)

# Get the first matching record
first_draft = await posts.get_first({
    'filter': 'published = false',
    'sort': '-created'
})

# Complex filtering
recent_popular_posts = await posts.get_full_list({
    'filter': 'created >= "2024-01-01" && views > 100',
    'sort': '-views,-created'
})
```

### Working with Relations

```python
# Create with relations
new_comment = await comments.create({
    'content': 'Great post!',
    'post': post_id,
    'author': user_id
})

# Expand relations when reading
posts_with_authors = await posts.get_full_list({
    'expand': 'author'
})

for post in posts_with_authors:
    author = post['expand']['author']
    print(f"'{post['title']}' by {author['name']}")
```

### File Uploads

```python
from pocketbase import FileUpload

# Create record with file
with open('image.jpg', 'rb') as f:
    new_post = await posts.create({
        'title': 'Post with Image',
        'content': 'Check out this image!',
        'featured_image': FileUpload('image.jpg', f.read(), 'image/jpeg')
    })

# Update with new file
with open('updated_image.jpg', 'rb') as f:
    updated_post = await posts.update(post_id, {
        'featured_image': FileUpload('updated_image.jpg', f.read(), 'image/jpeg')
    })
```

## Real-time Subscriptions

Subscribe to record changes:

```python
# Subscribe to all records in a collection
async def handle_post_update(event):
    action = event['action']  # 'create', 'update', 'delete'
    record = event['record']
    print(f"Post {action}: {record['title']}")

unsubscribe_all = await posts.subscribe_all(handle_post_update)

# Subscribe to a specific record
async def handle_specific_update(event):
    print(f"Specific post updated: {event['record']['title']}")

unsubscribe_one = await posts.subscribe(handle_specific_update, post_id)

# Later, unsubscribe
await unsubscribe_all()
await unsubscribe_one()
```

## Error Handling

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
        print(f"Error {e.status}: {e}")
```

## Filtering Reference

### Basic Operators

```python
# Equality
await posts.get_full_list({'filter': 'status = "published"'})

# Inequality  
await posts.get_full_list({'filter': 'status != "draft"'})

# Comparison
await posts.get_full_list({'filter': 'views > 100'})
await posts.get_full_list({'filter': 'created >= "2024-01-01"'})

# Text search (case-insensitive)
await posts.get_full_list({'filter': 'title ~ "python"'})
await posts.get_full_list({'filter': 'content !~ "spam"'})
```

### Logical Operators

```python
# AND
await posts.get_full_list({
    'filter': 'published = true && views > 50'
})

# OR
await posts.get_full_list({
    'filter': 'status = "draft" || status = "review"'
})

# Grouping
await posts.get_full_list({
    'filter': '(status = "published" || status = "featured") && views > 100'
})
```

### Working with Arrays

```python
# Check if array contains value
await posts.get_full_list({'filter': 'tags ?= "python"'})

# Check if array doesn't contain value  
await posts.get_full_list({'filter': 'tags ?!= "deprecated"'})
```

### Relations

```python
# Filter by related record fields
await posts.get_full_list({'filter': 'author.email = "john@example.com"'})
await posts.get_full_list({'filter': 'category.name = "Technology"'})
```

## Sorting Reference

```python
# Single field ascending
await posts.get_full_list({'sort': 'title'})

# Single field descending  
await posts.get_full_list({'sort': '-created'})

# Multiple fields
await posts.get_full_list({'sort': '-published,title,-created'})

# Sort by relation fields
await posts.get_full_list({'sort': 'author.name,title'})
```
