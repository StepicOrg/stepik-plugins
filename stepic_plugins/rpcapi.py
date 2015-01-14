from oslo import messaging
from oslo.config import cfg


messaging.set_transport_defaults(control_exchange='stepic.rpc')

ALLOWED_EXMODS = [
    'stepic_plugins.exceptions'
]


class QuizAPI(object):
    """Client side of the quizzes RPC API."""

    def __init__(self, transport_url, fake_server=False):
        if not fake_server:
            transport = messaging.get_transport(
                cfg.CONF, transport_url, allowed_remote_exmods=ALLOWED_EXMODS)
        else:
            from . import rpc
            fake_rpc_server = rpc.start_fake_server()
            transport = fake_rpc_server.transport
        target = messaging.Target(topic='quiz', version='0.1')
        self.client = messaging.RPCClient(transport, target)

    def ping(self, msg):
        return self.client.call({}, 'ping', msg=msg)

    def validate_source(self, quiz_ctxt):
        """Validate source from the quiz context.

        Returns None if the source is valid, otherwise raises FormatError

        :raises: FormatError

        """
        return self.client.call(quiz_ctxt, 'validate_source')

    def async_init(self, quiz_ctxt):
        return self.client.call(quiz_ctxt, 'async_init')

    def generate(self, quiz_ctxt):
        return self.client.call(quiz_ctxt, 'generate')

    def clean_reply(self, quiz_ctxt, reply, dataset=None):
        return self.client.call(quiz_ctxt, 'clean_reply',
                                reply=reply, dataset=dataset)

    def check(self, quiz_ctxt, reply, clue=None):
        return self.client.call(quiz_ctxt, 'check', reply=reply, clue=clue)

    # TODO: add clenaup method
