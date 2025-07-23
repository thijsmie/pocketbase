"""PocketBase Async - An async Python SDK for PocketBase.

This package provides an async Python interface for interacting with PocketBase,
a lightweight backend-as-a-service solution.

Basic usage:
    ```python
    from pocketbase import PocketBase

    pb = PocketBase('http://localhost:8090')

    # Authenticate
    await pb.collection('users').auth.with_password('user@example.com', 'password')

    # Create a record
    record = await pb.collection('posts').create({'title': 'Hello World'})

    # Query records
    records = await pb.collection('posts').get_list()
    ```
"""

"""PocketBase Async - An async Python client for PocketBase.

This package provides an async Python client for interacting with PocketBase,
a realtime backend service. It supports all major PocketBase features including
authentication, CRUD operations, real-time subscriptions, and file management.

Example:
    ```python
    from pocketbase import PocketBase
    
    # Initialize client
    pb = PocketBase('http://localhost:8090')
    
    # Authenticate
    await pb.collection('users').auth.with_password('user@example.com', 'password')
    
    # Create a record
    record = await pb.collection('posts').create({'title': 'Hello World'})
    
    # Subscribe to real-time updates
    async def handle_update(event):
        print(f"Record {event['action']}: {event['record']}")
    
    unsubscribe = await pb.realtime.subscribe('posts', handle_update)
    ```

Main Classes:
    PocketBase: The main client class for connecting to PocketBase
    PocketBaseError: Base exception class for PocketBase-related errors
    FileUpload: Type for file uploads
"""

from pocketbase.client import PocketBase
from pocketbase.models.errors import PocketBaseError
from pocketbase.utils.types import FileUpload

__all__ = ["FileUpload", "PocketBase", "PocketBaseError"]
