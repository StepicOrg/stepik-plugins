import unittest

from unittest.mock import ANY

from . import ChemicalQuiz
from stepic_plugins.exceptions import FormatError


class ChemicalQuizTest(unittest.TestCase):
    def setUp(self):
        self.default_source_formula = {
            'expression': 'C2H5OH',
            'template': ['normal', 'subsup', 'normal', 'subsup',
                         'normal', 'subsup', 'normal', 'subsup']
        }
        self.default_source_equation = {
            'expression': '2H2 + O2 -> 2H2O',
            'template': ['normal', 'subsup', 'normal', 'subsup', 'normal', 'normal', 'subsup',
                         'normal', 'normal', 'normal', 'subsup', 'normal']
        }


class ChemicalQuizInitTest(ChemicalQuizTest):
    def test_invalid_sources(self):
        invalid_sources = [
            {'expression': "", 'template': []},
            {'expression': "2", 'template': []},
            {'expression': "H2O(", 'template': []},
            {'expression': "H +", 'template': []},
            {'expression': 'C2H5OH', 'template': ['SUB']},
            {'expression': 'C2H5OH', 'template': ['normal', 'supsub']},
        ]
        for invalid_source in invalid_sources:
            source = ChemicalQuiz.Source(invalid_source)
            with self.assertRaises(FormatError):
                ChemicalQuiz(source)

    def test_valid_source(self):
        for source in [self.default_source_formula, self.default_source_equation]:
            ChemicalQuiz(ChemicalQuiz.Source(source))


class ChemicalQuizCleanReplyTest(ChemicalQuizTest):
    def test_invalid_slots_number(self):
        quiz = ChemicalQuiz(ChemicalQuiz.Source(self.default_source_formula))
        reply = ChemicalQuiz.Reply({'slots': [{'normal': 'C', 'sub': '', 'sup': ''}]})

        with self.assertRaises(FormatError):
            quiz.clean_reply(reply, None)


class ChemicalQuizCheckTest(ChemicalQuizTest):
    def test_unparsable_expression(self):
        quiz = ChemicalQuiz(ChemicalQuiz.Source(self.default_source_formula))

        self.assertEqual(quiz.check('', None), (False, ANY))
        self.assertEqual(quiz.check('C(', None), (False, ANY))

    def test_formula(self):
        quiz = ChemicalQuiz(ChemicalQuiz.Source(self.default_source_formula))

        self.assertIs(quiz.check('C3H5OH', None), False)
        self.assertIs(quiz.check('C2 H5 OH', None), True)

    def test_equation(self):
        quiz = ChemicalQuiz(ChemicalQuiz.Source(self.default_source_equation))

        self.assertIs(quiz.check('H2+O2->H2O', None), False)
        self.assertIs(quiz.check('O2  + 2H2 ->2H2O', None), True)
