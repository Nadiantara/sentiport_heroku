from flask import Flask
from flask_mail import Mail
import threading

thread_lock = threading.Lock()
pipeline_thread = threading.Thread()

app = Flask(__name__)
app.config.from_object('config.Config')
mail = Mail(app)

from sentiport import routes

