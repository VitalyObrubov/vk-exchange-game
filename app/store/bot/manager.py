import typing
from logging import getLogger
from app.game.messages import *
from app.store.vk_api.dataclasses import Update, Message

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")
    
    def split_mess(self, chat_id:int, user_id:int, mess:str):
        res = {}
        game = self.app.games.get(chat_id)
        if game == None:
            return NO_GAME_HELP
        else:
            res["game"] = game

        user = game.users.get(user_id)
        if user == None:
            return USER_NOT_GAMER
        else:
            res["user"] = user

        if user.state != "in_trade":
            return USER_NOT_IN_TRADE

        deal_params = mess.split()
        
        if deal_params[0] == "/finish": # при запросе окончания раунда остальные проверки не нужны
            return res

        if len(deal_params) < 3:
            return NOT_ALL_PARAMS


        if deal_params[0] == "/buy": #если операция покупки, то ищем продаваемые акции и наоборот
            security = game.traded_sequrites.get(deal_params[1])
        else:
            security = user.buyed_securites.get(deal_params[1])
        
        if security == None:
                return SHARES_NOT_ENOUGH + deal_params[1]
        else:
            res["secur"] = security

        try:     
            ammount = int(deal_params[2])
            res["ammount"] = ammount
        except Exception as e:
            return ERR_SECUR_AMMOUNT
               
        if (deal_params[0] == "/buy") and (user.points < security.price*ammount):
            return AMOUNT_INSUFFICIENT
        elif (deal_params[0] == "/sell") and (security.ammount < ammount):
            return SHARES_NOT_ENOUGH + deal_params[1]

        return res

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            chat_id=int(update.object.peer_id)
            if update.object.action == "chat_invite_user":
                message_text = INVITE_MEESGE

            elif update.object.text.startswith("/start_game"):
                users = await self.app.store.vk_api.get_users(chat_id) 
                message_text = await self.app.store.games.start_game(chat_id, users)
 
            elif update.object.text.startswith("/help"):
                message_text = self.app.store.games.get_help(chat_id)            
            
            elif update.object.text.startswith("/buy"):
                params = self.split_mess(chat_id, update.object.user_id, update.object.text)
                if type(params) != dict:
                    message_text = params
                else:
                    message_text = await self.app.store.games.buy_securyties(params)            
            
            elif update.object.text.startswith("/sell"):
                params = self.split_mess(chat_id,  update.object.user_id, update.object.text)
                if type(params) != dict:
                    message_text = params
                else:
                    message_text =  await self.app.store.games.sell_securyties(params)            
            
            elif update.object.text.startswith("/finish"):
                params = self.split_mess(chat_id,  update.object.user_id, update.object.text)
                if type(params) != dict:
                    message_text = params
                else:
                    message_text =  await self.app.store.games.finish_round_for_user(params)                      

            elif update.object.text.startswith("/info"):
                message_text = self.app.store.games.get_info(chat_id)            
           
            elif update.object.text.startswith("/stop_game"):
                message_text = await self.app.store.games.stop_game(chat_id)            
           
            else:
                message_text = UNKNOWN_COMMAND

            await self.app.store.vk_api.send_message(
                Message(
                    user_id=update.object.user_id,
                    peer_id=update.object.peer_id,
                    text=message_text,
                )
            )
        return "Успешно"
