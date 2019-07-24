from .views import views_index


def setup_routes(app):
    app.router.add_view('/', views_index.IndexHandler)
