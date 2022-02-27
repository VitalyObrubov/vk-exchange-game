from app.game.models import Game

IINVITE_MEESGE = "Привет!<br>Для запуска игры введите /start_game"

UNKNOWN_COMMAND = "Команда не опознана"

START_GAME_MESSAGE = """Игра начата!<br>
                       У каждого на счету 10000 монет<br>
                       Продаются следующие акции<br>      
                    """


def get_text_list_traded_sequrites(game: Game) -> str:
   text = ""
   for security in game.traded_sequrites:
      text += f"{security.id} {security.description} за {security.price} монет {security.market_event}<br>"
   return text