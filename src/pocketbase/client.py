from httpx import AsyncClient, Request, Response

from pocketbase.services.authorization import AuthStore
from pocketbase.services.backup import BackupService
from pocketbase.services.collection import CollectionService
from pocketbase.services.file import FileService
from pocketbase.services.health import HealthService
from pocketbase.services.log import LogService
from pocketbase.services.realtime import RealtimeService
from pocketbase.services.record import RecordService
from pocketbase.services.settings import SettingsService


class PocketBaseInners:
    """Internal class that manages the core components of PocketBase connection.

    This class handles the HTTP client and authentication store internally.
    Users should not interact with this class directly.
    """

    auth: AuthStore
    client: AsyncClient

    def __init__(self, pocketbase: "PocketBase", base_url: str) -> None:
        self.auth = AuthStore(pocketbase, self)
        self.client = AsyncClient(base_url=base_url)


class PocketBase:
    """Async Python client for PocketBase.

    PocketBase is the main entry point for interacting with a PocketBase backend.
    It provides access to collections, authentication, file management, and other services.

    Args:
        base_url: The base URL of your PocketBase instance (e.g., 'http://localhost:8090')

    Example:
        ```python
        from pocketbase import PocketBase

        pb = PocketBase('http://localhost:8090')

        # Authenticate
        await pb.collection('users').auth.with_password('user@example.com', 'password')

        # Create a record
        record = await pb.collection('posts').create({'title': 'Hello World'})
        ```
    """

    _inner_cls_: type[PocketBaseInners] = PocketBaseInners

    def __init__(self, base_url: str) -> None:
        """Initialize a new PocketBase client.

        Args:
            base_url: The base URL of your PocketBase instance
        """
        self._inners = self._inner_cls_(self, base_url)
        self._collections_service: CollectionService = CollectionService(self, self._inners)
        self._file_service: FileService = FileService(self, self._inners)
        self._log_service: LogService = LogService(self, self._inners)
        self._realtime_service: RealtimeService = RealtimeService(self, self._inners)
        self._health_service: HealthService = HealthService(self, self._inners)
        self._backup_service: BackupService = BackupService(self, self._inners)
        self._settings: SettingsService = SettingsService(self, self._inners)
        self._collections: dict[str, RecordService] = {}

    def headers(self) -> dict[str, str]:
        """Get default headers to be sent with requests.

        Returns:
            Dictionary of default headers
        """
        return {"Accept-Language": "en-US"}

    async def before_send(self, request: Request) -> Request | None:
        """Hook called before sending any HTTP request.

        Override this method to modify requests before they are sent.

        Args:
            request: The HTTP request about to be sent

        Returns:
            Modified request or None to proceed with the original request
        """
        pass

    async def after_send(self, response: Response) -> Response | None:
        """Hook called after receiving any HTTP response.

        Override this method to handle responses after they are received.

        Args:
            response: The HTTP response that was received

        Returns:
            Modified response or None to proceed with the original response
        """
        pass

    @property
    def collections(self) -> CollectionService:
        """Access to collection management operations.

        Returns:
            CollectionService for managing collections schema and metadata
        """
        return self._collections_service

    @property
    def files(self) -> FileService:
        """Access to file operations.

        Returns:
            FileService for file upload, download, and URL generation
        """
        return self._file_service

    @property
    def logs(self) -> LogService:
        """Access to application logs.

        Returns:
            LogService for querying application logs
        """
        return self._log_service

    @property
    def realtime(self) -> RealtimeService:
        """Access to realtime subscriptions.

        Returns:
            RealtimeService for subscribing to live data updates
        """
        return self._realtime_service

    @property
    def health(self) -> HealthService:
        """Access to health check operations.

        Returns:
            HealthService for checking application health status
        """
        return self._health_service

    @property
    def backups(self) -> BackupService:
        """Access to backup operations.

        Returns:
            BackupService for creating and managing backups
        """
        return self._backup_service

    def collection(self, id_or_name: str) -> RecordService:
        """Get a service for working with records in a specific collection.

        Args:
            id_or_name: The collection ID or name

        Returns:
            RecordService for CRUD operations on the specified collection

        Example:
            ```python
            users = pb.collection('users')
            posts = pb.collection('posts')
            ```
        """
        if id_or_name not in self._collections:
            self._collections[id_or_name] = RecordService(self, self._inners, id_or_name)
        return self._collections[id_or_name]
