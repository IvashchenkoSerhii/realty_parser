import aiohttp_jinja2
import ujson
from aiohttp import web

from .. import db
from ..settings import log


class IndexHandler(web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):

        # TODO separate func for parse filters.
        ACCEPTED_FILTERS = [
            'description', 'district_names', 'rooms_count',
            'price_min', 'price_max', 'price_curr', 'page', 'districts']
        filters = {}
        for key in self.request.rel_url.query:
            if key not in ACCEPTED_FILTERS:
                log.error(f'key: {key} not in ACCEPTED_FILTERS')
            elif key == 'description':
                filters[key] = self.request.rel_url.query[key]
            else:
                filters[key] = ujson.loads(self.request.rel_url.query[key])

        log.debug(f'filters: {filters}')

        data = {
            'title': 'Title',
            'body_header': 'Header',
            'filters': filters
        }
        try:
            result_list, count, pages = await db.search_realty(
                app=self.request.app, **filters)
            data.update(
                {
                    'result_list': result_list,
                    'pages': pages,
                    'page': filters.get('page', 0)
                }
            )
        except Exception as e:
            log.error(f'es search error: {e}')
        return data
