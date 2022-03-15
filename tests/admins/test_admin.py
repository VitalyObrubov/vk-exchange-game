from app.game.models import SecuritesModel
from app.store import Store

from tests.utils import ok_response

class TestAdmins:

    async def test_get_stopped_list(self, authed_cli, store: Store, started_game, chat_id):
        await store.games.stop_game(chat_id)      
        resp = await authed_cli.get("/game.list_stoped_games")
        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "ok"
        assert data['data']['game'].get(str(chat_id)) != None
        return


    async def test_get_list(self, authed_cli, started_game, chat_id,):
        resp = await authed_cli.get("/game.list_games")
        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "ok"
        assert data['data']['game'].get(str(chat_id)) != None
        return

 
    async def test_add_secur(self, authed_cli):
        pld =  {"id": "FSEC",
                "description": "Тестовая акция1",
                "price": 100}

        resp = await authed_cli.post("/game.add_security", json = pld)
        
        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "ok"
        db_secur = await SecuritesModel.query.where(SecuritesModel.id==pld["id"]).gino.first()
        assert db_secur != None
        return       