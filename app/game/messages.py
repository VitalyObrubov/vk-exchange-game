from http.client import NOT_FOUND
from app.game.models import Game, User, Security


INVITE_MEESGE = "Привет!<br>Для запуска игры введите /start_game"

UNKNOWN_COMMAND = "Команда не опознана<br>Для справки по коммандам наберите /help"

START_GAME_MESSAGE = """Игра начата!<br>
                       У каждого на счету 10000 монет<br>
                       Продаются следующие акции<br>      
                    """
BAD_USER_REQUEST = "Запрос пользователей не удался. Ошибка программы"

GAME_ALREADY_RUNNING = "Игра уже запущена.<br>Для справки по коммандам наберите /help "

NO_GAME_HELP = """Игра не запущена<br>
                  Для запуска игры наберите /start_game<br>
                  Для справки по коммандам наберите /help
               """

STARTED_GAME_HELP = """Игра запущена. Доступные комманды:<br>
                      /info - текущаяя информация об игре<br>
                      /buy <id акции> <количество> - купить акции<br>
                      /sell <id акции> <количество> - продать акции<br>
                      /finish - завершить торгавлю в этом раунде<br>
                      /stop_game - досрочно остановить игру<br>
                   """
USER_NOT_GAMER = """Пользователь не участвует в игре<br>
                    Торговля невозможна
                 """
NOT_ALL_PARAMS = "Указаны не все параметры сделки"

NOT_FOUND_SECUR = "Не найдена акция с кодом "

ERR_SECUR_AMMOUNT = "Ошибка получения количества акций"

AMOUNT_INSUFFICIENT = "Сумма на счету недостаточна"

USER_NOT_IN_TRADE = "Пользователь уже закончил торговлю. Ждите следующего раунда"

SHARES_NOT_ENOUGH = "Не хватает акций с кодом "

def get_text_list_traded_sequrites(game: Game) -> str:
   text = ""
   for security in game.traded_sequrites.values():
      text += f"{security.id} {security.description} за {security.price} монет {security.market_event}<br>"
   return text


def get_user_profile(game: Game, user: User) -> str:
   text = f"<br>Портфель пользователя {user.name}<br>"
   text += f"Сумма на счету {user.points} монет<br>"
   text += f"Купленные акции<br>"
   secur_cost = 0
   for b_secur in user.buyed_securites.values():
      b_secur_cost = b_secur.ammount*b_secur.security.price
      text += f"--{b_secur.security.id} {b_secur.security.description} - {b_secur.ammount} шт. на {b_secur_cost} монет<br> "
      secur_cost += b_secur_cost
   text += f"Итого акций на {secur_cost} монет<br>"
   text += f"Итого активов {user.points+secur_cost} монет<br><br>"
   return text   


def generate_game_result(game: Game):
   text = "Результаты игры<br>"
   text += f"Игра в чате {game.chat_id}<br>"
   text += f"Раунд {game.trade_round}<br>"
   text += f"Торгуемые акции<br>"
   text += get_text_list_traded_sequrites(game)
   text += "<br>"
   text += f"Портфели игроков<br>"
   for user in game.users.values():
      text += get_user_profile(game, user)
   
   return text