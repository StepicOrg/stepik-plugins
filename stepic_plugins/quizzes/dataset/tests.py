import textwrap
import unittest

from . import DatasetQuiz
from stepic_plugins.constants import WARNING_NEWLINE, WARNING_SPLIT_LINES


class DatasetQuizTest(unittest.TestCase):
    def setUp(self):
        self.default_source = {
            'code': textwrap.dedent("""
            def generate():
                return "5 7\\n"

            def solve(dataset):
                a, b = dataset.split()
                return str(int(a) + int(b))

            def check(reply, clue):
                return int(reply) == int(clue)

            tests = [("2 2\\n", "4", "4")]
            """)
        }

    def test_async_init_no_warnings(self):
        quiz = DatasetQuiz(DatasetQuiz.Source(self.default_source))

        async_result = quiz.async_init()

        self.assertEqual(async_result['warnings'], [])

    def test_async_init_warnings(self):
        warning_sources = [
            {
                'code': textwrap.dedent("""
                def generate():
                    return "5 7\\n"

                def solve(dataset):
                    a, b = dataset.split()
                    return str(int(a) + int(b))

                def check(reply, clue):
                    return int(reply) == int(clue)

                tests = [("2 2", "4", "4")]
                """)
            },
            {
                'code': textwrap.dedent("""
                def generate():
                    return "5 7"

                def solve(dataset):
                    a, b = dataset.split()
                    return str(int(a) + int(b))

                def check(reply, clue):
                    return int(reply) == int(clue)

                tests = [("2 2\\n", "4", "4")]
                """)
            }
        ]
        for source in warning_sources:
            quiz = DatasetQuiz(DatasetQuiz.Source(source))

            async_result = quiz.async_init()

            self.assertIn(WARNING_NEWLINE, async_result['warnings'])
