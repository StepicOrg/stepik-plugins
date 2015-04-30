import base64
import json
import logging
import subprocess
import tempfile
import time

import requests

from stepic_plugins import settings
from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError, PluginError
from stepic_plugins.executable_base import jail_code_wrapper


logger = logging.getLogger(__name__)

MAX_MEMORY_LIMIT = 1024

RNR_AUTH = (settings.ROOTNROLL_USERNAME, settings.ROOTNROLL_PASSWORD)
RNR_IMAGE_URL = '{}/images/{{image_id}}'.format(settings.ROOTNROLL_API_URL)
RNR_SERVERS_URL = '{}/servers'.format(settings.ROOTNROLL_API_URL)
RNR_SERVER_URL = '{}/servers/{{server_id}}'.format(settings.ROOTNROLL_API_URL)
RNR_TERMINALS_URL = '{}/terminals'.format(settings.ROOTNROLL_API_URL)
RNR_CHECKER_JOBS_URL = '{}/checker-jobs'.format(settings.ROOTNROLL_API_URL)
RNR_CHECKER_JOB_URL = '{}/checker-jobs/{{job_id}}'.format(
    settings.ROOTNROLL_API_URL)
RNR_SANDBOXES_URL = '{}/sandboxes'.format(settings.ROOTNROLL_API_URL)
RNR_SANDBOX_URL = '{}/sandboxes/{{sandbox_id}}'.format(
    settings.ROOTNROLL_API_URL)


class ServerStatus(object):
    ACTIVE = 'ACTIVE'
    ERROR = 'ERROR'


class CheckerJobStatus(object):
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    READY_SET = {COMPLETED, FAILED}


class CheckerJobResult(object):
    PASSED = 'passed'
    FAILED = 'failed'


class SandboxStatus(object):
    SUCCESS = 'success'
    FAILURE = 'failure'
    TIMEOUT = 'timeout'


