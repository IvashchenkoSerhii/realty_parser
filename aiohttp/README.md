#### Install requirements:

    pip install -r requirements_dev.txt

#### Run application:

    adev runserver aiohttp_handler  # dev tools
    python -m aiohttp_handler  # prod

#### Run tests:
`run elasticsearch before`

    pytest tests/ -vv

#### Open browser:
[localhost:8000](http://localhost:8000/)