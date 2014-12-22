import os
import sys

from datetime  import timedelta


PACKAGE_ROOT = os.path.dirname(os.path.dirname(__file__))

# use current user and python to execute `sandboxed` code.
SANDBOX_FOLDER = os.path.join(PACKAGE_ROOT, 'sandbox')
SANDBOX_PYTHON_PROTO = sys.executable
SANDBOX_REQUIREMENTS = os.path.join(PACKAGE_ROOT, 'requirements', 'sandbox.txt')
SANDBOX_USER = None
SANDBOX_ENV = {
    'LANG': 'en_US.UTF-8',
}
ARENA_DIR = os.path.join(PACKAGE_ROOT, 'arena')

SANDBOX_PYTHON = os.path.join(SANDBOX_FOLDER, 'bin', 'python3')
SANDBOX_JAVA = None
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
SUBMISSION_SIZE_LIMIT = DATASET_QUIZ_SIZE_LIMIT
ATTEMPT_POOL_SIZE = 10
ATTEMPT_CLEANUP_TIMEOUT = timedelta(minutes=15)

# These quizzes will be scored in separate celery queue.
COMPUTATIONALLY_HARD_QUIZZES = ['admin', 'code', 'dataset']

try:
    from edy.plugins_settings import *
except ImportError:
    pass

from .jail_config import configure_jail_code
configure_jail_code(sys.modules[__name__])
