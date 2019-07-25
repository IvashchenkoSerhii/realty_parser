# REALTY PARSER

Stack: python, aiohttp, elasticsearch.

Periodically updates realty info from source.

Set update timer (in seconds):

    aiohttp/config/config_base.yaml:data_source:upd_timeout

#### Run application:
    docker-compose up -d

#### Open browser:
[localhost:8000](http://localhost:8000/)

#### Stop application:
    docker-compose stop
    docker-compose down
