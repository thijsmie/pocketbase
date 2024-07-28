from typing import Any

from httpx import Response


class PocketBaseError(Exception):
    def __init__(self, url: str, status: int, data: Any) -> None:
        self.url = url
        self.status = status
        self.data = data

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(url={self.url},status={self.status},data={self.data})"

    __str__ = __repr__

    @classmethod
    def raise_for_status(cls, response: Response) -> None:
        if response.status_code == 400:
            raise PocketBaseBadRequestError(str(response.url), response.status_code, response.json())
        elif response.status_code == 401:
            raise PocketBaseUnauthorizedError(str(response.url), response.status_code, response.json())
        elif response.status_code == 403:
            raise PocketBaseForbiddenError(str(response.url), response.status_code, response.json())
        elif response.status_code == 404:
            raise PocketBaseNotFoundError(str(response.url), response.status_code, response.json())
        elif response.status_code == 500:
            raise PocketBaseServerError(str(response.url), response.status_code, response.json())
        elif response.status_code >= 400:
            raise PocketBaseError(str(response.url), response.status_code, response.json())


class PocketBaseNotFoundError(PocketBaseError):
    pass


class PocketBaseBadRequestError(PocketBaseError):
    pass


class PocketBaseUnauthorizedError(PocketBaseError):
    pass


class PocketBaseForbiddenError(PocketBaseError):
    pass


class PocketBaseServerError(PocketBaseError):
    pass
