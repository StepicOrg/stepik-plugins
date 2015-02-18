import base64
import fnmatch
import io
import os
import socket
import tarfile
import threading

import structlog

from base64 import b64encode

from oslo import messaging
from oslo.config import cfg

from . import settings
from .base import QUIZZES_DIR, load_by_name
from .exceptions import FormatError, PluginError
from .executable_base import jail_code_wrapper
from .schema import RPCSerializer, to_original


logger = structlog.get_logger()


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
        supplementary = self._quiz_instance(ctxt).async_init()
        return to_original(supplementary)

    @messaging.expected_exceptions(PluginError)
    def generate(self, ctxt):
        return self._quiz_instance(ctxt).generate()

    @messaging.expected_exceptions(FormatError)
    def clean_reply(self, ctxt, reply, dataset):
        reply = self._quiz_instance(ctxt).clean_reply(reply, dataset=dataset)
        return to_original(reply)

    def check(self, ctxt, reply, clue):
        return self._quiz_instance(ctxt).check(reply, clue=clue)

    def cleanup(self, ctxt, clue):
        return self._quiz_instance(ctxt).cleanup(clue=clue)

    def list_computationally_hard_quizzes(self, ctxt):
        return settings.COMPUTATIONALLY_HARD_QUIZZES

    def _collect_quiz_static(self, quiz_directory, tarball):
        log = logger.bind()
        log.info("Start to collect static from quiz directory",
                 quiz_directory=quiz_directory)
        quiz_basedir = os.path.basename(quiz_directory)
        tarball_quiz_dir = os.path.join('stepic_plugins', quiz_basedir)

        coffee_pattern = '*.coffee'
        patterns = ['*.js', '*.css', '*.hbs', coffee_pattern]

        for file in os.listdir(quiz_directory):
            if all(not fnmatch.fnmatch(file, p) for p in patterns):
                continue
            source_file = os.path.join(quiz_directory, file)
            tar_file = os.path.join(tarball_quiz_dir, file)
            if fnmatch.fnmatch(file, coffee_pattern):
                log = log.bind(file=source_file)
                try:
                    import coffeescript
                except ImportError:
                    log.error("Package 'CoffeeScript' is required to compile "
                              "static file, it will be skipped")
                    continue

                tar_file = os.path.splitext(tar_file)[0] + '.js'
                try:
                    source_compiled = (coffeescript.compile_file(source_file)
                                       .encode())
                except (coffeescript.EngineError,
                        coffeescript.CompilationError):
                    log.exception("Failed to compile coffeescript file, "
                                  "it will be skipped")
                    continue
                log.info("Successfully compiled coffeescript file")
                tar_info = tarfile.TarInfo(name=tar_file)
                tar_info.size = len(source_compiled)
                tar_info.mtime = os.path.getmtime(source_file)
                tarball.addfile(tar_info, fileobj=io.BytesIO(source_compiled))
            else:
                tarball.add(source_file, arcname=tar_file)

    def get_static(self, ctxt):
        """Get static files for all quizzes bundled in a tarball.

        Coffeescript files are dynamically compiled before being added
        to a resulting tarball.

        :return: A Base64-encoded tarball file

        """
        tarball_fileobj = io.BytesIO()
        with tarfile.open(fileobj=tarball_fileobj, mode='w:gz') as tarball:
            for directory in os.listdir(QUIZZES_DIR):
                quiz_directory = os.path.join(QUIZZES_DIR, directory)
                if os.path.isdir(quiz_directory):
                    self._collect_quiz_static(quiz_directory, tarball)
        return base64.b64encode(tarball_fileobj.getvalue()).decode()


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
                                    executor='blocking',
                                    serializer=RPCSerializer())


def start_fake_server():
    global _fake_server
    if _fake_server:
        return _fake_server
    _fake_server = get_server(None, fake=True)
    # TODO: configure logging
    print("Starting fake RPC server in thread...")
    threading.Thread(target=_fake_server.start, daemon=True).start()
    return _fake_server
