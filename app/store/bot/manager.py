import typing
from logging import getLogger

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
            if update.object.action == "chat_invite_user":
                message_text = "Привет! Для запуска игры введите /start_game"

            elif update.object.text.find("/start_game") >-1:
                chat_id=int(update.object.peer_id)
                message_text = await self.app.store.games.start_game(chat_id)

            else:
                message_text = "Команда не опознана"

            await self.app.store.vk_api.send_message(
                Message(
                    user_id=update.object.user_id,
                    peer_id=update.object.peer_id,
                    text=message_text,
                )
            )
