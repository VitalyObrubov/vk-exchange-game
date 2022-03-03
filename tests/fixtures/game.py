import pytest
from datetime import datetime

from app.game.models import Game, User, GameModel
from app.store import Store


@pytest.fixture(scope="function")
async def start_game(cli, store: Store):
    cli.app.games.pop(10001, None) # удаляем игру из списка игр
        
    users = {}
    user = User(
        vk_id=10001,
        name="Test User 1", 
        create_at=datetime.utcnow(),
        points = 10000,
        buyed_securites={},
        state = "in_trade")        
    users[user.vk_id] = user
    res = await store.games.start_game(10001, users)
    
    yield res

    cli.app.games.pop(10001, None) # удаляем игру из списка игр


@pytest.fixture(scope="function")
async def buy_secur(cli, store: Store):
    await store.games.buy_securyties(10001, 10001, "/buy AFLT 11")
    yield