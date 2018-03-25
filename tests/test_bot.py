import os
import sqlite3
from unittest.mock import call, patch

import pytest
from freezegun import freeze_time

from grandma.bot import BotNotConnected, CoffeeDB

from .fixtures import TEST_DB_NAME


class TestBotConnection:
    @classmethod
    def teardown_class(cls):
        os.remove(TEST_DB_NAME)

    @patch('grandma.bot.SlackClient.api_call')
    @patch('grandma.bot.SlackClient.rtm_connect')
    def test_connect_on_slack_api(self, rtm_connect_mock, api_call_mock, bot):
        expected_user_id = 'A1B999WWW'

        rtm_connect_mock.return_value = True
        api_call_mock.return_value = {'user_id': expected_user_id}

        bot.connect()

        assert bot._id == expected_user_id
        assert rtm_connect_mock.called
        assert api_call_mock.called

    @patch('grandma.bot.SlackClient.rtm_connect')
    def test_connection_with_slack_fails(self, rtm_connect_mock, bot):
        rtm_connect_mock.return_value = False

        assert hasattr(bot, '_id') is False

    def test_raise_exception_when_was_not_connected(self, bot):
        with pytest.raises(BotNotConnected):
            bot.listen_and_answer()

    @patch('grandma.bot.SlackClient.rtm_read')
    def test_read_from_slack_rtm(self, rtm_read_mock, connected_bot):
        rtm_read_mock.return_value = [{'type': 'hello'}]
        connected_bot.listen_and_answer()

        assert rtm_read_mock.called


class TestBotParser:
    @pytest.mark.parametrize('response', [
        'mention_at_the_beginning',
        'mention_in_the_middle',
        'mention_at_the_end',
    ])
    @patch('grandma.bot.SlackClient.api_call')
    @patch('grandma.bot.SlackClient.rtm_read')
    def test_read_from_slack_rtm(self, rtm_read_mock, api_call_mock,
                                 connected_bot, response, request):
        rtm_read_mock.return_value = request.getfuncargvalue(response)

        connected_bot.listen_and_answer()

        assert rtm_read_mock.called
        assert api_call_mock.called

    @pytest.mark.parametrize('response,content,mention', [
        ('mention_at_the_beginning', ' is there coffee?', 'U9D779NCR'),
        ('mention_in_the_middle', 'hi  coffee?', 'U9D779NCR'),
        ('mention_at_the_end', 'has coffee? ', 'U9D779NCR'),
    ])
    def test_parse_message(self, response, request, content, mention, bot):
        response = request.getfuncargvalue(response)
        message = bot._parse_message(response[0]['text'])

        assert message.content == content
        assert message.mention == mention

    def test_does_not_parse_message_if_bot_is_not_mentioned(self, bot):
        message = bot._parse_message('random stuff')

        assert message is None

    @pytest.mark.parametrize('message,response', [
        ('coffee?', 'I did coffee for you'),
        ('random stuff', "I'm not listening well. What did you say?"),
        ('coffee is done', 'The best coffee in town is served'),
        ('coffee is ready', 'The best coffee in town is served'),
        ('coffee is served', 'The best coffee in town is served'),
    ])
    @patch('grandma.bot.SlackClient.api_call')
    def test_answer(self, api_call_mock, message, response, connected_bot):
        connected_bot.db.update(has_coffee=True)
        connected_bot._answer_about_coffee(message)

        expected_args = [
            call(
                'chat.postMessage',
                channel=connected_bot.DEFAULT_CHANNEL,
                text=response)
        ]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args

    @pytest.mark.parametrize('response', [
        'response_hello', 'empty_response', 'response_subtype',
    ])
    @patch('grandma.bot.SlackClient.api_call')
    @patch('grandma.bot.SlackClient.rtm_read')
    def test_do_nothing_if_is_not_a_message(
            self, rtm_read_mock, api_call_mock, connected_bot, request, response):
        rtm_read_mock.return_value = request.getfuncargvalue(response)

        connected_bot.listen_and_answer()

        assert rtm_read_mock.called
        assert api_call_mock.called is False

    @patch('grandma.bot.SlackClient.api_call')
    @patch('grandma.bot.SlackClient.rtm_read')
    def test_if_does_not_mention_directly_reply_with_emoji(
            self, rtm_read_mock, api_call_mock, connected_bot):
        rtm_read_mock.return_value = [{
            'type': 'message',
            'text': 'my grandma is the best'
        }]

        connected_bot.listen_and_answer()

        expected_args1 = [
            call(
                'chat.postMessage',
                channel=connected_bot.DEFAULT_CHANNEL,
                text=':thinking_face:')
        ]
        expected_args2 = [
            call(
                'chat.postMessage',
                channel=connected_bot.DEFAULT_CHANNEL,
                text=':two_hearts:')
        ]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args1 or \
            api_call_mock.call_args_list == expected_args2


