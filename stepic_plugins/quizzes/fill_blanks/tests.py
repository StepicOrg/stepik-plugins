import unittest

from . import FillBlanksQuiz
from stepic_plugins.exceptions import FormatError


class FillBlanksQuizTest(unittest.TestCase):
    def setUp(self):
        self.source = {
            'components': [
                {'type': 'text', 'text': "May the ", 'options': []},
                {'type': 'select', 'text': '', 'options': [
                    {'text': "Force", 'is_correct': True},
                    {'text': "Death", 'is_correct': False},
                    {'text': "Luke", 'is_correct': False},
                ]},
                {'type': 'text', 'text': " be ", 'options': []},
                {'type': 'input', 'text': '', 'options': [
                    {'text': "with", 'is_correct': True},
                    {'text': "  without ", 'is_correct': True},
                ]},
                {'type': 'text', 'text': " you", 'options': []},
            ],
            'is_case_sensitive': False,
        }
        self.dataset = {
            'components': [
                {'type': 'text', 'text': "May the ", 'options': []},
                {'type': 'select', 'text': '', 'options': ["Force", "Death", "Luke"]},
                {'type': 'text', 'text': " be ", 'options': []},
                {'type': 'input', 'text': '', 'options': []},
                {'type': 'text', 'text': " you", 'options': []},
            ]
        }
        self.clue = [["Force"], ["with", "without"]]

    @property
    def quiz(self):
        return FillBlanksQuiz(FillBlanksQuiz.Source(self.source))


class FillBlanksQuizInitTest(FillBlanksQuizTest):
    def test_no_components(self):
        self.source['components'] = []

        with self.assertRaises(FormatError):
            # noinspection PyStatementEffect
            self.quiz

    def test_at_least_one_blank_component(self):
        # Only text components
        self.source['components'] = [self.source['components'][0],
                                     self.source['components'][2]]

        with self.assertRaises(FormatError):
            # noinspection PyStatementEffect
            self.quiz

    def test_invalid_component_type(self):
        self.source['components'][0]['type'] = 'invalid'

        with self.assertRaises(FormatError):
            # noinspection PyStatementEffect
            self.quiz

    def test_incorrect_html_text(self):
        self.source['components'][0]['text'] = "May the wrong <tag"

        with self.assertRaises(FormatError):
            FillBlanksQuiz(FillBlanksQuiz.Source(self.source))

    def test_correct_html_text(self):
        self.source['components'][0]['text'] = "May the new line<br> and a < b"

        FillBlanksQuiz(FillBlanksQuiz.Source(self.source))


class FillBlanksQuizGenerateTest(FillBlanksQuizTest):
    def test_generate(self):
        dataset, clue = self.quiz.generate()

        self.assertEqual(dataset, self.dataset)
        self.assertEqual(clue, self.clue)


class FillBlanksQuizCleanReplyTest(FillBlanksQuizTest):
    def test_wrong_blanks_number(self):
        reply = FillBlanksQuiz.Reply({'blanks': ["Force"]})

        with self.assertRaises(FormatError):
            self.quiz.clean_reply(reply, None)

    def test_strip_answers(self):
        reply = FillBlanksQuiz.Reply({'blanks': ["  Force ", "  \n"]})

        clean_reply = self.quiz.clean_reply(reply, None)

        self.assertEqual(clean_reply, ["Force", ""])


class FillBlanksQuizCheckTest(FillBlanksQuizTest):
    def test_incorrect_case_sensitive(self):
        self.source['is_case_sensitive'] = True

        self.assertEqual(self.quiz.check(["", ""], self.clue), False)
        self.assertEqual(self.quiz.check(["force", "with"], self.clue), False)
        self.assertEqual(self.quiz.check(["Force", "With"], self.clue), False)
        self.assertEqual(self.quiz.check(["with", "Force"], self.clue), False)

    def test_incorrect_case_insensitive(self):
        self.assertEqual(self.quiz.check(["", ""], self.clue), False)
        self.assertEqual(self.quiz.check(["force", "withh"], self.clue), False)
        self.assertEqual(self.quiz.check(["with", "Force"], self.clue), False)

    def test_correct_case_sensitive(self):
        self.source['is_case_sensitive'] = True

        self.assertEqual(self.quiz.check(["Force", "with"], self.clue), True)
        self.assertEqual(self.quiz.check(["Force", "without"], self.clue), True)

    def test_correct_case_insensitive(self):
        self.assertEqual(self.quiz.check(["Force", "with"], self.clue), True)
        self.assertEqual(self.quiz.check(["FORCE", "Without"], self.clue), True)
