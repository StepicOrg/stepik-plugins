import os
import pytest
import textwrap

from stepic_plugins.quizzes.code import Languages

from .base import BaseTestQuiz


class BaseTestLanguage(BaseTestQuiz):
    language = ''
    extension = ''

    a_plus_b_source = dict(BaseTestQuiz.default_source, **{
        'code': textwrap.dedent("""
            import random

            def generate():
                num_tests = 5
                tests = []
                for test in range(num_tests):
                    a = random.randrange(10)
                    b = random.randrange(10)
                    test_case = "{} {}\\n".format(a, b)
                    tests.append(test_case)
                return tests

            def solve(dataset):
                a, b = dataset.split()
                return str(int(a) + int(b))

            def check(reply, clue):
                return int(reply) == int(clue)
            """),
    })

    @classmethod
    def setup_class(cls):
        base_path = os.path.dirname(os.path.abspath(__file__))
        cls.code_path = os.path.join(base_path, 'code', cls.language)

    def get_code(self, basename):
        filename = basename + '.' + self.extension
        path = os.path.join(self.code_path, filename)
        if not os.path.exists(path):
            pytest.skip("There is no 'a_plus_b' solution for {}"
                        .format(self.language))
        with open(path) as f:
            return f.read()

    def test_basic(self):
        quiz = self.prepare_quiz(self.default_source)
        code = self.get_code('basic')

        score, feedback = self.submit(quiz, code)

        assert score is True
        assert feedback == ""

    def test_a_plus_b(self):
        quiz = self.prepare_quiz(self.a_plus_b_source)
        code = self.get_code('a_plus_b')

        score, feedback = self.submit(quiz, code)

        assert score is True
        assert feedback == ""


class TestCPP(BaseTestLanguage):
    language = Languages.CPP
    extension = 'cpp'
