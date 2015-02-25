import unittest

from . import SortingQuiz
from stepic_plugins.exceptions import FormatError


class SortingQuizTest(unittest.TestCase):
    def setUp(self):
        self.default_options = ['A', 'B', 'C']
        self.default_source = {'options': self.default_options}


class SortingQuizInitTest(SortingQuizTest):
    def test_invalid_sources(self):
        diff = [
            {'options': []},
            {'options': self.default_options + self.default_options},
        ]

        for bad_source in [dict(self.default_source, **d) for d in diff]:
            with self.assertRaises(FormatError):
                quiz = SortingQuiz(SortingQuiz.Source(bad_source))

    def test_valid_sources(self):
        diff = [
            {},
        ]
        for good_source in [dict(self.default_source, **d) for d in diff]:
            SortingQuiz(SortingQuiz.Source(good_source))
