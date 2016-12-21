import unittest

from itertools import permutations

from . import MatchingQuiz
from stepic_plugins.exceptions import FormatError


class MatchingQuizTest(unittest.TestCase):
    def setUp(self):
        self.default_pairs = [
            {'first': 'a', 'second': 'A'},
            {'first': 'b', 'second': 'B'},
            {'first': 'c', 'second': 'C'},
        ]
        blank_pairs = [
            {'first': 'blank1', 'second': ''},
            {'first': 'blank2', 'second': ''},
        ]
        self.default_source = {'preserve_firsts_order': False,
                               'pairs': self.default_pairs}
        self.blanks_source = {'preserve_firsts_order': False,
                              'pairs': self.default_pairs + blank_pairs}


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

    def test_blanks_in_second_part(self):
        MatchingQuiz(MatchingQuiz.Source(self.blanks_source))


class MatchingQuizGenerateTest(MatchingQuizTest):
    def test_unique_pairs(self):
        quiz = MatchingQuiz(MatchingQuiz.Source(self.default_source))

        dataset, (inverse_perm, blanks) = quiz.generate()

        pairs = dataset['pairs']
        matched_pairs = [{'first': pair['first'], 'second': pairs[inverse_perm[i]]['second']}
                         for i, pair in enumerate(pairs)]
        matched_pairs.sort(key=lambda x: x['first'])
        assert matched_pairs == self.default_pairs
        assert blanks == []

    def test_blanks_in_second_part(self):
        quiz = MatchingQuiz(MatchingQuiz.Source(self.blanks_source))

        dataset, (_, blanks) = quiz.generate()

        assert len(set(blanks)) == 2
        assert all(not dataset['pairs'][blank_index]['second'] for blank_index in blanks)


class MatchingQuizCheckTest(MatchingQuizTest):
    def test_unique_pairs(self):
        quiz = MatchingQuiz(MatchingQuiz.Source(self.default_source))
        clue = ([0, 2, 1], [])
        reply = [0, 2, 1]

        assert quiz.check(reply, clue)
        assert not quiz.check([0, 1, 2], clue)

    def test_blanks_in_second_part(self):
        quiz = MatchingQuiz(MatchingQuiz.Source(self.blanks_source))
        clue = ([3, 1, 2, 4, 0], [1, 4])

        correct_replies = [[3, 1, 2, 4, 0], [3, 4, 2, 1, 0]]
        wrong_replies = [list(perm) for perm in permutations(range(5))
                         if list(perm) not in correct_replies]

        for correct_reply in correct_replies:
            assert quiz.check(correct_reply, clue)
        for wrong_reply in wrong_replies:
            assert not quiz.check(wrong_reply, clue)
