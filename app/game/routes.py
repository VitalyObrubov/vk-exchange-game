import typing

from app.game.views import GameListView, StopGameListView, AddSecurityView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/game.list_games", GameListView)
    app.router.add_view("/game.list_stoped_games", StopGameListView)
    app.router.add_view("/game.add_security", AddSecurityView)
