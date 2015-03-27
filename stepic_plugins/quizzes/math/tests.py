import unittest

from . import MathQuiz


@unittest.skip
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

    def check(self, answer, reply, result, **kwargs):
        quiz = MathQuiz(MathQuiz.Source({
            'answer': answer,
            'numerical_test': dict(self.default_numerical_test, **kwargs),
        }))
        self.assertEqual(quiz.check(reply, '')[0], result)

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
