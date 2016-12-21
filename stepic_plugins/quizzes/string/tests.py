import textwrap
import unittest

from stepic_plugins.exceptions import FormatError
from stepic_plugins.utils import attachment_content, create_attachment
from . import StringQuiz


class StrigQuizTest(unittest.TestCase):
    def setUp(self):
        self.source = {
            'pattern': "Correct answer",
            'case_sensitive': False,
            'use_re': False,
            'match_substring': False,
            'code': '',
        }
        self.text_reply = {
            'text': "Correct answer",
            'files': [],
        }
        self.file = create_attachment('file.txt', "Correct answer")
        self.file_reply = {
            'text': "",
            'files': [self.file],
        }

    @property
    def quiz(self):
        return StringQuiz(StringQuiz.Source(self.source))

    def test_is_code_used_empty(self):
        self.assertFalse(self.quiz._is_code_used())

    def test_is_code_used_commented(self):
        self.source['code'] = textwrap.dedent("""

            # commented code
              # comment with heading spaces

            # def solve():
            #     return "42"

            """)

        self.assertFalse(self.quiz._is_code_used())

    def test_is_code_used(self):
        self.source['code'] = textwrap.dedent("""
            # commented code
            uncommented text
            """)

        self.assertTrue(self.quiz._is_code_used())

    def test_async_init_code_not_used(self):
        self.source['code'] = textwrap.dedent("""
            # def check(reply):
            #     return reply == "Hello"
              # comment
            """)

        self.quiz.async_init()

    def test_async_init_code_incomplete(self):
        self.source['code'] = textwrap.dedent("""
            def check(reply):
                return reply == "Hello"
            """)

        with self.assertRaises(FormatError) as cm:
            self.quiz.async_init()

        self.assertIn("Can't export `solve`", cm.exception.args[0])

    def test_async_init_code_used(self):
        self.source['code'] = textwrap.dedent("""
            def check(reply):
                return reply == "Hello"

            def solve():
                return "Hello"
            """)

        self.quiz.async_init()

    def test_clean_reply_valid(self):
        built_reply = StringQuiz.Reply(self.text_reply)

        self.assertEqual(self.quiz.clean_reply(built_reply, None)._original, self.text_reply)

    def test_clean_reply_invalid_number_of_files(self):
        self.file_reply['files'] *= 2
        built_reply = StringQuiz.Reply(self.file_reply)

        with self.assertRaises(FormatError):
            self.quiz.clean_reply(built_reply, None)

    def test_check_correct_text(self):
        self.assertTrue(self.quiz.check(self.text_reply, None))

    def test_check_correct_file(self):
        self.assertTrue(self.quiz.check(self.file_reply, None))

    def test_check_correct_file_after_normalization(self):
        self.source['pattern'] = "foo\nbar \nbaz"
        self.file_reply['files'] = [create_attachment('file.txt', "  foo\r\nbar \nbaz\r")]

        self.assertTrue(self.quiz.check(self.file_reply, None))

    def test_check_correct_file_incorrect_text(self):
        self.file_reply['text'] = "Incorrect answer"

        self.assertTrue(self.quiz.check(self.file_reply, None))

    def test_check_correct_text_incorrect_file(self):
        self.text_reply['files'] = [create_attachment('file.txt', "Incorrect answer")]

        self.assertFalse(self.quiz.check(self.text_reply, None))

    def test_check_incorrect_text(self):
        self.text_reply['text'] = "Incorrect answer"

        self.assertFalse(self.quiz.check(self.text_reply, None))

    def test_check_incorrect_file(self):
        self.file_reply['files'] = [create_attachment('file.txt', "Incorrect answer")]

        self.assertFalse(self.quiz.check(self.file_reply, None))
