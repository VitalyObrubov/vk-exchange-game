import typing
from logging import getLogger
from app.game.messages import *
from app.store.vk_api.dataclasses import Update, Message
from app.store.vk_api.keyboard import START_KEY, RUN_KEY
from app.store.vk_api.keyboard import kbd_buy, kbd_buy_ammount, kbd_sell, kbd_sell_ammount

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
            game = self.app.games.get(chat_id)
            if  game == None:
                knobs =  START_KEY
            else:
                knobs =  RUN_KEY

            if update.object.text.startswith("/start_game") or update.object.payload["command"]=="/start_game":
                users = await self.app.store.vk_api.get_users(chat_id) 
                message_text = await self.app.store.games.start_game(chat_id, users)
                knobs =  RUN_KEY
 
            elif update.object.text.startswith("/help") or update.object.payload["command"]=="/help":
                message_text = self.app.store.games.get_help(chat_id) 
                knobs =  RUN_KEY           
            
            elif update.object.text.startswith("/buy") or update.object.payload["command"]=="/buy":
                if update.type == "message_new":
                    params = self.split_mess(chat_id, update.object.user_id, update.object.text)
                    if type(params) != dict:
                        message_text = params
                    else:
                        message_text = await self.app.store.games.buy_securyties(params)
                else:
                    secur_id = update.object.payload.get("secur")
                    ammount = update.object.payload.get("ammount")
                    if secur_id == None:
                        message_text = f"{game.users[update.object.user_id].name} покупает" 
                        knobs = kbd_buy(game.traded_sequrites)
                    else:
                        if ammount == None:
                            message_text = f"{game.users[update.object.user_id].name} покупает {secur_id} в количестве"
                            knobs = kbd_buy_ammount(secur_id)
                        else:
                            params = self.split_mess(chat_id, update.object.user_id, f"/buy {secur_id} {ammount}")
                            if type(params) != dict:
                                message_text = params
                            else:
                                message_text = f"{game.users[update.object.user_id].name} покупает {secur_id} в количестве {ammount}<br>"
                                message_text += await self.app.store.games.buy_securyties(params)                            
                                knobs =  []
            
            elif update.object.text.startswith("/sell") or update.object.payload["command"]=="/sell":
                if update.type == "message_new":
                    params = self.split_mess(chat_id,  update.object.user_id, update.object.text)
                    if type(params) != dict:
                        message_text = params
                    else:
                        message_text =  await self.app.store.games.sell_securyties(params)            
                else:
                    secur_id = update.object.payload.get("secur")
                    ammount = update.object.payload.get("ammount")
                    if secur_id == None:
                        message_text = f"{game.users[update.object.user_id].name} продает" 
                        knobs = kbd_sell(game.traded_sequrites)
                    else:
                        if ammount == None:
                            message_text = f"{game.users[update.object.user_id].name} продает {secur_id} в количестве"
                            knobs = kbd_sell_ammount(secur_id)
                        else:
                            params = self.split_mess(chat_id, update.object.user_id, f"/sell {secur_id} {ammount}")
                            if type(params) != dict:
                                message_text = params
                            else:
                                message_text = f"{game.users[update.object.user_id].name} продает {secur_id} в количестве {ammount}<br>"
                                message_text += await self.app.store.games.sell_securyties(params)                            
                                knobs =  []
            
            elif update.object.text.startswith("/finish") or update.object.payload["command"]=="/finish":
                params = self.split_mess(chat_id,  update.object.user_id, "/finish")
                if type(params) != dict:
                    message_text = params
                else:
                    message_text =  await self.app.store.games.finish_round_for_user(params)                      
                knobs =  RUN_KEY

            elif update.object.text.startswith("/info") or update.object.payload["command"]=="/info":
                message_text = self.app.store.games.get_info(chat_id) 
                knobs =  RUN_KEY           
           
            elif update.object.text.startswith("/stop_game") or update.object.payload["command"]=="/stop_game":
                message_text = await self.app.store.games.stop_game(chat_id) 
                knobs =  START_KEY           
           
            else:
                message_text = UNKNOWN_COMMAND

            if update.type == "message_event":
                await self.app.store.vk_api.send_answer(update)
            

            if ((update.object.payload["command"]=="/buy" or update.object.payload["command"]=="/sell") 
                and (update.object.payload.get("secur") != None)):

                await self.app.store.vk_api.edit_message(
                    Message(
                        user_id=update.object.user_id,
                        peer_id=update.object.peer_id,
                        text=message_text,
                        id=update.object.mess_id
                        ),
                    knobs
                )            
            else:
                await self.app.store.vk_api.send_message(
                    Message(
                        user_id=update.object.user_id,
                        peer_id=update.object.peer_id,
                        text=message_text,
                        id=""
                        ),
                    knobs
                )
        return "Успешно"
