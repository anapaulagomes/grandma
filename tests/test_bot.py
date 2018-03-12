from grandma.bot import Grandma, BotNotConnected, create_db, update_coffee
from unittest.mock import patch, call
import pytest
import sqlite3


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
    ])
    @patch('grandma.bot.SlackClient.api_call')
    def test_answer(self, api_call_mock, message, response, connected_bot):
        connected_bot._answer_about_coffee(message)

        expected_args = [
            call('chat.postMessage', channel='general', text=response)]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args

    @patch('grandma.bot.SlackClient.api_call')
    def test_if_does_not_mention_directly_reply_with_emoji(self, api_call_mock, connected_bot):
        message = 'my grandma is the best'
        connected_bot._answer_random_interaction()

        expected_args1 = [
            call('chat.postMessage', channel='general', text=':thinking_face:')]
        expected_args2 = [
            call('chat.postMessage', channel='general', text=':two_hearts:')]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args1 or \
            api_call_mock.call_args_list == expected_args2

    @patch('grandma.bot.SlackClient.api_call')
    @patch('grandma.bot.SlackClient.rtm_read')
    def test_if_does_not_mention_directly_reply(self, rtm_read_mock, api_call_mock,
            connected_bot):
        rtm_read_mock.return_value = [{'type': 'message', 'text': 'my grandma is the best'}]

        connected_bot.listen_and_answer()

        expected_args1 = [
            call('chat.postMessage', channel='general', text=':thinking_face:')]
        expected_args2 = [
            call('chat.postMessage', channel='general', text=':two_hearts:')]

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args1 or \
            api_call_mock.call_args_list == expected_args2


class TestCoffeeStatuses:
    def _db(self):
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        yield cursor
        conn.close()

    def test_create_db_with_coffees_table(self):
        create_db(db_name=':memory:')

        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='coffees';")
        # cursor.execute("PRAGMA table_info(coffees)").fetchone()
        import pdb; pdb.set_trace()
        assert cursor.fetchone()

        conn.close()

    def test_save_coffee_status_if_someone_made_coffee(self):
        has_coffee = True
        update_coffee(has_coffee)

        cursor = next(self._db())
        cursor.execute('SELECT * FROM coffees ORDER BY id DESC LIMIT 1')

        assert cursor.fetchone()

    def test_save_coffee_status_if_coffee_is_over(self):
        pass

    def test_answer_coffee_is_cold_if_coffee_has_more_than_one_hour(self):
        pass

    def test_save_coffee_is_over_after_three_hours(self):
        pass
