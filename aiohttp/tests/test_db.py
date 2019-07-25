from aiohttp_handler import db


async def test_search_realty(cli):
    """Test for index_not_found_exception error."""

    await db.search_realty(app=cli.server.app)
