# Real-time

Real-time subscriptions for live data updates.

## RealtimeService

::: pocketbase.services.realtime.RealtimeService
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Basic Subscription

```python
from pocketbase import PocketBase

pb = PocketBase('http://localhost:8090')

# Define callback function
async def handle_post_update(event):
    action = event['action']  # 'create', 'update', 'delete'
    record = event['record']
    
    print(f"Post {action}: {record['title']}")
    
    if action == 'create':
        print(f"New post created: {record['title']}")
    elif action == 'update':
        print(f"Post updated: {record['title']}")
    elif action == 'delete':
        print(f"Post deleted: {record['id']}")

# Subscribe to all posts
unsubscribe = await pb.realtime.subscribe('posts', handle_post_update)

# Keep subscription alive (in a real app, this would be your main event loop)
import asyncio
await asyncio.sleep(60)  # Listen for 60 seconds

# Unsubscribe when done
await unsubscribe()
```

### Collection-Specific Subscriptions

```python
# Subscribe to specific collection
async def handle_user_update(event):
    user = event['record']
    if event['action'] == 'create':
        print(f"New user registered: {user['email']}")
    elif event['action'] == 'update':
        print(f"User updated: {user['email']}")

unsubscribe_users = await pb.realtime.subscribe('users', handle_user_update)

# Subscribe to different collections with different handlers
async def handle_comment_update(event):
    comment = event['record']
    print(f"Comment {event['action']} on post {comment['post']}")

unsubscribe_comments = await pb.realtime.subscribe('comments', handle_comment_update)
```

### Record-Specific Subscriptions

```python
# Subscribe to specific record
async def handle_specific_post(event):
    print(f"Specific post updated: {event['record']['title']}")

# Subscribe to specific post by ID
post_id = "POST_RECORD_ID"
unsubscribe_post = await pb.realtime.subscribe(f'posts/{post_id}', handle_specific_post)

# You can also use the RecordService helper
posts = pb.collection('posts')
unsubscribe_post = await posts.subscribe(handle_specific_post, post_id)
```

### Multiple Subscriptions

```python
async def main():
    # Handle different event types
    async def handle_posts(event):
        print(f"📝 Post {event['action']}: {event['record']['title']}")
    
    async def handle_users(event):
        print(f"👤 User {event['action']}: {event['record']['email']}")
    
    async def handle_comments(event):
        print(f"💬 Comment {event['action']}")
    
    # Subscribe to multiple collections
    unsubscribe_posts = await pb.realtime.subscribe('posts', handle_posts)
    unsubscribe_users = await pb.realtime.subscribe('users', handle_users)
    unsubscribe_comments = await pb.realtime.subscribe('comments', handle_comments)
    
    # Your application logic here
    await run_application()
    
    # Cleanup
    await unsubscribe_posts()
    await unsubscribe_users()
    await unsubscribe_comments()

asyncio.run(main())
```

## Event Structure

Real-time events have the following structure:

```python
{
    'action': 'create' | 'update' | 'delete',
    'record': {
        'id': 'RECORD_ID',
        'created': '2024-01-01T12:00:00.000Z',
        'updated': '2024-01-01T12:00:00.000Z',
        'collectionId': 'COLLECTION_ID',
        'collectionName': 'collection_name',
        # ... other record fields
    }
}
```

### Handling Different Actions

```python
async def handle_all_actions(event):
    action = event['action']
    record = event['record']
    
    if action == 'create':
        print(f"➕ New {record['collectionName']}: {record['id']}")
        # Handle new record creation
        await on_record_created(record)
        
    elif action == 'update':
        print(f"✏️ Updated {record['collectionName']}: {record['id']}")
        # Handle record updates
        await on_record_updated(record)
        
    elif action == 'delete':
        print(f"🗑️ Deleted {record['collectionName']}: {record['id']}")
        # Handle record deletion
        await on_record_deleted(record)

async def on_record_created(record):
    # Your create logic here
    pass

async def on_record_updated(record):
    # Your update logic here
    pass

async def on_record_deleted(record):
    # Your delete logic here
    pass
```

## Real-time Patterns

### Chat Application

```python
class ChatApp:
    def __init__(self, pb: PocketBase):
        self.pb = pb
        self.current_user = None
        
    async def start_chat(self, room_id: str):
        # Subscribe to messages in this room
        await self.pb.realtime.subscribe(
            f'messages', 
            self.handle_message,
            options={'filter': f'room = "{room_id}"'}
        )
    
    async def handle_message(self, event):
        if event['action'] == 'create':
            message = event['record']
            if message['author'] != self.current_user['id']:
                print(f"{message['author_name']}: {message['content']}")
    
    async def send_message(self, room_id: str, content: str):
        await self.pb.collection('messages').create({
            'room': room_id,
            'content': content,
            'author': self.current_user['id']
        })

# Usage
chat = ChatApp(pb)
await chat.start_chat('room_123')
```

### Live Dashboard

