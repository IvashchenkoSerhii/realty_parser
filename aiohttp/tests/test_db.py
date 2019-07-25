from aiohttp_handler import db


async def test_search_realty(cli):
    """Checks for the error index_not_found_exception."""

    await db.search_realty(app=cli.server.app)


async def test_get_filters(cli):
    """Checks get_filters functionality."""

    query_dct = {
        'districts': '[1,2,3]', 'rooms_count': '[2]', 'price_max': '100',
        'page': '0', 'description': 'text', 'wrong_key': 'wrong_data'}
    filters = db.get_filters(query_dct)
    assert filters
    assert filters['districts'] == [1, 2, 3]
    assert filters['rooms_count'] == [2]
    assert filters['price_max'] == 100
    assert filters['page'] == 0
    assert filters['description'] == 'text'
    assert filters['description'] == 'text'
    assert not filters.get('wrong_key')

    query_dct = {'districts': '[1bb,]', 'page': '0'}  # Unexpected character
    filters = db.get_filters(query_dct)
    assert filters == {'page': 0}
