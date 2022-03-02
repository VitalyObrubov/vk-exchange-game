import datetime
import functools

import pytest
from aioresponses import aioresponses
from dateutil import tz
from freezegun import freeze_time
from gino import GinoEngine

@pytest.fixture
async def mock_response():
    with aioresponses(passthrough=["http://127.0.0.1"]) as responses_mock:
        yield responses_mock