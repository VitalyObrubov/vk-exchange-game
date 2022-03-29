from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session
from aiohttp import web
import aiohttp_jinja2
from typing import Optional

from app.admin.schemes import AdminSchema
from app.admin.models import AdminModel
from app.game.models import UserModel, SecuritesModel
from app.web.app import View
from app.base.decorators import login_required



def get_adm(obj):
    try:
        adm = obj.request.admin.email
    except:
        adm = "Войти" 
    return adm   

class Index(View):
    """a view handler for home page"""
    @login_required
    async def get(self):
        # response.headers['Content-Language'] = 'utf-8'
        adm = get_adm(self)
        title = "Администрирование бота"
        return aiohttp_jinja2.render_template('index.html', self.request, locals())

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class AdminLoginView(View):

    async def get(self):
        adm = get_adm(self)
        return aiohttp_jinja2.render_template('login.html', self.request, locals())

    async def post(self):

        data = await self.request.post()
        email = data.get('email')
        password = data.get('password')

        admin = await self.store.admins.get_by_email(email)
        if not admin:
            msg = {'error_code': 20002, 'error_msg': 'Пользователь не найден'}
            return aiohttp_jinja2.render_template('login.html', self.request, locals())

        if not admin.is_password_valid(password):
            msg = {'error_code': 20004, 'error_msg': 'Неверный пароль'}
            return aiohttp_jinja2.render_template('login.html', self.request, locals())

        admin_data = AdminSchema().dump(admin)
        session = await new_session(request=self.request)
        session["admin"] = admin_data

        return web.Response(status=302, headers={'location': '/'})




class AdminListView(View):
    @login_required
    async def get(self): 
        adm = get_adm(self)   
        admins = await AdminModel.query.order_by(AdminModel.id).gino.all()
        return aiohttp_jinja2.render_template('admins.html', self.request, locals())

    async def post(self):

        data = await self.request.post()
        email = data.get('email')
        password = data.get('password')
        admin = await self.store.admins.create_admin(email, password)
        
        if not admin:
            msg = {'error_code': 20002, 'error_msg': 'Пользователь не создан'}
            return aiohttp_jinja2.render_template('login.html', self.request, locals())
        elif not admin.is_password_valid(password):
            msg = {'error_code': 20004, 'error_msg': 'Неверный пароль'}
            return aiohttp_jinja2.render_template('login.html', self.request, locals())           
        return web.Response(status=302, headers={'location': '/admins'})


class AdminDelView(View):
    @login_required
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        return

    async def post(self):
        data = await self.request.json()
        email = data.get('email')
        if email != "admin@admin.com":
            await AdminModel.delete.where(AdminModel.email == email).gino.status()
        else:
            msg = "Этого админа удалять нельзя"          
        return web.Response(status=302, headers={'location': '/admins'})



class GamersListView(View):
    @login_required
    async def get(self): 
        adm = get_adm(self)   
        users = await UserModel.query.order_by(UserModel.vk_id).gino.all()
        return aiohttp_jinja2.render_template('gamers.html', self.request, locals())


class SecursListView(View):
    @login_required
    async def get(self): 
        adm = get_adm(self)   
        securs = await SecuritesModel.query.order_by(SecuritesModel.id).gino.all()
                                               
        return aiohttp_jinja2.render_template('securs.html', self.request, locals())
    
    async def post(self):

        data = await self.request.post()
        id = data.get('id')
        description = data.get('description')
        start_price = int(data.get('start_price'))

        existing_secur = await self.store.games.get_secur_by_id(id)
        if existing_secur:
            msg = {'error_code': 20002, 'error_msg': 'Акция уже существует'}
            return aiohttp_jinja2.render_template('securs.html', self.request, locals())

        secur = await self.store.games.create_secur(id, description, start_price)
         
        return web.Response(status=302, headers={'location': '/securs'})

class GamesListView(View):
    @login_required
    async def get(self): 
        adm = get_adm(self)   
        games = await self.store.games.restore_games_on_startup("finished")
        return aiohttp_jinja2.render_template('games.html', self.request, locals())