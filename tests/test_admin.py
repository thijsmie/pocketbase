from uuid import uuid4

import pytest
from pocketbase import PocketBase
from pocketbase.models.dtos import AdminModel
from pocketbase.models.errors import PocketbaseError


async def test_login(admin_client: PocketBase, admin: tuple[str, str]):
    assert admin_client._inners.auth._authority["email"] == admin[0]


async def create_admin(admin_client: PocketBase) -> AdminModel:
    email = f"{uuid4().hex[:16]}@{uuid4().hex[:16]}.com"
    password = uuid4().hex
    return (
        await admin_client.admins.create(
            {
                "email": email,
                "password": password,
                "avatar": 8,
            }
        ),
        email,
        password,
    )


async def test_create_admin(admin_client: PocketBase):
    admin, _, _ = await create_admin(admin_client)
    # should stay logged in as previous admin
    assert admin_client._inners.auth._authority["id"] != admin["id"]


async def test_login_as_created_admin(admin_client: PocketBase, client: PocketBase):
    admin, email, password = await create_admin(admin_client)
    await client.admins.auth.with_password(email, password)
    assert client._inners.auth.admin_id != admin_client._inners.auth.admin_id
    assert client._inners.auth.admin_id == admin["id"]


async def test_update_admin(admin_client: PocketBase):
    await admin_client.admins.update(
        admin_client._inners.auth.admin_id,
        {
            "avatar": 4,
        },
    )

    assert admin_client._inners.auth._authority["avatar"] == 4


async def test_delete_admin(admin_client: PocketBase):
    admin, _, _ = await create_admin(admin_client)
    await admin_client.admins.delete(admin["id"])

    with pytest.raises(PocketbaseError) as e:
        await admin_client.admins.get_one(admin["id"])

    assert e.value.status == 404


async def test_invalid_login_exception(client: PocketBase):
    with pytest.raises(PocketbaseError) as exc:
        await client.admins.auth.with_password(uuid4().hex, uuid4().hex)
    assert exc.value.status == 400  # invalid login


async def test_auth_refresh(admin_client: PocketBase):
    oldid = admin_client._inners.auth.admin_id
    ar = await admin_client.admins.auth.refresh()
    assert admin_client._inners.auth._token == ar["token"]
    assert admin_client._inners.auth.admin_id == oldid
