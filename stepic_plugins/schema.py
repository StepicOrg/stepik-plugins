import base64
import datetime
import inspect
import keyword
import re
import time

import oslo_messaging as messaging

from decimal import Decimal

from .exceptions import FormatError


def is_valid_scheme(scheme):
    def is_valid_attr_name(name):
        return re.match('[A-Za-z][_a-zA-Z0-9]*$', name) and not keyword.iskeyword(name)

    def is_valid_scheme_rec(s):
        if _is_primitive(s):
            return True

        if isinstance(s, list):
            if len(s) != 1:
                raise SchemeError('Lists should include exactly one element: {}'.format(s))
            return is_valid_scheme_rec(s[0])

        if isinstance(s, dict):
            for k in s:
                if not (isinstance(k, str) and is_valid_attr_name(k)):
                    raise SchemeError('Invalid key: {}'.format(k))
            for k in s:
                is_valid_scheme_rec(s[k])
            return True
        raise SchemeError('Invalid object: {}'.format(s))

    if not isinstance(scheme, dict):
        raise SchemeError('Top level object should be dict')

    return is_valid_scheme_rec(scheme)


def build(scheme, obj):
    def ensure_type(obj, t):
        if not isinstance(obj, t):
            # if integer passed as string (EDY-1668)
            if not (t == int and is_int_as_string(obj)):
                raise FormatError('Expected {}, got {}'.format(t.__name__, obj))

    def is_int_as_string(obj):
        if isinstance(obj, str):
            try:
                int(obj)
            except ValueError:
                pass
            else:
                return True
        return False

    if inspect.isfunction(scheme):
        scheme = scheme()

    if _is_primitive(scheme):
        ensure_type(obj, scheme)
        # if integer passed as string (EDY-1668)
        if scheme == int and is_int_as_string(obj):
            return int(obj)
        else:
            return obj
    elif isinstance(scheme, list):
        ensure_type(obj, list)
        return [build(scheme[0], x) for x in obj]
    else:
        assert isinstance(scheme, dict), "Scheme should be dict"
        ensure_type(obj, dict)
        return ParsedJSON(scheme, obj)


class ParsedJSON(object):
    def __init__(self, scheme, obj):
        self._original = obj
        for k, sub_scheme in scheme.items():
            if k not in obj:
                raise FormatError('Expected key {} in {}'.format(k, obj))
            setattr(self, k, build(sub_scheme, obj[k]))

    def __repr__(self):
        return str(self._original)


class SchemeError(ValueError):
    pass


def _is_primitive(obj):
    return obj in [str, bytes, int, float, bool]


ATTACHMENT_HEADER = 'attachment$base64$'
attachment = lambda: {
    'name': str,
    'type': str,
    'size': int,
    'content': str,
    'url': str,
}


class RPCSerializer(messaging.NoOpSerializer):
    def serialize_entity(self, ctxt, entity):
        if isinstance(entity, (tuple, list)):
            return [self.serialize_entity(ctxt, v) for v in entity]
        if isinstance(entity, dict):
            return {k: self.serialize_entity(ctxt, v)
                    for k, v in entity.items()}
        if isinstance(entity, bytes):
            return {'_serialized.bytes': base64.b64encode(entity).decode()}
        if isinstance(entity, Decimal):
            return {'_serialized.decimal': str(entity)}
        if isinstance(entity, datetime.datetime):
            # doesn't preserve timezone
            return {'_serialized.datetime': entity.timestamp()}
        if isinstance(entity, datetime.date):
            return {'_serialized.date': int(time.mktime(entity.timetuple()))}
        if isinstance(entity, datetime.timedelta):
            return {'_serialized.timedelta': entity.total_seconds()}
        if isinstance(entity, ParsedJSON):
            return self.serialize_entity(ctxt, entity._original)
        return entity

    def deserialize_entity(self, ctxt, entity):
        if isinstance(entity, dict):
            if '_serialized.bytes' in entity:
                return base64.b64decode(entity['_serialized.bytes'])
            if '_serialized.decimal' in entity:
                return Decimal(entity['_serialized.decimal'])
            if '_serialized.datetime' in entity:
                return datetime.datetime.fromtimestamp(
                    entity['_serialized.datetime'])
            if '_serialized.date' in entity:
                return datetime.date.fromtimestamp(entity['_serialized.date'])
            if '_serialized.timedelta' in entity:
                return datetime.timedelta(
                    seconds=entity['_serialized.timedelta'])
            return {k: self.deserialize_entity(ctxt, v)
                    for k, v in entity.items()}
        if isinstance(entity, list):
            return [self.deserialize_entity(ctxt, v) for v in entity]
        return entity
