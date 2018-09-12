from grandma.server import app as api
import pytest


@pytest.fixture
def app():
    api.config['TESTING'] = True
    return api