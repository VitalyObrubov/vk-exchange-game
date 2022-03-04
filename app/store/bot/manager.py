import typing
from logging import getLogger
from app.game.messages import (INVITE_MEESGE, UNKNOWN_COMMAND)
from app.store.vk_api.dataclasses import Update, Message
if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            chat_id=int(update.object.peer_id)
            if update.object.action == "chat_invite_user":
                message_text = INVITE_MEESGE

            elif update.object.text.startswith("/start_game"):
                message_text = await self.app.store.games.start_game(chat_id)
            
            else:
                message_text = UNKNOWN_COMMAND

            await self.app.store.vk_api.send_message(
                Message(
                    user_id=update.object.user_id,
                    peer_id=update.object.peer_id,
                    text=message_text,
                )
            )
