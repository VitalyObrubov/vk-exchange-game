from app.game.models import Game
from app.game.messages import *
import typing
from typing import Optional, List, Union, Dict
if typing.TYPE_CHECKING:
    from app.web.app import Application


def game_by_id(app: "Application", id: int) -> Game:
    for app_game in app.games.values():
        if app_game.id == id:
            return app_game
    return None

def check_operation(app: "Application", chat_id: int, user_id: int, mess_text: str) -> Union[dict, str]:
    res = {}
    game = app.games.get(chat_id)
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

    deal_params = mess_text.split()
    
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