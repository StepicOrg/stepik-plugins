import unittest

from stepic_plugins.exceptions import FormatError
from . import SimpleChoiceQuiz


class SimpleChoiceTest(unittest.TestCase):
    def setUp(self):
        self.default_source = {
            'options': [
                {'is_correct': True, 'text': 'A'},
                {'is_correct': False, 'text': 'B'},
            ]
        }

        self.quiz = SimpleChoiceQuiz(SimpleChoiceQuiz.Source(self.default_source))


class SimpleChoiceInitTest(SimpleChoiceTest):
    def test_exactly_one_correct(self):
        with self.assertRaises(FormatError):
            SimpleChoiceQuiz(SimpleChoiceQuiz.Source({'options': [
                {'is_correct': True, 'text': 'A'},
                {'is_correct': True, 'text': 'B'},
            ]}))

        with self.assertRaises(FormatError):
            SimpleChoiceQuiz(SimpleChoiceQuiz.Source({'options': [
                {'is_correct': False, 'text': 'A'},
                {'is_correct': False, 'text': 'B'},
            ]}))


class SimpleChoiceCleanReplyTest(SimpleChoiceTest):
    def setUp(self):
        super().setUp()
        self.dataset = SimpleChoiceQuiz.Dataset({'options': ['A', 'B']})

    def test_correct_length(self):
        for choices in [[], [True], [True, False, False]]:
            reply = SimpleChoiceQuiz.Reply({'choices': choices})
            with self.assertRaises(FormatError):
                self.quiz.clean_reply(reply, self.dataset)

    def test_choices_extracted(self):
        reply = SimpleChoiceQuiz.Reply({'choices': [True, False]})
        clean = self.quiz.clean_reply(reply, self.dataset)
        self.assertEqual(clean, [True, False])


class SimpleChoiceSolveTest(SimpleChoiceTest):
    def test_solve(self):
        def solve(data):
            return SimpleChoiceQuiz.Reply({
                'choices': [x == 'A' for x in data.options]
            })

        dataset, clue = self.quiz.generate()
        dataset = SimpleChoiceQuiz.Dataset(dataset)
        clean_reply = self.quiz.clean_reply(solve(dataset), dataset)
        self.assertIs(self.quiz.check(clean_reply, clue), True)


class SimpleChoiceCheckTest(SimpleChoiceTest):
    def test_check(self):
        clue = [True, False]
        self.assertIs(self.quiz.check([True, False], clue), True)
        self.assertIs(self.quiz.check([False, True], clue), False)
