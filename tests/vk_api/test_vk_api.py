from app.game.models import Game, User
#from app.game.views import tst_list
from tests.utils import ok_response
from app.store import Store
import pytest
from tests.utils import check_empty_table_exists
from asyncpg.exceptions import UniqueViolationError
import re


class TestVkApi:
    async def test_get_users(self, store: Store, chat_id, mock_response, payload):

        path = re.compile(r"https://api.vk.com/method/messages.getConversationMembers\.*")
        mock_response.post(path,
                        status = 200,
                        payload = payload)
        answ =  await store.vk_api.get_users(chat_id)
        assert type(answ) == dict
        assert len(answ) == 3
