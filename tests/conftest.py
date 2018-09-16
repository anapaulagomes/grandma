from grandma.server.main import app as api

import pytest
import os
import tempfile
from playhouse.flask_utils import FlaskDB
from grandma.server.app import db_wrapper
from grandma.server.bot import Coffee
from functools import wraps
from peewee import *


test_db = SqliteDatabase(':memory:')
MODELS = [Coffee]


@pytest.fixture
def app():
    api.config['TESTING'] = True
    api.config['DATABASE'] = ':memory:'
    return api


def use_test_database(fn):
    @wraps(fn)
    def inner(*args, **kwds):
        with test_db.bind_ctx(MODELS):
            test_db.create_tables(MODELS, safe=True)
            try:
                fn(*args, **kwds)
            finally:
                test_db.drop_tables(MODELS)
    return inner


@pytest.fixture
def slack_calls_mock(mocker):
    rtm_connect_mock = mocker.patch('grandma.server.bot.SlackClient.rtm_connect')
    api_call_mock = mocker.patch('grandma.server.bot.SlackClient.api_call')
    rtm_connect_mock.return_value = True
    api_call_mock.return_value = {'user_id': 'A1B999WWW'}
    return api_call_mock
