from typing import Optional, List
from app.store.database.gino import db
from app.base.base_accessor import BaseAccessor
'''
from app.game.models import (
    Theme,
    Question,
    Answer,
    ThemeModel,
    QuestionModel,
    AnswerModel,
)
from asyncpg.exceptions import NotNullViolationError


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        #theme = await self.get_theme_by_title(title)
        #if theme:
        #    raise HTTPConflict

        res = await ThemeModel.create(title=title)
        theme = Theme(id=res.id, title=title)
        return theme

    async def get_theme_by_title(self, title: str) -> Optional[Theme]:
        res = await ThemeModel.query.where(ThemeModel.title==title).gino.first()
        if res is not None:
            theme = Theme(id=res.id, title=res.title)
            return theme
    async def get_theme_by_id(self, id_: int) -> Optional[Theme]:
        res = await ThemeModel.query.where(ThemeModel.id==id_).gino.first()
        if res is not None:
            theme = Theme(id=res.id, title=res.title)
            return theme
 
    async def list_themes(self) -> List[Theme]:
        res = await ThemeModel.query.gino.all()
        data = []
        for row in res:
            data.append(Theme(row.id,row.title))
        
        return data

    async def create_answers(self, question_id, answers: List[Answer]):
        for answer in answers:
            await AnswerModel.create(title=answer.title,is_correct=answer.is_correct,question_id=question_id)

    async def get_answers_by_question_id(self, question_id) -> Optional[List[Answer]]:
        res = await AnswerModel.query.where(AnswerModel.question_id==question_id).gino.all()
        answers = []
        for answer in res:
            answers.append(Answer(answer.title,answer.is_correct))
        return answers

    async def create_question(
        self, title: str, theme_id: int, answers: List[Answer]
    ) -> Question:
        if theme_id == None:
            raise NotNullViolationError 
        res = await QuestionModel.create(title=title,theme_id=theme_id)
        await self.create_answers(res.id, answers)
        question = Question(id=res.id, title=title,theme_id=res.theme_id,answers=answers)
        return question

    async def get_question_by_title(self, title: str) -> Optional[Question]:
        res = await QuestionModel.query.where(QuestionModel.title==title).gino.first()
        if res is not None:
            answers = await self.get_answers_by_question_id(res.id)
            question = Question(id=res.id, title=title,theme_id=res.theme_id,answers=answers)
            return question


    async def list_questions(self, theme_id: Optional[int] = None) -> List[Question]:
        
        if theme_id:

            res = await (
                QuestionModel.join(AnswerModel,QuestionModel.id == AnswerModel.question_id)
                .select()
                .where(QuestionModel.theme_id == theme_id)                
                .gino
                .load(QuestionModel.distinct(QuestionModel.id)
                .load(answers=AnswerModel))
                .all()
            ) 
        else:
            res = await (
                QuestionModel.join(AnswerModel,QuestionModel.id == AnswerModel.question_id)
                .select()
                .gino
                .load(QuestionModel.distinct(QuestionModel.id)
                .load(answers=AnswerModel))
                .all()
            )            
       

        questions = []
        
        
        loc_question = None
        for question in res:
            answers = []
            loc_question = Question(question.id,question.title,question.theme_id,answers)
            for answer in question.answers:
                loc_question.answers.append(Answer(answer.title,answer.is_correct))
            questions.append(loc_question) 
        o=0
        return questions    
'''
