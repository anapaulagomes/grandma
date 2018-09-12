import os
import random
import re
import sqlite3
import time
from collections import namedtuple
from datetime import datetime, timedelta

from slackclient import SlackClient

from peewee import SqliteDatabase, Model, BooleanField, DateTimeField


db = SqliteDatabase(os.getenv('DB_NAME', 'grandma.db'))


def start_db():
    db.connect()
    db.create_tables([Coffee], safe=True)
    db.close()


class Coffee(Model):
    is_over = BooleanField(default=False)
    created = DateTimeField(default=datetime.now)
    updated = DateTimeField(null=True)

    class Meta:
        database = db

    def update(self, *args, **kwargs):
        self.updated = datetime.now()
        return super(Coffee, self).update(*args, **kwargs)


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
            'chat.postMessage',
            channel=self._channel,
            text=response
        )

    def notify(self):
        coffee_is_served_message = 'Would you like a cup of coffee?'
        coffee = self._last_coffee_made()

        if coffee:
            more_than_twenty_minutes = datetime.now() > (coffee.created + timedelta(minutes=20))
            if not coffee.is_over and more_than_twenty_minutes:
                self.post_answer(coffee_is_served_message)

    def coffee_is_over(self):
        last_coffee = self._last_coffee_made()

        if last_coffee:
            last_coffee.update(is_over=True).execute()
        else:
            Coffee.create(is_over=True)
    
    def coffee_is_done(self):
        Coffee.create(is_over=False)
        self.notify()

    def _last_coffee_made(self):
        return Coffee.select().order_by(Coffee.id.desc()).first()
