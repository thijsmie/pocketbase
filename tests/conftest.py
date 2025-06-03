import secrets
import socket
from collections.abc import AsyncGenerator, Generator
from contextlib import closing
from pathlib import Path
from subprocess import DEVNULL, Popen
from time import sleep

import pytest
from aiosmtpd.controller import Controller

from pocketbase import PocketBase
from tests.prep import ensure_pocketbase_executable

SMTP_HOST = "localhost"


class MessageHandler:
    def __init__(self):
        self.messages = []

    async def handle_DATA(self, _server, _session, envelope):
        self.messages.append(envelope)
        return "250 Message accepted for delivery"


@pytest.fixture(scope="function")
async def smtp_server(superuser_client: PocketBase, port_smtp: int) -> AsyncGenerator[MessageHandler, None, None]:
    handler = MessageHandler()
    controller = Controller(handler, hostname=SMTP_HOST, port=port_smtp)
    controller.start()

    await superuser_client._settings.update(
        body={
            "smtp": {
                "enabled": True,
                "host": SMTP_HOST,
                "port": port_smtp,
            }
        }
    )

    try:
        yield {
            "host": SMTP_HOST,
            "port": port_smtp,
            "handler": handler,
        }
    finally:
        controller.stop()


def find_free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def executable() -> Path:
    return ensure_pocketbase_executable()


@pytest.fixture(scope="session")
def superuser() -> tuple[str, str]:
    return (f"{secrets.token_urlsafe(6)}@test.com", secrets.token_urlsafe(12))


@pytest.fixture(scope="session")
def port() -> int:
    return find_free_port()


@pytest.fixture(scope="session")
def port_smtp() -> int:
    return find_free_port()


@pytest.fixture(scope="session", autouse=True)
def process(superuser: tuple[str, str], port: int, executable: Path, tmpdir_factory) -> Generator[Popen, None, None]:
    directory = tmpdir_factory.mktemp("data")
    # Adding a --dev in the command below can be helpful when debugging tests
    p = Popen(
        args=["_", "serve", f"--dir={directory}", f"--http=127.0.0.1:{port}"],
        executable=executable,
    )
    sleep(0.3)
    Popen(
        args=["_", "superuser", "create", superuser[0], superuser[1], f"--dir={directory}"],
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
async def superuser_client(client_url: str, superuser: tuple[str, str]) -> PocketBase:
    pb = PocketBase(client_url)
    await pb.collection("_superusers").auth.with_password(*superuser)
    return pb
