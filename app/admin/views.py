from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session
from aiohttp import web
import aiohttp_jinja2
from typing import Optional

from app.admin.schemes import AdminSchema
from app.admin.models import AdminModel
from app.web.app import View
from aiohttp.web import HTTPForbidden, HTTPUnauthorized
from app.web.utils import json_response
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
        email, password = self.data["email"], self.data["password"]
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


class AdminCurrentView(View):
    @login_required
    @response_schema(AdminSchema, 200)
    async def get(self):
        if self.request.admin:
            return json_response(data=AdminSchema().dump(self.request.admin))
        raise HTTPUnauthorized


class AdminListView(View):
    @login_required
    async def get(self): 
        adm = get_adm(self)   
        admins = await AdminModel.query.order_by(AdminModel.id).gino.all()
        return aiohttp_jinja2.render_template('admins.html', self.request, locals())

    async def post(self):
        email, password = self.data["email"], self.data["password"]
        admin = await self.store.admins.create_admin(email, password)
        
        if not admin:
            msg = {'error_code': 20002, 'error_msg': 'Пользователь не создан'}
            return aiohttp_jinja2.render_template('login.html', self.request, locals())
        elif admin.is_password_valid(password):
            msg = {'error_code': 20004, 'error_msg': 'Неверный пароль'}
            return aiohttp_jinja2.render_template('login.html', self.request, locals())           
        return web.Response(status=302, headers={'location': '/admins'})


class AdminAddView(View):
    @login_required
    @aiohttp_jinja2.template('register.html')
    async def get(self):
        return




    
