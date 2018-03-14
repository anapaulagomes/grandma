from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/has-coffee')
def has_coffee():
    return jsonify(answer=True)
