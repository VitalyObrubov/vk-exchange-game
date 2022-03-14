
from tests.utils import ok_response
from app.store import Store
import pytest
from tests.utils import check_empty_table_exists
from asyncpg.exceptions import UniqueViolationError



class TestBot:
    async def test_handle_updates(self, cli, store: Store, updates):
        answ =  await store.bots_manager.handle_updates(updates)
        assert answ == 'Успешно'

    
 