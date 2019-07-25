import pathlib
import ujson

from elasticsearch import Elasticsearch
from aiohttp_handler.settings import get_config


CONFIG_ROOT = pathlib.Path(__file__).parent.parent / 'config'
TEST_CONFIG = get_config(CONFIG_ROOT, 'config_test.yaml')
TEST_ES_URL = TEST_CONFIG['es']['host']

es = Elasticsearch(TEST_ES_URL)


def create_index(es=es):
    # ignore 400 cause by IndexAlreadyExistsException when creating an index
    es.indices.create(index='test_index', ignore=400)
    es.indices.create(index='test_system_index', ignore=400)


def delete_index(es=es):
    # ignore 404 and 400
    es.indices.delete(index='test_index', ignore=[400, 404])
    es.indices.delete(index='test_system_index', ignore=[400, 404])


def sample_data(es=es):
    with open('tests/data/min.json') as f:
        items_min = ujson.load(f)
    for item_min in items_min:
        es.index(
            index='test_index',
            id=item_min['realty_id'],
            body=item_min)


if __name__ == '__main__':

    create_index(es=es)
    sample_data(es=es)
    # delete_index(es=es)
