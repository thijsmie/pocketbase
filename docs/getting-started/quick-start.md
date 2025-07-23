# Quick Start

This guide will help you get started with PocketBase Async in just a few minutes.

## Prerequisites

- Python 3.11+ installed
- PocketBase server running (default: http://localhost:8090)
- PocketBase Async installed (`pip install pocketbase-async`)

## Your First Connection

```python
import asyncio
from pocketbase import PocketBase

async def main():
    # Create a client instance
    pb = PocketBase('http://localhost:8090')
    
    # Test the connection
    health = await pb.health.check()
    print(f"PocketBase status: {health}")

# Run the async function
asyncio.run(main())
```

## Creating Your First Collection

Before you can work with records, you need a collection. You can either create one through the PocketBase admin UI or programmatically:

```python
async def create_collection():
    pb = PocketBase('http://localhost:8090')
    
    # First, authenticate as an admin
    # (You'll need to create an admin account in PocketBase first)
    await pb.collection('_superusers').auth.with_password(
        'admin@example.com', 
        'your-admin-password'
    )
    
    # Create a simple collection
    collection_data = {
        'name': 'posts',
        'type': 'base',
        'fields': [
            {
                'name': 'title',
                'type': 'text',
                'required': True
            },
            {
                'name': 'content',
                'type': 'text'
            },
            {
                'name': 'published',
                'type': 'bool'
            }
        ]
    }
    
    new_collection = await pb.collections.create(collection_data)
    print(f"Created collection: {new_collection['name']}")

asyncio.run(create_collection())
```

## Basic CRUD Operations

Once you have a collection, you can perform CRUD operations:

```python
async def crud_example():
    pb = PocketBase('http://localhost:8090')
    
    # Get the posts collection
    posts = pb.collection('posts')
    
    # Create a new record
    new_post = await posts.create({
        'title': 'My First Post',
        'content': 'Hello, PocketBase!',
        'published': True
    })
    print(f"Created post: {new_post['id']}")
    
    # Read records
    all_posts = await posts.get_full_list()
    print(f"Total posts: {len(all_posts)}")
    
    # Read a specific record
    post = await posts.get_one(new_post['id'])
    print(f"Post title: {post['title']}")
    
    # Update a record
    updated_post = await posts.update(new_post['id'], {
        'title': 'My Updated Post Title'
    })
    print(f"Updated title: {updated_post['title']}")
    
    # Delete a record
    await posts.delete(new_post['id'])
    print("Post deleted")

asyncio.run(crud_example())
```

## Working with Authentication

If your collection supports authentication (like a `users` collection):

```python
async def auth_example():
    pb = PocketBase('http://localhost:8090')
    
    users = pb.collection('users')
    
    # Sign up a new user
    try:
        new_user = await users.create({
            'email': 'user@example.com',
            'password': 'securepassword123',
            'passwordConfirm': 'securepassword123',
            'name': 'Test User'
        })
        print(f"Created user: {new_user['email']}")
    except Exception as e:
        print(f"User might already exist: {e}")
    
    # Sign in
    auth_result = await users.auth.with_password(
        'user@example.com', 
        'securepassword123'
    )
    
    print(f"Logged in as: {auth_result['record']['email']}")
    print(f"Auth token: {auth_result['token'][:20]}...")

asyncio.run(auth_example())
```

## Real-time Subscriptions

Subscribe to live updates:

```python
async def realtime_example():
    pb = PocketBase('http://localhost:8090')
    
    # Define a callback function
    async def handle_post_update(event):
        action = event['action']  # 'create', 'update', or 'delete'
        record = event['record']
        print(f"Post {action}: {record.get('title', 'Unknown')}")
    
    # Subscribe to all posts
    unsubscribe = await pb.realtime.subscribe('posts', handle_post_update)
    
    # Keep the connection alive for a while
    print("Listening for updates... (will stop after 30 seconds)")
    await asyncio.sleep(30)
    
    # Unsubscribe
    await unsubscribe()
    print("Unsubscribed from updates")

asyncio.run(realtime_example())
```

## Error Handling

Always handle potential errors:

```python
from pocketbase import PocketBase, PocketBaseError

async def error_handling_example():
    pb = PocketBase('http://localhost:8090')
    posts = pb.collection('posts')
    
    try:
        # Try to get a non-existent record
        post = await posts.get_one('invalid-id')
    except PocketBaseError as e:
        print(f"Error: {e}")
        print(f"Status code: {e.status}")
        print(f"Error data: {e.data}")

asyncio.run(error_handling_example())
```

## Next Steps

Now that you understand the basics, explore more advanced features:

- **[Basic Usage](basic-usage.md)** - Learn about filtering, sorting, and advanced queries
- **[API Reference](../api/client.md)** - Detailed documentation for all methods
- **[Examples](../examples/hello-world.md)** - More comprehensive examples
- **[Real-time Updates](../examples/realtime.md)** - Deep dive into real-time features

## Tips for Success

1. **Use async/await consistently** - This library is built for async code
2. **Handle errors gracefully** - Network requests can fail
3. **Keep your PocketBase server updated** - For the best compatibility
4. **Check the PocketBase docs** - Understanding PocketBase concepts helps a lot
5. **Use type hints** - The library provides full type support for better development experience
