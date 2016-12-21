import unittest

from unittest.mock import patch

from . import TableQuiz
from stepic_plugins.exceptions import FormatError


class TableQuizTest(unittest.TestCase):
    def setUp(self):
        default_rows = [
            {
                'name': "First row",
                'columns': [
                    {'choice': True}, {'choice': False}, {'choice': False}
                ]
            },
            {
                'name': "Second row",
                'columns': [
                    {'choice': False}, {'choice': True}, {'choice': False}
                ]
            },
        ]
        default_columns = [{'name': "1st column"},
                           {'name': "2nd column"},
                           {'name': "3rd column"}]
        self.default_source = {
            'description': "Rows:",
            'columns': default_columns,
            'rows': default_rows,
            'options': {
                'is_checkbox': False,
                'is_randomize_rows': False,
                'is_randomize_columns': False,
                'sample_size': -1
            },
            'is_always_correct': False,
        }


class TableQuizInitTest(TableQuizTest):
    def test_invalid_sources(self):
        diff = [
            # no right answers
            {'rows': [{
                'name': "First row",
                'columns': [
                    {'choice': False}, {'choice': False}, {'choice': False}
                ]
            }]},
            # multiple right answers
            {'rows': [{
                'name': "First row",
                'columns': [
                    {'choice': True}, {'choice': False}, {'choice': True}
                ]
            }]},
            # equal rows
            {'rows': [
                {'name': "First row",
                 'columns': self.default_source['rows'][0]['columns']},
                {'name': "First row",
                 'columns': self.default_source['rows'][0]['columns']},
            ]},
            # equal columns
            {'columns': [{'name': "First column"}, {'name': "First column"}]},
        ]

        for bad_source in [dict(self.default_source, **d) for d in diff]:
            source = TableQuiz.Source(bad_source)
            with self.assertRaises(FormatError):
                TableQuiz(source)

    def test_valid_source(self):
        TableQuiz(TableQuiz.Source(self.default_source))

    def test_valid_multiple_choice_source(self):
        self.default_source['options']['is_checkbox'] = True
        self.default_source['rows'][0]['columns'] = [
            {'choice': True}, {'choice': True}, {'choice': False}
        ]
        self.default_source['rows'][1]['columns'] = [
            {'choice': False}, {'choice': True}, {'choice': True}
        ]

        TableQuiz(TableQuiz.Source(self.default_source))

    def test_valid_no_right_answers_source(self):
        self.default_source['rows'][0]['columns'] = [
            {'choice': False}, {'choice': False}, {'choice': False}
        ]
        self.default_source['options']['is_checkbox'] = True

        TableQuiz(TableQuiz.Source(self.default_source))

    def test_valid_always_correct_source(self):
        self.default_source['rows'][0]['columns'] = [
            {'choice': False}, {'choice': False}, {'choice': False}
        ]
        self.default_source['is_always_correct'] = True

        TableQuiz(TableQuiz.Source(self.default_source))


class TableQuizGenerateTest(TableQuizTest):
    def setUp(self):
        super().setUp()
        self.default_dataset = {
            'description': "Rows:",
            'columns': ["1st column", "2nd column", "3rd column"],
            'rows': ["First row", "Second row"],
            'is_checkbox': False,
        }
        self.default_clue = [[True, False, False],
                             [False, True, False]]

    def test_generate(self):
        quiz = TableQuiz(TableQuiz.Source(self.default_source))

        dataset, clue = quiz.generate()

        self.assertEqual(dataset, self.default_dataset)
        self.assertEqual(clue, self.default_clue)

    @patch('stepic_plugins.quizzes.table.random')
    def test_generate_randomize_rows(self, mock_random):
        mock_random.shuffle = lambda l: l.reverse()
        self.default_source['options']['is_randomize_rows'] = True
        quiz = TableQuiz(TableQuiz.Source(self.default_source))

        dataset, clue = quiz.generate()

        self.default_dataset['rows'].reverse()
        self.default_clue.reverse()
        self.assertEqual(dataset, self.default_dataset)
        self.assertEqual(clue, self.default_clue)

    @patch('stepic_plugins.quizzes.table.random')
    def test_generate_randomize_rows(self, mock_random):
        mock_random.shuffle = lambda l: l.reverse()
        self.default_source['options']['is_randomize_columns'] = True
        quiz = TableQuiz(TableQuiz.Source(self.default_source))

        dataset, clue = quiz.generate()

        self.default_dataset['columns'].reverse()
        self.default_clue[0].reverse()
        self.assertEqual(dataset, self.default_dataset)
        self.assertEqual(clue, self.default_clue)


class TableQuizCheckTest(TableQuizTest):
    def test_check(self):
        quiz = TableQuiz(TableQuiz.Source(self.default_source))
        choices = [
            {'columns': [{'name_row': '1st column', 'answer': True},
                         {'name_row': '2nd column', 'answer': False},
                         {'name_row': '3rd column', 'answer': False}]},
            {'columns': [{'name_row': '1st column', 'answer': False},
                         {'name_row': '2nd column', 'answer': True},
                         {'name_row': '3rd column', 'answer': False}]}
        ]
        clue = [[True, False, False],
                [False, True, False]]

        self.assertIs(quiz.check(choices, clue), True)

        clue = [[False, True, False],
                [False, True, False]]

        self.assertIs(quiz.check(choices, clue), False)

        # multiple choice
        choices[0]['columns'][1]['answer'] = True
        clue = [[True, True, False],
                [False, True, False]]

        self.assertIs(quiz.check(choices, clue), True)
