import math

# from ..settings import log


def get_title(item):
    """Create short title for realty item."""

    # TODO get short_title if less fields exists.
    short_title = "р-н. {dn} {sn}, {rc} ком. г. {cn}"
    short_title_msn = "р-н. {dn} {sn}, {rc} ком. г. {cn} (М) ст. {msn}"

    if item.get('metro_station_name'):
        title = short_title_msn.format(
            dn=item['district_name'],
            sn=item['street_name'],
            rc=item['rooms_count'],
            cn=item['city_name'],
            msn=item['metro_station_name'])
    else:
        title = short_title.format(
            dn=item['district_name'],
            sn=item['street_name'],
            rc=item['rooms_count'],
            cn=item['city_name'])
    return title


def compact_item(item):
    result = item['_source']
    result['title'] = get_title(item['_source'])
    return result


async def search_realty(
        app, description=None, districts=None, rooms_count=None,
        price_min=None, price_max=None, price_curr=3, page=0, **kwargs):
    """Search realty in ES with filters.

    arg: description: str - searchable text
    arg: districts: [1, 2]
    arg: rooms_count: [1, 2]
    arg: price_min: int
    arg: price_max: int
    arg: price_curr: int : 1 - USD, 2 - EUR, 3 - UAH
    arg: page: int
    """

    offset = 10
    from_ = page * offset

    query = {
        'bool': {
            'must': [],
            'filter': []
        }
    }
    if description:
        # TODO search by short title.
        query['bool']['must'].append({'match': {'description': description}})

    if districts:
        d_dict = app.cfg['districts']
        name_list = [d_dict[i].lower() for i in districts if i in d_dict]
        # log.debug(f'district_names: {name_list}')
        query['bool']['filter'].append({"terms": {"district_name": name_list}})
    if rooms_count:
        query['bool']['filter'].append({"terms": {"rooms_count": rooms_count}})
    if price_min or price_max:
        prices = {}  # {'gte': price_min, 'lte': price_max}
        if price_min:
            prices['gte'] = price_min
        if price_max:
            prices['lte'] = price_max
        query['bool']['filter'].append(
            {"range": {f"priceArr.{price_curr}": prices}})

    res = await app.es.search(
        index=app.cfg['es']['indexes']['realty'],
        body={
            "from": from_, "size": offset,
            'query': query,
            "sort": [
                "_score",
                {"priceArr.3": {"order": "asc"}}
            ]
        }
    )

    result_list = [compact_item(item) for item in res['hits']['hits']]
    count = res['hits']['total']['value']
    pages = math.ceil(count / offset)  # 4.6 -> 5
    return result_list, count, pages
