# noqa: A005

from datetime import UTC, datetime
from typing import TypeAlias, cast

from httpx._types import FileTypes


class FileUpload:
    def __init__(self, *files: FileTypes):
        self.files = files


FileType: TypeAlias = FileTypes
SendableFiles: TypeAlias = list[tuple[str, FileTypes] | tuple[str, FileTypes, str]]
JsonType = None | int | str | bool | list["JsonType"] | dict[str, "JsonType"]
BodyField: TypeAlias = JsonType | FileUpload | datetime
BodyDict: TypeAlias = dict[str, BodyField]


def transform(data: BodyDict) -> tuple[dict[str, JsonType], SendableFiles]:
    files: SendableFiles = []

    for key, value in list(data.items()):
        if isinstance(value, datetime):
            if value.tzinfo is None:
                data[key] = value.isoformat(timespec="milliseconds") + "Z"
            else:
                data[key] = value.astimezone(UTC).isoformat(timespec="milliseconds").split("+")[0] + "Z"
        elif isinstance(value, FileUpload) and value.files:
            files.extend((key, file) for file in value.files)
            del data[key]

    return cast(dict[str, JsonType], data), files
