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
    except:  # TODO add specific exception
        abort(500)

    # TODO move logic from endpoint to the object
    # bot.notify()

    coffee_is_served_message = 'Would you like a cup of coffee?'

    _, last_time_was_made = bot.db.has_coffee()
    bot.db.update(has_coffee=True)

    if last_time_was_made:
        when = datetime.strptime(last_time_was_made, '%Y-%m-%d %H:%M:%S.%f')
        more_than_twenty_minutes = datetime.now() > (when + timedelta(minutes=20))

        if more_than_twenty_minutes:
            bot.post_answer(coffee_is_served_message)
    else:
        bot.post_answer(coffee_is_served_message)

    return ''
