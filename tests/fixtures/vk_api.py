import json
import pytest


@pytest.fixture
async def vk_connected(cli):
    await cli.app.store.vk_api.connect(cli.app)
    yield
    await cli.app.store.vk_api.disconnect(cli.app)

@pytest.fixture
async def payload(cli):
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
    return pld 