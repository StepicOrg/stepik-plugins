import base64
import os
import unittest

from . import TrikQuiz
from stepic_plugins.exceptions import FormatError
from stepic_plugins.schema import ATTACHMENT_HEADER


TESTS_DATA_PATH = os.path.join(os.path.dirname(__file__), 'tests_data')


class TrikQuizTest(unittest.TestCase):
    def setUp(self):
        self.studio_save = self.load_attachment('hello-world.qrs')
        self.source = {
            'studio_save': [self.studio_save],
            'fields_archive': [],
        }

    def load_attachment(self, filename):
        with open(os.path.join(TESTS_DATA_PATH, filename), 'rb') as f:
            content = f.read()
        return {
            'name': filename,
            'type': 'application/octet-stream',
            'size': len(content),
            'content': ATTACHMENT_HEADER + base64.b64encode(content).decode(),
            'url': '',
        }

    def test_valid_source(self):
        TrikQuiz(TrikQuiz.Source(self.source))

    def test_invalid_source(self):
        self.source['studio_save'] = []

        with self.assertRaises(FormatError):
            TrikQuiz(TrikQuiz.Source(self.source))

    def test_invalid_source_fields_archive(self):
        self.source['fields_archive'] = [self.load_attachment('hello-world.qrs')]

        with self.assertRaises(FormatError):
            TrikQuiz(TrikQuiz.Source(self.source))

    def test_generate(self):
        quiz = TrikQuiz(TrikQuiz.Source(self.source))

        dataset, clue = quiz.generate()

        self.assertEqual(dataset, {'file': self.studio_save})
        self.assertIsNone(clue)

    def test_clean_reply_empty_attachment(self):
        quiz = TrikQuiz(TrikQuiz.Source(self.source))
        reply = TrikQuiz.Reply({'studio_save': []})

        with self.assertRaises(FormatError):
            quiz.clean_reply(reply, None)

    def test_clean_reply(self):
        quiz = TrikQuiz(TrikQuiz.Source(self.source))
        reply = TrikQuiz.Reply({'studio_save': [self.studio_save]})

        clean_reply = quiz.clean_reply(reply, {})

        self.assertEqual(clean_reply._original, self.studio_save)

    def test_check(self):
        quiz = TrikQuiz(TrikQuiz.Source(self.source))

        self.assertTrue(quiz.check(self.studio_save, None))

    def test_check_incorrect_studio_save(self):
        quiz = TrikQuiz(TrikQuiz.Source(self.source))
        incorrect_studio_save = self.load_attachment('hello-world.zip')

        score, hint = quiz.check(incorrect_studio_save, None)

        self.assertFalse(score)
        self.assertEqual(hint, "TRIK Studio save file is incorrect or corrupted")

    def test_check_with_fields(self):
        self.source['fields_archive'] = [self.load_attachment('hello-world.zip')]
        quiz = TrikQuiz(TrikQuiz.Source(self.source))

        self.assertTrue(quiz.check(self.studio_save, None))

    def test_check_fail_circle(self):
        quiz = TrikQuiz(TrikQuiz.Source(self.source))
        reply = self.load_attachment('circle-fail.qrs')

        score, hint = quiz.check(reply, None)

        self.assertFalse(score)
        self.assertEqual(hint, "робот едет не по кругу заданного радиуса")

    def test_check_fail_image_control(self):
        quiz = TrikQuiz(TrikQuiz.Source(self.source))
        reply = self.load_attachment('image-control-fail.qrs')

        score, hint = quiz.check(reply, None)

        self.assertFalse(score)
        self.assertEqual(hint, "Программа работала слишком долго")

    def test_check_fail_move_forward(self):
        quiz = TrikQuiz(TrikQuiz.Source(self.source))
        reply = self.load_attachment('move-forward-fail.qrs')

        score, hint = quiz.check(reply, None)

        self.assertFalse(score)
        self.assertEqual(hint, "Программа отработала, но задание не выполнено.")

    def test_check_fail_with_fields(self):
        self.source['fields_archive'] = [self.load_attachment('hello-world-fail.zip')]
        quiz = TrikQuiz(TrikQuiz.Source(self.source))

        score, hint = quiz.check(self.studio_save, None)

        self.assertFalse(score)
        self.assertEqual(hint, "Робот так и не поехал в первую секунду")
