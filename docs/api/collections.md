# Collections

Collection management for PocketBase schemas and metadata.

## CollectionService

::: pocketbase.services.collection.CollectionService
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Creating Collections

```python
from pocketbase import PocketBase

pb = PocketBase('http://localhost:8090')

# First authenticate as admin
await pb.collection('_superusers').auth.with_password(
    'admin@example.com', 
    'admin_password'
)

# Create a simple blog posts collection
posts_collection = await pb.collections.create({
    'name': 'posts',
    'type': 'base',
    'fields': [
        {
            'name': 'title',
            'type': 'text',
            'required': True,
            'min': 5,
            'max': 200
        },
        {
            'name': 'content',
            'type': 'editor',
            'required': True
        },
        {
            'name': 'published',
            'type': 'bool'
        },
        {
            'name': 'author',
            'type': 'relation',
            'required': True,
            'options': {
                'collectionId': 'users_collection_id',
                'cascadeDelete': False,
                'minSelect': 1,
                'maxSelect': 1
            }
        },
        {
            'name': 'tags',
            'type': 'select',
            'options': {
                'maxSelect': 5,
                'values': ['python', 'javascript', 'web', 'tutorial', 'news']
            }
        },
        {
            'name': 'featured_image',
            'type': 'file',
            'options': {
                'maxSelect': 1,
                'maxSize': 5242880,  # 5MB
                'mimeTypes': ['image/jpeg', 'image/png', 'image/webp']
            }
        }
    ]
})

print(f"Created collection: {posts_collection['name']}")
```

### Reading Collections

```python
# Get all collections
all_collections = await pb.collections.get_full_list()

for collection in all_collections:
    print(f"Collection: {collection['name']} ({collection['type']})")

# Get a specific collection
posts_collection = await pb.collections.get_one('posts')
print(f"Posts collection has {len(posts_collection['fields'])} fields")

# Get collections with filtering
base_collections = await pb.collections.get_full_list({
    'filter': 'type = "base"'
})
```

### Updating Collections

```python
# Add a new field to existing collection
updated_collection = await pb.collections.update('posts', {
    'fields': [
        # ... existing fields ...
        {
            'name': 'views',
            'type': 'number',
            'min': 0
        }
    ]
})

# Update collection settings
await pb.collections.update('posts', {
    'listRule': 'published = true',  # Public can only see published posts
    'viewRule': 'published = true || author = @request.auth.id',  # Authors can see their drafts
    'createRule': '@request.auth.id != ""',  # Only authenticated users can create
    'updateRule': 'author = @request.auth.id',  # Only author can update
    'deleteRule': 'author = @request.auth.id'   # Only author can delete
})
```

### Importing/Exporting Collections

```python
# Export current collections
current_collections = await pb.collections.get_full_list()

# Save to file for backup
import json
with open('collections_backup.json', 'w') as f:
    json.dump(current_collections, f, indent=2)

# Import collections from backup
with open('collections_backup.json', 'r') as f:
    collections_data = json.load(f)

await pb.collections.import_collections(
    collections_data,
    delete_missing=False  # Don't delete existing collections not in import
)

# Replace all collections (be careful!)
await pb.collections.import_collections(
    collections_data,
    delete_missing=True  # This will delete collections not in the import
)
```

## Field Types Reference

### Text Fields
```python
{
    'name': 'title',
    'type': 'text',
    'required': True,
    'min': 1,
    'max': 255,
    'pattern': '^[A-Za-z0-9 ]+$'  # Optional regex pattern
}
```

### Number Fields
```python
{
    'name': 'price',
    'type': 'number',
    'required': True,
    'min': 0,
    'max': 999999.99
}
```

### Boolean Fields
```python
{
    'name': 'is_active',
    'type': 'bool'
}
```

### Email Fields
```python
{
    'name': 'email',
    'type': 'email',
    'required': True
}
```

### URL Fields
```python
{
    'name': 'website',
    'type': 'url'
}
```

### Date Fields
```python
{
    'name': 'published_date',
    'type': 'date',
    'required': True
}
```

