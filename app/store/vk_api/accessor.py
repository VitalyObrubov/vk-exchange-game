import random
import typing
import json
from typing import Optional, List

from aiohttp import TCPConnector
from aiohttp.client import ClientSession
from datetime import datetime
from app.base.base_accessor import BaseAccessor
from app.base.decorators import errors_catching_async
from app.store.vk_api.dataclasses import Update, Message, UpdateObject
from app.store.vk_api.poller import Poller
from app.game.models import User


if typing.TYPE_CHECKING:
    from app.web.app import Application

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)
        self.poller = Poller(app.store)
        self.logger.info("start polling")
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        #if self.session:
            #await self.session.close()
        #if self.poller:
            #await self.poller.stop()
        return

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    def make_dict(self, pld):
        res = {"command":"None"}
        if isinstance(pld, str):
            res = json.loads(pld)

        return res

    async def _get_long_poll_service(self):
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="groups.getLongPollServer",
                params={
                    "group_id": self.app.config.bot.group_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = (await resp.json())["response"]
            self.logger.info(data)
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]
            self.logger.info(self.server)

    @errors_catching_async
    async def poll(self):
        async with self.session.get(
            self._build_query(
                host=self.server,
                method="",
                params={
                    "act": "a_check",
                    "key": self.key,
                    "ts": self.ts,
                    "wait": 30,
                },
            )
        ) as resp:
            data = await resp.json()
            if data.get("failed") in [2,3]:
                try:
                    await self._get_long_poll_service()
                except Exception as e:
                    self.logger.error("Exception", exc_info=e)
                return []                
            self.logger.info(data)
            self.ts = data["ts"]
            raw_updates = data.get("updates", [])
            updates = []
            for update in raw_updates:
                if update["type"] == "message_new":    
                    update_ = Update(
                        type=update["type"],
                        object=UpdateObject(
                            id=update["object"]["message"]["id"],
                            user_id=update["object"]["message"]["from_id"],
                            peer_id=update["object"]["message"]["peer_id"],
                            text=update["object"]["message"]["text"],                            
                            payload = self.make_dict(update["object"]["message"].get('payload')),
                            mess_id = ""
                        ),
                    )
                elif update["type"] == "message_event":  
                    update_ = Update(
                        type=update["type"],
                        object=UpdateObject(
                            id=update["object"]["event_id"],
                            user_id=update["object"]["user_id"],
                            peer_id=update["object"]["peer_id"],
                            text="",                            
                            payload = update["object"]["payload"],
                            mess_id = update["object"].get("conversation_message_id")
                        ),
                    )

                updates.append(update_)       
            return updates
  

    async def send_message(self, message: Message, kbd) -> None:

        keyboard = json.dumps(kbd, ensure_ascii=False).encode('utf-8')
        keyboard = str(keyboard.decode('utf-8'))
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "random_id": random.randint(1, 2 ** 32),
                    "peer_id":message.peer_id,
                    "message": message.text,
                    "access_token": self.app.config.bot.token,
                    "keyboard": keyboard,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def edit_message(self, message: Message, kbd) -> None:

        keyboard = json.dumps(kbd, ensure_ascii=False).encode('utf-8')
        keyboard = str(keyboard.decode('utf-8'))
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.edit",
                params={
                    "conversation_message_id":message.id,
                    "peer_id":message.peer_id,
                    "message": message.text,
                    "access_token": self.app.config.bot.token,
                    "keyboard": keyboard,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
    async def send_answer(self, update: Update) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.sendMessageEventAnswer",
                params={
                    "access_token": self.app.config.bot.token,
                    "event_id": update.object.id,
                    "peer_id":update.object.peer_id,
                    "user_id": update.object.user_id,
                    #"event_data": evdata,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)


    async def get_users(self, chat_id) -> List[User]:
        qry = self._build_query(
                host=API_PATH,
                method="messages.getConversationMembers",
                params={
                    "peer_id": chat_id,
                    "fields":"first_name, last_name",
                    "access_token": self.app.config.bot.token,
                })
        async with self.session.post(qry) as resp:
            users = {}
            if resp.status != 200:
                self.logger.error(f"???????????? ???????????? ?????????????????????????? ???? ???????????? resp.status = {resp.status}")
                return users
            resp_json = (await resp.json())
            try:
                profiles = resp_json["response"]["profiles"]
            except :
                self.logger.error(f"???????????? ???????????? ??????????????????????????: ???????????????? ?????????????????? ????????????")
                return users

            self.logger.info(profiles)
            for raw_user in profiles:
                user = User(
                    vk_id=raw_user["id"],
                    name=f'{raw_user["first_name"]} {raw_user["last_name"]}', 
                    create_at=datetime.utcnow(),
                    points = 10000,
                    buyed_securites={},
                    state = "in_trade")
                users[user.vk_id] = user
            return users
           
