from flask import Flask, abort, jsonify
from grandma.bot import Grandma, BotNotConnected, start_db, Coffee
from playhouse.shortcuts import model_to_dict

app = Flask(__name__)
bot = Grandma()


@app.route('/')
def coffees():
    obj = [model_to_dict(c, backrefs=True) for c in Coffee.select()]
    return jsonify(obj)


@app.route('/coffee/done')
def coffee_is_done():
    try:
        bot.connect()
    except BotNotConnected:
        abort(500)
    else:
        bot.coffee_is_done()
    return ''


@app.route('/coffee/over')
def coffee_is_over():
    bot.coffee_is_over()
    return ''


if __name__ == '__main__':
    start_db()
    app.run()