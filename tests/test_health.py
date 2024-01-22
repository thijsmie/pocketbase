from pocketbase import PocketBase


async def test_health(admin_client: PocketBase):
    health = await admin_client.health.check({"params": {"fields": "*"}})
    assert health["code"] == 200
    assert health["data"]["canBackup"]
