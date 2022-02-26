import typing
from hashlib import sha256
from typing import Optional
from app.store.database.gino import db
from app.base.base_accessor import BaseAccessor
#from app.admin.models import Admin, AdminModel

if typing.TYPE_CHECKING:
    from app.web.app import Application

