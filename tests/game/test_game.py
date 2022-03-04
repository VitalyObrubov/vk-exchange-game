from app.game.models import Game, User
from tests.utils import ok_response
from app.store import Store
import pytest
from tests.utils import check_empty_table_exists
from asyncpg.exceptions import UniqueViolationError


class TestGame:
    async def test_restore_games_on_startup(self, cli, store: Store):
        answ = await store.games.restore_games_on_startup()
        assert answ == "Игры восстановлены успешно"


 