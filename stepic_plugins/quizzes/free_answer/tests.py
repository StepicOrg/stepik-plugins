import unittest

from hypothesis import given
from hypothesis.strategies import booleans

from . import FreeAnswerQuiz
from stepic_plugins.utils import create_attachment


class FreeAnswerQuizTest(unittest.TestCase):
    def setUp(self):
        self.source = {
            'is_attachments_enabled': True,
            'is_html_enabled': True,
            'manual_scoring': False,
        }
        self.attachment = create_attachment('file.txt', "Attachment content")
        self.reply = {
            'text': "Response text here \n",
            'attachments': [self.attachment],
        }

    @property
    def quiz(self):
        return FreeAnswerQuiz(FreeAnswerQuiz.Source(self.source))

    @given(booleans(), booleans())
    def test_generate(self, is_attachments_enabled, is_html_enabled):
        self.source['is_attachments_enabled'] = is_attachments_enabled
        self.source['is_html_enabled'] = is_html_enabled

        dataset, clue = self.quiz.generate()
        FreeAnswerQuiz.Dataset(dataset)  # validate schema

        expected_dataset = {
            'is_attachments_enabled': is_attachments_enabled,
            'is_html_enabled': is_html_enabled,
        }
        self.assertEqual(dataset, expected_dataset)
        self.assertIsNone(clue)

    def test_clean_reply_not_sanitized(self):
        self.reply = FreeAnswerQuiz.Reply({'text': "42", 'attachments': []})

        assert self.quiz.clean_reply(self.reply, None) is self.reply

    def test_clean_reply_sanitized(self):
        self.reply = {'text': '<script>alert("XSS");</script>', 'attachments': []}

        cleaned_reply = self.quiz.clean_reply(FreeAnswerQuiz.Reply(self.reply), None)

        assert cleaned_reply == {'text': 'alert("XSS");', 'attachments': []}

    def text_check_empty_reply(self):
        self.reply = {'text': " <p> </p>", 'attachments': []}

        score, feedback = self.quiz.check(self.reply, None)

        assert not score
        assert "Empty reply" in feedback

    def test_check_empty_reply_html_disabled(self):
        self.source['is_html_enabled'] = False
        self.reply = {'text': "  \n   ", 'attachments': []}

        score, feedback = self.quiz.check(self.reply, None)

        assert not score
        assert "Empty reply" in feedback

    def test_check_correct(self):
        assert self.quiz.check(self.reply, None) is True

    def text_check_correct_html_disabled(self):
        self.source['is_html_enabled'] = False
        self.reply['text'] = "<p></p>"

        assert self.quiz.check(self.reply, None) is True

    def test_check_correct_only_attachment(self):
        self.reply['text'] = ""

        assert self.quiz.check(self.reply, None) is True
