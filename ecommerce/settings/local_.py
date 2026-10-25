from .base import *

SECRET_KEY = ''

ALLOWED_HOSTS = []

DEBUG = True/False

CORS_REPLACE_HTTPS_REFERER      = False
HOST_SCHEME                     = "http://"
SECURE_PROXY_SSL_HEADER         = None
SECURE_SSL_REDIRECT             = False
SESSION_COOKIE_SECURE           = False
SECURE_HSTS_SECONDS             = None
SECURE_HSTS_INCLUDE_SUBDOMAINS  = False
SECURE_FRAME_DENY               = False

MANAGER = os.environ.get("MANAGER",None)
MANAGER_NAME = os.environ.get("MANAGER_NAME",None)

ADMINS =[
    (MANAGER_NAME, MANAGER),
]

# https://docs.djangoproject.com/en/5.0/ref/databases/#postgresql-notes

DATABASES = {
    "default": {
        "ENGINE": "",
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
