import pytest
from datetime import datetime

from app.store.vk_api.dataclasses import Update, Message, UpdateObject
from app.store import Store


@pytest.fixture()
def updates(cli):
    upds = []
    upds.append(
        Update(
            type="new_message",
            object=UpdateObject(
                id=1,
                user_id=10001,
                peer_id=10001,
                text="",
                action="chat_invite_user"                
            ),
        )
    )    
    upds.append(
        Update(
            type="new_message",
            object=UpdateObject(
                id=1,
                user_id=10001,
                peer_id=10001,
                text="/help",
                action=None                
            ),
        )
    )    
    # upds.append(
    #     Update(
    #         type="new_message",
    #         object=UpdateObject(
    #             id=1,
    #             user_id=10001,
    #             peer_id=10001,
    #             text="/start_game",
    #             action=None                
    #         ),
    #     )
    # )    
    upds.append(
        Update(
            type="new_message",
            object=UpdateObject(
                id=1,
                user_id=10001,
                peer_id=10001,
                text="/buy AFLT 10",
                action=None                
            ),
        )
    )    
    upds.append(
        Update(
            type="new_message",
            object=UpdateObject(
                id=1,
                user_id=10001,
                peer_id=10001,
                text="/sell AFLT 5",
                action=None                
            ),
        )
    )    
    upds.append(
        Update(
            type="new_message",
            object=UpdateObject(
                id=1,
                user_id=10001,
                peer_id=10001,
                text="/finish",
                action=None                
            ),
        )
    )    
    upds.append(
        Update(
            type="new_message",
            object=UpdateObject(
                id=1,
                user_id=10001,
                peer_id=10001,
                text="",
                action=None                
            ),
        )
    )    
    upds.append(
        Update(
            type="new_message",
            object=UpdateObject(
                id=1,
                user_id=10001,
                peer_id=10001,
                text="/info",
                action=None                
            ),
        )
    )
    upds.append(
        Update(
            type="new_message",
            object=UpdateObject(
                id=1,
                user_id=10001,
                peer_id=10001,
                text="/stop_game",
                action=None                
            ),
        )
    )
    return upds
    