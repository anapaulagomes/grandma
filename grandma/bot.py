import os
import random
import re
import sqlite3
import time
from collections import namedtuple
from datetime import datetime, timedelta

from slackclient import SlackClient

READ_DELAY = 1


class CoffeeDB:
    def __init__(self, db_name):
        self.db_name = db_name

    def create(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS coffees
                 (id integer primary key autoincrement,
                 timestamp timestamp, has_coffee integer)''')
        conn.commit()
        conn.close()

    def update(self, has_coffee):
        timestamp = datetime.now()
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO coffees(timestamp, has_coffee)
                    VALUES (?, ?)''', (timestamp, has_coffee))
        conn.commit()
        conn.close()

    def has_coffee(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM coffees ORDER BY id DESC LIMIT 1''')
        result = cursor.fetchone()
        if result:
            _, timestamp, status = result
        else:
            return False, None
        conn.commit()
        conn.close()
        return bool(status), timestamp


class BotNotConnected(BaseException):
    pass


class Grandma:
    NAME = 'grandma'
    DEFAULT_CHANNEL = 'general'
    MENTION_REGEX = r'(.*)<@(|[WU].+?)>(.*)'
    MAGIC_WORDS = 'coffee?'
    COFFEE_IS_READY = [
        'coffee is done',
        'coffee is ready',
        'coffee is served',
    ]
    COFFEE_IS_OVER = [
        'coffee is over',
        "it's over",
    ]

    def __init__(self, db, slack_bot_token=None):
        self.db = db
        self._token = os.environ.get('SLACK_BOT_TOKEN', slack_bot_token)
        self.DEFAULT_CHANNEL = os.environ.get('DEFAULT_CHANNEL', 'general')

    def connect(self):
        self.db.create()
        self.slack_client = SlackClient(self._token)
        if self.slack_client.rtm_connect(with_team_state=False):
            self._id = self.slack_client.api_call('auth.test')['user_id']
            print('Grandma is online')

    def listen_and_answer(self):
        if self._is_not_connected():
            raise BotNotConnected

        response = self.slack_client.rtm_read()
        if not response:
            return None
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
            return None

        mention = matches.group(2)
        content = matches.group(1) + matches.group(3)
        Message = namedtuple('message', ['content', 'mention'])
        return Message(content, mention)

    def _answer_about_coffee(self, message):
        response = "I'm not listening well. What did you say?"

        if self.MAGIC_WORDS in message:
            has_coffee, when_was_made = self.db.has_coffee()
            if has_coffee:
                if self._probably_over(when_was_made):
                    response = "I don't think so"
                elif self._probably_cold(when_was_made):
                    response = 'Maybe, if you like cold coffee... :grimacing:'
                else:
                    response = 'I did coffee for you'
            else:
                response = "I'm afraid we don't have it :face_with_monocle:"
        elif self._someone_made_coffee(message):
            response = 'The best coffee in town is served'
        elif self._coffee_is_over(message):
            response = 'Oh no'

        self.post_answer(response)

    def _answer_random_interaction(self):
        answers = [':thinking_face:', ':two_hearts:']
        option = random.randint(0, 1)
        response = answers[option]

        self.post_answer(response)

    def post_answer(self, response):
        self.slack_client.api_call(
            'chat.postMessage',
            channel=self.DEFAULT_CHANNEL,
            text=response
        )

    def _is_not_connected(self):
        return not hasattr(self, 'slack_client') and not hasattr(self, '_id')

    def _is_a_message(self, response):
        return response['type'] == 'message' and not ('subtype' in response)

    def _someone_made_coffee(self, message):
        result = message.lower().lstrip() in self.COFFEE_IS_READY
        if result:
            self.db.update(has_coffee=True)
        return result

    def _probably_cold(self, when_was_made):
        when = datetime.strptime(when_was_made, '%Y-%m-%d %H:%M:%S.%f')
        return (when + timedelta(hours=1)) < datetime.now()

    def _probably_over(self, when_was_made):
        when = datetime.strptime(when_was_made, '%Y-%m-%d %H:%M:%S.%f')
        return (when + timedelta(hours=2)) < datetime.now()

    def _coffee_is_over(self, message):
        result = message.lower().lstrip() in self.COFFEE_IS_OVER
        if result:
            self.db.update(has_coffee=False)
        return result


if __name__ == '__main__':
    db = CoffeeDB(db_name='grandma.db')
    bot = Grandma(db)
    bot.connect()

    while True:
        print(bot.listen_and_answer())
        time.sleep(READ_DELAY)
