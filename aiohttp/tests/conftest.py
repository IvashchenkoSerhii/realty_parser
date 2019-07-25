import pytest
from aiohttp_handler.main import create_app
from .init_db import create_index, sample_data, delete_index


@pytest.fixture(scope='module')
def index():
    create_index()
    sample_data()
    yield
    delete_index()


@pytest.fixture
def create_then_delete():
    create_index()
    sample_data()
    yield
    delete_index()


@pytest.fixture
def delete_create_after():
    yield
    delete_index()
    create_index()
    sample_data()


@pytest.fixture
def delete_create_before():
    delete_index()
    create_index()
    sample_data()
    yield


@pytest.fixture
async def cli(loop, aiohttp_client, index):
    app = create_app(config_filename='config_test.yaml')
    return await aiohttp_client(app)
