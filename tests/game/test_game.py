from sqlalchemy import true
from datetime import datetime
import pytest
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy import and_

from app.game.models import (
    User, 
    BuyedSecuritesModel, 
    GameUsersModel, 
    GameModel,
    TradeRoundsModel
)
from app.store import Store


class TestGame:
    async def test_restore_games_on_startup(self, cli, store: Store):
        answ = await store.games.restore_games_on_startup()
        if type(answ) == list:
            assert true # если вернулся список то все нормально
        
        else:
            assert answ == "" #иначе вернулся текст ошибки. будет выведен как ошибка теста

    async def test_start_game(self, cli, store: Store, users, chat_id):
               
        answ =  await store.games.start_game(chat_id, users)

        cli.app.games.pop(chat_id, None) # удаляем игру из списка игр
        db_game = await GameModel.query.where(GameModel.chat_id == 10001).gino.first()
        if answ.startswith("Игра начата!"):
            assert true
        else:
            assert answ == ""
        assert db_game != None
   
    async def test_buy_securyties(self, cli, store: Store, started_game, chat_id, user_id):
        game = cli.app.games.get(chat_id)
        db_g_user = await GameUsersModel.query.where(
            and_(GameUsersModel.game_id == game.id, 
                 GameUsersModel.user_id == user_id)
            ).gino.first()
        db_b_secur = await BuyedSecuritesModel.query.where(
            and_(BuyedSecuritesModel.security_id == "AFLT", 
                 BuyedSecuritesModel.user_in_game_id == db_g_user.id)
            ).gino.first()
        start_points = db_g_user.points
        if db_b_secur == None:
            start_ammount = 0
        else:
            start_ammount = db_b_secur.ammount

        answ =  await store.games.buy_securyties(chat_id, user_id, "/buy AFLT 11")

        db_g_user = await GameUsersModel.query.where(and_(GameUsersModel.game_id == game.id, GameUsersModel.user_id == 10001)).gino.first()
        db_b_secur = await BuyedSecuritesModel.query.where(and_(BuyedSecuritesModel.security_id == "AFLT", BuyedSecuritesModel.user_in_game_id == db_g_user.id)).gino.first()
        end_points = db_g_user.points
        end_ammount = db_b_secur.ammount
        if answ.startswith("Удачная покупка"):
            assert true
        else:
            assert answ == ""
        assert start_ammount < end_ammount
        assert start_points > end_points
         

    async def test_sell_securyties(self, cli, store: Store, started_game, buyed_secur, chat_id, user_id):
        game = cli.app.games.get(chat_id)
        db_g_user = await GameUsersModel.query.where(and_(GameUsersModel.game_id == game.id, GameUsersModel.user_id == user_id)).gino.first()
        db_b_secur = await BuyedSecuritesModel.query.where(and_(BuyedSecuritesModel.security_id == "AFLT", BuyedSecuritesModel.user_in_game_id == db_g_user.id)).gino.first()
        start_points = db_g_user.points
        if db_b_secur == None:
            start_ammount = 0
        else:
            start_ammount = db_b_secur.ammount
        
        answ =  await store.games.sell_securyties(chat_id, user_id, "/sell AFLT 11")
        
        db_g_user = await GameUsersModel.query.where(and_(GameUsersModel.game_id == game.id, GameUsersModel.user_id == user_id)).gino.first()
        db_b_secur = await BuyedSecuritesModel.query.where(and_(BuyedSecuritesModel.security_id == "AFLT", BuyedSecuritesModel.user_in_game_id == db_g_user.id)).gino.first()
        end_points = db_g_user.points
        end_ammount = db_b_secur.ammount
        
        if answ.startswith("Удачная продажа"):
            assert true
        else:
            assert answ == ""
        assert start_ammount > end_ammount
        assert start_points < end_points

    async def test_finish(self, cli, store: Store, started_game, chat_id, user_id):
        answ =  await store.games.finish_round_for_user(chat_id, user_id, "/finish")
        if answ.startswith("Игрок"):
            assert true
        else:
            assert answ == ""

    async def test_stop_game(self, cli, store: Store, started_game, chat_id):
        answ =  await store.games.stop_game(chat_id)
        if answ.startswith("Завершена игра"):
            assert true
        else:
            assert answ == ""
        db_game = await GameModel.query.where(GameModel.chat_id == chat_id).gino.first()
        db_t_round = await TradeRoundsModel.query.where(TradeRoundsModel.game_id == db_game.id).gino.first()
        assert db_game.state == "finished"
        assert db_t_round.state == "finished"
 