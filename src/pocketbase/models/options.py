from typing import Literal, TypedDict

from httpx._types import PrimitiveData

from pocketbase.utils.types import BodyDict, SendableFiles


class SendOptions(TypedDict, total=False):
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    headers: dict[str, str]
    body: BodyDict
    params: dict[str, PrimitiveData]
    files: SendableFiles


class CommonOptions(TypedDict, total=False):
    headers: dict[str, str]
    params: dict[str, PrimitiveData]


class ListOptions(CommonOptions, total=False):
    sort: str
    filter: str


class FullListOptions(ListOptions, total=False):
    batch: int


class FirstOptions(CommonOptions, total=False):
    filter: str


class LogStatsOptions(CommonOptions, total=False):
    filter: str


class FileOptions(CommonOptions, total=False):
    thumb: str
