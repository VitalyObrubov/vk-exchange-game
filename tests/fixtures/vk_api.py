import datetime
import functools

import pytest
from aioresponses import aioresponses
from dateutil import tz
from freezegun import freeze_time
from gino import GinoEngine

@pytest.fixture
async def vk_connected(cli):
    await cli.app.store.vk_api.connect(cli.app)
    return