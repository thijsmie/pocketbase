import base64
import json
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from httpx import Request

from pocketbase.models.dtos import AuthResult, Record
from pocketbase.services.base import Service
from pocketbase.utils.types import JsonType

if TYPE_CHECKING:
    from pocketbase.client import PocketBase, PocketBaseInners


def get_token_payload(token: str | None) -> dict[str, JsonType]:
    if not token:
        return {}

    payload = token.split(".")[1]
    padded = payload + "=" * divmod(len(payload), 4)[1]
    jsondata = base64.urlsafe_b64decode(padded)
    return json.loads(jsondata)


class AuthStore(Service):
    _expiration_threshold_ = 60.0

    def __init__(self, pocketbase: "PocketBase", inners: "PocketBaseInners") -> None:
        super().__init__(pocketbase, inners)
        self._authority: Record | None = None
        self._token: str | None = None
        self._payload: dict[str, JsonType] = {}
        self._refreshing: bool = False

    def set_is_refreshing(self, refreshing: bool) -> None:
        self._refreshing = refreshing

    async def authorize(self, request: Request) -> None:
        if self._token:
            if not self._refreshing and self._is_token_expired() and self._authority:
                col: str = self._authority.get("collectionName", "users")
                await self._pb.collection(col).auth.refresh()

            request.headers["Authorization"] = self._token

    def set_user(self, model: AuthResult) -> None:
        self._authority = model.get("record", self._authority)
        self._token = model.get("token", self._token)
        self._payload = get_token_payload(self._token)

    def clean(self) -> None:
        self._authority = None
        self._token = None
        self._payload = {}

    def _is_token_expired(self) -> bool:
        exp = self._payload.get("exp")
        if exp and isinstance(exp, (float | int)):
            now = datetime.now(tz=UTC).timestamp()
            if now > float(exp) - self._expiration_threshold_:
                return True
        return False
