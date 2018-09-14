import os

from flask import Flask
from peewee import SqliteDatabase

APP_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.getenv('DB_NAME', 'grandma.db')
DEBUG = True

def initialize(db):
    from grandma.server.bot import Coffee
    Coffee.create_table(True)

app = Flask(__name__)
app.config.from_object(__name__)
db = SqliteDatabase(app.config['DATABASE'])
initialize(db)