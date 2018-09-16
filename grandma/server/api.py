from flask import abort, jsonify
from playhouse.shortcuts import model_to_dict

from grandma.server.app import app, db_wrapper
from grandma.server.bot import Grandma, BotNotConnected, Coffee


peewee_db = db_wrapper.database


@app.route('/')
def coffees():
    with peewee_db.atomic():
        obj = [
            model_to_dict(c, backrefs=True)
            for c in Coffee.select()
        ]
    return jsonify(obj)


@app.route('/coffee/done')
def coffee_is_done():
    bot = Grandma()
    try:
        bot.connect()
    except BotNotConnected:
        abort(500)
    else:
        bot.coffee_is_done()
    return ''


@app.route('/coffee/over')
def coffee_is_over():
    bot = Grandma()
    bot.coffee_is_over()
    return ''
