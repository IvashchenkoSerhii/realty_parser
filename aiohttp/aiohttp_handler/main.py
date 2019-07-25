import aiohttp
import aiohttp_jinja2
import asyncio
import jinja2
import pathlib
import uvloop
import ujson
from aiohttp import web

from aiohttp_handler import db
from aiohttp_handler.routes import setup_routes
from aiohttp_handler.settings import get_config


CONFIG_ROOT = pathlib.Path(__file__).parent.parent / 'config'
TEMPLATES_ROOT = pathlib.Path(__file__).parent / 'templates'

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def close_client_session(app):
    await app.client_session.close()


async def create_client_session(app):
    app.client_session = aiohttp.ClientSession(json_serialize=ujson.dumps)


def setup_jinja(app):
    jinja_loader = jinja2.FileSystemLoader(TEMPLATES_ROOT.as_posix())
    jinja_env = aiohttp_jinja2.setup(app, loader=jinja_loader)
    return jinja_env


def create_app(config_filename='config_local.yaml'):
    # used for adev runserver aiohttp_handler

    app = web.Application(
        middlewares=[
            web.normalize_path_middleware(
                append_slash=True,
                merge_slashes=True,
            )]
    )
    app.cfg = get_config(CONFIG_ROOT, config_filename)
    setup_jinja(app)
    setup_routes(app)

    app.on_startup.append(db.init_es)
    app.on_shutdown.append(db.close_es)

    app.on_startup.append(create_client_session)
    app.on_shutdown.append(close_client_session)

    if not app.cfg['is_test']:
        app.on_startup.append(db.periodic_updater_init)

    return app


def main(config_filename='config_local.yaml'):
    # used for python -m aiohttp_handler

    app = create_app(config_filename)
    web.run_app(
        app,
        host=app.cfg['host'],
        port=app.cfg['port'],
        access_log=None)


if __name__ == '__main__':
    main()
