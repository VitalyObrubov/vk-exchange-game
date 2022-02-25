from dataclasses import dataclass, field
from re import A
import string
from typing import Optional, List, Dict
from datetime  import datetime
from app.store.database.gino import db

@dataclass
class Security:
    id: str
    description: str


@dataclass
class User:
    vk_id: int
    name: str
    create_at: datetime
    points: int #кошелек
    securites: Dict["Security", int] = field(default_factory=dict)  #{security:ammount} купленные акции

@dataclass
class Security:
    id: str
    description: str
    start_price: int
 
@dataclass
class Game:
    id: int
    create_at: datetime
    chat_id: int
    state: str #started|finished
    trade_round: int
    trade_jornal: List[dict] = field(default_factory=list) #{user, operation,security,ammount} торгуемые акции
    users: List["User"] = field(default_factory=list)
    traded_sequrites: Dict["Security", int] = field(default_factory=dict) #{security:start_price} торгуемые акции


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
    chat_id = db.Column(db.Integer())
    state = db.Column(db.String(30),nullable = False)

class GameUsersModel(db.Model):
    __tablename__ = "game_users"
    id = db.Column(db.Integer(), primary_key=True)
    game_id = db.Column(db.Integer(),db.ForeignKey("games.id", ondelete='CASCADE'),nullable=False)
    user_id = db.Column(db.Integer(),db.ForeignKey("users.vk_id", ondelete='CASCADE'),nullable=False)
    points = db.Column(db.Integer())

class BuyedSecuritesModel(db.Model):
    __tablename__ = "buyed_securites"
    user_in_game_id = db.Column(db.Integer(),db.ForeignKey("game_users.id", ondelete='CASCADE'),nullable=False)
    security_id = db.Column(db.String(10),db.ForeignKey("securites.id", ondelete='CASCADE'),nullable=False) 
    ammount = db.Column(db.Integer()) 

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
    diff = db.Column(db.Integer()) 

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
    user_id = db.Column(db.Integer(),db.ForeignKey("users.vk_id", ondelete='CASCADE'),nullable=False)
    sequrity_id = db.Column(db.String(10),db.ForeignKey("securites.id", ondelete='CASCADE'),nullable=False)
    operation = db.Column(db.String(30),nullable = False)
    ammount = db.Column(db.Integer()) 

'''
# Дописать все необходимые поля модели

@dataclass
class Question:
    id: Optional[int]
    title: str
    theme_id: int
    answers: list["Answer"]

# TODO
# Дописать все необходимые поля модели

class AnswerModel(db.Model):
    __tablename__ = "answers"
    title = db.Column(db.String(300),nullable = False)
    is_correct = db.Column(db.Boolean())
    question_id = db.Column(db.Integer(),db.ForeignKey("questions.id", ondelete='CASCADE'),nullable=False)

class QuestionModel(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(300),nullable = False, unique=True)
    theme_id = db.Column(db.Integer(),db.ForeignKey("themes.id", ondelete='CASCADE'), nullable=False)
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self._answers: List[AnswerModel] = []

    @property
    def answers(self) -> List[AnswerModel]:
        return self._answers

    @answers.setter
    def answers(self,val: Optional[AnswerModel]):
        if val is not None:
            self._answers.append(val)



    

@dataclass
class Answer:
    title: str
    is_correct: bool
'''