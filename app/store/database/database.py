import gino
import typing
from gino.api import Gino
from app.store.database.gino import db
from app.admin.models import *
from app.game.models import *
from sqlalchemy.engine.url import URL
if typing.TYPE_CHECKING:
    from app.web.app import Application

class Database:
    db: Gino

    def __init__(self, app: "Application"):
        self.app = app
        self.db: Optional[Gino] = None

    async def connect(self, *_, **kw):
        self._engine = await gino.create_engine(
            URL(
                drivername="asyncpg",
                host=self.app.config.database.host,
                database=self.app.config.database.database,
                username=self.app.config.database.user,
                password=self.app.config.database.password,
                port=self.app.config.database.port,
            ),
            min_size=1,
            max_size=1,
        )
        self.db = db
        self.db.bind = self._engine
        db.bind = self._engine #for del
    async def disconnect(self, *_, **kw):
        return None

