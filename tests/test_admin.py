from uuid import uuid4

import pytest

from pocketbase import PocketBase
from pocketbase.models.dtos import Record
from pocketbase.models.errors import PocketBaseError


async def test_login(superuser_client: PocketBase, superuser: tuple[str, str]):
    assert superuser_client._inners.auth._authority["email"] == superuser[0]


async def create_superuser(superuser_client: PocketBase) -> Record:
    email = f"{uuid4().hex[:16]}@{uuid4().hex[:16]}.com"
    password = uuid4().hex
    return (
        await superuser_client.collection("_superusers").create(
            {
                "email": email,
                "password": password,
            }
        ),
        email,
        password,
    )


async def test_create_superuser(superuser_client: PocketBase):
    superuser, _, _ = await create_superuser(superuser_client)
    # should stay logged in as previous superuser
    assert superuser_client._inners.auth._authority["id"] != superuser["id"]


async def test_login_as_created_superuser(superuser_client: PocketBase, client: PocketBase):
    superuser, email, password = await create_superuser(superuser_client)
    await client.collection("_superusers").auth.with_password(email, password)
    assert client._inners.auth._authority["id"] != superuser_client._inners.auth._authority["id"]
    assert client._inners.auth._authority["id"] == superuser["id"]


async def test_delete_superuser(superuser_client: PocketBase):
    superuser, _, _ = await create_superuser(superuser_client)
    await superuser_client.collection("_superusers").delete(superuser["id"])

    with pytest.raises(PocketBaseError) as e:
        await superuser_client.collection("_superusers").get_one(superuser["id"])

    assert e.value.status == 404


async def test_invalid_login_exception(client: PocketBase):
    with pytest.raises(PocketBaseError) as exc:
        await client.collection("_superusers").auth.with_password(uuid4().hex, uuid4().hex)
    assert exc.value.status == 400  # invalid login


async def test_auth_refresh(superuser_client: PocketBase):
    oldid = superuser_client._inners.auth._authority["id"]
    ar = await superuser_client.collection("_superusers").auth.refresh()
    assert superuser_client._inners.auth._token == ar["token"]
    assert superuser_client._inners.auth._authority["id"] == oldid
