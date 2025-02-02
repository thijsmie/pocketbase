import asyncio

from pocketbase import PocketBase


async def test_backups(superuser_client: PocketBase):
    bk = await superuser_client.backups.get_full_list()
    await superuser_client.backups.create("test.zip")
    bk2 = await superuser_client.backups.get_full_list()

    assert len(bk) == len(bk2) - 1
    assert any(b["key"] == "test.zip" for b in bk2)

    await superuser_client.backups.restore("test.zip")
    backup = await superuser_client.backups.download("test.zip")
    await superuser_client.backups.delete("test.zip")
    bk3 = await superuser_client.backups.get_full_list()

    assert len(bk) == len(bk3)
    assert not any(b["key"] == "test.zip" for b in bk3)

    await superuser_client.backups.upload(("test.zip", backup))
    bk2 = await superuser_client.backups.get_full_list()

    assert len(bk) == len(bk2) - 1
    assert any(b["key"] == "test.zip" for b in bk2)

    assert "token=" in await superuser_client.backups.get_download_url("test.zip")

    # This takes a couple seconds and can disturb the next test
    await superuser_client.backups.restore("test.zip")
    await asyncio.sleep(5)
