import pytest
from datetime import datetime

from app.game.models import Game, User, GameModel
from app.store import Store


@pytest.fixture()
async def started_game(cli, store: Store):
    users = {}
    user = User(
        vk_id=10001,
        name="Test User 1", 
        create_at=datetime.utcnow(),
        points = 10000,
        buyed_securites={},
        state = "in_trade")        
    users[user.vk_id] = user
    user = User(
        vk_id=10002,
        name="Test User 2", 
        create_at=datetime.utcnow(),
        points = 10000,
        buyed_securites={},
        state = "in_trade")        
    users[user.vk_id] = user
    res = await store.games.start_game(10001, users)
    game = cli.app.games.get(10001)
    sequr = game.traded_sequrites.get("AFLT")
    sequr.price = 100
    yield res

    cli.app.games.pop(10001, None) # удаляем игру из списка игр


@pytest.fixture()
async def buyed_secur(cli, store: Store):
    game:Game = cli.app.games.get(10001)
    user:User = game.users.get(10001)
    params = {}
    params["game"] = game
    params["user"] = user
    params["secur"] = game.traded_sequrites.get("AFLT")
    params["ammount"] = 10
    await store.games.buy_securyties(params)
    return

@pytest.fixture()
def users(cli):
    users = {}
    user = User(
        vk_id=10001,
        name="Test User 1", 
        create_at=datetime.utcnow(),
        points = 10000,
        buyed_securites={},
        state = "in_trade")        
    users[user.vk_id] = user
    user = User(
        vk_id=10002,
        name="Test User 2", 
        create_at=datetime.utcnow(),
        points = 10000,
        buyed_securites={},
        state = "in_trade")        
    users[user.vk_id] = user

    return users

@pytest.fixture()
def chat_id(cli):
    return 10001

@pytest.fixture()
def user_id(cli):
    return 10001

@pytest.fixture()
def sell_params(cli):
    game:Game = cli.app.games.get(10001)
    user:User = game.users.get(10001)
    params = {}
    params["game"] = game
    params["user"] = user
    params["secur"] = user.buyed_securites.get("AFLT")
    params["ammount"] = 10
    return params

@pytest.fixture()
def buy_params(cli):
    game:Game = cli.app.games.get(10001)
    user:User = game.users.get(10001)
    params = {}
    params["game"] = game
    params["user"] = user
    params["secur"] = game.traded_sequrites.get("AFLT")
    params["ammount"] = 10
    return params