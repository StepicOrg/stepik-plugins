import unittest

from . import PycharmQuiz
from stepic_plugins.base import quiz_wrapper_factory


class PycharmQuizTest(unittest.TestCase):
    def setUp(self):
        self.source = {
            'title': 'PyCharm Problem',
            'files': [{
                'name': 'hello_world.py',
                'text': 'print("Hello, world! My name is type your name")',
                'placeholders': [{
                    'line': 0,
                    'start': 32,
                    'length': 14,
                    'hint': 'Type your name here',
                    'possible_answer': 'Liana',
                }]
            }],
            'test': [{
                'name': 'tests.py',
                'text': '# python code here',
            }],
        }

    @property
    def quiz(self):
        quiz_wrapper = quiz_wrapper_factory(PycharmQuiz)
        return quiz_wrapper(self.source)

    def test_init(self):
        assert self.quiz

    def test_async_init(self):
        supplementary = self.quiz.async_init()

        assert supplementary['options'] == self.source

    def test_check(self):
        reply = {
            'score': '0',
            'solution': [{
                'name': 'hello_world.py',
                'text': 'print("Hello, world! My name is Liana")'
            }],
        }
        clean_reply = self.quiz.clean_reply(reply, None)

        score, feedback = self.quiz.check(clean_reply._original, None)

        assert score == 0.0
        assert feedback == ""
