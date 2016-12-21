import base64
import time

import requests
import structlog

from stepic_plugins import settings
from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError, PluginError
from stepic_plugins.schema import attachment
from stepic_plugins.utils import attachment_content


logger = structlog.get_logger(plugin='linux_code')


STATUS_URL = '{}/status'.format(settings.LINUX_CODE_API_URL)
SUBMISSION_LIST_URL = '{}/submissions'.format(settings.LINUX_CODE_API_URL)
SUBMISSION_URL = SUBMISSION_LIST_URL + '/{id}'

STATUS_IDDLE = 'IDDLE'

DEFAULT_TIMEOUT = 15
CHECK_STARTED_TIMEOUT = 60
CHECK_READY_TIMEOUT = 180


class LinuxCodeQuiz(BaseQuiz):
    name = 'linux-code'

    class Schemas:
        source = {
            'task_id': int,
            'is_makefile_required': bool,
        }
        dataset = {
            'is_makefile_required': bool,
        }
        reply = {
            'solution': [attachment],
            'makefile': [attachment],
        }

    def generate(self):
        dataset = {
            'is_makefile_required': self.source.is_makefile_required,
        }
        return dataset, None

    def clean_reply(self, reply, dataset):
        if len(reply.solution) != 1:
            raise FormatError("The reply should contain a solution.c file")
        if self.source.is_makefile_required and len(reply.makefile) != 1:
            raise FormatError("The reply should contain a Makefile file")
        clean_reply = {
            'solution': reply.solution[0]._original,
            'makefile': reply.makefile[0]._original if self.source.is_makefile_required else None,
        }
        return clean_reply

    def check(self, reply, clue):
        status = self._get_service_status()
        if status != STATUS_IDDLE:
            return False, "Service is busy right now. Try to submit again a bit later."
        data = {
            'task_id': self.source.task_id,
            'solution': base64.b64encode(attachment_content(reply['solution'])).decode(),
            'makefile': '',
        }
        if self.source.is_makefile_required:
            data['makefile'] = base64.b64encode(attachment_content(reply['makefile'])).decode()
        log = logger.bind(task_id=self.source.task_id)
        log.info("Creating new submission")
        response = requests.post(SUBMISSION_LIST_URL, json=data, timeout=DEFAULT_TIMEOUT)
        if not response:
            msg = "Failed to check the reply"
            logger.error(msg, status_code=response.status_code, body=response.text)
            raise PluginError(msg)
        submission_id = response.json()['id']
        log.info("Submission created", submission_id=submission_id)
        submission = self._wait_submission_checked(submission_id)
        feedback_list = []
        if submission['error_message']:
            feedback_list.append("Error: " + submission['error_message'])
        compilation_log = submission['comp_log'].strip()
        if compilation_log:
            feedback_list.append("Compilation log: " + compilation_log)
        execution_log = submission['comp_exec'].strip()
        if execution_log:
            feedback_list.append("Execution log: " + execution_log)
        feedback_list.append("Unique solution id: {0}".format(submission_id))
        feedback = '\n\n'.join(feedback_list)
        return submission['solve_status'], feedback

    def _get_service_status(self):
        response = requests.get(STATUS_URL, timeout=DEFAULT_TIMEOUT)
        if not response:
            return None
        return response.text

    def _get_submission(self, submission_id):
        response = requests.get(SUBMISSION_URL.format(id=submission_id),
                                timeout=DEFAULT_TIMEOUT)
        if not response:
            logger.info("Failed to get submission", submission_id=submission_id)
            return None
        return response.json()

    def _wait_submission_checked(self, submission_id):
        log = logger.bind(submission_id=submission_id)
        log.info("Waiting for submission check to be started")
        check_started_timeout = CHECK_STARTED_TIMEOUT
        while check_started_timeout > 0:
            submission = self._get_submission(submission_id)
            if submission and 'solve_status' in submission:
                break
            check_started_timeout -= 1
            time.sleep(1)
        else:
            msg = "Timed out while waiting for submission check to be started"
            log.error(msg)
            raise PluginError(msg)
        log.info("Submission check started. Waiting for check readiness",
                 submission=submission)
        check_ready_timeout = CHECK_READY_TIMEOUT
        while check_ready_timeout > 0:
            submission = self._get_submission(submission_id)
            if submission and submission['solve_status'] != '':
                break
            check_ready_timeout -= 1
            time.sleep(1)
        else:
            msg = "Failed to check submission"
            log.error(msg)
            raise PluginError(msg)
        log.info("Submission has been checked successfully", submission=submission)
        solve_status = submission['solve_status']
        if not isinstance(solve_status, (int, float)) or not (0 <= solve_status <= 1):
            log.error("Submission solve_status is incorrect", solve_status=solve_status)
            raise PluginError("Failed to score the reply")
        return submission
