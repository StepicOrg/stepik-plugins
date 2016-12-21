import unittest

from . import MathQuiz, is_math_quiz_enabled
from stepic_plugins.exceptions import FormatError


@unittest.skipUnless(is_math_quiz_enabled(), 'sympy is not installed')
class MathQuizCheckTest(unittest.TestCase):
    def setUp(self):
        self.default_numerical_test = {
            'z_re_min': '2',
            'z_re_max': '3',
            'z_im_min': '-1',
            'z_im_max': '1',
            'max_error': '1e-06',
            'integer_only': False,
        }

    def test_invalid_sources(self):
        diff = [
            {'z_re_min': 'not-a-number'},
            {'z_re_max': 'not-a-number'},
            {'z_im_min': 'not-a-number'},
            {'z_im_max': 'not-a-number'},
            {'max_error': 'not-a-number'},
            {'z_re_min': '42', 'z_re_max': '24'},
            {'z_im_min': '42', 'z_im_max': '24'},
            {'max_error': '-1'},
        ]

        for bad_numerical_test in [dict(self.default_numerical_test, **d) for d in diff]:
            bad_source = {'answer': 'x', 'numerical_test': bad_numerical_test}
            with self.assertRaises(FormatError):
                MathQuiz(MathQuiz.Source(bad_source))

    def check(self, answer, reply, result, feedback_contains=None,
              feedback_not_contains=None, **kwargs):
        quiz = MathQuiz(MathQuiz.Source({
            'answer': answer,
            'numerical_test': dict(self.default_numerical_test, **kwargs),
        }))
        score, feedback = quiz.check(reply, '')
        self.assertEqual(score, result, feedback)
        if feedback_contains is not None:
            if not isinstance(feedback_contains, (list, tuple)):
                feedback_contains = [feedback_contains]
            for msg in feedback_contains:
                self.assertIn(msg, feedback, "Feedback should contain '{0}'".format(msg))
        if feedback_not_contains is not None:
            if not isinstance(feedback_not_contains, (list, tuple)):
                feedback_not_contains = [feedback_not_contains]
            for msg in feedback_not_contains:
                self.assertNotIn(msg, feedback, "Feedback should not contain '{0}'".format(msg))

    def test_check(self):
        self.check('cos(2*x)', 'cos(x+x)', True)
        self.check('cos(2*x)', 'cos(x+x+x)', False)
        self.check('cos(pi)', '-1', True)
        self.check('cos(pi)', '-3', False)
        self.check('x + y', '2*x + y - x', True)
        self.check('pi', '3.141592', True)
        self.check('pi', '3.1415', False)
        self.check('pi', '3.1415', True, max_error='1e-04')
        self.check('33**12-(8*33**7-3*33**2)-2*(9*33**8-10*33**4+1)+2*12*33**3+20*33**4-6',
                   '(33**12)-2*(12-3)*(33**(12-4))-(12-4)*(33**(12-5))+2*10*(33**3)*2+6*(33**2)*2',
                   False)
        self.check('7**7 / (2**2 * 5**5)', '(3.5**3.5 / 2.5**2.5)**2', True)
        self.check('2*floor(n/2)+n-5', '4*(ceiling(n/2)-3)+3*(1-(n-2*floor(n/2)))+4', False)
        self.check('2*floor(n/2)+n-5', '4*(ceiling(n/2)-3)+3*(1-(n-2*floor(n/2)))+4', True,
                   integer_only=True)

    def test_check_inequality(self):
        self.check('x > 5', 'x > 5', True)
        self.check('x > -5', 'x - 2 > -7', True)
        self.check('5 <= -2 + sin(x)', 'sin(x) + 4 >= 11', True)
        self.check('x < y ^ z', 'y ^ z > x', True)
        self.check('x > 5', '5', False, feedback_contains='must be an inequality')
        self.check('x > 5', 'x > 3', False, feedback_not_contains='Cannot check answer')
        self.check('x >= 0', 'x > 0', False, feedback_not_contains='Cannot check answer')
        self.check('x >= y + cos(2*x)', 'x > 0', False, feedback_not_contains='Cannot check answer')
        self.check('x', 'x > 5', False,
                   feedback_contains='must not be an inequality',
                   feedback_not_contains='Cannot check answer')

    def test_check_trigonometric_misnaming(self):
        feedback_pattern = 'You wrote "{wrote}", maybe you meant to write "{meant}".'
        sympy_trigonometric_notation_map = {
            'tg': 'tan',
            'ctg': 'cot',
            'arccos': 'acos',
            'arcsin': 'asin',
            'arctg': 'atan',
            'atg': 'atan',
            'arcctg': 'acot',
            'actg': 'acot',
        }
        for f, f_correct in sympy_trigonometric_notation_map.items():
            answer = '{func}(x)'.format(func=f_correct)
            reply = '{func}(x)'.format(func=f)
            expected_feedback = feedback_pattern.format(wrote=f, meant=f_correct)

            self.check(answer, reply, False, feedback_contains=expected_feedback)
        self.check('E', 'e', False, feedback_contains=feedback_pattern.format(wrote='e', meant='E'))
        self.check('x+acot(E + y)', 'x+arcctg(e + y)', False,
                   feedback_contains=['wrote "e"', 'wrote "arcctg"'],
                   feedback_not_contains=['wrote "ctg"', 'wrote "tg"'])
