import random
import typing
from wave import Wave_write

from app.base.decorators import errors_catching, errors_catching_async
from typing import Optional, List, Union, Dict
from app.store.database.gino import db
from app.base.base_accessor import BaseAccessor
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert
from app.game.messages import *
from app.store.game.utils import *
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

MAX_ROUNDS = 3

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
            t_secur = Security(id=row.id, description=row.description, price=row.start_price, market_event="")
            game.traded_sequrites[t_secur.id] = t_secur
           # эти данные переносятся в базу кода создаются все записи в базе
    
    def validate_game(self, game: Game):
        """Проверка игры

        Проверяет, что все поля заполнены корректно, что пользователей достаточно для начала игры
        Возвращает None если все нормально или текст с ошибками

        """
        return None
    

    async def create_next_trade_round(self, game: Game):
        if game.trade_round > 0: # закрываем предыдущий раунд в бд
            await TradeRoundsModel.update.values(state = "finished").where(and_(TradeRoundsModel.number_in_game==game.trade_round, TradeRoundsModel.game_id==game.id)).gino.status()
            if game.trade_round < MAX_ROUNDS: # разрешаем пользователям снова торговать
                await GameUsersModel.update.values(state = "in_trade").where(GameUsersModel.game_id==game.id).gino.status()
                for user in game.users.values():
                    user.state = "in_trade"

        game.trade_round +=1
        if game.trade_round > MAX_ROUNDS: #Завершаем игру
            game.state = "finished"
            game.trade_round -=1
            await GameModel.update.values(state = "finished").where(GameModel.id==game.id).gino.status()
            self.app.games.pop(game.chat_id, None)
            return "Завершена игра<br>" + generate_game_result(game)

        db_trade_round = await TradeRoundsModel.create(number_in_game=game.trade_round, state="started", game_id=game.id)
        market_events = await MarketEventsModel.query.gino.all()
        events_count = len(market_events)
        traded_securites = [] #сбор данных для загрузки в базу
        for sequrity in game.traded_sequrites.values():
            random_event = market_events[random.randint(0, events_count-1)]
            sequrity.price += sequrity.price / 100 * random_event.diff
            sequrity.market_event = f"{random_event.description} цена изменилась на {random_event.diff}%"
            traded_securites.append({"sequrity_id":sequrity.id, "price":sequrity.price, "round_id":db_trade_round.id, "market_event_id":random_event.id})

        await insert(TradedSecuritesModel).values(traded_securites).on_conflict_do_nothing().gino.status()

        res = "Новые цены на акции<br>" + get_text_list_traded_sequrites(game)
        return res


    @errors_catching_async
    async def create_game_in_db(self, game: Game):
        """Создает в базе данных объекты игры

        """
        async with db.transaction():           
            db_game = await GameModel.create(create_at=game.create_at, chat_id=game.chat_id, state=game.state)
            game.id = db_game.id
            game_users = [] # подготовка данных для загрузки в базу
            all_users = []
            for user in game.users.values():
                all_users.append({"vk_id":user.vk_id, "name":user.name, "create_at":user.create_at})
                game_users.append({"game_id":game.id, "user_id":user.vk_id, "points":user.points, "state":"in_trade"})
            
            await insert(UserModel).values(all_users).on_conflict_do_nothing().gino.status()
            await insert(GameUsersModel).values(game_users).on_conflict_do_nothing().gino.status()

            res = await self.create_next_trade_round(game)
            
            return res
                
 

    def get_help(self, chat_id: int):
        game = self.app.games.get(chat_id)
        if game == None:
            return NO_GAME_HELP
        else:
            return STARTED_GAME_HELP
               
    @errors_catching_async
    async def start_game(self, chat_id: int, users: Dict[int, User]) -> str:
        game = self.app.games.get(chat_id)
        if game != None:
            return GAME_ALREADY_RUNNING 
        if len(users) == 0:
            return BAD_USER_REQUEST
        game = Game(id=0, 
                    create_at=datetime.utcnow(),
                    chat_id=chat_id,
                    state="started",
                    trade_round=0,
                    users={},
                    traded_sequrites={})
        game.users = users
        await self.create_traded_sequrites(game)
        res = self.validate_game(game)
        if res == None:
            text = await self.create_game_in_db(game)
            
            self.app.games[game.chat_id] = game
            text = START_GAME_MESSAGE + text
            return text
 
        else:
            return res

    @errors_catching_async
    async def restore_games_on_startup(self) -> Union[list, str]:
        created_games = []
        SecuritesModelAls = SecuritesModel.alias()
        db_games = (
            await GameModel
            .outerjoin(GameUsersModel, GameModel.id == GameUsersModel.game_id)
            .outerjoin(UserModel, UserModel.vk_id == GameUsersModel.user_id)
            .outerjoin(BuyedSecuritesModel, BuyedSecuritesModel.user_in_game_id == GameUsersModel.id)
            .outerjoin(SecuritesModel, SecuritesModel.id == BuyedSecuritesModel.security_id)
            .outerjoin(TradeRoundsModel,  GameModel.id == TradeRoundsModel.game_id)
            .outerjoin(TradedSecuritesModel, TradeRoundsModel.id == TradedSecuritesModel.round_id)
            .outerjoin(SecuritesModelAls, TradedSecuritesModel.sequrity_id == SecuritesModelAls.id)
            .outerjoin(MarketEventsModel, TradedSecuritesModel.market_event_id == MarketEventsModel.id)            .select()
            .where(and_(GameModel.state == "started", TradeRoundsModel.state == "started"))
            .order_by(GameModel.id, GameUsersModel.id) 
            .gino.load(
                GameModel.distinct(GameModel.id)
                .load(
                    users=GameUsersModel.distinct(GameUsersModel.id)
                    .load(
                        vk_user = UserModel,
                        buyed_securites = BuyedSecuritesModel.load(
                            security = SecuritesModel
                        )
                    )
                )
                .load(
                    trade_round = TradeRoundsModel.distinct(TradeRoundsModel.id)
                    .load(
                        traded_securites = TradedSecuritesModel.distinct(TradedSecuritesModel.sequrity_id)
                        .load(
                            market_event = MarketEventsModel,
                            security = SecuritesModelAls,
                        )
                    )
                )
            )
            .all()
        )
        for db_game in db_games:
            game = db_game.get_game()
            await self.create_traded_sequrites(game)
            for db_user in db_game.users:
                user = db_user.get_user()
                game.users[user.vk_id] = user
                for db_b_secur in db_user.buyed_securites:
                    b_secur = db_b_secur.get_b_secur(game)
                    user.buyed_securites[b_secur.security.id] = b_secur
            db_round = db_game.trade_round
            game.trade_round = db_round.number_in_game
            for db_tr_secur in db_round.traded_securites:
                tr_secur = game.traded_sequrites.get(db_tr_secur.sequrity_id)
                tr_secur.price = db_tr_secur.price
                tr_secur.market_event = f"{db_tr_secur.market_event.description} цена изменилась на {db_tr_secur.market_event.diff}%"
            self.app.games[game.chat_id] = game
            created_games.append(game)
            
        return created_games

    @errors_catching_async
    async def buy_securyties(self, chat_id: int, user_id: int, mess_text: str):
        answ = check_operation(self.app, chat_id, user_id, mess_text)
        if type(answ) != dict:
            return answ
        game: Game = answ["game"]
        user: User = answ["user"]
        security: Security = answ["secur"]
        ammount: int = answ["ammount"]
        #Выполняем операцию покупки
        buyed_sequrity = user.buyed_securites.get(security.id)
        if buyed_sequrity == None:
            buyed_sequrity = BuyedSecurity(security = security, ammount = 0)
            user.buyed_securites[buyed_sequrity.security.id] = buyed_sequrity
        buyed_sequrity.ammount +=ammount
        user.points -= security.price*ammount
        async with db.transaction():
            db_t_round = await TradeRoundsModel.query.where(and_(TradeRoundsModel.game_id == game.id, TradeRoundsModel.number_in_game == game.trade_round)).gino.first()  
            await TradeJornalModel.create(round_id=db_t_round.id, user_id=user_id, sequrity_id=security.id, operation="buy", ammount=ammount)
           
            db_game_user = await(
                insert(GameUsersModel)
                .values(
                    game_id = game.id, 
                    user_id = user.vk_id, 
                    points = user.points, 
                    state = "in_trade")
                .on_conflict_do_update(
                    index_elements=[GameUsersModel.game_id, GameUsersModel.user_id], set_=dict(points = user.points))
                .returning(*GameUsersModel).gino.first()  
                )
            
            await(
                insert(BuyedSecuritesModel)
                .values(
                    user_in_game_id = db_game_user.id, 
                    security_id = security.id, 
                    ammount = buyed_sequrity.ammount)
                .on_conflict_do_update(
                    index_elements=[BuyedSecuritesModel.user_in_game_id, BuyedSecuritesModel.security_id], set_=dict(ammount=buyed_sequrity.ammount))
                .returning(*BuyedSecuritesModel).gino.status()  
            )
                

        return f"Удачная покупка. Остаток {user.points} монет"


    @errors_catching_async
    async def sell_securyties(self, chat_id: int, user_id: int, mess_text: str):
        answ = check_operation(self.app, chat_id, user_id, mess_text)
        if type(answ) != dict:
            return answ
        game: Game = answ["game"]
        user: User = answ["user"]
        buyed_sequrity: BuyedSecurity = answ["secur"]
        ammount:int = answ["ammount"]
        #Выполняем операцию продажи
        security = buyed_sequrity.security

        buyed_sequrity.ammount -=ammount
        user.points += security.price*ammount
        async with db.transaction():
            db_t_round = await TradeRoundsModel.query.where(and_(TradeRoundsModel.game_id == game.id, TradeRoundsModel.number_in_game == game.trade_round)).gino.first()  
            await TradeJornalModel.create(round_id=db_t_round.id, user_id=user_id, sequrity_id=security.id, operation="sell", ammount=ammount)
           
            db_game_user = await(insert(GameUsersModel)
                .values(
                    game_id = game.id, 
                    user_id = user.vk_id, 
                    points = user.points, 
                    state = "in_trade")
                .on_conflict_do_update(index_elements=[GameUsersModel.game_id, GameUsersModel.user_id], set_=dict(points = user.points))
                .returning(*GameUsersModel)
                .gino.first()
            )           

            await(insert(BuyedSecuritesModel)
                .values(
                    user_in_game_id = db_game_user.id,
                    security_id = security.id, 
                    ammount = buyed_sequrity.ammount)
                .on_conflict_do_update(index_elements=[BuyedSecuritesModel.user_in_game_id, BuyedSecuritesModel.security_id], set_=dict(ammount=buyed_sequrity.ammount))
                .returning(*BuyedSecuritesModel)
                .gino.status()
            )
                       
        

        return f"Удачная продажа. Остаток {user.points} монет"
    
    
    @errors_catching_async
    async def finish_round_for_user(self, chat_id: int, user_id: int, mess_text: str):
        answ = check_operation(self.app, chat_id, user_id, mess_text)
        if type(answ) != dict:
            return answ
        game: Game = answ["game"]
        user: User = answ["user"]

        #Выполняем операцию завершения торгов пользователя

        user.state = "finished"
        async with db.transaction():
            db_game_user = await(insert(GameUsersModel)
                .values(
                    game_id = game.id, 
                    user_id = user.vk_id, 
                    points = user.points, 
                    state = "finished")
                .on_conflict_do_update(index_elements=[GameUsersModel.game_id, GameUsersModel.user_id], set_=dict(state =  "finished"))
            .returning(*GameUsersModel)
            .gino.first() 
            )          
        
        
        counter = db.func.count(GameUsersModel.id) # Запрос количества пользователей завершивших игру
        finished_users_count = await db.select([counter]).where(and_(GameUsersModel.game_id == game.id ,GameUsersModel.state == "finished")).gino.scalar()
        res = ""
        if finished_users_count == len(game.users):
            async with db.transaction():
                res = await self.create_next_trade_round(game)
            res = f"Завершен {game.trade_round-1} раунд.<br>" + res
        
        res = f"Игрок {user.name} завершил раунд. " + res
        
        return res

    @errors_catching
    def get_info(self, chat_id: int):
        game = self.app.games.get(chat_id)
        if game == None:
            return NO_GAME_HELP

        text = generate_game_result(game)
        return text

    @errors_catching_async
    async def stop_game(self, chat_id: int):
        game = self.app.games.get(chat_id)
        if game == None:
            return NO_GAME_HELP 

        await GameModel.update.values(state = "finished").where(GameModel.id==game.id).gino.status()
        await TradeRoundsModel.update.values(state = "finished").where(TradeRoundsModel.game_id==game.id).gino.status()
        await GameUsersModel.update.values(state = "finished").where(GameUsersModel.game_id==game.id).gino.status()

        self.app.games.pop(chat_id, None)
        return "Завершена игра<br>" + generate_game_result(game)

 