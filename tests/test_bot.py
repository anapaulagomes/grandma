import os
import sqlite3
from unittest.mock import call, patch

import pytest

from grandma.server.bot import BotNotConnected, Grandma
from tests.conftest import use_test_database


class TestGrandma:
    @pytest.fixture
    def bot(self):
        return Grandma()

    def test_connect_on_slack_api(self, bot, slack_calls_mock):
        expected_user_id = 'A1B999WWW'
        bot.connect()

        assert bot._id == expected_user_id
        assert slack_calls_mock.called

    @patch('grandma.server.bot.SlackClient.rtm_connect')
    def test_raise_exception_when_was_not_connected(self, rtm_connect_mock,
                                                    bot):
        rtm_connect_mock.return_value = None
        with pytest.raises(BotNotConnected):
            bot.connect()

    @use_test_database
    def test_does_not_notify_on_slack_when_notified_in_less_than_20_minutes(
            self, bot, slack_calls_mock):
        expected_args = [
            call('auth.test'),
            call(
                'chat.postMessage',
                channel=bot._channel,
                text='Would you like a cup of coffee?')
        ]
        bot.connect()

        bot.coffee_is_done()  # should notify
        bot.coffee_is_done()  # should not notify

        assert slack_calls_mock.called
        assert slack_calls_mock.call_args_list == expected_args
