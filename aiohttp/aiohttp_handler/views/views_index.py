import aiohttp_jinja2
from aiohttp import web

from .. import db
from ..settings import log


class IndexAPIView(web.View):
    @aiohttp_jinja2.template('index_api.html')
    async def get(self):
        return {}


class IndexJinjaView(web.View):
    @aiohttp_jinja2.template('index_jinja.html')
    async def get(self):

        filters = db.get_filters(self.request.rel_url.query_string)
        log.debug(f'filters: {filters}')

        data = {'filters': filters}
        try:
            result_list, count, pages = await db.search_realty(
                app=self.request.app, **filters)
            page = filters.get('page', 0)
            pagination = db.abbreviated_pages(page=page + 1, n=pages)
            data.update(
                {
                    'result_list': result_list,
                    'pages': pages,
                    'page': page,
                    'count': count,
                    'pagination': pagination
                }
            )
        except Exception as e:
            log.error(f'es search error: {e}')
        return data
