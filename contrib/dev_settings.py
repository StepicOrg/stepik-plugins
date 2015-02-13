from .base import *


DEBUG = True

LOGGING['loggers']['stepic_plugins']['level'] = 'DEBUG' if DEBUG else 'INFO'
