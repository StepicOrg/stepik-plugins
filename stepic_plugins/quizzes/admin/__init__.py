import time
import random

import requests

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError, PluginError
from stepic_plugins.quizzes.executable_base import settings


MAX_MEMORY_LIMIT = 1024

RNR_AUTH = (settings.ROOTNROLL_USERNAME, settings.ROOTNROLL_PASSWORD)
RNR_IMAGE_URL = '{}/images/{{image_id}}'.format(settings.ROOTNROLL_API_URL)
RNR_SERVERS_URL = '{}/servers'.format(settings.ROOTNROLL_API_URL)
RNR_SERVER_URL = '{}/servers/{{server_id}}'.format(settings.ROOTNROLL_API_URL)
RNR_TERMINALS_URL = '{}/terminals'.format(settings.ROOTNROLL_API_URL)


class ServerStatus(object):
    ACTIVE = 'ACTIVE'
    ERROR = 'ERROR'


class AdminQuiz(BaseQuiz):
    name = 'admin'

    class Schemas:
        source = {
            'image_id': int,
            'memory': int,
        }
        dataset = {
            'terminal_id': str,
            'kaylee_url': str,
        }
        reply = {}

    def __init__(self, source):
        super().__init__(source)
        self.image_id = source.image_id
        self.memory = source.memory

    def async_init(self):
        r = requests.get(RNR_IMAGE_URL.format(image_id=self.image_id),
                         auth=RNR_AUTH)
        if r.status_code != 200:
            raise FormatError("Image not found with ID: {}"
                              .format(self.image_id))
        if self.memory > MAX_MEMORY_LIMIT:
            raise FormatError("Maximum value for memory limit is {} MB"
                              .format(MAX_MEMORY_LIMIT))

    def generate(self):
        server = self._create_server(self.image_id, self.memory)
        self._wait_server_status(server['id'], ServerStatus.ACTIVE)
        terminal = self._create_terminal(server['id'])
        terminal_config = {
            'terminal_id': terminal['id'],
            'kaylee_url': 'http://{host}:{port}/sockjs'.format(
                host=terminal['config']['kaylee_host'],
                port=terminal['config']['kaylee_port'],
            ),
        }
        return terminal_config, server['id']

    def check(self, reply, clue):
        print("# CHECK called with clue:", clue)
        # TODO: call checker and wait for result
        # TODO: destroy the server if quiz solved
        return random.choice([True, (False, "You aren't lucky")])

    def _create_server(self, image_id, memory):
        server_body = {
            'image_id': image_id,
            'memory': memory,
        }
        r = requests.post(RNR_SERVERS_URL, data=server_body, auth=RNR_AUTH)
        print("Create server request:", r.status_code, r.content)
        if r.status_code != 201:
            raise PluginError("Failed to create new virtual machine instance")
        return r.json()

    def _wait_server_status(self, server_id, until_status, timeout=60):
        """Wait for server status to become `until_status`."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            r = requests.get(RNR_SERVER_URL.format(server_id=server_id),
                             auth=RNR_AUTH)
            if r:
                server_status = r.json().get('status')
                if server_status == until_status:
                    return
                if server_status == ServerStatus.ERROR:
                    raise PluginError("Failed to create new virtual machine "
                                      "instance")
            time.sleep(1)
        else:
            raise PluginError("Timed out creating new virtual machine "
                              "instance")

    def _create_terminal(self, server_id):
        """Create a terminal for the given ACTIVE server."""
        terminal_body = {
            'server_id': server_id,
        }
        r = requests.post(RNR_TERMINALS_URL, data=terminal_body, auth=RNR_AUTH)
        if r.status_code != 201:
            raise PluginError("Failed to create a terminal for your virtual "
                              "machine instance")
        return r.json()
