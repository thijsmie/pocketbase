import asyncio

from pocketbase import PocketBase
from pocketbase.models.dtos import CollectionModel
from pocketbase.services.realtime import RealtimeEvent


async def test_realtime(admin_client: PocketBase) -> CollectionModel:
    await admin_client.collections.create(
        {
            "name": "test",
            "type": "base",
            "schema": [
                {
                    "name": "title",
                    "type": "text",
                    "required": True,
                },
            ],
        }
    )
    col = admin_client.collection("test")

    event_trigger = asyncio.Event()
    event_payload: RealtimeEvent | None = None

    async def test(event: RealtimeEvent) -> None:
        nonlocal event_trigger, event_payload
        event_payload = event
        event_trigger.set()

    unsub = await col.subscribe_all(callback=test)
    record = await col.create({"title": "hi"})

    async with asyncio.timeout(0.5):
        await event_trigger.wait()

    assert event_payload
    assert event_payload["action"] == "create"
    assert event_payload["record"] == record
    await unsub()

    event_trigger.clear()
    unsub = await col.subscribe(callback=test, record_id=record["id"])
    record = await col.update(record["id"], {"title": "ho"})

    async with asyncio.timeout(0.5):
        await event_trigger.wait()

    assert event_payload
    assert event_payload["action"] == "update"
    assert event_payload["record"] == record
    await unsub()
