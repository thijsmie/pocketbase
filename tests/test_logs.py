import asyncio

from pocketbase import PocketBase


async def test_get_logs(superuser_client: PocketBase):
    """
    Note that this test doesn't really test this properly
    As there are probably no logs in the api yet.
    """

    # Empirically: logs get added slowly, this is enough to ensure there is logs
    await superuser_client.logs.get_list()
    await asyncio.sleep(4)
    logs = await superuser_client.logs.get_list()
    await superuser_client.logs.get_list(options={"filter": "level>0"})
    await superuser_client.logs.get_stats()
    await superuser_client.logs.get_stats(options={"filter": 'data.auth!="superuser"'})
    assert logs["items"]
    assert logs["items"][0] == await superuser_client.logs.get_one(logs["items"][0]["id"])
