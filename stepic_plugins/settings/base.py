import os

from datetime import timedelta


PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))))
DEBUG = False

RPC_TRANSPORT_URL = 'rabbit://guest:guest@localhost:5672//'

# use current user to execute `sandboxed` code.
SANDBOX_USER = None
SANDBOX_FOLDER = os.path.join(PACKAGE_ROOT, 'sandbox')
SANDBOX_PYTHON = os.path.join(SANDBOX_FOLDER, 'python', 'bin', 'python3')
SANDBOX_JAVA = None
SANDBOX_ENV = {
    'LANG': 'en_US.UTF-8',
}
ARENA_DIR = os.path.join(PACKAGE_ROOT, 'arena')

MB = 1024 * 1024
JAVA_RESERVED_MEMORY = 400 * MB

SANDBOX_LIMITS = {
    'TIME': 60,
    'MEMORY': 256 * MB,
    'CAN_FORK': False,
    'FILE_SIZE': 0
}

COMPILERS = {

}

INTERPRETERS = {

}

COMPILER_LIMITS = {
    'TIME': 60,
    'MEMORY': 512 * MB,
    'CAN_FORK': True,
    'FILE_SIZE': 256 * MB
}

USER_CODE_LIMITS = {
    'TIME': 10,
    'MEMORY': 512 * MB,
    'CAN_FORK': False,
    'FILE_SIZE': 0
}

DATASET_QUIZ_TIME_LIMIT = timedelta(minutes=5)
DATASET_QUIZ_SIZE_LIMIT = 10 * MB

# These quizzes will be scored in edy in a separate celery queue.
COMPUTATIONALLY_HARD_QUIZZES = ['admin', 'code', 'dataset']

ROOTNROLL_API_URL = ''
ROOTNROLL_USERNAME = ''
ROOTNROLL_PASSWORD = ''

LOGGING_CONFIGURE = True
LOGGING_JSON = False
LOGGING_SENTRY = False
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(name)s] %(levelname)s %(message)s'
        },
        'structlog_json': {
            '()': 'stepic_plugins.log.LoggingJsonFormatter',
            'format': '%(message)s'
        }
    },
    'filters': {
        'require_logging_json_true': {
            '()': 'stepic_plugins.log.RequireLoggingJsonTrue'
        },
        'require_logging_json_false': {
            '()': 'stepic_plugins.log.RequireLoggingJsonFalse'
        },
        'require_logging_sentry_true': {
            '()': 'stepic_plugins.log.RequireLoggingSentryTrue'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'filters': ['require_logging_sentry_true'],
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': '',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_logging_json_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'console_json': {
            'level': 'DEBUG',
            'filters': ['require_logging_json_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'structlog_json',
        },
    },
    'loggers': {
        'py.warnings': {
            'handlers': ['console'],
            'propagate': False,
        },
        'stepic_plugins': {
            'handlers': ['console', 'console_json', 'sentry'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'console_json', 'sentry'],
            'level': 'INFO',
        },
    }
}
