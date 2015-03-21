import unittest

from . import MathQuiz


@unittest.skip
class MathQuizCheckTest(unittest.TestCase):
    def check(self, answer, reply, result):
        quiz = MathQuiz(MathQuiz.Source({'answer': answer}))
        self.assertEqual(quiz.check(reply, '')[0], result)

    def test_check(self):
        self.check('cos(2*x)', 'cos(x+x)', True)
        self.check('cos(2*x)', 'cos(x+x+x)', False)
        self.check('cos(pi)', '-1', True)
        self.check('cos(pi)', '-3', False)
        self.check('x + y', '2*x + y - x', True)
        self.check('pi', '3.141592', True)
        self.check('pi', '3.1415', False)
        self.check('33**12-(8*33**7-3*33**2)-2*(9*33**8-10*33**4+1)+2*12*33**3+20*33**4-6',
                   '(33**12)-2*(12-3)*(33**(12-4))-(12-4)*(33**(12-5))+2*10*(33**3)*2+6*(33**2)*2',
                   False)
