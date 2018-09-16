import os
from datetime import datetime, timedelta

from peewee import BooleanField, DateTimeField
from slackclient import SlackClient

from grandma.server.app import db_wrapper


class Coffee(db_wrapper.Model):
    is_over = BooleanField(default=False)
    created = DateTimeField(default=datetime.now)
    updated = DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if self.id:
            self.updated = datetime.now()
        return super(Coffee, self).save(*args, **kwargs)


class BotNotConnected(BaseException):
    pass


class Grandma:
    def __init__(self, slack_bot_token=None):
        self._token = os.environ.get('SLACK_BOT_TOKEN', slack_bot_token)
        self._channel = os.environ.get('DEFAULT_CHANNEL', 'general')

    def connect(self):
        self.slack_client = SlackClient(self._token)
        if self.slack_client.rtm_connect(with_team_state=False):
            self._id = self.slack_client.api_call('auth.test')['user_id']
        else:
            raise BotNotConnected

    def post_answer(self, response):
        self.slack_client.api_call(
            'chat.postMessage', channel=self._channel, text=response)

    def notify(self):
        coffee_is_served_message = 'Would you like a cup of coffee?'
        coffee = self._last_coffee_made()

        if coffee and not coffee.is_over:
            when = self._when_previous_coffee_was_made()

            if when:
                twenty_minutes_ahead = when + timedelta(minutes=20)
                now = datetime.now()
                more_than_twenty_minutes = now > twenty_minutes_ahead
                if more_than_twenty_minutes:
                    self.post_answer(coffee_is_served_message)
            else:
                self.post_answer(coffee_is_served_message)

    def coffee_is_over(self):
        last_coffee = self._last_coffee_made()

        if last_coffee:
            last_coffee.is_over = True
            last_coffee.save()
        else:
            Coffee.create(is_over=True)

    def coffee_is_done(self):
        Coffee.create(is_over=False)
        self.notify()

    def _last_coffee_made(self):
        return Coffee.select().order_by(Coffee.id.desc()).first()

    def _when_previous_coffee_was_made(self):
        try:
            previous = Coffee.select().order_by(Coffee.id.desc())[1]
            return previous.created
        except IndexError:
            return None
