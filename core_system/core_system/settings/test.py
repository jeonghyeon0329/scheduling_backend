from .base import *
from decouple import config

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": config("DATABASES_ENGINE"),
        "NAME": f"{config('DATABASES_NAME')}",
        "USER": config("DATABASES_USER"),
        "PASSWORD": config("DATABASES_PASSWORD"),
        "HOST": "localhost",
        "PORT": config("DATABASES_PORT"),
    }
}

HR_BASE_URL = config("HR_BASE_URL_LOCAL")
# "NAME": f"{config('DATABASES_NAME')}_test",
