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
                payload= "",
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
                payload= "",
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
    #             payload= "",
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
                payload= "",
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
                payload= "",
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
                payload= "",
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
                payload= "",
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
                payload= "",
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
                payload= "",
                action=None                
            ),
        )
    )
    return upds
    