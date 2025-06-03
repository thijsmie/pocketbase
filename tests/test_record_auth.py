import asyncio
from uuid import uuid4

import pytest

from pocketbase import PocketBase
from pocketbase.models.dtos import Record
from pocketbase.models.errors import PocketBaseError
from tests.conftest import SMTP_HOST, SMTP_PORT


@pytest.fixture
async def user(superuser_client: PocketBase) -> tuple[Record, str, str]:
    email = f"{uuid4().hex[:16]}@{uuid4().hex[:16]}.com"
    password = uuid4().hex
    await superuser_client.collection("users").create(
        {
            "email": email,
            "password": password,
            "passwordConfirm": password,
            "verified": False,
        }
    )
    return email, password


@pytest.fixture
async def set_smtp_server(superuser_client: PocketBase):
    await superuser_client._settings.update(
        body={
            "smtp": {
                "enabled": True,
                "host": SMTP_HOST,
                "port": SMTP_PORT,
            }
        }
    )


async def test_login_user(client: PocketBase, user: tuple[str, str]):
    client._inners.auth.clean()
    await client.collection("users").auth.with_password(*user)

    assert client._inners.auth._authority["collectionName"] == "users"
    assert client._inners.auth._authority["email"] == user[0]
    assert client._inners.auth._token is not None


async def test_auth_refresh(client: PocketBase, user: tuple[str, str]):
    client._inners.auth.clean()
    await client.collection("users").auth.with_password(*user)
    await client.collection("users").auth.refresh()


async def test_delete_user(superuser_client: PocketBase, client: PocketBase, user: tuple[str, str]):
    await client.collection("users").auth.with_password(*user)
    user = await superuser_client.collection("users").get_first({"filter": f'email = "{user[0]}"'})
    await superuser_client.collection("users").delete(user["id"])


async def test_invalid_login_exception(client: PocketBase):
    with pytest.raises(PocketBaseError) as exc:
        await client.collection("users").auth.with_password(uuid4().hex, uuid4().hex)
    assert exc.value.status == 400


async def test_list_auth_methods(client: PocketBase):
    val = await client.collection("users").auth.methods()
    assert isinstance(val["password"]["enabled"], bool)
    assert isinstance(val["oauth2"]["enabled"], bool)
    assert isinstance(val["oauth2"]["providers"], list)
    assert isinstance(val["mfa"]["enabled"], bool)


async def test_request_password_reset(client: PocketBase, user: tuple[str, str], smtp_server, set_smtp_server):
    email = user[0]
    await client.collection("users").auth.request_password_reset(email)
    await asyncio.sleep(1)
    messages = smtp_server["handler"].messages
    assert len(messages) > 0, "No password reset request received"
    email_content = messages[-1].content.decode()
    assert ">Reset password<" in email_content, "Password reset link not found in email content"
