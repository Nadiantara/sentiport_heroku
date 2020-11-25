from flask import Flask
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object('config.Config')
mail = Mail(app)

from sentiport import routes

