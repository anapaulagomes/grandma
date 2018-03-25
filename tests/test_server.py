from grandma import server
from flask import url_for
from .fixtures import TEST_DB_NAME, USER_ID
from unittest.mock import call, patch
from freezegun import freeze_time


def test_save_and_notify_on_slack_when_has_coffee(client, mocker, connected_bot):
    rtm_connect_mock = mocker.patch('grandma.bot.SlackClient.rtm_connect')
    api_call_mock = mocker.patch('grandma.bot.SlackClient.api_call')

    rtm_connect_mock.return_value = True
    api_call_mock.return_value = {'user_id': USER_ID}

    expected_args = [
        call('auth.test'),
        call(
            'chat.postMessage',
            channel=connected_bot.DEFAULT_CHANNEL,
            text='The best coffee in town is served')
    ]

    with freeze_time('2017-12-01 12:10:01.262065'):
        response = client.get(url_for('has_coffee'))

    assert response.status_code == 200
    assert api_call_mock.called
    assert api_call_mock.call_args_list == expected_args


def test_does_not_notify_on_slack_when_notified_in_less_than_20_minutes(client, mocker, connected_bot):
    rtm_connect_mock = mocker.patch('grandma.bot.SlackClient.rtm_connect')
    api_call_mock = mocker.patch('grandma.bot.SlackClient.api_call')

    rtm_connect_mock.return_value = True
    api_call_mock.return_value = {'user_id': USER_ID}

    expected_args = [
        call('auth.test'),
        call('auth.test'),
    ]

    client.get(url_for('has_coffee'))
    response = client.get(url_for('has_coffee'))

    assert response.status_code == 200
    assert api_call_mock.called
    assert api_call_mock.call_args_list == expected_args
