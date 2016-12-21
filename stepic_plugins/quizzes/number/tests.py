import unittest

from stepic_plugins.exceptions import FormatError
from stepic_plugins.quizzes.number import NumberQuiz


class NumberQuizTest(unittest.TestCase):
    def setUp(self):
        self.default_option = {
            'answer': '42',
            'max_error': '1',
        }
        self.default_source = {
            'options': [self.default_option],
        }

        self.quiz = NumberQuiz(NumberQuiz.Source(self.default_source))


class NumberQuizInitTest(NumberQuizTest):
    def test_invalid_options_number(self):
        with self.assertRaises(FormatError):
            self.default_source = {'options': []}
            NumberQuiz(NumberQuiz.Source(self.default_source))

    def test_negative_error(self):
        with self.assertRaises(FormatError):
            self.default_option['max_error'] = '-1'
            NumberQuiz(NumberQuiz.Source(self.default_source))

    def test_different_formats(self):
        for answer in ['42', '42.1', '42,1', '.42', ',42']:
            self.default_option['answer'] = answer
            NumberQuiz(NumberQuiz.Source(self.default_source))


class NumberQuizCleanReplyTest(NumberQuizTest):
    def test_number_is_extracted(self):
        cleaned_reply = self.quiz.clean_reply(NumberQuiz.Reply({'number': '111'}), None)
        self.assertEqual(cleaned_reply, '111')


class NumberQuizCheckTest(NumberQuizTest):
    def get_reply(self, number):
        return self.quiz.clean_reply(NumberQuiz.Reply({'number': number}), None)

    def test_correct_answers(self):
        for number in ['42', '42.5', '41', '43']:
            self.assertIs(self.quiz.check(self.get_reply(number), None)[0], True)

    def test_wrong_answers(self):
        for number in ['-42', '40', '44', '43.0001']:
            self.assertIs(self.quiz.check(self.get_reply(number), None)[0], False)


class NumberQuizReplyFormatTest(unittest.TestCase):
    def get_quiz(self, answer, max_error):
        return NumberQuiz(NumberQuiz.Source({
            'options': [{
                'answer': answer,
                'max_error': max_error,
            }]
        }))

    def get_reply(self, quiz, number):
        return quiz.clean_reply(NumberQuiz.Reply({'number': number}), None)

    def test_unicode_minus_sign(self):
        quiz = self.get_quiz('-42', '1')
        for number in ['\u201042', '\u201142', '\u201242', '\u201342', '\u201442', '\u201542', '\u221242']:
            self.assertIs(quiz.check(self.get_reply(quiz, number), None)[0], True, str(ord(number[0])))
