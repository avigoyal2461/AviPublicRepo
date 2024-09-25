# Imports
import os

class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = '\xfd@\x90e,\x9aya\xebt\x86g\xefg\x11\xc3'

    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    TENANT_ID = os.environ['TENANT_ID']
    CLIENT_ID = os.environ['CLIENT_ID']
    CLIENT_SECRET = os.environ['CLIENT_SECRET']
    AUTHORITY = os.environ['AUTHORITY']
    
    REDIRECT_PATH = "/getAToken"
    
    ENDPOINT = 'https://graph.microsoft.com/v1.0/users'
    
    SCOPE = ["User.ReadBasic.All"]
    
    SESSION_TYPE = "filesystem"

    HOME_URL = "https://trinity-rpa-dev.trinity-solar.com/login"

class DevelopmentConfig(ConfigClass):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
