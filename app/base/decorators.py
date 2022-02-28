from logging import getLogger
import functools
from aiohttp.web_exceptions import HTTPUnauthorized

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

def errors_catching_asinc(func):
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