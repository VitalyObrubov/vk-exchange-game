from app.game.models import Game, User
from tests.utils import ok_response
from app.store import Store
import pytest
from tests.utils import check_empty_table_exists
from asyncpg.exceptions import UniqueViolationError


class TestVkApi:
    async def test_get_users(self, cli, store: Store):
        """
        , mock_response
        mock_response.get(
            "https://www.metaweather.com/api/location/44418/",
            status=200,
            payload={"temp": 23},
        )"""
        answ = await store.vk_api.get_users(200001)
        assert len(answ) > 0

    
 