# PocketBase Async

An async Python 3.11+ client for [PocketBase](https://pocketbase.io), providing a modern, type-safe interface for interacting with your PocketBase backend.

[![Static Badge](https://img.shields.io/badge/status-beta-blue?style=for-the-badge&label=status)](https://github.com/thijsmie/pocketbase-async)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://github.com/thijsmie/pocketbase-async/blob/main/LICENSE.txt)
[![Checks status](https://img.shields.io/github/actions/workflow/status/thijsmie/pocketbase-async/check.yml?style=for-the-badge&label=Checks)](https://github.com/thijsmie/pocketbase-async/actions)

## Features

- **Async/Await Support**: Built from the ground up with async/await for modern Python applications
- **Type Safety**: Full type hints and mypy compatibility
- **Real-time Subscriptions**: Subscribe to live data updates via Server-Sent Events
- **Authentication**: Support for email/password, OAuth2, and OTP authentication
- **File Management**: Upload, download, and manage files with ease
- **CRUD Operations**: Full support for Create, Read, Update, Delete operations
- **Collection Management**: Programmatically manage collection schemas
- **Health Monitoring**: Check application health and view logs
- **Backup Management**: Create and manage database backups

## Quick Start

```python
from pocketbase import PocketBase

# Initialize the client
pb = PocketBase('http://localhost:8090')

# Authenticate
await pb.collection('users').auth.with_password('user@example.com', 'password')

# Create a record
record = await pb.collection('posts').create({
    'title': 'Hello World',
    'content': 'This is my first post!'
})

# Subscribe to real-time updates
async def handle_update(event):
    print(f"Record {event['action']}: {event['record']}")

unsubscribe = await pb.realtime.subscribe('posts', handle_update)
```

## Why PocketBase Async?

PocketBase is an amazing tool for rapidly building backends, but existing Python SDKs were synchronous while most modern Python applications use async/await. This library was built from scratch to provide:

- **Native async support** - No blocking calls, perfect for web frameworks like FastAPI, Quart, or Sanic
- **Modern Python features** - Takes advantage of Python 3.11+ features and type hints
- **Clean API design** - Intuitive methods that feel natural to Python developers
- **Comprehensive coverage** - Supports all PocketBase features including real-time subscriptions

## Installation

```bash
pip install pocketbase-async
# or with poetry
poetry add pocketbase-async
```

## Requirements

- Python 3.11 or higher
- A running PocketBase instance

## Getting Help

- 📖 **Documentation**: You're reading it! Check the sidebar for detailed guides
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/thijsmie/pocketbase-async/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/thijsmie/pocketbase-async/discussions)
- 📝 **Examples**: Check out the [examples directory](https://github.com/thijsmie/pocketbase-async/tree/main/examples)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/thijsmie/pocketbase-async/blob/main/LICENSE.txt) file for details.
