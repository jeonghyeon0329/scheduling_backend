from .base import *
from decouple import config

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": config("DATABASES_ENGINE"),
        "NAME": config("DATABASES_NAME"),
        "USER": config("DATABASES_USER"),
        "PASSWORD": config("DATABASES_PASSWORD"),
        "HOST": "core_db",
        "PORT": config("DATABASES_PORT"),
    }
}

HR_BASE_URL = config("HR_BASE_URL")