class TestCoffeeDB:

    @pytest.fixture
    def cursor(self):
        conn = sqlite3.connect(TEST_DB_NAME)
        cursor = conn.cursor()
        yield cursor
        conn.close()

        os.remove(TEST_DB_NAME)

    def test_create_db_with_coffees_table(self, cursor):
        db = CoffeeDB(db_name=TEST_DB_NAME)
        db.create()

        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='coffees';
        """
        cursor.execute(query)

        assert cursor.fetchone()

    @pytest.mark.parametrize('expected_has_coffee,result', [(True, 1),
                                                            (False, 0)])
    def test_save_coffee_according_status(
            self, expected_has_coffee, result, cursor):
        db = CoffeeDB(db_name=TEST_DB_NAME)
        db.create()
        db.update(expected_has_coffee)

        cursor.execute('SELECT * FROM coffees ORDER BY id DESC LIMIT 1')
        _, _, has_coffee = cursor.fetchone()

        assert has_coffee == result


class TestBotAnswers:
    @classmethod
    def teardown_class(cls):
        os.remove(TEST_DB_NAME)

    @patch('grandma.bot.SlackClient.api_call')
    def test_answer_if_has_coffee(self, api_call_mock, bot_ask_for_coffee):
        bot_ask_for_coffee.db.update(has_coffee=True)
        bot_ask_for_coffee.listen_and_answer()

        expected_args = [
            call(
                'chat.postMessage',
                channel=bot_ask_for_coffee.DEFAULT_CHANNEL,
                text='I did coffee for you')
        ]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args

    @patch('grandma.bot.SlackClient.api_call')
    def test_answer_if_coffee_is_over(self, api_call_mock, bot_ask_for_coffee):
        bot_ask_for_coffee.db.update(has_coffee=False)

        bot_ask_for_coffee.listen_and_answer()

        expected_args = [
            call(
                'chat.postMessage',
                channel=bot_ask_for_coffee.DEFAULT_CHANNEL,
                text="I'm afraid we don't have it :face_with_monocle:")
        ]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args

    @patch('grandma.bot.SlackClient.api_call')
    def test_answer_coffee_is_cold_if_coffee_has_more_than_one_hour(
            self, api_call_mock, bot_ask_for_coffee):
        with freeze_time('2017-12-01 12:10:01.262065'):
            bot_ask_for_coffee.db.update(has_coffee=True)

        with freeze_time('2017-12-01 13:15:00.262065'):
            bot_ask_for_coffee.listen_and_answer()

        expected_args = [
            call(
                'chat.postMessage',
                channel=bot_ask_for_coffee.DEFAULT_CHANNEL,
                text='Maybe, if you like cold coffee... :grimacing:')
        ]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args

    @patch('grandma.bot.SlackClient.api_call')
    def test_answer_i_dont_think_so_if_after_two_hours(
            self, api_call_mock, bot_ask_for_coffee):
        with freeze_time('2017-12-01 12:10:01.262065'):
            bot_ask_for_coffee.db.update(has_coffee=True)

        with freeze_time('2017-12-01 14:15:00.262065'):
            bot_ask_for_coffee.listen_and_answer()

        expected_args = [
            call(
                'chat.postMessage',
                channel=bot_ask_for_coffee.DEFAULT_CHANNEL,
                text="I don't think so")
        ]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args

    @patch('grandma.bot.SlackClient.api_call')
    @patch('grandma.bot.SlackClient.rtm_read')
    def test_answer_when_someone_else_made_coffee(
            self, rtm_read_mock, api_call_mock, connected_bot):
        rtm_read_mock.return_value = [{
            'type': 'message',
            'text': '<@U9D779NCR> coffee is done'
        }]
        connected_bot.db.update(has_coffee=False)

        connected_bot.listen_and_answer()

        expected_args = [
            call(
                'chat.postMessage',
                channel=connected_bot.DEFAULT_CHANNEL,
                text='The best coffee in town is served')
        ]

        assert connected_bot.db.has_coffee()[0] is True
        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args

    @patch('grandma.bot.SlackClient.api_call')
    @patch('grandma.bot.SlackClient.rtm_read')
    def test_answer_when_someone_else_inform_that_coffee_is_over(
            self, rtm_read_mock, api_call_mock, connected_bot):
        rtm_read_mock.return_value = [{
            'type': 'message',
            'text': '<@U9D779NCR> coffee is over'
        }]
        connected_bot.db.update(has_coffee=False)

        connected_bot.listen_and_answer()

        expected_args = [
            call(
                'chat.postMessage',
                channel=connected_bot.DEFAULT_CHANNEL,
                text='Oh no')
        ]

        assert connected_bot.db.has_coffee()[0] is False
        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args
