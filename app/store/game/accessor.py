import random
import typing
from typing import Optional, List
from app.store.database.gino import db
from app.base.base_accessor import BaseAccessor
from datetime import datetime
from app.game.messages import (START_GAME_MESSAGE,)
from app.game.messages import get_text_list_traded_sequrites
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
    '''
    def create_game_users(self, game: Game, raw_users):
        for raw_user in raw_users:
            user = User(vk_id=raw_user["id"], 
                        name=f'{raw_user["first_name"]} {raw_user["last_name"]}', 
                        create_at=datetime.now(),
                        points = 10000,
                        buyed_securites=[])
            game.users.append(user)
'''
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
        for sequrity in game.traded_sequrites:
            random_event = market_events[random.randint(0, events_count-1)]
            sequrity.price += sequrity.price / 100 * random_event.diff
            sequrity.market_event = f"{random_event.description} цена акции изменилась на {random_event.diff}%"
            await TradedSecuritesModel.create(sequrity_id = sequrity.id, price=sequrity.price, round_id=db_trade_round.id, market_event_id=random_event.id)


    async def create_game_in_db(self, game: Game):
        """Создает в базе данных объекты игры

        Args:
            game (Game): _description_
        """
        
        try:        
            async with db.transaction():           
                db_game = await GameModel.create(create_at=game.create_at, chat_id=game.chat_id, state=game.state)
                game.id = db_game.id
                for user in game.users:
                    db_user =  await UserModel.query.where(UserModel.vk_id==user.vk_id).gino.first()
                    if db_user == None:
                        db_user =  await UserModel.create(vk_id=user.vk_id, name = user.name, create_at=user.create_at)
                    await GameUsersModel.create(game_id=game.id, user_id=user.vk_id, points=user.points)
                await self.create_next_trade_round(game)
                
        except Exception as e:
            self.logger.info(e)

    async def start_game(self, chat_id: int):
        users = await self.app.store.vk_api.get_users(chat_id)
        game = Game(id=0, 
                    create_at=datetime.now(),
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


