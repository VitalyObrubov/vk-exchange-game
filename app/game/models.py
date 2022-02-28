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
    security: Security
    ammount: int

@dataclass
class User:
    vk_id: int
    name: str
    create_at: datetime
    points: int #кошелек
    buyed_securites: list[BuyedSecurity]

 
@dataclass
class Game:
    id: int
    create_at: datetime
    chat_id: int
    state: str #started|finished
    trade_round: int
    users: list[User] 
    traded_sequrites: list[Security]


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

class GameUsersModel(db.Model):
    __tablename__ = "game_users"
    id = db.Column(db.Integer(), primary_key=True)
    game_id = db.Column(db.Integer(),db.ForeignKey("games.id", ondelete='CASCADE'),nullable=False)
    user_id = db.Column(db.Integer(),db.ForeignKey("users.vk_id"),nullable=False)
    points = db.Column(db.Integer(),nullable=False)

class BuyedSecuritesModel(db.Model):
    __tablename__ = "buyed_securites"
    user_in_game_id = db.Column(db.Integer(),db.ForeignKey("game_users.id", ondelete='CASCADE'),nullable=False)
    security_id = db.Column(db.String(10),db.ForeignKey("securites.id", ondelete='CASCADE'),nullable=False) 
    ammount = db.Column(db.Integer(),nullable=False) 

class TradeRoundsModel(db.Model):
    __tablename__ = "trade_rounds"
    id = db.Column(db.Integer(), primary_key=True)
    number_in_game = db.Column(db.Integer(),nullable = False)
    state = db.Column(db.String(30),nullable = False)
    game_id = db.Column(db.Integer(),db.ForeignKey("games.id", ondelete='CASCADE'),nullable=False)

class MarketEventsModel(db.Model):
    __tablename__ = "market_events"
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.Unicode,nullable = False)
    diff = db.Column(db.Integer(), nullable=False) 

class TradedSecuritesModel(db.Model):
    __tablename__ = "traded_securites"
    sequrity_id = db.Column(db.String(10),db.ForeignKey("securites.id", ondelete='CASCADE'),nullable=False)
    price = db.Column(db.Integer()) 
    round_id = db.Column(db.Integer(),db.ForeignKey("trade_rounds.id", ondelete='CASCADE'),nullable=False)
    market_event_id = db.Column(db.Integer(),db.ForeignKey("market_events.id", ondelete='CASCADE'),nullable=False)

class TradeJornalModel(db.Model):
    __tablename__ = "trade_jornal"
    id = db.Column(db.Integer(), primary_key=True)
    round_id = db.Column(db.Integer(),db.ForeignKey("trade_rounds.id", ondelete='CASCADE'),nullable=False)
    user_id = db.Column(db.Integer(),db.ForeignKey("users.vk_id"),nullable=False)
    sequrity_id = db.Column(db.String(10),db.ForeignKey("securites.id", ondelete='CASCADE'),nullable=False)
    operation = db.Column(db.String(30),nullable = False)
    ammount = db.Column(db.Integer()) 

