
from aiohttp_apispec import response_schema

from app.game.schemes import ListGameSchema
from app.web.app import View, app
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response

class GameListView(AuthRequiredMixin, View):
    @response_schema(ListGameSchema)
    async def get(self):
        try:
            data=ListGameSchema().dump({"game":app.games})
        except Exception as err:
            print(err.messages) 

        return json_response(data)

