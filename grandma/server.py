from flask import Flask, jsonify, abort
from grandma.bot import CoffeeDB, Grandma
from datetime import datetime, timedelta
from slackclient.server import SlackLoginError

app = Flask(__name__)


@app.route('/coffee/done')
def coffee_is_done():
    db = CoffeeDB(db_name='grandma.db')  # FIXME how to test it - Makefile?
    bot = Grandma(db)
    try:
        bot.connect()
    except SlackLoginError:
        abort(500)

    bot.notify()
    return ''


@app.route('/coffee/over')
def coffee_is_over():
    db = CoffeeDB(db_name='grandma.db')
    bot = Grandma(db)
    bot.db.update(has_coffee=False)
    return ''
