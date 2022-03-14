
from aiohttp_apispec import response_schema, request_schema
from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound, HTTPBadRequest

from app.game.schemes import ListOfGames, Security
from app.web.app import View, app
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response

class GameListView(AuthRequiredMixin, View):
    @response_schema(ListOfGames)
    async def get(self):
        try:
            data=ListOfGames().dump({"game":app.games})
        except Exception as err:
            print(err) 

        return json_response(data)


class StopGameListView(AuthRequiredMixin, View):
    @response_schema(ListOfGames)
    async def get(self):
        games = await app.store.games.restore_games_on_startup("finished") 
        try:
            data=ListOfGames().dump({"game":games})
        except Exception as err:
            print(err) 

        return json_response(data)

class AddSecurityView(AuthRequiredMixin, View):
    @request_schema(Security)
    @response_schema(Security)
    async def post(self):
        id = self.data["id"]
        existing_secur = await self.store.games.get_secur_by_id(id)
        if existing_secur:
            raise HTTPConflict

        if len(self.data) < 3:
            raise HTTPBadRequest
        secur = await self.store.games.create_secur(self.data["id"], self.data["description"], self.data["price"])
        return json_response(data=Security().dump(secur))