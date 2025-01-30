import asyncio
import json
from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch
from urllib.parse import quote
from uuid import uuid4

import httpx
from httpx_sse import ServerSentEvent

from pocketbase import PocketBase
from pocketbase.services.realtime import RealtimeEvent


async def test_realtime(superuser_client: PocketBase) -> None:
    await superuser_client.collections.create(
        {
            "name": "test",
            "type": "base",
            "fields": [
                {
                    "name": "title",
                    "type": "text",
                    "required": True,
                },
            ],
        }
    )
    col = superuser_client.collection("test")

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


# The test below takes five minutes at least (until we get disconnected)
# so we don't run it normally, you'll have to turn it on manually
# Feature request, configurable timeout for realtime connections?


class MockAsyncIteratorCallable:
    def __init__(self, generator_function):
        self.generator_function = generator_function
        self.case = -1

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            self.case += 1
            return await self.generator_function(self.case)
        except StopIteration:
            raise StopAsyncIteration


async def test_realtime_all_records(superuser_client: PocketBase) -> None:
    def handler(_r):
        return httpx.Response(200, json={})

    transport = httpx.MockTransport(handler)
    pb = PocketBase("http://bla.com")
    pb._inners.client = httpx.AsyncClient(base_url="http://bla.com", transport=transport)

    col = pb.collection("test_realtime_disconnect_all_records")

    event_counter = 0

    async def callback(event: RealtimeEvent) -> None:
        nonlocal event_counter
        event_counter += 1

    async def behaviour(case: int) -> ServerSentEvent:
        match case:
            case 0:
                return ServerSentEvent(event="PB_CONNECT", data=str(uuid4()), id="something")
            case 1:
                return ServerSentEvent(
                    event=quote("test_realtime_disconnect_all_records"),
                    data=json.dumps({"action": "create", "record": {"title": "Hi"}}),
                    id="something",
                )
            case 2:
                await asyncio.sleep(0.02)
                raise TimeoutError()

    @asynccontextmanager
    async def repl_aconnect_sse(*args, **kwargs):
        mock = MagicMock()
        mock.aiter_sse.return_value = MockAsyncIteratorCallable(behaviour)
        yield mock

    with patch("pocketbase.services.realtime.aconnect_sse", repl_aconnect_sse):
        unsub = await col.subscribe_all(callback=callback)
        await asyncio.sleep(0.1)
        await unsub()

    assert event_counter > 1
