import unittest

from . import MatchingQuiz
from stepic_plugins.exceptions import FormatError


class MatchingQuizTest(unittest.TestCase):
    def setUp(self):
        self.default_pairs = [
            {'first': 'a', 'second': 'A'},
            {'first': 'b', 'second': 'B'},
            {'first': 'c', 'second': 'C'},
        ]
        self.default_source = {'preserve_firsts_order': False,
                               'pairs': self.default_pairs}


class MatchingQuizInitTest(MatchingQuizTest):
    def test_invalid_sources(self):
        diff = [
            {'pairs': []},
            {'pairs': self.default_pairs + [{'first': 'c', 'second': 'C'}]},
            {'pairs': self.default_pairs + [{'first': 'c', 'second': 'C2'}]},
            {'pairs': self.default_pairs + [{'first': 'c2', 'second': 'C'}]},
        ]

        for bad_source in [dict(self.default_source, **d) for d in diff]:
            with self.assertRaises(FormatError):
                quiz = MatchingQuiz(MatchingQuiz.Source(bad_source))

    def test_valid_sources(self):
        diff = [
            {'preserve_firsts_order': False,
             'pairs': self.default_pairs[:1]},
            {'preserve_firsts_order': True},
        ]
        for good_source in [dict(self.default_source, **d) for d in diff]:
            MatchingQuiz(MatchingQuiz.Source(good_source))
