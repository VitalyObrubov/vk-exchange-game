import os
from unittest.mock import AsyncMock
import pytest
from aiohttp.test_utils import TestClient, loop_context
from gino import GinoEngine
import functools
from aioresponses import aioresponses

from app.store import Store
from app.web.app import setup_app
from app.web.config import Config
from app.store import Database


@pytest.fixture(scope="session")
def loop():
    with loop_context() as _loop:
        yield _loop


@pytest.fixture(scope="session")
def server():
    app = setup_app(
        config_path=os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "config.yml"
        )
    )
    app.on_startup.clear()
    app.on_shutdown.clear()
    #app.store.vk_api = AsyncMock()
    app.store.vk_api.send_message = AsyncMock()

    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_shutdown.append(app.database.disconnect)

    app.on_startup.append(app.store.games.connect)
    app.on_shutdown.append(app.store.games.disconnect)

    
    app.on_startup.append(app.store.vk_api.connect)
    app.on_shutdown.append(app.store.vk_api.disconnect)

    app.on_startup.append(app.store.admins.connect)
    app.on_shutdown.append(app.store.admins.connect)
    return app


@pytest.fixture
def store(server) -> Store:
    return server.store

@pytest.fixture(autouse=True, scope="function")
async def db_transaction(cli):

    db = cli.app.database.db
    real_acquire = GinoEngine.acquire

    async with db.acquire() as conn:

        class _AcquireContext:
            __slots__ = ["_acquire", "_conn"]

            def __init__(self, acquire):
                self._acquire = acquire

            async def __aenter__(self):
                return conn

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

            def __await__(self):
                return conn

        def acquire(
            self, *, timeout=None, reuse=False, lazy=False, reusable=True
        ):
            return _AcquireContext(
                functools.partial(self._acquire, timeout, reuse, lazy, reusable)
            )

        GinoEngine.acquire = acquire
        transaction = await conn.transaction()
        yield
        await transaction.rollback()
        GinoEngine.acquire = real_acquire

@pytest.fixture
def config(server) -> Config:
    return server.config


@pytest.fixture(autouse=True)
def cli(aiohttp_client, loop, server) -> TestClient:
    return loop.run_until_complete(aiohttp_client(server))


@pytest.fixture
async def authed_cli(cli, config) -> TestClient:
    await cli.post(
        "/admin.login",
        data={
            "email": config.admin.email,
            "password": config.admin.password,
        },
    )
    yield cli

@pytest.fixture(autouse=True)
async def mock_response(cli):
    with aioresponses(passthrough=["http://127.0.0.1"]) as responses_mock:
        yield responses_mock