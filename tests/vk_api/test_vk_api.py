from app.game.models import Game, User
#from app.game.views import tst_list
from tests.utils import ok_response
from app.store import Store
import pytest
from tests.utils import check_empty_table_exists
from asyncpg.exceptions import UniqueViolationError
import re
import json

pld = json.loads("""
{
    "response": {
        "count": 4,
        "items": [
            {
                "member_id": 70268011,
                "invited_by": 70268011,
                "join_date": 1645778283,
                "is_admin": true,
                "is_owner": true
            },
            {
                "member_id": -210525858,
                "invited_by": 70268011,
                "join_date": 1645809131,
                "is_admin": true
            },
            {
                "member_id": 155779742,
                "can_kick": true,
                "invited_by": 70268011,
                "join_date": 1645877346
            },
            {
                "member_id": 5011018,
                "can_kick": true,
                "invited_by": 70268011,
                "join_date": 1645982279
            }
        ],
        "profiles": [
            {
                "id": 5011018,
                "first_name": "Валентин",
                "last_name": "Чехлаев",
                "can_access_closed": true,
                "is_closed": true
            },
            {
                "id": 70268011,
                "first_name": "Vitaly",
                "last_name": "Obrubov",
                "can_access_closed": true,
                "is_closed": false
            },
            {
                "id": 155779742,
                "first_name": "Марина",
                "last_name": "Обрубова",
                "can_access_closed": true,
                "is_closed": true
            }
        ],
        "groups": [
            {
                "id": 210525858,
                "name": "Exchange",
                "screen_name": "club210525858",
                "is_closed": 0,
                "type": "page",
                "photo_50": "https://vk.com/images/community_50.png",
                "photo_100": "https://vk.com/images/community_100.png",
                "photo_200": "https://vk.com/images/community_200.png"
            }
        ]
    }
}        
""")

class TestVkApi:
    async def test_get_users(self, store: Store, chat_id, mock_response, vk_connected):

        path = re.compile(r"https://api.vk.com/method/messages.getConversationMembers\.*")
        mock_response.post(path,
                        status = 200,
                        payload = pld)
        answ =  await store.vk_api.get_users(chat_id)
        assert type(answ) == dict
        assert len(answ) == 3
