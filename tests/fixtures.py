from grandma.bot import Grandma
import pytest


USER_ID = 'U9D779NCR'


@pytest.fixture
def connected_bot(mocker):
    rtm_connect_mock = mocker.patch('grandma.bot.SlackClient.rtm_connect')
    api_call_mock = mocker.patch('grandma.bot.SlackClient.api_call')

    bot = Grandma()
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
def response_with_different_type():
    return [{
        'type': 'user_typing',
        'channel': 'D9DPELVBL',
        'user': USER_ID
    }]


@pytest.fixture
def ask_for_coffee(mocker, connected_bot, mention_at_the_end):
    rtm_read_mock = mocker.patch('grandma.bot.SlackClient.rtm_read')
    rtm_read_mock.return_value = mention_at_the_end
    return connected_bot
