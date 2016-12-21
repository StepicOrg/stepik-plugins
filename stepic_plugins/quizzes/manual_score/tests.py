import unittest

from . import ManualScoreQuiz
from stepic_plugins.base import quiz_wrapper_factory


class ManualScoreQuizTest(unittest.TestCase):
    def setUp(self):
        self.source = {}

    @property
    def quiz(self):
        quiz_wrapper = quiz_wrapper_factory(ManualScoreQuiz)
        return quiz_wrapper(self.source)

    def test_init(self):
        assert self.quiz

    def test_generate(self):
        assert self.quiz.generate() is None

    def test_check(self):
        reply = self.quiz.clean_reply({}, None)

        score, feedback = self.quiz.check(reply, None)

        assert score is False
        assert "instructor" in feedback
