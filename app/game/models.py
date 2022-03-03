from dataclasses import dataclass, field
from re import A
from typing import Optional, List, Dict
from datetime  import datetime
from app.store.database.gino import db

@dataclass
class Security:
    id: str
    description: str
    price: int
    market_event: Optional[str] #причина изменения цены и процент изменения

@dataclass
class BuyedSecurity:
    id: int
    security: Security
    ammount: int

@dataclass
class User:
    vk_id: int
    name: str
    create_at: datetime
    points: int #кошелек
    buyed_securites: Dict[str, BuyedSecurity] 
    state: str #in_trade|finished

 
@dataclass
class Game:
    id: int
    create_at: datetime
    chat_id: int
    state: str #started|finished
    trade_round: int
    db_trade_round_id: int
    users: Dict[int, User] 
    traded_sequrites: Dict[str, Security]

#===================================================================================================================================

class UserModel(db.Model):
    __tablename__ = "users"
    vk_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode,nullable = False)
    create_at = db.Column(db.DateTime(timezone=True), nullable=False)

class SecuritesModel(db.Model):
    __tablename__ = "securites"
    id = db.Column(db.String(10), primary_key=True)
    description = db.Column(db.Unicode,nullable = False)
    start_price = db.Column(db.Integer())

class GameModel(db.Model):
    __tablename__ = "games"
    id = db.Column(db.Integer(), primary_key=True)
    create_at = db.Column(db.DateTime(timezone=True), nullable=False)
    chat_id = db.Column(db.Integer(), nullable=False)
    state = db.Column(db.String(30), nullable = False)
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self._id_list = []
        self._users = []
  
    @property
    def users(self):
        return self._users

    @users.setter
    def users(self,val):
        if val is not None:
            if val.id in self._id_list:
                return
            self._users.append(val)
            self._id_list.append(val.id)

class GameUsersModel(db.Model):
    __tablename__ = "game_users"
    id = db.Column(db.Integer(), primary_key=True)
    game_id = db.Column(db.Integer(), db.ForeignKey("games.id", ondelete='CASCADE'),nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.vk_id"), nullable=False)
    points = db.Column(db.Integer(), nullable=False)
    state = db.Column(db.String(10), nullable = False) #in_trade|finished
    uniq_constr = db.UniqueConstraint('game_id', 'user_id', name='unc_game_user')
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self._vk_user: UserModel
        self._buyed_securites = []

    @property
    def vk_user(self) -> "UserModel":
        return self._vk_user

    @vk_user.setter
    def vk_user(self,val: "UserModel"):
        self._vk_user=val

    @property
    def buyed_securites(self):
        return self._buyed_securites

    @buyed_securites.setter
    def buyed_securites(self,val):
        if val is not None:
            self._buyed_securites.append(val)

class BuyedSecuritesModel(db.Model):
    __tablename__ = "buyed_securites"
    id = db.Column(db.Integer(), primary_key=True)
    user_in_game_id = db.Column(db.Integer(),db.ForeignKey("game_users.id", ondelete='CASCADE'),nullable=False)
    security_id = db.Column(db.String(10),db.ForeignKey("securites.id", ondelete='CASCADE'),nullable=False) 
    ammount = db.Column(db.Integer(),nullable=False)
    uniq_constr = db.UniqueConstraint('user_in_game_id', 'security_id', name='unc_user_secur')
   
    
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self._sequrity: SecuritesModel
        
    @property
    def sequrity(self) -> "SecuritesModel":
        return self._sequrity

    @sequrity.setter
    def sequrity(self,val: "SecuritesModel"):
        self._sequrity=val

class TradedSecuritesModel(db.Model):
    __tablename__ = "traded_securites"
    sequrity_id = db.Column(db.String(10),db.ForeignKey("securites.id", ondelete='CASCADE'),nullable=False)
    price = db.Column(db.Integer()) 
    round_id = db.Column(db.Integer(),db.ForeignKey("trade_rounds.id", ondelete='CASCADE'),nullable=False)
    market_event_id = db.Column(db.Integer(),db.ForeignKey("market_events.id", ondelete='CASCADE'),nullable=False)
    uniq_constr = db.UniqueConstraint('sequrity_id', 'round_id', name='unc_secur_round') 
 
  
    def __init__(self, **kw):
        super().__init__(**kw)
        self._security: SecuritesModel
        self._market_event: MarketEventsModel
      
    @property
    def market_event(self) -> "MarketEventsModel":
        return self._market_event

    @market_event.setter
    def market_event(self,val: "MarketEventsModel"):
        self._market_event=val

    @property
    def security(self) -> "SecuritesModel":
        return self._security

    @security.setter
    def security(self,val: "SecuritesModel"):
        self._security=val


class TradeRoundsModel(db.Model):
    __tablename__ = "trade_rounds"
    id = db.Column(db.Integer(), primary_key=True)
    number_in_game = db.Column(db.Integer(),nullable = False)
    state = db.Column(db.String(30),nullable = False)
    game_id = db.Column(db.Integer(),db.ForeignKey("games.id", ondelete='CASCADE'),nullable=False)
    uniq_constr = db.UniqueConstraint('number_in_game', 'game_id', name='unc_game_num_in_game')

    def __init__(self, **kw):
        super().__init__(**kw)
        self._traded_securites = []

    @property
    def traded_securites(self):
        return self._traded_securites

    @traded_securites.setter
    def traded_securites(self,val):
        if val is not None:
            self._traded_securites.append(val)

class MarketEventsModel(db.Model):
    __tablename__ = "market_events"
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.Unicode,nullable = False)
    diff = db.Column(db.Integer(), nullable=False) 

class TradeJornalModel(db.Model):
    __tablename__ = "trade_jornal"
    id = db.Column(db.Integer(), primary_key=True)
    round_id = db.Column(db.Integer(),db.ForeignKey("trade_rounds.id", ondelete='CASCADE'),nullable=False)
    user_id = db.Column(db.Integer(),db.ForeignKey("users.vk_id"),nullable=False)
    sequrity_id = db.Column(db.String(10),db.ForeignKey("securites.id", ondelete='CASCADE'),nullable=False)
    operation = db.Column(db.String(30),nullable = False)
    ammount = db.Column(db.Integer()) 

