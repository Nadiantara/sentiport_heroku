from flask import Flask
from flask_mail import Mail
from threading import Lock
import redis

# Flask App
app = Flask(__name__)
app.config.from_object('config.Config')

# Mailing Service
mail = Mail(app)

# Multithreading
thread_lock = Lock()
threads = {}

# Redis key-val store
store = redis.Redis(host="redis", port=6379)

from sentiport import routes