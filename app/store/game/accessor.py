import random
import typing
from wave import Wave_write

from app.base.decorators import errors_catching, errors_catching_asinc
from typing import Optional, List, Union
from app.store.database.gino import db
from app.base.base_accessor import BaseAccessor
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert
from app.game.messages import *
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
        if game.trade_round > 0: # закрываем предыдущий раунд в бд
            await TradeRoundsModel.update.values(state = "finished").where(TradeRoundsModel.id==game.db_trade_round_id).gino.status()
            if game.trade_round < MAX_ROUNDS: # разрешаем пользователям снова торговать
                await GameUsersModel.update.values(state = "in_trade").where(GameUsersModel.game_id==game.id).gino.status()
                for user in game.users:
                    user.state = "in_trade"


        game.trade_round +=1
        if game.trade_round > MAX_ROUNDS:
            game.state = "finished"
            await GameModel.update.values(state = "finished").where(GameModel.id==game.id).gino.status()
            self.app.games.remove(game)

            res = generate_game_result(game)
            return "Завершена игра<br>" + res  # завершить игру

        db_trade_round = await TradeRoundsModel.create(number_in_game=game.trade_round, state="started", game_id=game.id)
        game.db_trade_round_id = db_trade_round.id
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
        return ""


    @errors_catching_asinc
    async def create_game_in_db(self, game: Game):
        """Создает в базе данных объекты игры

        Args:
            game (Game): _description_
        """
      
        async with db.transaction():           
            db_game = await GameModel.create(create_at=game.create_at, chat_id=game.chat_id, state=game.state)
            game.id = db_game.id
            game_users = [] # подготовка данных для загрузки в базу
            all_users = []
            for user in game.users:
                all_users.append({"vk_id":user.vk_id, "name":user.name, "create_at":user.create_at})
                game_users.append({"game_id":game.id, "user_id":user.vk_id, "points":user.points, "state":"in_trade"})
            
            stmt = insert(UserModel).values(all_users)
            stmt = stmt.on_conflict_do_nothing()
            await stmt.gino.model(UserModel).all()
            
            stmt = insert(GameUsersModel).values(game_users)
            stmt = stmt.on_conflict_do_nothing().returning(*GameUsersModel)
            db_game_users = await stmt.gino.model(GameUsersModel).all()
            
            for db_game_user in db_game_users:
                user = self.find_user(game,db_game_user.user_id)
                user.game_user_id = db_game_user.id
            res = await self.create_next_trade_round(game)
            
            return res
                
 
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
    def get_help(self, chat_id: int):
        game = self.game_by_chat_id(chat_id)
        if game == None:
            return NO_GAME_HELP
        else:
            return STARTED_GAME_HELP
               
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
                    db_trade_round_id=0,
                    users=[],
                    traded_sequrites=[])
        game.users = users
        await self.create_traded_sequrites(game)
        res = self.validate_game(game)
        if res == None:
            res = await self.create_game_in_db(game)
            if res != "":
                return res
            self.app.games.append(game)
            text = START_GAME_MESSAGE + get_text_list_traded_sequrites(game)
            return text
        else:
            return res

    @errors_catching_asinc
    async def restore_games_on_startup(self):# -> Union(List(Game), str):
        created_games = []
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
                db_trade_round_id=0,
                users=[],
                traded_sequrites=[])
            await self.create_traded_sequrites(game)
            for db_user in db_game.users:
                user = User(
                    vk_id=db_user.vk_user.vk_id,
                    game_user_id=db_user.id, 
                    name=db_user.vk_user.name, 
                    create_at=db_user.vk_user.create_at,
                    points = db_user.points,
                    buyed_securites=[],
                    state =  db_user.state)
                game.users.append(user)
                for db_b_secur in db_user.buyed_securites:
                    b_secur = BuyedSecurity(
                        id=db_b_secur.id,
                        security=self.find_seciruty(game, user, db_b_secur.security_id,"traded"),
                        ammount=db_b_secur.ammount
                    )
                    user.buyed_securites.append(b_secur)
            self.app.games.append(game)
            created_games.append(game)

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
            game.db_trade_round_id = db_round.id
            for db_tr_secur in db_round.traded_securites:
                tr_secur = self.find_seciruty(game,None,db_tr_secur.sequrity_id,"traded")
                tr_secur.price = db_tr_secur.price
                tr_secur.market_event = f"{db_tr_secur.market_event.description} цена акции изменилась на {db_tr_secur.market_event.diff}%"
        
        return created_games

    def check_operation(self, chat_id: int, user_id: int, mess_text: str):
        res = {}
        game = self.game_by_chat_id(chat_id)
        if game == None:
            return NO_GAME_HELP
        else:
            res["game"] = game

        user = self.find_user(game, user_id)
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

        sequr_type = "traded" if deal_params[0] == "/buy" else "buyed" #tckb операция покупки, то ищем продаваемые акции и наоборот
        security = self.find_seciruty(game, user, deal_params[1], sequr_type)
        
        if security == None:
             return SHARES_NOT_ENOUGH + deal_params[1]
        else:
            res["secur"] = security

        try:     
            ammount = int(deal_params[2])
            res["ammount"] = ammount
        except Exception as e:
            self.logger.error("Exception", exc_info=e)
            return ERR_SECUR_AMMOUNT
        
        if (deal_params[0] == "/buy") and (user.points < security.price*ammount):
            return AMOUNT_INSUFFICIENT
        elif (deal_params[0] == "/sell") and (security.ammount < ammount):
            return SHARES_NOT_ENOUGH + deal_params[1]


        return res
  

    @errors_catching_asinc
    async def buy_securyties(self, chat_id: int, user_id: int, mess_text: str):
        answ = self.check_operation(chat_id, user_id, mess_text)
        if type(answ) != dict:
            return answ
        game = answ["game"]
        user = answ["user"]
        security = answ["secur"]
        ammount = answ["ammount"]
        #Выполняем операцию покупки
        buyed_sequrity = self.find_seciruty(game, user, security.id, "buyed")
        if buyed_sequrity == None:
            buyed_sequrity = BuyedSecurity(id = 0 ,security = security, ammount = 0)
            user.buyed_securites.append(buyed_sequrity)
        buyed_sequrity.ammount +=ammount
        user.points -= security.price*ammount
        async with db.transaction():
            await TradeJornalModel.create(round_id=game.db_trade_round_id, user_id=user_id, sequrity_id=security.id, operation="buy", ammount=ammount)
           
            stmt = insert(GameUsersModel).values(id = user.game_user_id, game_id = game.id, user_id = user.vk_id, points = user.points, state = "in_trade")
            stmt = stmt.on_conflict_do_update(
                index_elements=[GameUsersModel.id], set_=dict(points = user.points)
            ).returning(*GameUsersModel)
            db_game_user = await stmt.gino.model(GameUsersModel).first()           

            stmt = insert(BuyedSecuritesModel).values(user_in_game_id = db_game_user.id, security_id = security.id, ammount = buyed_sequrity.ammount)
            stmt = stmt.on_conflict_do_update(
                index_elements=["user_in_game_id", "security_id"], set_=dict(ammount=buyed_sequrity.ammount)
            ).returning(*BuyedSecuritesModel)
            db_buyed_sequrity = await stmt.gino.model(BuyedSecuritesModel).first()           
            buyed_sequrity.id = db_buyed_sequrity.id        

        return "Удачная покупка"


    @errors_catching_asinc
    async def sell_securyties(self, chat_id: int, user_id: int, mess_text: str):
        answ = self.check_operation(chat_id, user_id, mess_text)
        if type(answ) != dict:
            return answ
        game = answ["game"]
        user = answ["user"]
        buyed_sequrity = answ["secur"]
        ammount = answ["ammount"]
        #Выполняем операцию продажи
        security = buyed_sequrity.security

        buyed_sequrity.ammount -=ammount
        user.points += security.price*ammount
        async with db.transaction():
            await TradeJornalModel.create(round_id=game.db_trade_round_id, user_id=user_id, sequrity_id=security.id, operation="sell", ammount=ammount)
           
            stmt = insert(GameUsersModel).values(id = user.game_user_id, game_id = game.id, user_id = user.vk_id, points = user.points, state = "in_trade")
            stmt = stmt.on_conflict_do_update(
                index_elements=[GameUsersModel.id], set_=dict(points = user.points)
            ).returning(*GameUsersModel)
            db_game_user = await stmt.gino.model(GameUsersModel).first()           

            stmt = insert(BuyedSecuritesModel).values(user_in_game_id = db_game_user.id, security_id = security.id, ammount = buyed_sequrity.ammount)
            stmt = stmt.on_conflict_do_update(
                index_elements=["user_in_game_id", "security_id"], set_=dict(ammount=buyed_sequrity.ammount)
            ).returning(*BuyedSecuritesModel)
            db_buyed_sequrity = await stmt.gino.model(BuyedSecuritesModel).first()           
        

        return "Удачная продажа"
    
    
    @errors_catching_asinc
    async def finish_round_for_user(self, chat_id: int, user_id: int, mess_text: str):
        answ = self.check_operation(chat_id, user_id, mess_text)
        if type(answ) != dict:
            return answ
        game: Game = answ["game"]
        user: User = answ["user"]

        #Выполняем операцию завершения торгов пользователя

        user.state = "finished"
        async with db.transaction():
            stmt = insert(GameUsersModel).values(id = user.game_user_id, game_id = game.id, user_id = user.vk_id, points = user.points, state = "finished")
            stmt = stmt.on_conflict_do_update(
                index_elements=[GameUsersModel.id], set_=dict(state =  "finished")
            ).returning(*GameUsersModel)
            db_game_user = await stmt.gino.model(GameUsersModel).first()           
        
        
        counter = db.func.count(GameUsersModel.id) # Запрос количества пользователей завершивших игру
        finished_users_count = await db.select([counter]).where(and_(GameUsersModel.game_id == game.id ,GameUsersModel.state == "finished")).gino.scalar()
        res = ""
        if finished_users_count == len(game.users):
            async with db.transaction():
                res = await self.create_next_trade_round(game)
            res = f"Завершен {game.trade_round-1} раунд. " + res
        
        res = f"Игрок {user.name} завершил раунд. " + res
        
        return res