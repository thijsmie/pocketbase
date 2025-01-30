from pocketbase import PocketBase


async def test_health(superuser_client: PocketBase):
    health = await superuser_client.health.check({"params": {"fields": "*"}})
    assert health["code"] == 200
    assert health["data"]["canBackup"]