class AdminQuiz(BaseQuiz):
    name = 'admin'

    class Schemas:
        source = {
            'image_id': int,
            'memory': int,
            'is_bootstrap': bool,
            'bootstrap_script': str,
            'test_scenario': str,
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
        self.is_bootstrap = source.is_bootstrap
        self.bootstrap_script = source.bootstrap_script
        self.test_scenario = source.test_scenario

    def async_init(self):
        r = requests.get(RNR_IMAGE_URL.format(image_id=self.image_id),
                         auth=RNR_AUTH)
        if r.status_code != 200:
            if r.status_code == 404:
                raise FormatError("Image not found with ID: {}"
                                  .format(self.image_id))
            raise PluginError("Internal server error: failed to connect to "
                              "backend which serves virtual machines")
        if self.memory > MAX_MEMORY_LIMIT:
            raise FormatError("Maximum value for memory limit is {} MB"
                              .format(MAX_MEMORY_LIMIT))
        # Check bootstrap script syntax
        self._check_bootstrap_script(self.bootstrap_script)
        # Check pytest scenario (try to collect tests, but don't execute them)
        test_filename = 'test_scenario.py'
        pytest_files = [(self.test_scenario, test_filename)]
        pytest_argv = ['-m', 'pytest', '-s', '--collect-only', test_filename]
        result = jail_code_wrapper('python',
                                   code=None,
                                   files=pytest_files,
                                   argv=pytest_argv,
                                   stdin=None)
        if result.status != 0:
            output = result.stdout.decode(errors='replace')
            errput = result.stderr.decode(errors='replace')
            if errput:
                msg = ("Internal error while checking test scenario "
                       "correctness:\n\n{0}{1}".format(output, errput))
                logger.error(msg)
                raise PluginError(msg)
            msg = "Test scenario code contains errors:\n\n{0}".format(output)
            raise FormatError(msg)
        return {'options': {'time_limit': 60 * 60}}

    def generate(self):
        server = self._create_server(self.image_id, self.memory)
        server = self._wait_server_status(server['id'], ServerStatus.ACTIVE)

        if self.is_bootstrap:
            self._bootstrap_server(server, self.bootstrap_script)

        terminal = self._create_terminal(server['id'])
        terminal_config = {
            'terminal_id': terminal['id'],
            'kaylee_url': terminal['config']['kaylee_url'],
        }
        return terminal_config, server['id']

    def check(self, reply, clue):
        server_id = clue
        job = self._create_checker_job(server_id, self.test_scenario)
        try:
            job = self._wait_checker_job_ready(job['id'])
        except TimeoutError:
            raise PluginError("Check system timeout")
        if job['status'] == CheckerJobResult.FAILED:
            raise PluginError("Check system internal error")

        assert job['status'] == CheckerJobStatus.COMPLETED
        return job['result'] == CheckerJobResult.PASSED, job['hint']

    def cleanup(self, clue):
        server_id = clue
        print("CLeaning up admin quiz attempt, server_id:", server_id)
        self._destroy_server(server_id)

    def _check_bootstrap_script(self, script):
        with tempfile.NamedTemporaryFile(prefix='bootstrap-', suffix='.sh',
                                         mode='w', encoding='utf-8') as tf:
            tf.file.write(script)
            tf.flush()
            proc = subprocess.Popen(['/bin/bash', '-n', tf.name],
                                    stderr=subprocess.PIPE)
            try:
                _, stderr = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                raise FormatError("Cannot check bootstrap script syntax, "
                                  "took too much time")
            if proc.returncode != 0:
                msg = "Syntax error in bootstrap script:\n\n{0}".format(
                    stderr.decode(errors='replace'))
                raise FormatError(msg)

    def _create_server(self, image_id, memory):
        server_body = {
            'image_id': image_id,
            'memory': memory,
        }
        r = requests.post(RNR_SERVERS_URL, data=server_body, auth=RNR_AUTH)
        print("Create server response:", r.status_code, r.content)
        if r.status_code != 201:
            raise PluginError("Failed to create new virtual machine instance")
        return r.json()

    def _wait_server_status(self, server_id, until_status, timeout=180):
        """Wait for server status to become `until_status`."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            r = requests.get(RNR_SERVER_URL.format(server_id=server_id),
                             auth=RNR_AUTH)
            if r:
                server = r.json()
                if server['status'] == until_status:
                    return server
                if server['status'] == ServerStatus.ERROR:
                    raise PluginError("Failed to create new virtual machine "
                                      "instance")
            time.sleep(1)
        else:
            # TODO: delete instance
            raise PluginError("Timed out creating new virtual machine "
                              "instance")

    def _bootstrap_server(self, server, script):
        print("Start to bootstrap server:", server)
        if not server['private_ip']:
            raise PluginError("Failed to bootstrap your virtual machine: "
                              "VM network is down")

        sandbox = self._create_bootstrap_sandbox(server, script)
        try:
            sandbox = self._wait_sandbox_terminated(sandbox, timeout=300)
        except TimeoutError:
            raise PluginError("Failed to bootstrap your virtual machine: "
                              "took too much time")
        if (sandbox['status'] == SandboxStatus.SUCCESS and
                sandbox['exit_code'] != 0):
            stdout = base64.b64decode(sandbox['stdout']).decode(errors='replace')
            stderr = base64.b64decode(sandbox['stderr']).decode(errors='replace')
            raise PluginError("Failed to bootstrap your virtual machine.\n\n"
                              "{0}\n{1}".format(stdout, stderr))
        elif sandbox['status'] == SandboxStatus.FAILURE:
            raise PluginError("Failed to bootstrap your virtual machine: {0}"
                              .format(sandbox['error']))

    def _create_bootstrap_sandbox(self, server, script):
        sandbox_cmd = (
            'fab bootstrap -f /bootstrap/fabfile.py -i /bootstrap/ssh-key '
            '-H {ip} -u root --hide=aborts,running,stdout'
        ).format(ip=server['private_ip'])
        sandbox_body = {
            'profile': 'linux-bootstrap',
            'command': sandbox_cmd,
            "files": [{
                "name": "bootstrap.sh",
                "content": base64.b64encode(script.encode()).decode()
            }],
            "limits": {
                "cputime": 305,
                "realtime": 305,
                "memory": 32,
            }
        }
        headers = {'content-type': 'application/json'}
        r = requests.post(RNR_SANDBOXES_URL, data=json.dumps(sandbox_body),
                          headers=headers, auth=RNR_AUTH)
        print("Create bootstrap sandbox response:", r.status_code, r.content)
        if r.status_code != 201:
            raise PluginError("Failed to bootstrap your virtual machine")
        return r.json()

    def _wait_sandbox_terminated(self, sandbox, timeout=60):
        start_time = time.time()
        while time.time() - start_time < timeout:
            r = requests.get(RNR_SANDBOX_URL.format(sandbox_id=sandbox['id']),
                             auth=RNR_AUTH)
            if r:
                sandbox = r.json()
                if sandbox['timeout']:
                    raise TimeoutError()
                if sandbox['status'] in [SandboxStatus.SUCCESS,
                                         SandboxStatus.FAILURE]:
                    return sandbox
            time.sleep(0.5)
        raise TimeoutError()

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

    def _create_checker_job(self, server_id, test_scenario):
        job_body = {
            'server': server_id,
            'test_scenario': test_scenario,
        }
        r = requests.post(RNR_CHECKER_JOBS_URL, data=job_body, auth=RNR_AUTH)
        print("Create checker job response:", r.status_code, r.content)
        if r.status_code != 201:
            raise PluginError("Failed to create new checker job for server_id:"
                              " {0}".format(server_id))
        return r.json()

    def _wait_checker_job_ready(self, job_id, timeout=120):
        start_time = time.time()
        while time.time() - start_time < timeout:
            r = requests.get(RNR_CHECKER_JOB_URL.format(job_id=job_id),
                             auth=RNR_AUTH)
            if r:
                server_status = r.json().get('status')
                if server_status in CheckerJobStatus.READY_SET:
                    return r.json()
            time.sleep(1)
        raise PluginError("Timed out waiting for checker job readiness")

    def _destroy_server(self, server_id):
        r = requests.delete(RNR_SERVER_URL.format(server_id=server_id),
                            auth=RNR_AUTH)
        if r.status_code not in [204, 404]:
            raise PluginError("Failed to destroy the virtual machine: {0}"
                              .format(server_id))
