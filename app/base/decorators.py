from logging import getLogger
import functools
from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp import web

def errors_catching(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = getLogger("handler")
            logger.error("Exception", exc_info=e) 
            return e
    return wrapper

def errors_catching_async(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger = getLogger("handler")
            logger.error("Exception", exc_info=e) 
            return e
    return wrapper

def require_auth(func):
    @functools.wraps(func)
    async def require_auth_wrap(self, *args, **kwargs):
        if "user_id" not in self.request:
            raise HTTPUnauthorized
        return await func(self, *args, **kwargs)
    return require_auth_wrap

def login_required (func): # Проверка статуса входа пользователя
    """This function applies only to class views."""
    @functools.wraps(func)
    async def inner(self, *args, **kwargs):
        try:
            adm = self.request.admin.email
            return await func(self,*args, **kwargs)            
        except Exception as e:
            print(e)
            return web.Response(status=302, headers={'location': '/login'}) 
    return inner