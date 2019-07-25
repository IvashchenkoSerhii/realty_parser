import asyncio
import time
import ujson

from datetime import datetime
from ..settings import log


def get_filters(query_dct):
    ACCEPTED_FILTERS = [
        'description', 'district_names', 'rooms_count',
        'price_min', 'price_max', 'price_curr', 'page', 'districts'
    ]
    filters = {}
    for key in query_dct:
        if key not in ACCEPTED_FILTERS:
            log.error(f'key: {key} not in ACCEPTED_FILTERS')
        elif key == 'description':
            filters[key] = query_dct[key]
        else:
            try:
                filters[key] = ujson.loads(query_dct[key])
            except ValueError as e:
                log.error(f'ujson loads({query_dct[key]}) error: {e}')
    return filters


def minimaze_item(item):
    required_fields = [
        'realty_id', 'beautiful_url', 'description', 'rooms_count',
        'district_name', 'street_name', 'city_name', 'metro_station_name',
        'priceArr'
    ]
    item_min = {k: item.get(k, '') for k in required_fields}
    item_min['priceArr'] = {
        k: int(v.replace(' ', ''))
        for k, v in item_min['priceArr'].items()}
    return item_min


async def periodic_updater_init(app):
    app.on_shutdown.append(periodic_updater_cancel)
    loop = asyncio.get_event_loop()
    app.periodic_updater = loop.create_task(periodic_updater(app))


async def periodic_updater_cancel(app):
    app.periodic_updater.cancel()


async def periodic_updater(app):
    """
    Periodic get updates from a source.

    Asks for update information and sleeps before the timeout expires.
    """
    while True:
        date_from, date_update = await get_update_date(app)
        sleep = date_update - time.time()
        if sleep > 0:
            log.debug(f'periodic_updater sleep: {sleep:.05f} s.')
            await asyncio.sleep(sleep + 1)

        log.debug('periodic_updater start')
        await download_realty_list(app, date_from, page=0)
        log.debug(f'periodic_updater done.')
        await asyncio.sleep(5)  # wait ES update index


async def get_update_date(app):

    index = app.cfg['es']['indexes']['system']
    if not await app.es.exists(index=index, id='update_date'):
        # date_from = '2019-07-25'
        date_from = ''
        date_update = time.time()
    else:
        res = await app.es.get(index=index, id='update_date')
        date_from = res['_source']['date_from']
        date_update = res['_source']['date_update']

    return date_from, date_update


async def set_next_update_date(app):

    index = app.cfg['es']['indexes']['system']
    upd_timeout = app.cfg['data_source']['upd_timeout']
    date_update = time.time() + upd_timeout
    data = {
        'date_from': f'{datetime.now():%Y-%m-%d}',
        'date_update': date_update}
    log.debug(f'set_next_update_date: {data}')
    index = await app.es.index(index=index, id='update_date', body=data)
    return True


async def store_realty(app, realty_id):
    """
    Store realty item on ES.

    Checks if an item already exists. Download, minimaze and insert to ES.
    Return codes: 0 - download error, 1 - updated, 2 - created
    """
    index = app.cfg['es']['indexes']['realty']
    exists = await app.es.exists(index=index, id=realty_id)

    r_json = await get_realty_json(app, realty_id)
    if not r_json:
        # log.debug(f'store_realty: error  {realty_id}')
        return 0

    # TODO check district name before storing.
    item = minimaze_item(r_json)
    inserted = await insert_realty_es(app, realty_id, item)
    if not inserted:
        return 0
    if exists:
        # log.debug(f'store_realty: update {realty_id}')
        return 1
    log.debug(f'store_realty: create {realty_id}')
    return 2


async def insert_realty_es(app, realty_id, item):
    index = app.cfg['es']['indexes']['realty']
    # TODO error handling
    try:
        index = await app.es.index(index=index, id=realty_id, body=item)
        return True
    except Exception as e:
        log.error(f'insert_realty_es error: {e}')
        return False


async def get_realty_json(app, realty_id):
    item_url = app.cfg['data_source']['item_url'].format(realty_id=realty_id)
    try:
        r = await app.client_session.get(
            item_url, headers=app.cfg['headers'], timeout=20)
        assert r.status == 200
        r_json = await r.json()
        return r_json
    except Exception as e:
        log.error(f'get_realty_json: {realty_id} error: {e}')
        return None


async def download_realty_list(app, date_from, page=0):
    """
    Download realty_id list loop.

    Loop while no errors or next page exists.
    Creates async tasks for download each realty item.
    arg: date_from: {%Y-%m-%d}. Download all items if date_from == ''.
    arg: page: int.
    """
    while True:
        log.debug(f'download_realty_list: d:{date_from} p:{page}')

        list_url = app.cfg['data_source']['list_url'].format(
            date_from=date_from, page=page)

        try:
            r = await app.client_session.get(
                list_url, headers=app.cfg['headers'], timeout=20)
            assert r.status == 200
            r_json = await r.json()
        except Exception as e:
            log.error(f'download_realty_list error: {e}')
            break

        realty_id_list = r_json['items']
        count = r_json['count']
        tasks = []
        for realty_id in realty_id_list:
            task = asyncio.ensure_future(store_realty(app, realty_id))
            tasks.append(task)
        res = await asyncio.gather(*tasks)
        log.debug(
            f'Total: {len(res)} created: {res.count(2)} '
            f'updated: {res.count(1)} error: {res.count(0)}')

        page += 1
        if page * 100 > count:  # limit=100
            log.debug('download_realty_list done')
            break
        await asyncio.sleep(1)  # for ES indexing
    await set_next_update_date(app)
