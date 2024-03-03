import secrets
import socket
from collections.abc import Generator
from contextlib import closing
from pathlib import Path
from subprocess import DEVNULL, Popen
from time import sleep

import pytest
from pocketbase import PocketBase

from tests.prep import ensure_pocketbase_executable


def find_free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def executable() -> Path:
    return ensure_pocketbase_executable()


@pytest.fixture(scope="session")
def admin() -> tuple[str, str]:
    return (f"{secrets.token_urlsafe(6)}@test.com", secrets.token_urlsafe(12))


@pytest.fixture(scope="session")
def port() -> int:
    return find_free_port()


@pytest.fixture(scope="session", autouse=True)
def process(admin: tuple[str, str], port: int, executable: Path, tmpdir_factory) -> Generator[Popen, None, None]:
    directory = tmpdir_factory.mktemp("data")
    # Adding a --dev in the command below can be helpful when debugging tests
    p = Popen(
        args=["_", "serve", f"--dir={directory}", f"--http=127.0.0.1:{port}"],
        executable=executable,
    )
    sleep(0.3)
    Popen(
        args=["_", "admin", "create", admin[0], admin[1], f"--dir={directory}"],
        executable=executable,
        stdout=DEVNULL,
        stderr=DEVNULL,
    ).communicate()
    yield p
    p.kill()
    p.communicate()


@pytest.fixture(scope="session")
def client_url(port):
    return f"http://127.0.0.1:{port}"


@pytest.fixture()
def client(client_url: str) -> PocketBase:
    return PocketBase(client_url)


@pytest.fixture()
async def admin_client(client_url: str, admin: tuple[str, str]) -> PocketBase:
    pb = PocketBase(client_url)
    await pb.admins.auth.with_password(*admin)
    return pb
