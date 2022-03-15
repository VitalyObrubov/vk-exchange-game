
from app.store import Store

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
