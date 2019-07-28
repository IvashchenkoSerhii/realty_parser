from aiohttp import web

from .. import db
from ..settings import log


class APIHandler(web.View):
    async def get(self):

        filters = db.get_filters(self.request.rel_url.query_string)
        page = filters.get('page', 0)
        log.debug(f'filters: {filters}')

        data = {
            'filters': filters,
            'results': [],
            'pages': 0,
            'page': page,
            'count': 0,
            'pagination': []
        }
        try:
            result_list, count, pages = await db.search_realty(
                app=self.request.app, **filters)
            pagination = db.abbreviated_pages(page=page + 1, n=pages)
            data.update(
                {
                    'results': result_list,
                    'pages': pages,
                    'page': page,
                    'count': count,
                    'pagination': pagination
                }
            )
        except Exception as e:
            log.error(f'error: {e}')

        return web.json_response(data)
