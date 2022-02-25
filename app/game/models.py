from dataclasses import dataclass
from re import A
from typing import Optional, List

from app.store.database.gino import db

'''
@dataclass
class Theme:
    id: Optional[int]
    title: str

# TODO
# Дописать все необходимые поля модели

class ThemeModel(db.Model):
    __tablename__ = "themes"
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(300),nullable = False, unique=True)
   
# TODO
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