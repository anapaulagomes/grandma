from grandma import server
from flask import url_for
from unittest.mock import call
from freezegun import freeze_time


def test_save_and_notify_on_slack_when_has_coffee(client, mocker):
    rtm_connect_mock = mocker.patch('grandma.server.bot.SlackClient.rtm_connect')
    api_call_mock = mocker.patch('grandma.server.bot.SlackClient.api_call')
    update = mocker.patch('grandma.server.bot.Grandma.coffee_is_done')

    response = client.get(url_for('coffee_is_done'))

    assert response.status_code == 200
    assert api_call_mock.called


def test_update_coffee_when_coffee_is_over(client, mocker):
    rtm_connect_mock = mocker.patch('grandma.server.bot.SlackClient.rtm_connect')
    api_call_mock = mocker.patch('grandma.server.bot.SlackClient.api_call')
    update = mocker.patch('grandma.server.bot.Grandma.coffee_is_over')

    client.get(url_for('coffee_is_done'))
    response = client.get(url_for('coffee_is_over'))

    assert response.status_code == 200
    assert update.called
