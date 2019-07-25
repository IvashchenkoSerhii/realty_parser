from elasticsearch_async import AsyncElasticsearch


async def init_es(app):
    ES_URL = app.cfg['es']['host']
    app.es = AsyncElasticsearch(ES_URL)
    # for index in app.cfg['es']['indexes'].values():
    #     app.es.indices.create(index=index, ignore=400)


async def close_es(app):
    await app.es.transport.close()
    # await app['es'].wait_closed()
