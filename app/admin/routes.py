import typing

from app.admin.views import (
    AdminLoginView, 
    AdminListView,
    AdminDelView,
    Index,
    GamersListView,
    SecursListView,
    GamesListView,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application

  


def setup_routes(app: "Application"):

    app.router.add_view("/", Index, name = "Index")
    app.router.add_view("/login", AdminLoginView, name = "AdminLoginView")
    app.router.add_view("/gamers", GamersListView, name = "GamersListView")
    app.router.add_view("/securs", SecursListView, name = "SecursListView")
    app.router.add_view("/admins", AdminListView, name = "AdminListView")
    app.router.add_view("/admins.del", AdminDelView, name = "AdminDelView")
    app.router.add_view("/games", GamesListView, name = "GamesListView")
   

    app.router.add_static("/static/", path="static", name='static')