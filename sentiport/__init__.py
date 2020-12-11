from flask import Flask
from flask_mail import Mail
from threading import Lock

app = Flask(__name__)
app.config.from_object('config.Config')
mail = Mail(app)
thread_lock = Lock()
threads = {}

from sentiport import routes