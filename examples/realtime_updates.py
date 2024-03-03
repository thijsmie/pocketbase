import asyncio
from datetime import datetime

from pocketbase import PocketBase
from pocketbase.services.realtime import RealtimeEvent

CONNECTION_URL = "http://localhost:8123"
ADMIN_EMAIL = "test@example.com"
ADMIN_PASSWORD = "test"
COLLECTION_NAME = "example_collection"


async def callback(event: RealtimeEvent) -> None:
    """Callback function for handling Realtime events.

    Args:
        event (RealtimeEvent): The event object containing information about the record change.
    """
    # This will get called for every event
    # Lets print what is going on
    at = datetime.now().isoformat()
    print(f"[{at}] {event['action'].upper()}: {event['record']}")


async def realtime_updates():
    """Establishes a PocketBase connection, authenticates, and subscribes to Realtime events."""

    try:
        # Instantiate the PocketBase connector
        pb = PocketBase(CONNECTION_URL)

        # Authenticate as an admin
        await pb.admins.auth.with_password(ADMIN_EMAIL, ADMIN_PASSWORD)

        # Get the collection object
        col = pb.collection(COLLECTION_NAME)

        # Subscribe to Realtime events for the specific record ID in the collection
        unsubscribe = await col.subscribe_all(callback=callback)

        # Infinite loop to wait for events (adjusted from the second snippet)
        while True:
            await asyncio.sleep(60 * 60)  # Sleep for an hour to avoid hitting PocketBase's rate limits

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Unsubscribe if still active
        if unsubscribe:
            try:
                await unsubscribe()
            except Exception as e:
                print(f"Error unsubscribing: {e}")


if __name__ == "__main__":
    asyncio.run(realtime_updates())
