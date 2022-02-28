import random
import typing
from app.base.decorators import errors_catching, errors_catching_asinc
from typing import Optional, List
from app.store.database.gino import db
from app.base.base_accessor import BaseAccessor
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert
from app.game.messages import (START_GAME_MESSAGE,BAD_USER_REQUEST)
from app.game.messages import get_text_list_traded_sequrites
from logging import getLogger
if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.game.models import (
    Security,
    User,
    Security,
    Game,
    UserModel,
    SecuritesModel,
    GameModel,
    GameUsersModel,
    BuyedSecuritesModel,
    TradeRoundsModel,
    MarketEventsModel,
    TradedSecuritesModel,
    TradeJornalModel,
)

class GameAccessor(BaseAccessor):
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("accessor")

    async def create_traded_sequrites(self, game: Game):
        res = await SecuritesModel.query.gino.all()
        for row in res:
            game.traded_sequrites.append(Security(id=row.id, description=row.description, price=row.start_price, market_event=""))
            # эти данные переносятся в базу кода создаются все записи в базе
    
    def validate_game(self, game: Game):
        """Проверка игры

        Проверяет, что все поля заполнены корректно, что пользователей достаточно для начала игры
        Возвращает None если все нормально или текст с ошибками

        Args:
            game (Game): _description_
        """
        return None
    async def create_next_trade_round(self, game: Game):
        game.trade_round +=1
        db_trade_round = await TradeRoundsModel.create(number_in_game=game.trade_round, state="started", game_id=game.id)
        market_events = await MarketEventsModel.query.gino.all()
        events_count = len(market_events)
        traded_securites = [] #сбор данных для загрузки в базу
        for sequrity in game.traded_sequrites:
            random_event = market_events[random.randint(0, events_count-1)]
            sequrity.price += sequrity.price / 100 * random_event.diff
            sequrity.market_event = f"{random_event.description} цена акции изменилась на {random_event.diff}%"
            traded_securites.append({"sequrity_id":sequrity.id, "price":sequrity.price, "round_id":db_trade_round.id, "market_event_id":random_event.id})
            
        stmt = insert(TradedSecuritesModel).values(traded_securites)
        stmt = stmt.on_conflict_do_nothing()
        await stmt.gino.model(TradedSecuritesModel).all()



    async def create_game_in_db(self, game: Game):
        """Создает в базе данных объекты игры

        Args:
            game (Game): _description_
        """
        
        try:        
            async with db.transaction():           
                db_game = await GameModel.create(create_at=game.create_at, chat_id=game.chat_id, state=game.state)
                game.id = db_game.id
                game_users = [] # подготовка данных для загрузки в базу
                all_users = []
                for user in game.users:
                    all_users.append({"vk_id":user.vk_id, "name":user.name, "create_at":user.create_at})
                    game_users.append({"game_id":game.id, "user_id":user.vk_id, "points":user.points})
                
                stmt = insert(UserModel).values(all_users)
                stmt = stmt.on_conflict_do_nothing()
                await stmt.gino.model(UserModel).all()
                stmt = insert(GameUsersModel).values(game_users)
                stmt = stmt.on_conflict_do_nothing()
                await stmt.gino.model(GameUsersModel).all()
                await self.create_next_trade_round(game)
                
        except Exception as e:
            self.logger.info(e)

    @errors_catching_asinc
    async def start_game(self, chat_id: int):
        users = await self.app.store.vk_api.get_users(chat_id)
        if len(users) == 0:
            return BAD_USER_REQUEST
        game = Game(id=0, 
                    create_at=datetime.utcnow(),
                    chat_id=chat_id,
                    state="started",
                    trade_round=0,
                    users=[],
                    traded_sequrites=[])
        game.users = users
        await self.create_traded_sequrites(game)
        res = self.validate_game(game)
        if res == None:
            await self.create_game_in_db(game)
            self.app.games.append(game)
            text = START_GAME_MESSAGE + get_text_list_traded_sequrites(game)
            return text
        else:
            return res


