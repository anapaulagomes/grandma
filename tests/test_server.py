from tests.conftest import use_test_database


@use_test_database
def test_save_and_notify_on_slack_when_has_coffee(client, mocker, slack_calls_mock):
    update = mocker.patch('grandma.server.bot.Grandma.coffee_is_done')
    response = client.get('/coffee/done')

    assert response.status_code == 200
    assert slack_calls_mock.called
    assert update.called


@use_test_database
def test_update_coffee_when_coffee_is_over(client, mocker, slack_calls_mock):
    update = mocker.patch('grandma.server.bot.Grandma.coffee_is_over')

    client.get('/coffee/done')
    response = client.get('/coffee/over')

    assert response.status_code == 200
    assert slack_calls_mock.called
    assert update.called
