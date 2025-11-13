from decouple import config

ENV = config('DJANGO_ENV', default='development')

if ENV == 'production': from .prod import *
elif ENV == 'test': from .test import *
else:
    from .dev import *