```python
class LiveDashboard:
    def __init__(self, pb: PocketBase):
        self.pb = pb
        self.stats = {}
        
    async def start_monitoring(self):
        # Monitor different collections
        await self.pb.realtime.subscribe('orders', self.handle_order_update)
        await self.pb.realtime.subscribe('users', self.handle_user_update)
        await self.pb.realtime.subscribe('products', self.handle_product_update)
        
    async def handle_order_update(self, event):
        if event['action'] == 'create':
            self.stats['new_orders'] = self.stats.get('new_orders', 0) + 1
            await self.update_dashboard()
            
    async def handle_user_update(self, event):
        if event['action'] == 'create':
            self.stats['new_users'] = self.stats.get('new_users', 0) + 1
            await self.update_dashboard()
            
    async def update_dashboard(self):
        print(f"📊 Dashboard: Orders: {self.stats.get('new_orders', 0)}, "
              f"Users: {self.stats.get('new_users', 0)}")

# Usage
dashboard = LiveDashboard(pb)
await dashboard.start_monitoring()
```

### Content Moderation

```python
async def moderate_content(event):
    if event['action'] == 'create':
        record = event['record']
        
        # Check for inappropriate content
        if contains_inappropriate_content(record.get('content', '')):
            # Flag for review
            await pb.collection(record['collectionName']).update(record['id'], {
                'flagged': True,
                'status': 'under_review'
            })
            
            # Notify moderators
            await notify_moderators(record)

def contains_inappropriate_content(content: str) -> bool:
    # Your content moderation logic
    banned_words = ['spam', 'inappropriate']
    return any(word in content.lower() for word in banned_words)

# Subscribe to all user-generated content
await pb.realtime.subscribe('posts', moderate_content)
await pb.realtime.subscribe('comments', moderate_content)
```

## Advanced Usage

### Authenticated Subscriptions

```python
# Some subscriptions require authentication
await pb.collection('users').auth.with_password('user@example.com', 'password')

# Now subscribe to private data
async def handle_private_data(event):
    print(f"Private data updated: {event['record']['id']}")

await pb.realtime.subscribe('private_collection', handle_private_data)
```

### Conditional Subscriptions

```python
# Use collection rules to control what updates are sent
# In collection settings, you might have:
# realtimeRule: '@request.auth.id != "" && author = @request.auth.id'

# This means users only get real-time updates for their own records
await pb.realtime.subscribe('user_documents', handle_my_documents)
```

### Connection Management

```python
class RealtimeManager:
    def __init__(self, pb: PocketBase):
        self.pb = pb
        self.subscriptions = {}
        
    async def subscribe_with_retry(self, topic: str, callback, max_retries: int = 3):
        """Subscribe with automatic retry on connection failure"""
        for attempt in range(max_retries):
            try:
                unsubscribe = await self.pb.realtime.subscribe(topic, callback)
                self.subscriptions[topic] = unsubscribe
                print(f"✅ Subscribed to {topic}")
                return unsubscribe
            except Exception as e:
                print(f"❌ Subscription attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    async def cleanup_all(self):
        """Unsubscribe from all topics"""
        for topic, unsubscribe in self.subscriptions.items():
            try:
                await unsubscribe()
                print(f"🔌 Unsubscribed from {topic}")
            except Exception as e:
                print(f"⚠️ Error unsubscribing from {topic}: {e}")
        
        self.subscriptions.clear()

# Usage
manager = RealtimeManager(pb)
await manager.subscribe_with_retry('posts', handle_posts)
await manager.subscribe_with_retry('users', handle_users)

# Later, cleanup
await manager.cleanup_all()
```

## Error Handling

```python
from pocketbase import PocketBaseError

async def safe_subscribe():
    try:
        unsubscribe = await pb.realtime.subscribe('posts', handle_posts)
        return unsubscribe
    except PocketBaseError as e:
        if e.status == 401:
            print("Authentication required for real-time subscription")
        elif e.status == 403:
            print("Not authorized to subscribe to this collection")
        else:
            print(f"Subscription error: {e}")
        return None

# Use safe subscription
unsubscribe = await safe_subscribe()
if unsubscribe:
    # Subscription successful
    pass
```

## Performance Considerations

### 1. Subscription Limits
```python
# Don't create too many subscriptions
# Better to subscribe to collections than individual records when possible

# Good: One subscription for all posts
await pb.realtime.subscribe('posts', handle_all_posts)

# Avoid: Many individual record subscriptions
# for post_id in post_ids:
#     await pb.realtime.subscribe(f'posts/{post_id}', handle_post)
```

### 2. Event Filtering
```python
# Filter events in your callback rather than creating multiple subscriptions
async def handle_posts(event):
    record = event['record']
    
    # Filter by your criteria
    if record.get('category') == 'important':
        await handle_important_post(event)
    elif record.get('author') == current_user_id:
        await handle_my_post(event)
```

### 3. Connection Cleanup
```python
# Always clean up subscriptions
async def main():
    unsubscribes = []
    
    try:
        # Set up subscriptions
        unsubscribes.append(await pb.realtime.subscribe('posts', handle_posts))
        unsubscribes.append(await pb.realtime.subscribe('users', handle_users))
        
        # Your app logic
        await run_app()
        
    finally:
        # Cleanup
        for unsubscribe in unsubscribes:
            await unsubscribe()
```

## WebSocket Connection Details

The real-time service uses Server-Sent Events (SSE) over HTTP, not WebSockets. This provides:

- **Better compatibility** with proxies and firewalls
- **Automatic reconnection** handling
- **Built-in authentication** via standard HTTP headers
- **Simpler debugging** with standard HTTP tools

The connection is automatically managed by the client, including:
- Connection establishment
- Authentication header injection
- Automatic reconnection on failure
- Proper cleanup on client shutdown
