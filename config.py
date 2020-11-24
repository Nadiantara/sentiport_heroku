"""Flask config."""
from os import environ, path
from dotenv import load_dotenv

BASE_DIR = path.abspath(path.dirname(__file__))
load_dotenv(path.join(BASE_DIR, '.env'))

class Config:
    """Flask configuration variables."""

    # General Config
    FLASK_ASSETS_USE_CDN = True
    PROPAGATE_EXCEPTIONS = True
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get('FLASK_ENV')
    SECRET_KEY = environ.get('SECRET_KEY')
 
    # Cache Config
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 86400 # 24 hours in seconds
    CACHE_IGNORE_ERRORS = True

    # Static Assets
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    COMPRESSOR_DEBUG = environ.get('COMPRESSOR_DEBUG')
