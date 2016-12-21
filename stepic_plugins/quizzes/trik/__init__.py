import io
import json
import zipfile

import epicbox
import structlog

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError, PluginError
from stepic_plugins.schema import attachment
from stepic_plugins.settings import EPICBOX_TRIK_LIMITS
from stepic_plugins.utils import attachment_content


logger = structlog.get_logger(plugin='trik')

EXIT_CODE_OK = 0
EXIT_CODE_TEST_FAILED = 1

INTERNAL_ERROR = "Internal check system error: {0}"
CHECKER_RESULT_MSG = "\nEXIT CODE: {exit_code}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"

UNARCHIVE_LIMITS = {'cputime': 15, 'realtime': 30}


class TrikQuiz(BaseQuiz):
    name = 'trik'

    class Schemas:
        source = {
            'studio_save': [attachment],
            'fields_archive': [attachment],
        }
        dataset = {
            'file': attachment,
        }
        reply = {
            'studio_save': [attachment],
        }

    def __init__(self, source):
        super().__init__(source)
        if len(source.studio_save) != 1:
            raise FormatError("TRIK Studio save file is not selected")
        if source.fields_archive:
            content = attachment_content(source.fields_archive[0])
            content_reader = io.BytesIO(content)
            try:
                zipfile.ZipFile(content_reader)
            except zipfile.BadZipFile:
                raise FormatError("Fields archive is not a valid zip file")

    def generate(self):
        # noinspection PyProtectedMember
        dataset = {
            'file': self.source.studio_save[0]._original,
        }
        return dataset, None

    def clean_reply(self, reply, dataset):
        if len(reply.studio_save) != 1:
            raise FormatError("The reply should contain a TRIK Studio save file")
        return reply.studio_save[0]

    def _process_checker_result(self, result, workdir):
        exit_code = result['exit_code']
        if exit_code == EXIT_CODE_OK:
            return True
        if exit_code == EXIT_CODE_TEST_FAILED:
            report_result = epicbox.run('trik', command='cat ./report', workdir=workdir)
            if report_result['exit_code']:
                return False, "TRIK Studio save file is incorrect or corrupted"
            try:
                report = json.loads(report_result['stdout'].decode(errors='replace'))
            except ValueError:
                msg = "Failed to parse the report file"
                self.log.exception(msg)
                return False, INTERNAL_ERROR.format(msg)
            # noinspection PyBroadException
            try:
                return False, report[0]['message']
            except Exception:
                msg = "Report format is incorrect"
                self.log.exception(msg, report=report)
                return False, INTERNAL_ERROR.format(msg)
        # Exit code is not OK or TEST_FAILED
        stdout = result['stdout'].decode(errors='replace')
        stderr = result['stderr'].decode(errors='replace')
        self.log.error("Checker failed", exit_code=exit_code, stdout=stdout, stderr=stderr)
        return False, INTERNAL_ERROR.format(
            CHECKER_RESULT_MSG.format(exit_code=exit_code, stdout=stdout, stderr=stderr))

    def check(self, reply, clue):
        studio_files = [{
            'name': 'main.qrs',
            'content': attachment_content(reply)
        }]
        with epicbox.working_directory() as workdir:
            # noinspection PyAttributeOutsideInit
            self.log = logger.bind(workdir=workdir)
            if self.source.fields_archive:
                # TODO: extract all xmls from archive and upload using one epicbox run
                fields_files = [{
                    'name': 'fields.zip',
                    'content': attachment_content(self.source.fields_archive[0])
                }]
                self.log.info("Uploading and unpacking fields archive")
                command = 'mkdir -p fields/main && unzip fields.zip -d fields/main'
                result = epicbox.run('trik', command=command, files=fields_files,
                                     limits=UNARCHIVE_LIMITS, workdir=workdir)
                if result['exit_code'] != 0:
                    raise PluginError("Failed to extract fields from the archive")

            self.log.info("Starting trik sandbox")
            result = epicbox.run('trik', files=studio_files,
                                 limits=EPICBOX_TRIK_LIMITS, workdir=workdir)
            return self._process_checker_result(result, workdir)
