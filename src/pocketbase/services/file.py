from urllib.parse import quote

from pocketbase.models.options import CommonOptions, FileOptions, SendOptions
from pocketbase.services.base import Service


class FileService(Service):
    """Service for file operations including download, URL generation, and tokens.

    This service provides methods to work with files attached to records,
    including downloading files, generating file URLs, and managing file tokens.
    """

    __base_sub_path__ = "/api/files"

    def get_url(self, collection: str, record_id: str, filename: str) -> str:
        """Generate a URL for accessing a file.

        Args:
            collection: The collection name
            record_id: The record ID that owns the file
            filename: The filename

        Returns:
            The complete URL to access the file

        Example:
            ```python
            url = pb.files.get_url('posts', 'RECORD_ID', 'image.jpg')
            # Returns: 'http://localhost:8090/api/files/posts/RECORD_ID/image.jpg'
            ```
        """
        return self._build_url(f"/{quote(collection)}/{quote(record_id)}/{filename}")

    async def download_file(
        self, collection: str, record_id: str, filename: str, options: FileOptions | None = None
    ) -> bytes:
        """Download a file and return its content as bytes.

        Args:
            collection: The collection name
            record_id: The record ID that owns the file
            filename: The filename to download
            options: Additional options including thumbnail settings

        Returns:
            The file content as bytes

        Example:
            ```python
            # Download original file
            content = await pb.files.download_file('posts', 'RECORD_ID', 'image.jpg')

            # Download thumbnail
            thumb_content = await pb.files.download_file(
                'posts', 'RECORD_ID', 'image.jpg',
                options={'thumb': '100x100'}
            )
            ```
        """
        url = f"/{quote(collection)}/{quote(record_id)}/{filename}"
        send_options: SendOptions = {"method": "GET", "params": {"download": True}}
        if options and "params" in options:
            send_options["params"].update(options["params"])

        if options and "headers" in options:
            send_options["headers"] = options["headers"]

        if options and "thumb" in options:
            send_options["params"]["thumb"] = options["thumb"]

        return (await self._send_raw(url, send_options)).content

    async def get_token(self, options: CommonOptions | None = None) -> str:
        """Get a file token for accessing protected files.

        Args:
            options: Additional request parameters

        Returns:
            A file access token string

        Example:
            ```python
            token = await pb.files.get_token()
            # Use token in file URLs for accessing protected files
            ```
        """
        send_options: SendOptions = {"method": "POST"}

        if options:
            send_options.update(options)

        return (await self._send("/token", send_options))["token"]  # type: ignore
