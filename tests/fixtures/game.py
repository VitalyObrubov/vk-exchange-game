import pytest
from datetime import datetime

from app.game.models import Game, User, GameModel
from app.store import Store


@pytest.fixture()
async def started_game(cli, store: Store):
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


@pytest.fixture()
async def buyed_secur(cli, store: Store):
    await store.games.buy_securyties(10001, 10001, "/buy AFLT 11")
    yield

@pytest.fixture()
async def users(cli):
    users = {}
    user = User(
        vk_id=10001,
        name="Test User 1", 
        create_at=datetime.utcnow(),
        points = 10000,
        buyed_securites={},
        state = "in_trade")        
    users[user.vk_id] = user

    yield users

@pytest.fixture()
async def chat_id(cli):
    yield 10001

@pytest.fixture()
async def user_id(cli):
    yield 10001