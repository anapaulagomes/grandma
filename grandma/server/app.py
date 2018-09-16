import os

from flask import Flask
from playhouse.flask_utils import FlaskDB


app = Flask(__name__)
app.config.from_object(__name__)
app.config['DATABASE'] = f'sqlite:///{os.getcwd()}/grandma.db'

db_wrapper = FlaskDB(app)
print(app.config['DATABASE'])
