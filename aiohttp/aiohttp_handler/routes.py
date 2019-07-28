import pathlib
from .views import api, views_index


def setup_routes(app):
    app.router.add_view('/', views_index.IndexAPIView, name='index_api')
    app.router.add_view('/jinja/', views_index.IndexJinjaView, name='jinja')
    app.router.add_view('/api/', api.APIHandler, name='api')

    app.router.add_static(
        '/static/',
        path=pathlib.Path(__file__).parent / 'static',
        name='static')
