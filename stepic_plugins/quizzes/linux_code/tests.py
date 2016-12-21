import base64
import os
import unittest

from hypothesis import given
from hypothesis.strategies import booleans

from . import LinuxCodeQuiz
from stepic_plugins.exceptions import FormatError
from stepic_plugins.schema import ATTACHMENT_HEADER


TESTS_DATA_PATH = os.path.join(os.path.dirname(__file__), 'tests_data')


class LinuxCodeQuizTest(unittest.TestCase):
    def setUp(self):
        self.source = {
            'task_id': 1,
            'is_makefile_required': True
        }
        self.solution = self.load_attachment('solution.c')
        self.makefile = self.load_attachment('Makefile')
        self.reply = {
            'solution': [self.solution],
            'makefile': [self.makefile],
        }

    @property
    def quiz(self):
        return LinuxCodeQuiz(LinuxCodeQuiz.Source(self.source))

    @property
    def built_reply(self):
        return LinuxCodeQuiz.Reply(self.reply)

    def load_attachment(self, filename):
        with open(os.path.join(TESTS_DATA_PATH, filename), 'rb') as f:
            content = f.read()
        return {
            'name': filename,
            'type': 'application/octet-stream',
            'size': len(content),
            'content': ATTACHMENT_HEADER + base64.b64encode(content).decode(),
            'url': '',
        }

    def test_valid_source(self):
        LinuxCodeQuiz(LinuxCodeQuiz.Source(self.source))

    @given(booleans())
    def test_generate(self, is_makefile_required):
        self.source['is_makefile_required'] = is_makefile_required

        dataset, clue = self.quiz.generate()

        self.assertEqual(dataset, {'is_makefile_required': is_makefile_required})

    def test_clean_reply_empty_solution(self):
        self.reply['solution'] = []

        with self.assertRaises(FormatError):
            self.quiz.clean_reply(self.built_reply, None)

    def test_clean_reply_empty_makefile(self):
        self.reply['makefile'] = []

        with self.assertRaises(FormatError):
            self.quiz.clean_reply(self.built_reply, None)

    def test_clean_reply(self):
        clean_reply = self.quiz.clean_reply(self.built_reply, None)

        expected_clean_reply = {
            'solution': self.solution,
            'makefile': self.makefile,
        }
        self.assertEqual(set(clean_reply.keys()), set(expected_clean_reply.keys()))
        self.assertEqual(clean_reply['solution']['content'], expected_clean_reply['solution']['content'])
        self.assertEqual(clean_reply, expected_clean_reply)

    def test_clean_reply_makefile_not_required(self):
        self.source['is_makefile_required'] = False
        self.reply['makefile'] = []

        clean_reply = self.quiz.clean_reply(self.built_reply, None)

        expected_clean_reply = {
            'solution': self.solution,
            'makefile': None,
        }
        self.assertEqual(clean_reply, expected_clean_reply)

    @unittest.skipUnless(os.environ.get('RUN_LINUX_CODE_API_TESTS'), "Linux code API tests skipped")
    def test_check(self):
        score, feedback = self.quiz.check(self.quiz.clean_reply(self.built_reply, None), None)

        self.assertTrue(score)
        self.assertIn("Execution log: Success", feedback)

    @unittest.skipUnless(os.environ.get('RUN_LINUX_CODE_API_TESTS'), "Linux code API tests skipped")
    def test_check_empty_makefile(self):
        self.source['is_makefile_required'] = False
        self.reply['makefile'] = []

        score, feedback = self.quiz.check(self.quiz.clean_reply(self.built_reply, None), None)

        self.assertFalse(score)
        self.assertIn("no makefile found", feedback)
