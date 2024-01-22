import asyncio

from pocketbase import PocketBase


async def test_get_logs(admin_client: PocketBase):
    """
    Note that this test doesn't really test this properly
    As there are probably no logs in the api yet.
    """

    # Empirically: logs get added slowly, this is enough to ensure there is logs
    await admin_client.logs.get_list()
    await asyncio.sleep(4)
    logs = await admin_client.logs.get_list()
    await admin_client.logs.get_list(options={"filter": "level>0"})
    await admin_client.logs.get_stats()
    await admin_client.logs.get_stats(options={"filter": 'data.auth!="admin"'})
    assert logs["items"]
    assert logs["items"][0] == await admin_client.logs.get_one(logs["items"][0]["id"])
