# Client

The `PocketBase` client is the main entry point for interacting with your PocketBase backend.

::: pocketbase.client.PocketBase
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Basic Client Setup

```python
from pocketbase import PocketBase

# Initialize with your PocketBase URL
pb = PocketBase('http://localhost:8090')

# Or use HTTPS for production
pb = PocketBase('https://your-app.pockethost.io')
```

### Custom Headers

You can override the default headers by subclassing:

```python
class CustomPocketBase(PocketBase):
    def headers(self) -> dict[str, str]:
        base_headers = super().headers()
        base_headers.update({
            'X-Custom-Header': 'MyApp/1.0',
            'X-API-Version': '2024-01'
        })
        return base_headers

pb = CustomPocketBase('http://localhost:8090')
```

### Request/Response Hooks

Intercept and modify requests/responses:

```python
from httpx import Request, Response

class LoggingPocketBase(PocketBase):
    async def before_send(self, request: Request) -> Request | None:
        print(f"Sending {request.method} {request.url}")
        return request
    
    async def after_send(self, response: Response) -> Response | None:
        print(f"Received {response.status_code} from {response.url}")
        return response

pb = LoggingPocketBase('http://localhost:8090')
```

### Authentication State

Check the current authentication state:

```python
# Check if authenticated
if pb._inners.auth.is_valid():
    current_user = pb._inners.auth.model
    print(f"Logged in as: {current_user['email']}")
else:
    print("Not authenticated")

# Clear authentication
pb._inners.auth.clear()
```

## Service Properties

The client provides access to various services through properties:

| Property | Service | Description |
|----------|---------|-------------|
| `collections` | [CollectionService](collections.md) | Manage collection schemas |
| `files` | [FileService](files.md) | File operations |
| `logs` | [LogService](logs.md) | Application logs |
| `realtime` | [RealtimeService](realtime.md) | Real-time subscriptions |
| `health` | [HealthService](health.md) | Health checks |
| `backups` | [BackupService](backups.md) | Backup management |

## Collection Access

Get services for specific collections:

```python
# Get services for different collections
users = pb.collection('users')
posts = pb.collection('posts')
comments = pb.collection('comments')

# All return RecordService instances for CRUD operations
new_post = await posts.create({'title': 'Hello World'})
all_users = await users.get_full_list()
```
