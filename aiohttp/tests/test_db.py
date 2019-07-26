import ujson

from datetime import datetime
from urllib import parse

from aiohttp_handler import db


def test_get_filters():
    """Checks get_filters functionality."""

    query_dct = {
        'districts': '1', 'rooms_count': '2', 'price_max': '100',
        'page': '0', 'description': 'text', 'wrong_key': 'wrong_data'}
    filters = db.get_filters(parse.urlencode(query_dct))
    assert filters
    assert filters['districts'] == [1]
    assert filters['rooms_count'] == [2]
    assert filters['price_max'] == 100
    assert filters['page'] == 0
    assert filters['description'] == 'text'
    assert filters['description'] == 'text'
    assert not filters.get('wrong_key')

    query_dct = {'districts': '1bb', 'page': '0'}  # ValueError
    filters = db.get_filters(parse.urlencode(query_dct))
    assert filters == {}
    filters = db.get_filters('districts=6&districts=7&districts=8')
    assert filters['districts'] == [6, 7, 8]


def test_abbreviated_pages():
    res = db.abbreviated_pages(page=1, n=3)
    assert res == [1, 2, 3]
    res = db.abbreviated_pages(page=1, n=11)
    assert res == [1, 2, '...', 11]
    res = db.abbreviated_pages(page=5, n=11)
    assert res == [1, '...', 4, 5, 6, '...', 11]
    res = db.abbreviated_pages(page=11, n=11)
    assert res == [1, '...', 10, 11]


def test_get_title():
    item = {
        "description": "description",
        "metro_station_name": "station",
        "street_name": "street",
        "district_name": "district",
        "city_name": "city",
        "rooms_count": 1,
    }
    title = db.get_title(item)
    assert title == 'р-н. district street, 1 ком. г. city (М) ст. station'
    item.pop('metro_station_name')
    title = db.get_title(item)
    assert title == 'р-н. district street, 1 ком. г. city'


def test_minimaze_item():
    with open('tests/data/big.json') as f:
        item = ujson.load(f)
    item_min = db.minimaze_item(item)
    assert item_min == {
        "street_name": "street_name",
        "rooms_count": 1,
        "beautiful_url": "beautiful_url",
        "description": "description",
        "publishing_date": datetime(2019, 7, 24, 0, 0),
        "city_name": "city_name",
        "realty_id": 123456,
        "district_name": "district_name",
        "metro_station_name": "",
        "priceArr":
        {
            "1": 851,
            "2": 763,
            "3": 22000
        }
    }
