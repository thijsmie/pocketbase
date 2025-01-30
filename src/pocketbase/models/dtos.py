from typing import Generic, Literal, NotRequired, TypedDict, TypeVar

from pocketbase.utils.types import JsonType

_T = TypeVar("_T")


class ListResult(TypedDict, Generic[_T]):
    page: int
    per_page: int
    total_items: int
    total_pages: int
    items: list[_T]


class BaseDict(TypedDict):
    id: str


class SchemaField:
    id: str
    name: str
    type: str
    system: bool
    required: bool
    presentable: bool
    options: dict[str, JsonType]


class CollectionModel(BaseDict):
    name: str
    type: str
    schema: list[SchemaField]
    indexes: list[str]
    system: bool
    options: dict[str, JsonType]
    listRule: NotRequired[str]
    viewRule: NotRequired[str]
    createRule: NotRequired[str]
    updateRule: NotRequired[str]
    deleteRule: NotRequired[str]


class Collection(TypedDict, total=False):
    name: str
    type: str
    schema: list[SchemaField]
    indexes: list[str]
    system: bool
    options: dict[str, JsonType]
    listRule: NotRequired[str]
    viewRule: NotRequired[str]
    createRule: NotRequired[str]
    updateRule: NotRequired[str]
    deleteRule: NotRequired[str]


class ExternalAuthModel(BaseDict):
    recordId: str
    collectionId: str
    provider: str
    providerId: str


class LogModel(BaseDict):
    level: str
    message: str
    data: dict[str, JsonType]


class HourlyStats(TypedDict):
    total: int
    date: str


class HealthCheckResponse(TypedDict):
    code: int
    message: str
    data: JsonType


class AuthProvider(TypedDict):
    name: str
    state: str
    codeVerifier: str
    codeChallenge: str
    codeChallengeMethod: str
    authUrl: str


class Oauth2Payload(TypedDict):
    provider: str
    code: str
    codeVerifier: str
    redirectUrl: str
    createData: NotRequired[dict[str, JsonType]]


class Record(TypedDict, total=False):
    collectionId: str
    collectionName: str
    id: str
    extend: JsonType


class AuthResult(TypedDict):
    token: str
    record: Record
    meta: NotRequired[JsonType]


class OTPResult(TypedDict):
    otpId: str


class RealtimeEvent(TypedDict):
    action: Literal["create", "update", "delete"]
    record: Record


class AuthMethodPassword(TypedDict):
    enabled: bool
    identityFields: list[str]


class AuthMethodOauth2(TypedDict):
    enabled: bool
    providers: list[AuthProvider]


class AuthMethodMfa(TypedDict):
    enabled: bool
    duration: int


class AuthMethodOtp(TypedDict):
    enabled: bool
    duration: int


class AuthMethods(TypedDict):
    password: AuthMethodPassword
    oauth2: AuthMethodOauth2
    mfa: AuthMethodMfa
    otp: AuthMethodOtp
