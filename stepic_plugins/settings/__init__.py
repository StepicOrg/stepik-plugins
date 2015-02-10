import importlib
import logging
import logging.config
import os
import sys

import structlog

from .. import log
from ..utils import configure_jail_code


def load_everything_from_module(name):
    module = importlib.import_module(name)
    attrs = getattr(module, '__all__', None)
    if attrs is None:
        attrs = [attr for attr in dir(module) if not attr.startswith('_')]
    for attr_name in attrs:
        globals()[attr_name] = getattr(module, attr_name)


settings_module_name = os.environ.get('STEPIC_PLUGINS_SETTINGS_MODULE')
if settings_module_name:
    load_everything_from_module(settings_module_name)
else:
    from .local import *


if LOGGING_CONFIGURE:
    logging.config.dictConfig(LOGGING)
    logging.captureWarnings(True)

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        log.add_supervisor_instance_id,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer() if LOGGING_JSON else
        structlog.processors.KeyValueRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

configure_jail_code(sys.modules[__name__])