### Select Fields
```python
{
    'name': 'status',
    'type': 'select',
    'required': True,
    'options': {
        'maxSelect': 1,
        'values': ['draft', 'published', 'archived']
    }
}

# Multi-select
{
    'name': 'tags',
    'type': 'select',
    'options': {
        'maxSelect': 5,
        'values': ['python', 'javascript', 'tutorial', 'news']
    }
}
```

### Relation Fields
```python
{
    'name': 'author',
    'type': 'relation',
    'required': True,
    'options': {
        'collectionId': 'users_collection_id',
        'cascadeDelete': False,
        'minSelect': 1,
        'maxSelect': 1,
        'displayFields': ['name', 'email']  # Fields to show in admin UI
    }
}
```

### File Fields
```python
{
    'name': 'attachments',
    'type': 'file',
    'options': {
        'maxSelect': 10,
        'maxSize': 10485760,  # 10MB per file
        'mimeTypes': [
            'image/jpeg',
            'image/png',
            'application/pdf',
            'text/plain'
        ],
        'thumbs': ['100x100', '300x300']  # Auto-generate thumbnails
    }
}
```

### JSON Fields
```python
{
    'name': 'metadata',
    'type': 'json'
}
```

### Editor Fields (Rich Text)
```python
{
    'name': 'content',
    'type': 'editor',
    'required': True
}
```

## Collection Types

### Base Collections
```python
{
    'name': 'posts',
    'type': 'base',
    'fields': [...]
}
```

### Auth Collections
```python
{
    'name': 'users',
    'type': 'auth',
    'options': {
        'allowEmailAuth': True,
        'allowOAuth2Auth': True,
        'allowUsernameAuth': False,
        'requireEmail': True,
        'manageRule': None,  # Who can manage users
        'allowOAuth2Auth': True,
        'oauth2': {
            'enabled': True,
            'providers': [
                {
                    'name': 'google',
                    'clientId': 'your_google_client_id',
                    'clientSecret': 'your_google_client_secret'
                }
            ]
        }
    },
    'fields': [
        {
            'name': 'name',
            'type': 'text',
            'required': True
        },
        {
            'name': 'avatar',
            'type': 'file',
            'options': {
                'maxSelect': 1,
                'mimeTypes': ['image/jpeg', 'image/png']
            }
        }
    ]
}
```

### View Collections
```python
{
    'name': 'popular_posts',
    'type': 'view',
    'options': {
        'query': 'SELECT id, title, views FROM posts WHERE views > 100 ORDER BY views DESC'
    }
}
```

## Access Rules

Define who can access records in your collections:

```python
collection_rules = {
    'listRule': 'published = true',  # Public listing rule
    'viewRule': 'published = true || author = @request.auth.id',  # Who can view records
    'createRule': '@request.auth.id != ""',  # Who can create records
    'updateRule': 'author = @request.auth.id',  # Who can update records
    'deleteRule': 'author = @request.auth.id'   # Who can delete records
}

await pb.collections.update('posts', collection_rules)
```

### Rule Examples

```python
# Public read, authenticated write
'listRule': '',  # Everyone can list
'viewRule': '',  # Everyone can view
'createRule': '@request.auth.id != ""',  # Must be logged in
'updateRule': '@request.auth.id != ""',  # Must be logged in

# Author-only access
'createRule': '@request.auth.id != ""',
'updateRule': 'author = @request.auth.id',
'deleteRule': 'author = @request.auth.id',

# Admin-only management
'createRule': '@request.auth.role = "admin"',
'updateRule': '@request.auth.role = "admin"',
'deleteRule': '@request.auth.role = "admin"',

# Time-based rules
'listRule': 'published_date <= @now',
'viewRule': 'published_date <= @now || author = @request.auth.id',

# Complex rules
'updateRule': 'author = @request.auth.id && status != "published"'  # Can't edit published posts
```

## Error Handling

```python
from pocketbase import PocketBaseError

try:
    collection = await pb.collections.create(collection_data)
except PocketBaseError as e:
    if e.status == 400:
        print("Invalid collection data:", e.data)
    elif e.status == 403:
        print("Not authorized to create collections")
    else:
        print(f"Error creating collection: {e}")
```
