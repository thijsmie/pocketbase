from pocketbase import PocketBase
from pocketbase.services.realtime import RealtimeEvent
from datetime import datetime
import asyncio


CONNECTION_URL = "http://localhost:8123"
ADMIN_EMAIL = "test@example.com"
ADMIN_PASSWORD = "test"


async def callback(event: RealtimeEvent) -> None:
    # This will get called for every event
    # Lets print what is going on
    at = datetime.now().isoformat()
    print(f"[{at}] {event['action'].upper()}: {event['record']}")


async def realtime_updates():
    # Instantiate the PocketBase connector
    pb = PocketBase("http://localhost:8123")

    # Authenticate as an admin
    await pb.admins.auth.with_password(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)

    # Subscribe to all events
    unsubscribe = await pb.realtime.subscribe(
        topic="*",
        callback=callback
    )

    # Wait for ctrl-c
    try:
        while True:
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        pass

    # Unsubscribe using the function returned by the subscribe action
    await unsubscribe()


if __name__ == "__main__":
    asyncio.run(realtime_updates())
