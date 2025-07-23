# Installation

## Requirements

PocketBase Async requires Python 3.11 or higher. Make sure you have a compatible Python version installed:

```bash
python --version
# Should show Python 3.11.x or higher
```

## Install via pip

The easiest way to install PocketBase Async is using pip:

```bash
pip install pocketbase-async
```

## Install via Poetry

If you're using Poetry for dependency management:

```bash
poetry add pocketbase-async
```

## Development Installation

If you want to contribute to the project or install from source:

```bash
# Clone the repository
git clone https://github.com/thijsmie/pocketbase-async.git
cd pocketbase-async

# Install with poetry (recommended for development)
poetry install

# Or install with pip in development mode
pip install -e .
```

## Verify Installation

To verify that the installation was successful, you can import the library:

```python
from pocketbase import PocketBase

print("PocketBase Async installed successfully!")
```

## Dependencies

PocketBase Async has minimal dependencies:

- **httpx** (>=0.25.1) - For HTTP requests
- **httpx-sse** (>=0.4.0) - For Server-Sent Events (real-time subscriptions)

These will be automatically installed when you install pocketbase-async.

## PocketBase Server

You'll also need a running PocketBase server. You can:

1. **Download PocketBase** from the [official website](https://pocketbase.io/docs/)
2. **Use Docker**: 
   ```bash
   docker run -p 8090:8090 -v /path/to/data:/pb_data ghcr.io/muchobien/pocketbase:latest
   ```
3. **Use PocketHost** for managed hosting

## Next Steps

Once you have both PocketBase Async and a PocketBase server running, you're ready to start building! Check out the [Quick Start](quick-start.md) guide to learn the basics.
