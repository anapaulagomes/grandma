import pytest

from grandma.bot import CoffeeDB, Grandma

USER_ID = 'U9D779NCR'
TEST_DB_NAME = 'grandma-test.db'


@pytest.fixture
def bot():
    db = CoffeeDB(db_name=TEST_DB_NAME)
    return Grandma(db)


@pytest.fixture
def connected_bot(mocker):
    rtm_connect_mock = mocker.patch('grandma.bot.SlackClient.rtm_connect')
    api_call_mock = mocker.patch('grandma.bot.SlackClient.api_call')

    db = CoffeeDB(db_name='grandma-test.db')
    bot = Grandma(db)
    rtm_connect_mock.return_value = True
    api_call_mock.return_value = {'user_id': USER_ID}
    bot.connect()
    return bot


@pytest.fixture
def response_hello():
    return [{'type': 'hello'}]


@pytest.fixture
def empty_response():
    return []


@pytest.fixture
def response_subtype():
    return [{'subtype': 'bot_message', 'type': 'random'}]


@pytest.fixture
def mention_at_the_beginning():
    return [{
        'type': 'message',
        'channel': 'C9D338VA4',
        'user': USER_ID,
        'text': '<@U9D779NCR> is there coffee?',
        'ts': '1520350435.000740',
        'source_team': 'T9EPV9NH5',
        'team': 'T9EPV9NH5'
    }]


@pytest.fixture
def mention_at_the_end():
    return [{
        'type': 'message',
        'channel': 'C9D338VA4',
        'user': USER_ID,
        'text': 'has coffee? <@U9D779NCR>',
        'ts': '1520350435.000740',
        'source_team': 'T9EPV9NH5',
        'team': 'T9EPV9NH5'
    }]


@pytest.fixture
def mention_in_the_middle():
    return [{
        'type': 'message',
        'channel': 'C9D338VA4',
        'user': USER_ID,
        'text': 'hi <@U9D779NCR> coffee?',
        'ts': '1520350435.000740',
        'source_team': 'T9EPV9NH5',
        'team': 'T9EPV9NH5'
    }]


@pytest.fixture
def bot_ask_for_coffee(mocker, connected_bot):
    rtm_read_mock = mocker.patch('grandma.bot.SlackClient.rtm_read')
    rtm_read_mock.return_value = [{
        'type': 'message',
        'text': '<@U9D779NCR> coffee?'
    }]
    return connected_bot
