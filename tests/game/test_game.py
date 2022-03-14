from sqlalchemy import true
from datetime import datetime
import pytest
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy import and_

from app.game.models import (
    Game,
    User, 
    BuyedSecuritesModel, 
    GameUsersModel, 
    GameModel,
    TradeRoundsModel
)
from app.store import Store


class TestGame:
    async def test_start_game(self, cli, store: Store, users, chat_id):
                
        answ =  await store.games.start_game(chat_id, users)

        cli.app.games.pop(chat_id, None) # удаляем игру из списка игр
        db_game = await GameModel.query.where(GameModel.chat_id == 10001).gino.first()
        if answ.startswith("Игра начата!"):
            assert true
        else:
            assert answ == ""
        assert db_game != None
   
    async def test_buy_securyties(self, cli, store: Store, started_game, buy_params, chat_id, user_id):
        game = cli.app.games.get(chat_id)
        answ =  await store.games.buy_securyties(buy_params)
        db_g_user = await GameUsersModel.query.where(and_(GameUsersModel.game_id == game.id, GameUsersModel.user_id == 10001)).gino.first()
        db_b_secur = await BuyedSecuritesModel.query.where(and_(BuyedSecuritesModel.security_id == "AFLT", BuyedSecuritesModel.user_in_game_id == db_g_user.id)).gino.first()
        end_points = db_g_user.points
        end_ammount = db_b_secur.ammount
        if answ.startswith("Удачная покупка"):
            assert true
        else:
            assert answ == ""
        assert end_ammount == 10
        assert end_points == 9000
         

    async def test_sell_securyties(self, cli, store: Store, started_game, buyed_secur, sell_params, chat_id, user_id):
        game:Game = cli.app.games.get(chat_id)
        user:User = game.users.get(user_id)
        params = {}
        params["game"] = game
        params["user"] = user
        params["secur"] = user.buyed_securites.get("AFLT")
        params["ammount"] = 10
       
        answ =  await store.games.sell_securyties(sell_params)
        
        db_g_user = await GameUsersModel.query.where(and_(GameUsersModel.game_id == game.id, GameUsersModel.user_id == user_id)).gino.first()
        db_b_secur = await BuyedSecuritesModel.query.where(and_(BuyedSecuritesModel.security_id == "AFLT", BuyedSecuritesModel.user_in_game_id == db_g_user.id)).gino.first()
        end_points = db_g_user.points
        end_ammount = db_b_secur.ammount
        
        if answ.startswith("Удачная продажа"):
            assert true
        else:
            assert answ == ""
        assert end_ammount == 0
        assert end_points == 10000

    async def test_finish(self, cli, store: Store, started_game, chat_id, user_id):
        game:Game = cli.app.games.get(chat_id)
        user:User = game.users.get(user_id)
        params = {}
        params["game"] = game
        params["user"] = user
        await store.games.finish_round_for_user(params)
        db_user = await GameUsersModel.query.where(and_(GameUsersModel.game_id == game.id, GameUsersModel.user_id == user_id)).gino.first()
        assert db_user.state == "finished"

    async def test_stop_game(self, cli, store: Store, started_game, chat_id):
        answ =  await store.games.stop_game(chat_id)

        db_game = await GameModel.query.where(GameModel.chat_id == chat_id).gino.first()
        db_t_round = await TradeRoundsModel.query.where(TradeRoundsModel.game_id == db_game.id).gino.first()
        assert db_game.state == "finished"
        assert db_t_round.state == "finished"
    
    def test_get_info(sself, cli, store: Store, started_game, chat_id):
        answ =  store.games.stop_game(chat_id) 
        assert answ != None

    async def test_resore_game(self, cli, store: Store, started_game, chat_id):
        # фикстура started_game создает игру в памяти и в бд
        game = cli.app.games.pop(chat_id) #удаляем игру из памяти 
        answ =  await store.games.restore_games_on_startup() # восстанавливает игру из бд в память
        game = cli.app.games.get(chat_id) #получаем игру из памяти

        assert game != None



    async def test_get_list(self):
        from app.game.views import GameListView

        answ = await GameListView.get()
        assert len(answ) >= 3
