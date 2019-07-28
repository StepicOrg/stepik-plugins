import os

from datetime import timedelta


PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))))
DEBUG = False

RPC_TRANSPORT_URL = 'rabbit://guest:guest@localhost:5672//'
RPC_DEFAULT_TIMEOUT = 305
USE_RPC_TIMEOUT_KILLER = True

#: See the `RAID_OLD_STYLE_CLEAN_REPLY_QUIZZES` option in edy settings.
OLD_STYLE_CLEAN_REPLY_QUIZZES = ['admin', 'chemical', 'choice', 'code', 'dataset', 'fill-blanks',
                                 'linux-code', 'matching', 'math', 'number', 'puzzle',
                                 'random-tasks', 'schulte', 'sorting', 'sql', 'table', 'trik']

USE_EPICBOX = False
# use current user to execute `sandboxed` code.
SANDBOX_USER = None
SANDBOX_FOLDER = os.path.join(PACKAGE_ROOT, 'sandbox')
SANDBOX_PYTHON = os.path.join(SANDBOX_FOLDER, 'python', 'bin', 'python3')
SANDBOX_JAVA = None
SANDBOX_JAVA_HOME = None
SANDBOX_JAVA8 = None
SANDBOX_ENV = {
    'LANG': 'en_US.UTF-8',
}
ARENA_DIR = os.path.join(PACKAGE_ROOT, 'arena')

MB = 1024 * 1024
JAVA_RESERVED_MEMORY = 400 * MB
JAVA_DISASSEMBLE_TIMEOUT = 5

SANDBOX_LIMITS = {
    'TIME': 120,
    'MEMORY': 512 * MB,
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

EPICBOX_BASE_PROFILES = {
    'base': {
        'docker_image': 'stepik/epicbox-base:alpine',
        'user': 'sandbox',
        'read_only': True,
    },
    'base_root': {
        'docker_image': 'stepik/epicbox-base:alpine',
    },
}
EPICBOX_PROFILES = {}
EPICBOX_DOCKER_URL = 'unix:///var/run/docker.sock'
EPICBOX_BASE_WORKDIR = None
EPICBOX_COMPILE_LIMITS = {
    'cputime': 30,
    'realtime': 60,
    'memory': 512,
}
EPICBOX_TRIK_LIMITS = {
    'cputime': 60,
    'realtime': 120,
    'memory': 512,
}

#: Specify epicbox configs for languages. Epicbox sandboxes are used
#: for these languages instead of codejail.
CODE_LANGUAGES = {}

DATASET_QUIZ_TIME_LIMIT = timedelta(minutes=5)
DATASET_QUIZ_SIZE_LIMIT = 10 * MB

SQL_DOCKER_HOST = 'unix:///var/run/docker.sock'
SQL_CONTAINER_IMAGE = 'mysql:5.7.12'
SQL_CONTAINER_NAME = 'sql-challenge'
SQL_CONTAINER_PORT = 3306
SQL_CONTAINER_VOLUME = '/var/lib/mysql'
SQL_BIND_HOST = '127.0.0.1'
SQL_BIND_PORT = 13306
SQL_DB_CONF_OPTIONS = '--skip-innodb_adaptive_hash_index'
SQL_DB_HOST = '127.0.0.1'
SQL_DB_ROOT_PASS = 'root'
SQL_MAX_EXECUTION_TIME = 30
SQL_QUERY_RESULT_MAX_SIZE = 100

LINUX_CODE_API_URL = ''

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
