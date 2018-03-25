from flask import Flask, jsonify, abort
from grandma.bot import CoffeeDB, Grandma
from datetime import datetime, timedelta


app = Flask(__name__)


@app.route('/has-coffee')
def has_coffee():
    db = CoffeeDB(db_name='grandma.db')  # FIXME how to test it
    bot = Grandma(db)
    try:
        bot.connect()
    except:
        abort(500)

    _, last_time_was_made = bot.db.has_coffee()
    bot.db.update(has_coffee=True)

    if last_time_was_made:  # TODO add test for this case
        when = datetime.strptime(last_time_was_made, '%Y-%m-%d %H:%M:%S.%f')
        more_than_twenty_minutes = datetime.now() > (when + timedelta(minutes=20))

        if more_than_twenty_minutes:
            bot._post_answer('The best coffee in town is served')
    else:
        bot._post_answer('The best coffee in town is served')

    return ''
