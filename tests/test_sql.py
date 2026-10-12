import pytest

from pocketbase import PocketBase, PocketBaseError


async def test_run_select(superuser_client: PocketBase):
    result = await superuser_client.sql.run("SELECT 1 AS one, 'x' AS two")
    assert [c["name"] for c in result["columns"]] == ["one", "two"]
    assert len(result["rows"]) == 1
    assert result["affectedRows"] == 0


async def test_run_write(superuser_client: PocketBase):
    await superuser_client.sql.run("CREATE TABLE IF NOT EXISTS sql_test (v TEXT)")
    result = await superuser_client.sql.run("INSERT INTO sql_test (v) VALUES ('a'), ('b')")
    assert result["affectedRows"] == 2
    await superuser_client.sql.run("DROP TABLE sql_test")


async def test_run_requires_superuser(client: PocketBase):
    with pytest.raises(PocketBaseError) as exc:
        await client.sql.run("SELECT 1")
    assert exc.value.status == 401


async def test_run_invalid(superuser_client: PocketBase):
    with pytest.raises(PocketBaseError) as exc:
        await superuser_client.sql.run("SELEC nonsense")
    assert exc.value.status == 400
