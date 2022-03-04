import random
import typing

from app.base.decorators import errors_catching, errors_catching_asinc
from typing import Optional, List, Union
from app.store.database.gino import db
from app.base.base_accessor import BaseAccessor
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert
from app.game.messages import (START_GAME_MESSAGE, BAD_USER_REQUEST, GAME_ALREADY_RUNNING)
from app.game.messages import get_text_list_traded_sequrites
from logging import getLogger
from sqlalchemy import and_

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.game.models import (
    Security,
    User,
    Security,
    BuyedSecurity,
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
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.logger = getLogger("accessor")

    async def connect(self, app: "Application"):
        await self.restore_games_on_startup()

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

    def game_by_chat_id(self,chat_id: int) -> Game:
        for app_game in self.app.games:
            if app_game.chat_id == chat_id:
                return app_game
        return None

    def game_by_id(self,id: int) -> Game:
        for app_game in self.app.games:
            if app_game.id == id:
                return app_game
        return None

    def find_user(self, game: Game, user_id: int) -> User:
        for user in game.users:
            if user.vk_id == user_id:
                return user
        return None

    def find_seciruty(self, game: Game, user: Optional[User], secur_id: str, secur_type: str) -> Union[Security,BuyedSecurity]:
        if secur_type == "traded":
            for seciruty in game.traded_sequrites:
                if seciruty.id == secur_id:
                    return seciruty
        else:
            for seciruty in user.buyed_securites:
                if seciruty.security.id == secur_id:
                    return seciruty
            
        return None
    
    @errors_catching_asinc
    async def start_game(self, chat_id: int) -> str:
        game = self.game_by_chat_id(chat_id)
        if game != None:
            return GAME_ALREADY_RUNNING 
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

    @errors_catching_asinc
    async def restore_games_on_startup(self):
        #Запрос ветки Игра - пользователи игры - купленные акции
        db_games_users = (
            await GameModel
            .outerjoin(GameUsersModel, GameModel.id == GameUsersModel.game_id)
            .outerjoin(UserModel, UserModel.vk_id == GameUsersModel.user_id)
            .outerjoin(BuyedSecuritesModel, BuyedSecuritesModel.user_in_game_id == GameUsersModel.id)
            .outerjoin(SecuritesModel, SecuritesModel.id == BuyedSecuritesModel.security_id)
            .select()
            .where(GameModel.state == "started")
            .order_by(GameModel.id, GameUsersModel.id) 
            .gino.load(
                GameModel.distinct(GameModel.id).load(
                    users=GameUsersModel.distinct(GameUsersModel.id).load(
                        vk_user = UserModel,
                        buyed_securites = BuyedSecuritesModel.load(
                            security = SecuritesModel
                        )
                    )
                )
            )
            .all()
        )

        for db_game in db_games_users:
            game = Game(
                id=db_game.id, 
                create_at=db_game.create_at,
                chat_id=db_game.chat_id,
                state=db_game.state,
                trade_round=0,
                users=[],
                traded_sequrites=[])
            await self.create_traded_sequrites(game)
            for db_user in db_game.users:
                user = User(
                    vk_id=db_user.vk_user.vk_id, 
                    name=db_user.vk_user.name, 
                    create_at=db_user.vk_user.create_at,
                    points = db_user.points,
                    buyed_securites=[])
                game.users.append(user)
                for db_b_secur in db_user.buyed_securites:
                    b_secur = BuyedSecurity(
                        id=db_b_secur.id,
                        security=self.find_seciruty(game, user, db_b_secur.security_id,"traded"),
                        ammount=db_b_secur.ammount
                    )
                    user.buyed_securites.append(b_secur)
            self.app.games.append(game)

        #Запрос ветки Игра - Раунд игры - Торгуемые акции
        db_games_rounds = (
            await TradeRoundsModel
            .outerjoin(TradedSecuritesModel, TradeRoundsModel.id == TradedSecuritesModel.round_id)
            .outerjoin(SecuritesModel, TradedSecuritesModel.sequrity_id == SecuritesModel.id)
            .outerjoin(MarketEventsModel, TradedSecuritesModel.market_event_id == MarketEventsModel.id)
            .select()
            .where(TradeRoundsModel.state == "started")
            .order_by(TradeRoundsModel.game_id, TradedSecuritesModel.sequrity_id)
            .gino.load(
                TradeRoundsModel.distinct(TradeRoundsModel.id)
                .load(
                    traded_securites = TradedSecuritesModel.load(
                        market_event = MarketEventsModel,
                        security = SecuritesModel,
                    )
                )
            )
            .all()
        )
        for db_round in db_games_rounds:
            game = self.game_by_id(db_round.game_id)
            game.trade_round = db_round.number_in_game
            for db_tr_secur in db_round.traded_securites:
                tr_secur = self.find_seciruty(game,None,db_tr_secur.sequrity_id,"traded")
                tr_secur.price = db_tr_secur.price
                tr_secur.market_event = f"{db_tr_secur.market_event.description} цена акции изменилась на {db_tr_secur.market_event.diff}%"
        return "Игры восстановлены успешно"

