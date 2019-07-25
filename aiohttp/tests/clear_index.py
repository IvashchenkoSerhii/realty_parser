from elasticsearch import Elasticsearch


es = Elasticsearch('http://elastic:changeme@localhost:9200')


def create_index(es=es):
    # ignore 400 cause by IndexAlreadyExistsException when creating an index
    es.indices.create(index='parser_index', ignore=400)
    es.indices.create(index='parser_system_index', ignore=400)
    print('Indices created')


def delete_index(es=es):
    # ignore 404 and 400
    es.indices.delete(index='parser_index', ignore=[400, 404])
    es.indices.delete(index='parser_system_index', ignore=[400, 404])
    print('Indices deleted')


if __name__ == '__main__':

    # create_index(es=es)
    delete_index(es=es)
    # input('Press Enter to exit')
