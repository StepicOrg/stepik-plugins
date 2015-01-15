import socket
import threading

from oslo import messaging
from oslo.config import cfg

from .base import load_by_name
from .exceptions import FormatError, PluginError


class QuizEndpoint(object):
    target = messaging.Target(version='0.1')

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
        return self._quiz_instance(ctxt).clean_reply(reply, dataset=dataset)

    def check(self, ctxt, reply, clue):
        return self._quiz_instance(ctxt).check(reply, clue=clue)

    def cleanup(self, ctxt, clue):
        return self._quiz_instance(ctxt).cleanup(clue=clue)


_fake_transport = messaging.get_transport(cfg.CONF, 'fake:')
_fake_server = None


def get_server(transport_url, fake=False):
    if not fake:
        transport = messaging.get_transport(cfg.CONF, transport_url)
        server_name = socket.gethostname()
        executor = 'eventlet'
    else:
        transport = _fake_transport
        server_name = 'fake_server'
        executor = 'blocking'
    target = messaging.Target(topic='quiz', server=server_name)
    endpoints = [
        QuizEndpoint(),
    ]
    return messaging.get_rpc_server(transport, target, endpoints,
                                    executor=executor)


def start_fake_server():
    global _fake_server
    if _fake_server:
        return _fake_server
    _fake_server = get_server(None, fake=True)
    # TODO: configure logging
    print("Starting fake RPC server in thread...")
    threading.Thread(target=_fake_server.start, daemon=True).start()
    return _fake_server
