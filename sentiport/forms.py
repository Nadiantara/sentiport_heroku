import re
import requests
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from datetime import date
from wtforms.fields.html5 import DateField
from wtforms.fields.html5 import DateTimeField




class AppForm(FlaskForm):
    app_id = StringField(
        'App id',
        validators=[
            DataRequired(),
            Regexp(
                '^((\w+\.){2,}\w+)$',
                message="You seem to have entered invalid app id."
            )
        ]
    )
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


def _guess_store(appid):
    """
    Return either 'AppStore' or 'PlayStore' based on the string pattern
    if string pattern conforms to a known pattern.
    """
    if re.fullmatch(r"^(\d){8,}$", appid):
        return "AppStore"
    elif re.fullmatch(r"^(\w+\.){2,}\w+$", appid):
        return "PlayStore"
    else:
        return None


#not being used
def validate_appid(appid: str, country: str):
    store = _guess_store(appid)
    assert store in ["AppStore", "PlayStore"]
    if store == "AppStore":
        url = f"http://apps.apple.com/{country}/app/{appid}"
        res = requests.get(url)
        if res.status_code == 200:
            appname = re.search('(?<="name":").*?(?=")', res.text).group(0)
            return store, appname
        else:
            return None

    if store == "PlayStore":
        try:
            appinfo = app(appid, country=country)
            appname = appinfo["title"]
            return store, appname
        except:
            return None

    if store == None:
        return None


