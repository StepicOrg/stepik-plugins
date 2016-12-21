import unittest

from stepic_plugins.exceptions import FormatError
from stepic_plugins.quizzes.random_tasks import RandomTasksQuiz


class RandomTasksQuizTest(unittest.TestCase):
    def setUp(self):
        self.default_source = {
            'task': '\\x + \\y',
            'solve': 'x + y',
            'max_error': '0.5',
            'ranges': [
                {'variable': 'x', 'num_from': '1', 'num_to': '100', 'num_step': '1'},
                {'variable': 'y', 'num_from': '1', 'num_to': '200', 'num_step': '0.5'}
            ]
        }

    @property
    def quiz(self):
        return RandomTasksQuiz(RandomTasksQuiz.Source(self.default_source))


class RandomTasksQuizRandomVariablesTest(RandomTasksQuizTest):
    def test_float_ranges_incorrect(self):
        with self.assertRaises(FormatError):
            self.default_source['ranges'][0]['num_from'] = '1,0'
            RandomTasksQuiz(RandomTasksQuiz.Source(self.default_source))._random_variables()
        with self.assertRaises(FormatError):
            self.default_source['ranges'][0]['num_from'] = 'a'
            RandomTasksQuiz(RandomTasksQuiz.Source(self.default_source))._random_variables()
        with self.assertRaises(FormatError):
            self.default_source['ranges'][0]['num_from'] = ''
            RandomTasksQuiz(RandomTasksQuiz.Source(self.default_source))._random_variables()
        with self.assertRaises(FormatError):
            self.default_source['ranges'][0]['num_from'] = ' '
            RandomTasksQuiz(RandomTasksQuiz.Source(self.default_source))._random_variables()

    def test_float_ranges_correct(self):
        self.default_source['ranges'][0]['num_from'] = '1.'
        RandomTasksQuiz(RandomTasksQuiz.Source(self.default_source))._random_variables()
        self.default_source['ranges'][0]['num_from'] = '1.0'
        RandomTasksQuiz(RandomTasksQuiz.Source(self.default_source))._random_variables()
        self.default_source['ranges'][0]['num_from'] = '1'
        RandomTasksQuiz(RandomTasksQuiz.Source(self.default_source))._random_variables()


class RandomTasksQuizRandomContextTest(RandomTasksQuizTest):
    def test_regexp_replace_correct(self):
        quiz = self.quiz
        quiz.task = '{:Max}'
        quiz._random_context()
        self.assertEqual(quiz.task, 'Max')

        quiz.task = '{:man:Max} {:man:}'
        quiz._random_context()
        self.assertEqual(quiz.task, 'Max Max')


class RandomTasksQuizGenerateTest(RandomTasksQuizTest):
    def test_solve_expression_incorrect(self):
        with self.assertRaises(FormatError):
            self.default_source['solve'] = 'x + y + z'
            RandomTasksQuiz(RandomTasksQuiz.Source(self.default_source)).generate()
        with self.assertRaises(FormatError):
            self.quiz.solve = 'x + y + z'
            self.quiz.generate()

    def test_clue(self):
        self.default_source.update({
            'task': '\\x \\y',
            'solve': 'x - y',
            'ranges': [
                {'variable': 'x', 'num_from': '1', 'num_to': '100', 'num_step': '1'},
                {'variable': 'y', 'num_from': '1', 'num_to': '100', 'num_step': '1'},
            ],
        })

        dataset, clue = self.quiz.generate()

        x, y = map(float, dataset['task'].split())
        self.assertEqual(clue, x - y)

    def test_clue_negative_numbers(self):
        self.default_source.update({
            'task': '\\x \\y',
            'solve': 'x - y^2',
            'ranges': [
                {'variable': 'x', 'num_from': '-100', 'num_to': '100', 'num_step': '1'},
                {'variable': 'y', 'num_from': '-100', 'num_to': '-50', 'num_step': '1'},
            ],
        })

        dataset, clue = self.quiz.generate()

        x, y = map(float, dataset['task'].split())
        self.assertEqual(clue, x - y ** 2)
