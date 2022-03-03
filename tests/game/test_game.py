from sqlalchemy import true
from datetime import datetime
import pytest
from asyncpg.exceptions import UniqueViolationError

from app.game.models import Game, User, GameModel
from app.store import Store


class TestGame:
    async def test_restore_games_on_startup(self, cli, store: Store):
        answ = await store.games.restore_games_on_startup()
        if type(answ) == list:
            assert true # если вернулся список то все нормально
        
        else:
            assert answ == "" #иначе вернулся текст ошибки. будет выведен как ошибка теста

    async def test_start_game(self, cli, store: Store):
        cli.app.games.pop(10001, None) # удаляем игру из списка игр
            
        users = {}
        user = User(
            vk_id=10001,
            name="Test User 1", 
            create_at=datetime.utcnow(),
            points = 10000,
            buyed_securites={},
            state = "in_trade")        
        users[user.vk_id] = user
        answ =  await store.games.start_game(10001, users)

        cli.app.games.pop(10001, None) # удаляем игру из списка иг

        if answ.startswith("Игра начата!"):
            assert true
        else:
            assert answ == ""

   
    async def test_buy_securyties(self, cli, store: Store, start_game):
        answ =  await store.games.buy_securyties(10001, 10001, "/buy AFLT 11")
        if answ.startswith("Удачная покупка"):
            assert true
        else:
            assert answ == ""

    async def test_sell_securyties(self, cli, store: Store, start_game, buy_secur):
        answ =  await store.games.sell_securyties(10001, 10001, "/sell AFLT 11")
        if answ.startswith("Удачная продажа"):
            assert true
        else:
            assert answ == ""
    
    async def test_finish(self, cli, store: Store, start_game):
        answ =  await store.games.finish_round_for_user(10001, 10001, "/finish")
        if answ.startswith("Игрок"):
            assert true
        else:
            assert answ == ""

    async def test_stop_game(self, cli, store: Store, start_game):
        answ =  await store.games.stop_game(10001)
        if answ.startswith("Завершена игра"):
            assert true
        else:
            assert answ == ""
 