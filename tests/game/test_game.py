from sqlalchemy import true
from app.game.models import Game, User
from tests.utils import ok_response
from app.store import Store
import pytest
from tests.utils import check_empty_table_exists
from asyncpg.exceptions import UniqueViolationError


class TestGame:
    async def test_restore_games_on_startup(self, cli, store: Store):
        answ = await store.games.restore_games_on_startup()
        if type(answ) == list:
            assert true # если вернулся список то все нормально
            # удаляем созданные тестом игры
            for game in answ:
                while true:
                    try:
                        cli.app.games.remove(game)
                    except:
                        break
        
        else:
            assert answ == "" #иначе вернулся текст ошибки. будет выведен как ошибка теста

    async def test_buy_securyties(self, cli, store: Store):
        answ =  await store.games.buy_securyties(2000000002, 70268011, "\buy AFLT 11")
        assert answ == "Удачная покупка"

 