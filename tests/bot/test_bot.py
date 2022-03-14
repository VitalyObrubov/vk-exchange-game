from app.store import Store


class TestBot:
    async def test_handle_updates(self, cli, store: Store, updates):
        answ =  await store.bots_manager.handle_updates(updates)
        assert answ == 'Успешно'

    
 