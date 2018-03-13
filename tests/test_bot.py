from grandma.bot import (
    Grandma, BotNotConnected, create_db, update_coffee,
    DEFAULT_CHANNEL, DB_NAME)
from unittest.mock import patch, call
import pytest
import sqlite3
import os


TEST_DB_NAME = 'grandma-test.db'

class TestBotConnection:

    @patch('grandma.bot.SlackClient.api_call')
    @patch('grandma.bot.SlackClient.rtm_connect')
    def test_connect_on_slack_api(self, rtm_connect_mock, api_call_mock):
        bot = Grandma()
        expected_user_id = 'A1B999WWW'

        rtm_connect_mock.return_value = True
        api_call_mock.return_value = {'user_id': expected_user_id}

        bot.connect()

        assert bot._id == expected_user_id
        assert rtm_connect_mock.called
        assert api_call_mock.called

    @patch('grandma.bot.SlackClient.rtm_connect')
    def test_connection_with_slack_fails(self, rtm_connect_mock):
        bot = Grandma()
        rtm_connect_mock.return_value = False

        assert hasattr(bot, '_id') is False

    def test_raise_exception_when_was_not_connected(self):
        bot = Grandma()

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
    def test_parse_message(self, response, request, content, mention):
        response = request.getfuncargvalue(response)
        bot = Grandma()
        message = bot._parse_message(response[0]['text'])

        assert message.content == content
        assert message.mention == mention

    def test_does_not_parse_message_if_bot_is_not_mentioned(self):
        bot = Grandma()
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
        connected_bot._answer_about_coffee(message)

        expected_args = [
            call('chat.postMessage', channel=DEFAULT_CHANNEL, text=response)]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args

    @patch('grandma.bot.SlackClient.api_call')
    def test_if_does_not_mention_directly_reply_with_emoji(
            self, api_call_mock, connected_bot):
        message = 'my grandma is the best'
        connected_bot._answer_random_interaction()

        expected_args1 = [
            call(
                'chat.postMessage',
                channel=DEFAULT_CHANNEL,
                text=':thinking_face:')]
        expected_args2 = [
            call(
                'chat.postMessage',
                channel=DEFAULT_CHANNEL,
                text=':two_hearts:')]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args1 or \
            api_call_mock.call_args_list == expected_args2

    @patch('grandma.bot.SlackClient.api_call')
    @patch('grandma.bot.SlackClient.rtm_read')
    def test_if_does_not_mention_directly_reply(self, rtm_read_mock,
            api_call_mock, connected_bot):
        rtm_read_mock.return_value = [
            {'type': 'message', 'text': 'my grandma is the best'}]

        connected_bot.listen_and_answer()

        expected_args1 = [
            call(
                'chat.postMessage',
                channel=DEFAULT_CHANNEL,
                text=':thinking_face:')]
        expected_args2 = [
            call(
                'chat.postMessage',
                channel=DEFAULT_CHANNEL,
                text=':two_hearts:')]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args1 or \
            api_call_mock.call_args_list == expected_args2


class TestCoffeeDatabase:
    def _db(self):
        conn = sqlite3.connect(TEST_DB_NAME)
        cursor = conn.cursor()
        yield cursor
        conn.close()

        os.remove(TEST_DB_NAME)

    def test_create_db_with_coffees_table(self):
        create_db(db_name=TEST_DB_NAME)

        conn = sqlite3.connect(TEST_DB_NAME)
        cursor = conn.cursor()
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='coffees';
        """
        cursor.execute(query)

        assert cursor.fetchone()

        conn.close()

    @pytest.mark.parametrize(
        'expected_has_coffee,result',
        [(True, 1), (False, 0)]
    )
    def test_save_coffee_according_status(self, expected_has_coffee, result):
        update_coffee(expected_has_coffee, db_name=TEST_DB_NAME)

        cursor = next(self._db())
        cursor.execute('SELECT * FROM coffees ORDER BY id DESC LIMIT 1')
        _, _, has_coffee = cursor.fetchone()

        assert has_coffee == result


class TestBotAnswers:

    @patch('grandma.bot.SlackClient.api_call')
    @patch('grandma.bot.SlackClient.rtm_read')
    def test_answer_if_has_coffee(self, rtm_read_mock, api_call_mock,
            connected_bot):
        rtm_read_mock.return_value = [
            {'type': 'message', 'text': '<@U9D779NCR> coffee?'}]

        connected_bot.listen_and_answer()

        expected_args = [
            call('chat.postMessage',
            channel=DEFAULT_CHANNEL,
            text='I did coffee for you'
        )]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args

    @patch('grandma.bot.SlackClient.api_call')
    @patch('grandma.bot.SlackClient.rtm_read')
    def test_answer_if_coffee_is_over(
            self, rtm_read_mock, api_call_mock, connected_bot):
        rtm_read_mock.return_value = [
            {'type': 'message', 'text': '<@U9D779NCR> coffee?'}]

        DB_NAME = TEST_DB_NAME
        expected_has_coffee = False
        update_coffee(expected_has_coffee, db_name=TEST_DB_NAME)

        connected_bot.listen_and_answer()

        expected_args = [
            call('chat.postMessage',
            channel=DEFAULT_CHANNEL,
            text=':face_with_monocle:'
        )]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args

    def test_answer_coffee_is_cold_if_coffee_has_more_than_one_hour(self):
        pass

    def test_answer_i_dont_think_so_if_after_two_hours(self):
        pass
