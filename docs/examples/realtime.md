# Real-time Updates

This example demonstrates how to subscribe to real-time updates using pocketbase-async's Server-Sent Events (SSE) integration.

## Prerequisites

Make sure you have a PocketBase instance running locally on port 8123 with a superuser account and a collection named `example_collection`. You can create one using the PocketBase admin interface or programmatically.

## Code Example

```python
--8<-- "examples/realtime_updates.py"
```

## What This Example Does

1. **Authentication**: Connects and authenticates as a superuser
2. **Real-time Subscription**: Subscribes to all events in the `example_collection`
3. **Event Handling**: Processes create, update, and delete events as they happen
4. **Graceful Cleanup**: Properly unsubscribes when the application shuts down

## Key Concepts

### Event Types

The callback function receives `RealtimeEvent` objects with:

- `action`: The type of operation (`"create"`, `"update"`, or `"delete"`)
- `record`: The affected record data

### Subscription Types

```python
# Subscribe to all records in a collection
unsubscribe_all = await collection.subscribe_all(callback)

# Subscribe to a specific record
unsubscribe_one = await collection.subscribe(callback, "RECORD_ID")

# Subscribe to any topic (advanced usage)
unsubscribe_topic = await pb.realtime.subscribe("custom_topic", callback)
```

### Event Handling

```python
async def handle_event(event: RealtimeEvent) -> None:
    action = event['action']
    record = event['record']
    
    if action == 'create':
        print(f"New record created: {record['id']}")
    elif action == 'update':
        print(f"Record updated: {record['id']}")
    elif action == 'delete':
        print(f"Record deleted: {record['id']}")
```

## Running the Example

1. **Start PocketBase** with the example collection:
   ```bash
   ./pocketbase serve --http=127.0.0.1:8123
   ```

2. **Create a collection** called `example_collection` through the admin interface or programmatically

3. **Run the example**:
   ```bash
   python examples/realtime_updates.py
   ```

4. **Test the subscription** by modifying records in the collection through the PocketBase admin interface or another script

## Expected Output

When records are modified, you'll see output like:

```
[2023-07-22T14:30:15.123456] CREATE: {'id': 'abc123', 'title': 'New Post', 'created': '2023-07-22 14:30:15.123Z', ...}
[2023-07-22T14:30:45.654321] UPDATE: {'id': 'abc123', 'title': 'Updated Post', 'updated': '2023-07-22 14:30:45.654Z', ...}
[2023-07-22T14:31:20.987654] DELETE: {'id': 'abc123', 'title': 'Updated Post', 'updated': '2023-07-22 14:30:45.654Z', ...}
```

## Advanced Usage

### Multiple Subscriptions

You can subscribe to multiple topics simultaneously:

```python
async def main():
    pb = PocketBase("http://localhost:8123")
    await pb.collection("_superusers").auth.with_password("test@example.com", "test")
    
    # Subscribe to multiple collections
    unsub1 = await pb.collection("posts").subscribe_all(handle_posts)
    unsub2 = await pb.collection("users").subscribe_all(handle_users)
    unsub3 = await pb.collection("comments").subscribe_all(handle_comments)
    
    try:
        # Keep running
        await asyncio.sleep(3600)
    finally:
        # Clean up all subscriptions
        await unsub1()
        await unsub2()
        await unsub3()
```

### Error Handling

```python
async def robust_callback(event: RealtimeEvent) -> None:
    try:
        # Process the event
        await process_event(event)
    except Exception as e:
        print(f"Error processing event: {e}")
        # Log error, retry logic, etc.
```

### Connection Management

The real-time connection is automatically managed, but you can handle connection events:

```python
async def connection_callback(event: RealtimeEvent) -> None:
    if event.get('type') == 'connect':
        print("Connected to real-time updates")
    elif event.get('type') == 'disconnect':
        print("Disconnected from real-time updates")
```

## Use Cases

Real-time subscriptions are perfect for:

- **Live dashboards** that show real-time data changes
- **Chat applications** with instant message delivery
- **Collaborative tools** where multiple users edit the same data
- **Notification systems** that trigger on data changes
- **Live content feeds** that update automatically
