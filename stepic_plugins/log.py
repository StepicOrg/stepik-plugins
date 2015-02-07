import json
import logging
import os
import pytz
import re

from datetime import datetime


class RequireLoggingJsonTrue(logging.Filter):
    def filter(self, record):
        from . import settings
        return settings.LOGGING_JSON


class RequireLoggingJsonFalse(logging.Filter):
    def filter(self, record):
        from . import settings
        return not settings.LOGGING_JSON


class RequireLoggingSentryTrue(logging.Filter):
    def filter(self, record):
        from . import settings
        return settings.LOGGING_SENTRY


class LoggingJsonFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        if msg.startswith('{'):
            # Skip a json formatted log message rendered by structlog
            return msg
        timestamp = datetime.fromtimestamp(record.created, tz=pytz.UTC)
        log = {
            'event': msg,
            'logger': record.name,
            'level': record.levelname.lower(),
            'timestamp': timestamp.isoformat(),
        }
        return json.dumps(log)


def add_supervisor_instance_id(logger, method_name, event_dict):
    """
    Add the supervisor process id to the structlog event dict.
    """
    process_name = os.environ.get('SUPERVISOR_PROCESS_NAME')
    if not process_name:
        # the process is not launched by supervisor
        return event_dict
    match = re.search('\d+$', process_name)
    if not match:
        return event_dict
    instance_id = int(match.group(0))
    event_dict['instance_id'] = instance_id
    return event_dict
