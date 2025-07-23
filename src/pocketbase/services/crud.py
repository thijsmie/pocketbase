from typing import Generic, TypeVar
from urllib.parse import quote

from pocketbase.models.dtos import ListResult
from pocketbase.models.errors import PocketBaseNotFoundError
from pocketbase.models.options import CommonOptions, FirstOptions, FullListOptions, ListOptions, SendOptions
from pocketbase.services.base import Service
from pocketbase.utils.types import BodyDict

_T = TypeVar("_T")


class CrudService(Service, Generic[_T]):
    """Base service providing CRUD (Create, Read, Update, Delete) operations.

    This is a generic service that other services inherit from to provide
    standard database operations for different types of records.
    """

    async def get_list(
        self,
        page: int = 1,
        per_page: int = 30,
        options: ListOptions | SendOptions | None = None,
    ) -> ListResult[_T]:
        """Retrieve a paginated list of records.

        Args:
            page: Page number (1-based, defaults to 1)
            per_page: Number of records per page (defaults to 30)
            options: Additional options like filters, sorting, or request parameters

        Returns:
            ListResult containing the records and pagination info

        Example:
            ```python
            # Get first page with 10 records
            result = await collection.get_list(page=1, per_page=10)

            # Get filtered records
            result = await collection.get_list(
                options={'filter': 'status="active"', 'sort': '-created'}
            )
            ```
        """
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        send_options["params"] = send_options.get("params", {}).copy()
        send_options["params"]["page"] = page
        send_options["params"]["perPage"] = per_page

        if options and "filter" in options:
            send_options["params"]["filter"] = options["filter"]  # type: ignore
            del send_options["filter"]  # type: ignore

        if options and "sort" in options:
            send_options["params"]["sort"] = options["sort"]  # type: ignore
            del send_options["sort"]  # type: ignore

        return await self._send("", send_options)  # type: ignore

    async def get_full_list(self, options: FullListOptions | None = None) -> list[_T]:
        """Retrieve all records by automatically paginating through all pages.

        Args:
            options: Options including filters, sorting, and batch size

        Returns:
            List of all records matching the criteria

        Warning:
            This method fetches ALL records. Use with caution on large datasets.

        Example:
            ```python
            # Get all records
            all_records = await collection.get_full_list()

            # Get all active records
            active_records = await collection.get_full_list(
                options={'filter': 'status="active"'}
            )
            ```
        """
        list_options: ListOptions = {}
        batch = options.get("batch", 500) if options else 500

        if options:
            list_options.update(options)

        list_options["params"] = list_options.get("params", {}).copy()
        list_options["params"]["skipTotal"] = 1

        page = 1
        items: list[_T] = []
        result = None

        while result is None or len(result["items"]) == batch:
            result = await self.get_list(page, batch, list_options)
            items.extend(result["items"])
            page += 1

        return items

    async def get_first(self, options: FirstOptions | None = None) -> _T:
        """Retrieve the first record matching the criteria.

        Args:
            options: Options including filters and request parameters

        Returns:
            The first record matching the criteria

        Raises:
            PocketBaseNotFoundError: If no records match the criteria

        Example:
            ```python
            # Get first record
            first = await collection.get_first()

            # Get first active record
            first_active = await collection.get_first(
                options={'filter': 'status="active"'}
            )
            ```
        """
        list_options: ListOptions = {}

        if options:
            list_options.update(options)

        list_options["params"] = list_options.get("params", {}).copy()
        list_options["params"]["skipTotal"] = 1
        result = await self.get_list(1, 1, list_options)
        if not result["items"]:
            raise PocketBaseNotFoundError(
                url=self._build_url(""),
                status=404,
                data={"code": 404, "message": "The requested resource wasn't found.", "data": {}},
            )
        return result["items"][0]

    async def get_one(self, record_id: str, options: CommonOptions | None = None) -> _T:
        """Retrieve a single record by its ID.

        Args:
            record_id: The unique identifier of the record
            options: Additional request parameters

        Returns:
            The record with the specified ID

        Raises:
            PocketBaseNotFoundError: If no record exists with the given ID

        Example:
            ```python
            record = await collection.get_one('RECORD_ID')
            ```
        """
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)
            send_options["params"] = send_options.get("params", {}).copy()

        return await self._send(f"/{quote(record_id)}", send_options)  # type: ignore

    async def create(self, params: BodyDict, options: CommonOptions | None = None) -> _T:
        """Create a new record.

        Args:
            params: Dictionary containing the record data
            options: Additional request parameters

        Returns:
            The created record with populated fields like ID and timestamps

        Note:
            If 'password' is provided without 'passwordConfirm',
            'passwordConfirm' will be automatically set to the same value.

        Example:
            ```python
            record = await collection.create({
                'title': 'Hello World',
                'content': 'This is my first post',
                'status': 'active'
            })
            ```
        """
        if "password" in params and "passwordConfirm" not in params:
            params["passwordConfirm"] = params["password"]

        send_options: SendOptions = {"method": "POST", "body": params}

        if options:
            send_options.update(options)
            send_options["params"] = send_options.get("params", {}).copy()

        return await self._send("", send_options)  # type: ignore

    async def update(self, record_id: str, params: BodyDict, options: CommonOptions | None = None) -> _T:
        """Update an existing record.

        Args:
            record_id: The unique identifier of the record to update
            params: Dictionary containing the fields to update
            options: Additional request parameters

        Returns:
            The updated record

        Raises:
            PocketBaseNotFoundError: If no record exists with the given ID

        Example:
            ```python
            updated = await collection.update('RECORD_ID', {
                'title': 'Updated Title',
                'status': 'published'
            })
            ```
        """
        send_options: SendOptions = {"method": "PATCH", "body": params}

        if options:
            send_options.update(options)
            send_options["params"] = send_options.get("params", {}).copy()

        return await self._send(f"/{quote(record_id)}", send_options)  # type: ignore

    async def delete(self, record_id: str, options: CommonOptions | None = None) -> None:
        """Delete a record.

        Args:
            record_id: The unique identifier of the record to delete
            options: Additional request parameters

        Raises:
            PocketBaseNotFoundError: If no record exists with the given ID

        Example:
            ```python
            await collection.delete('RECORD_ID')
            ```
        """
        send_options: SendOptions = {"method": "DELETE"}

        if options:
            send_options.update(options)
            send_options["params"] = send_options.get("params", {}).copy()

        await self._send_noreturn(f"/{quote(record_id)}", send_options)
