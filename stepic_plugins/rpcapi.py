import io
import tarfile

import oslo_messaging as messaging

from base64 import b64decode
from contextlib import contextmanager

from oslo_config import cfg
from oslo_messaging.rpc.client import _client_opts

from .schema import RPCSerializer


messaging.set_transport_defaults(control_exchange='stepic.rpc')

ALLOWED_EXMODS = [
    'stepic_plugins.exceptions'
]


def set_default_response_timeout(timeout):
    """Set default timeout to wait for a response from a call.

    Given timeout is applied for all rpc calls.

    :param timeout: default timeout in seconds

    """
    cfg.CONF.register_opts(_client_opts)
    cfg.CONF.set_default('rpc_response_timeout', timeout)


@contextmanager
def set_response_timeout(timeout):
    """Context manager to set timeout to wait for a response from a call."""

    current_timeout = cfg.CONF.rpc_response_timeout
    set_default_response_timeout(timeout)
    try:
        yield
    finally:
        set_default_response_timeout(current_timeout)


class BaseAPI(object):
    """Base class for RPC API clients.

    It sets up the RPC client and binds it to the given topic.
    If required, it handles the starting of a fake RPC server.

    """
    topic = None
    namespace = None
    version = None

    def __init__(self, transport_url, fake_server=False):
        if not fake_server:
            transport = messaging.get_transport(
                cfg.CONF, transport_url, allowed_remote_exmods=ALLOWED_EXMODS)
        else:
            from . import rpc
            fake_rpc_server = rpc.start_fake_server()
            transport = fake_rpc_server.transport
        target = messaging.Target(topic=self.topic, namespace=self.namespace,
                                  version=self.version)
        self.client = messaging.RPCClient(transport, target,
                                          serializer=RPCSerializer())


class QuizAPI(BaseAPI):
    """Client side of the quizzes RPC API."""

    topic = 'plugins'
    namespace = 'quiz'
    version = '0.1'

    def ping(self, msg):
        return self.client.call({}, 'ping', msg=msg)

    def validate_source(self, quiz_ctxt):
        """Validate source from the quiz context.

        Returns None if the source is valid, otherwise raises FormatError

        :raises FormatError: if source is not valid

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

    def cleanup(self, quiz_ctxt, clue=None):
        return self.client.call(quiz_ctxt, 'cleanup', clue=clue)

    def list_computationally_hard_quizzes(self):
        return self.client.call({}, 'list_computationally_hard_quizzes')

    def get_static(self):
        """Get static files for all quizzes bundled in a tarball.

        :return: A :class:`TarFile` instance

        """
        tarball_serialized = self.client.call({}, 'get_static')
        tarball_bytes = b64decode(tarball_serialized)
        return tarfile.open(fileobj=io.BytesIO(tarball_bytes))


class CodeJailAPI(BaseAPI):
    """Client side of the codejail RPC API."""

    topic = 'plugins'
    namespace = 'codejail'
    version = '0.1'

    def run_code(self, command, code=None, files=None, argv=None, stdin=None):
        result = self.client.call({}, 'run_code',
                                  command=command, code=code, files=files,
                                  argv=argv, stdin=stdin)
        result['stdout'] = b64decode(result['stdout'])
        result['stderr'] = b64decode(result['stderr'])
        return result
