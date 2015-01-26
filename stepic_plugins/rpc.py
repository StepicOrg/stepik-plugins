import socket
import threading

from base64 import b64encode

from oslo import messaging
from oslo.config import cfg

from . import settings
from .base import load_by_name
from .exceptions import FormatError, PluginError
from .executable_base import jail_code_wrapper
from .schema import ParsedJSON


class QuizEndpoint(object):
    target = messaging.Target(namespace='quiz', version='0.1')

    @messaging.expected_exceptions(KeyError, FormatError)
    def _quiz_instance(self, ctxt):
        quiz_class = load_by_name(ctxt['name'])
        return quiz_class(ctxt['source'],
                          supplementary=ctxt.get('supplementary'))

    def ping(self, ctxt, msg):
        # TODO: configure logging and add debug logs
        print("Called ping")
        return msg

    def validate_source(self, ctxt):
        self._quiz_instance(ctxt)

    @messaging.expected_exceptions(PluginError)
    def async_init(self, ctxt):
        return self._quiz_instance(ctxt).async_init()

    @messaging.expected_exceptions(PluginError)
    def generate(self, ctxt):
        return self._quiz_instance(ctxt).generate()

    @messaging.expected_exceptions(FormatError)
    def clean_reply(self, ctxt, reply, dataset):
        reply = self._quiz_instance(ctxt).clean_reply(reply, dataset=dataset)
        if isinstance(reply, ParsedJSON):
            return reply._original
        return reply

    def check(self, ctxt, reply, clue):
        return self._quiz_instance(ctxt).check(reply, clue=clue)

    def cleanup(self, ctxt, clue):
        return self._quiz_instance(ctxt).cleanup(clue=clue)

    def list_computationally_hard_quizzes(self, ctxt):
        return settings.COMPUTATIONALLY_HARD_QUIZZES


class CodeJailEndpoint(object):
    target = messaging.Target(namespace='codejail', version='0.1')

    def run_code(self, ctxt, command, code, files, argv, stdin):
        result = jail_code_wrapper(
            command, code=code, files=files, argv=argv, stdin=stdin)
        serializable_result = {
            'status': result.status,
            'stdout': b64encode(result.stdout).decode(),
            'stderr': b64encode(result.stderr).decode(),
            'time_limit_exceeded': result.time_limit_exceeded,
        }
        return serializable_result


_fake_transport = messaging.get_transport(cfg.CONF, 'fake:')
_fake_server = None


def get_server(transport_url, fake=False):
    if not fake:
        transport = messaging.get_transport(cfg.CONF, transport_url)
        server_name = socket.gethostname()
    else:
        transport = _fake_transport
        server_name = 'fake_server'
    target = messaging.Target(topic='plugins', server=server_name)
    endpoints = [
        QuizEndpoint(),
        CodeJailEndpoint(),
    ]
    return messaging.get_rpc_server(transport, target, endpoints,
                                    executor='blocking')


def start_fake_server():
    global _fake_server
    if _fake_server:
        return _fake_server
    _fake_server = get_server(None, fake=True)
    # TODO: configure logging
    print("Starting fake RPC server in thread...")
    threading.Thread(target=_fake_server.start, daemon=True).start()
    return _fake_server
