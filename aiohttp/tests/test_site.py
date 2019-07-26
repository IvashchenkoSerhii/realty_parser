from aiohttp_handler import db


async def test_es_ping(cli):
    """
    Wait ES connection.

    Calls `sample_data` from `index` pytest.fixture for insert items.
    """
    await db.wait_es_ping(
        app=cli.server.app,
        sleep=0.1,
        log_errors=False)


async def test_search_realty(cli, wait_index):
    """Checks for the error index_not_found_exception."""

    result_list, count, pages = await db.search_realty(app=cli.server.app)
    assert count == 3
    assert pages == 1
    assert len(result_list) == 3


async def test_index(cli):
    resp = await cli.get('/')
    assert resp.status == 200
