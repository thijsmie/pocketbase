from httpx import AsyncClient, Request, Response

from pocketbase.services.admin import AdminService
from pocketbase.services.authorization import AuthStore
from pocketbase.services.backup import BackupService
from pocketbase.services.collection import CollectionService
from pocketbase.services.file import FileService
from pocketbase.services.health import HealthService
from pocketbase.services.log import LogService
from pocketbase.services.realtime import RealtimeService
from pocketbase.services.record import RecordService


class PocketBaseInners:
    auth: AuthStore
    client: AsyncClient

    def __init__(self, pocketbase: "PocketBase", base_url: str) -> None:
        self.auth = AuthStore(pocketbase, self)
        self.client = AsyncClient(base_url=base_url)


class PocketBase:
    _inner_cls_: type[PocketBaseInners] = PocketBaseInners

    def __init__(self, base_url: str) -> None:
        self._inners = self._inner_cls_(self, base_url)
        self._admin_service: AdminService = AdminService(self, self._inners)
        self._collections_service: CollectionService = CollectionService(self, self._inners)
        self._file_service: FileService = FileService(self, self._inners)
        self._log_service: LogService = LogService(self, self._inners)
        self._realtime_service: RealtimeService = RealtimeService(self, self._inners)
        self._health_service: HealthService = HealthService(self, self._inners)
        self._backup_service: BackupService = BackupService(self, self._inners)
        self._collections: dict[str, RecordService] = {}

    def headers(self) -> dict[str, str]:
        return {"Accept-Language": "en-US"}

    async def before_send(self, request: Request) -> Request | None:
        pass

    async def after_send(self, response: Response) -> Response | None:
        pass

    @property
    def admins(self) -> AdminService:
        return self._admin_service

    @property
    def collections(self) -> CollectionService:
        return self._collections_service

    @property
    def files(self) -> FileService:
        return self._file_service

    @property
    def logs(self) -> LogService:
        return self._log_service

    @property
    def realtime(self) -> RealtimeService:
        return self._realtime_service

    @property
    def health(self) -> HealthService:
        return self._health_service

    @property
    def backups(self) -> BackupService:
        return self._backup_service

    def collection(self, id_or_name: str) -> RecordService:
        if id_or_name not in self._collections:
            self._collections[id_or_name] = RecordService(self, self._inners, id_or_name)
        return self._collections[id_or_name]
