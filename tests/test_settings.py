from uuid import uuid4

import pytest

from pocketbase import PocketBase, PocketBaseError


async def test_write_setting(superuser_client: PocketBase):
    app_name = uuid4().hex
    await superuser_client._settings.update(
        body={
            "meta": {
                "appName": app_name,
            },
        }
    )
    settings = await superuser_client._settings.get_all()
    assert settings["meta"]["appName"] == app_name


async def test_s3(superuser_client: PocketBase):
    # The context manager pytest.raises works with async code
    with pytest.raises(PocketBaseError) as exc:
        # The new test_s3 method can take 'options'
        await superuser_client._settings.test_s3()
    assert exc.value.status == 400
