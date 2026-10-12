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


class CollectionField(TypedDict):
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
    fields: list[CollectionField]
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
    fields: list[CollectionField]
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
    displayName: str
    logo: str
    state: str
    codeVerifier: str
    codeChallenge: str
    codeChallengeMethod: str
    authURL: str
    authUrl: str  # deprecated upstream, use authURL


class ConfigurableOAuth2Provider(TypedDict):
    name: str
    displayName: str
    logo: str


class Oauth2Payload(TypedDict):
    provider: str
    code: str
    codeVerifier: str
    redirectURL: NotRequired[str]
    redirectUrl: NotRequired[str]  # deprecated upstream, use redirectURL
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


class DryRunViewResult(TypedDict):
    fields: list[CollectionField]
    sample: list[Record]


class SQLResultColumn(TypedDict):
    name: str
    type: str
    nullable: bool


class SQLResult(TypedDict):
    execTime: int
    affectedRows: int
    columns: list[SQLResultColumn]
    rows: list[list[JsonType]]
