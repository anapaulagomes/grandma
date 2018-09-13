import os
import sqlite3
from unittest.mock import call, patch

import pytest
from freezegun import freeze_time

from grandma.bot import Grandma, BotNotConnected


class TestGrandma:
    @pytest.fixture
    def bot(self):
        return Grandma()

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

    @patch('grandma.bot.SlackClient.rtm_connect')
    def test_raise_exception_when_was_not_connected(self, rtm_connect_mock, bot):
        rtm_connect_mock.return_value = None
        with pytest.raises(BotNotConnected):
            bot.connect()
    
    @patch('grandma.bot.SlackClient.api_call')
    @patch('grandma.bot.SlackClient.rtm_connect')
    def test_does_not_notify_on_slack_when_notified_in_less_than_20_minutes(self, rtm_connect_mock, api_call_mock, bot):
        rtm_connect_mock.return_value = True
        api_call_mock.return_value = {'user_id': 'USER_ID'}

        # FIXME the database must be clean in this point

        expected_args = [
            call('auth.test'),
            call('chat.postMessage', channel=bot._channel, text='Would you like a cup of coffee?')
        ]
        bot.connect()

        bot.coffee_is_done()  # should notify
        bot.coffee_is_done()  # should not notify

        assert api_call_mock.called
        assert api_call_mock.call_args_list == expected_args
