import asyncio
import json
import logging
from asyncio.tasks import Task
from collections import defaultdict
from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from httpx import ReadError, RemoteProtocolError
from httpx_sse import aconnect_sse

from pocketbase.models.dtos import RealtimeEvent
from pocketbase.models.options import CommonOptions
from pocketbase.services.base import Service

if TYPE_CHECKING:
    from pocketbase.client import PocketBase, PocketBaseInners


Callback = Callable[[RealtimeEvent], Awaitable[None]]


class RealtimeService(Service):
    __base_sub_path__ = "/api/realtime"

    def __init__(self, pocketbase: "PocketBase", inners: "PocketBaseInners") -> None:
        super().__init__(pocketbase, inners)
        self._last_transmit: set[str] = set()
        self._subscriptions: dict[str, list[Callback]] = defaultdict(list)
        self._client_id: str | None = None
        self._connection: Task | None = None

    async def _ensure_connection(self) -> None:
        if self._connection and not self._connection.done():
            # Already running
            return

        sentinel = asyncio.Event()
        self._connection = asyncio.create_task(self._make_connection(sentinel))
        await sentinel.wait()

    async def _make_connection(self, sentinel: asyncio.Event) -> None:
        headers: dict[str, Any] = {}
        last_event_id: Any | None = None
        try:
            while True:
                try:
                    async with aconnect_sse(
                        self._in.client, "GET", self.__base_sub_path__, headers=headers, timeout=900
                    ) as sse:
                        async for message in sse.aiter_sse():
                            if message.event == "PB_CONNECT":
                                self._client_id = message.id
                                await self._transmit_subscriptions(force=True)
                                sentinel.set()
                                continue

                            last_event_id = message.id

                            if message.event in self._subscriptions:
                                for callback in self._subscriptions[message.event]:
                                    try:
                                        await callback(message.json())
                                    except:  # noqa: E722
                                        # We never want any exception to break the realtime handler.
                                        logging.exception("Unhandled exception in realtime event handler")
                except (ReadError, asyncio.TimeoutError, RemoteProtocolError):
                    logging.debug("Connection lost, reconnecting automatically")
                    if last_event_id:
                        headers["Last-Event-ID"] = last_event_id

        finally:
            # Disconnected, reset to plain state.
            logging.exception("Connection to realtime endpoint lost")
            self._connection = None
            self._client_id = None
            self._last_transmit = set()
            sentinel.set()

    async def _transmit_subscriptions(self, force: bool = False) -> None:
        to_transmit = set(self._subscriptions.keys())
        if not force and (to_transmit == self._last_transmit or not self._client_id):
            return

        self._last_transmit = to_transmit

        await self._send_noreturn(
            "", {"method": "POST", "body": {"clientId": self._client_id, "subscriptions": list(to_transmit)}}
        )

    async def subscribe(
        self, topic: str, callback: Callback, options: CommonOptions | None = None
    ) -> Callable[[], Awaitable[None]]:
        key = quote(topic)

        if options:
            value = json.dumps({"query": options["params"], "headers": options["headers"]})
            key += f"?options={quote(value)}"

        async def unsubscribe() -> None:
            try:
                self._subscriptions[key].remove(callback)
                if not self._subscriptions[key]:
                    del self._subscriptions[key]
                if not self._subscriptions:
                    await self.close()
            except ValueError:
                pass

        self._subscriptions[key].append(callback)
        await self._transmit_subscriptions()
        await self._ensure_connection()
        return unsubscribe

    async def close(self) -> None:
        if self._connection:
            self._connection.cancel()
            with suppress(asyncio.CancelledError):
                await self._connection
            self._connection = None
            self._client_id = None
            self._last_transmit = set()
