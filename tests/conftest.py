from grandma.server.main import app as api

import pytest


@pytest.fixture
def app():
    api.config['TESTING'] = True
    api.config['DATABASE'] = 'grandma-test.db'
    return api