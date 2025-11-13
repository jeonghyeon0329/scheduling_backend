from .base import *
from decouple import config

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": config("DATABASES_ENGINE"),
        "NAME": config("DATABASES_NAME"),
        "USER": config("DATABASES_USER"),
        "PASSWORD": config("DATABASES_PASSWORD"),
        "HOST": "localhost",
        "PORT": config("DATABASES_PORT"),
    }
}

HR_BASE_URL = config("HR_BASE_URL_LOCAL")
