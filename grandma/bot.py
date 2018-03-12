import os
import time
import re
from slackclient import SlackClient
import random
from collections import namedtuple
import sqlite3
from datetime import datetime


def create_db(db_name='grandma-test.db'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS coffees
             (id integer primary key autoincrement,
             timestamp timestamp, has_coffee integer)''')
    conn.commit()
    conn.close()


def update_coffee(has_coffee):
    timestamp = datetime.now()
    conn = sqlite3.connect('grandma-test.db')
    c = conn.cursor()
    c.execute('''INSERT INTO coffees(timestamp, has_coffee)
                VALUES (?, ?)''', (timestamp, has_coffee))
    conn.commit()
    conn.close()


class BotNotConnected(BaseException):
    pass


class Grandma:
    NAME = 'grandma'
    MENTION_REGEX = r'(.*)<@(|[WU].+?)>(.*)'
    MAGIC_WORDS = 'coffee?'
    COFFEE_IS_READY = [
        'coffee is done',
        'coffee is ready',
        'coffee is served',
    ]

    def __init__(self, slack_bot_token=None):
        self._token = os.environ.get('SLACK_BOT_TOKEN', slack_bot_token)

    def connect(self):
        self.slack_client = SlackClient(self._token)
        if self.slack_client.rtm_connect(with_team_state=False):
            self._id = self.slack_client.api_call('auth.test')['user_id']
            print('Grandma is online')

    def listen_and_answer(self):
        if self._is_not_connected():
            raise BotNotConnected

        response = self.slack_client.rtm_read()
        if not response:
            return
        response = response[0]

        if self._is_a_message(response):
            message = self._parse_message(response['text'])

            if message and message.mention == self._id:
                self._answer_about_coffee(message.content)
            elif self.NAME in response['text']:
                self._answer_random_interaction()

        return response

    def _parse_message(self, text):
        matches = re.search(self.MENTION_REGEX, text)

        if not matches:
            return

        mention = matches.group(2)
        content = matches.group(1) + matches.group(3)
        Message = namedtuple('message', ['content', 'mention'])
        return Message(content, mention)

    def _answer_about_coffee(self, message):
        response = "I'm not listening well. What did you say?"

        if self.MAGIC_WORDS in message:
            # TODO check the database
            response = 'I did coffee for you'

        self._post_answer(response)

    def _answer_random_interaction(self):
        answers = [':thinking_face:', ':two_hearts:']
        option = random.randint(0, 1)
        response = answers[option]

        self._post_answer(response)

    def _post_answer(self, response):
        self.slack_client.api_call(
            'chat.postMessage',
            channel='general',# TODO check the database
            text=response
        )

    def _is_not_connected(self):
        return not hasattr(self, 'slack_client') and not hasattr(self, '_id')

    def _is_a_message(self, response):
        return response['type'] == 'message' and not 'subtype' in response


if __name__ == '__main__':
    READ_DELAY = 1
    create_db()

    bot = Grandma()
    bot.connect()

    while True:
        print(bot.listen_and_answer())
        time.sleep(READ_DELAY)
