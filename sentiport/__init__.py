from flask import Flask
from flask_mail import Mail
from threading import Lock
from os import environ, path
import redis

# Flask App
app = Flask(__name__)
app.config.from_object('config.Config')

# Mailing Service
mail = Mail(app)

# Multithreading
thread_lock = Lock()
threads = {}

# Redis key-val store (use this for heroku deployment without docker)
# store = redis.from_url(environ.get('REDISCLOUD_URL'))

# Redis key-val store (use if you want run it in your local machine or deploy it using docker)
store = redis.Redis(host="redis", port=6379)

from sentiport import routes
