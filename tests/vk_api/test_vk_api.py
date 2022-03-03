from app.game.models import Game, User
from tests.utils import ok_response
from app.store import Store
import pytest
from tests.utils import check_empty_table_exists
from asyncpg.exceptions import UniqueViolationError



class TestVkApi:
    async def test_get_users(self, cli, store: Store):

        assert 1 == 1

    
 