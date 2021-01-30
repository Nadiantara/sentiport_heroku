from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email, URL


class AppForm(FlaskForm):
    app_id = StringField('App id', validators=[DataRequired(), URL()])
    email = StringField('Email', validators=[DataRequired(), Email()])
