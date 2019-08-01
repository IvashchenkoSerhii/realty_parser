import math

# from ..settings import log


SEARCH_FIELDS = [
    'description', 'district_name', 'street_name', 'metro_station_name'
]
TITLE_TEMPLATE = {
    'district_name': 'р-н. {}',
    'street_name': '{},',
    'rooms_count': '{} ком.',
    'city_name': 'г. {}',
    'metro_station_name': '(М) ст. {}',
}


def get_title(item):
    """Create short title for realty item."""

    title_buffer = []
    for field in TITLE_TEMPLATE:
        if item.get(field):
            title_buffer.append(TITLE_TEMPLATE[field].format(item[field]))
    return ' '.join(title_buffer)


def compact_item(item):
    result = item['_source']
    result['title'] = get_title(item['_source'])
    return result


async def search_realty(
        app, description=None, districts=None, rooms_count=None,
        price_min=None, price_max=None, price_curr=3, page=0, sort=None,
        **kwargs):
    """Search realty in ES with filters.

    Args:
        description: str - searchable text
        districts: [1, 2]
        rooms_count: [1, 2]
        price_min: int
        price_max: int
        price_curr: int : 1 - USD, 2 - EUR, 3 - UAH
        page: int
        sort: pr_a, pr_d, pd_a, pd_d

    Returns:
        result_list:list:
        count:int:
        pages:int:
    """
    offset = 10
    from_ = page * offset

    query = {
        'bool': {
            'should': [],
            'filter': [],
            'must': [{'match': {'deleted_by.keyword': ''}}],
        },
    }
    if description:
        for key in SEARCH_FIELDS:
            query['bool']['should'].append({'match': {key: description}})

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
    sort_query = []
    if sort:
        abbreviations = {
            'pd': 'publishing_date',
            'pr': f'priceArr.{price_curr}',
            'sc': '_score',
            'a': 'asc',
            'd': 'desc',
        }
        field, order = sort.split('_')
        sort_query.append(
            {abbreviations[field]: {"order": abbreviations[order]}})
    res = await app.es.search(
        index=app.cfg['es']['indexes']['realty'],
        body={
            "from": from_, "size": offset,
            'query': query,
            "sort": sort_query
        }
    )

    result_list = [compact_item(item) for item in res['hits']['hits']]
    count = res['hits']['total']['value']
    pages = math.ceil(count / offset)  # 4.6 -> 5
    return result_list, count, pages
