from .base import *


DEBUG = True

LOGGING['loggers']['stepic_plugins']['level'] = 'DEBUG' if DEBUG else 'INFO'

EPICBOX_PROFILES = {
    'gcc': {
        'docker_image': 'stepik/epicbox-gcc:5.3.0',
    },
    'trik': {
        'command': '/trikStudio-checker/bin/check-solution.sh main.qrs',
        'docker_image': 'stepic/epicbox-trik:20151217',
    }
}

CODE_LANGUAGES = {
    'c++': {
        'compiled': True,
        'filename': 'main.cpp',
        'compile_profile': 'gcc',
        'compile_command': 'g++ -pipe -O2 -static -o main main.cpp',
    }
}

SQL_BIND_PORT = 23306
