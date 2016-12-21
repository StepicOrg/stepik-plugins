import pytest
import unittest

from unittest.mock import patch

from stepic_plugins import settings
from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError, PluginError
from stepic_plugins.schema import build
from .utils import override_settings


class SchemaBuildTest(unittest.TestCase):
    def test_positive_int_from_string(self):
        obj = build({'number': int}, {'number': "42"})
        self.assertEqual(obj.number, 42)

    def test_negative_int_from_string(self):
        obj = build({'number': int}, {'number': "-42 "})
        self.assertEqual(obj.number, -42)


def test_override_settings():
    debug_orig_value = settings.DEBUG
    debug_new_value = not settings.DEBUG
    assert not hasattr(settings, 'NEW_SETTING')

    @override_settings(DEBUG=debug_new_value, NEW_SETTINGS='new_value')
    def assert_override():
        assert settings.DEBUG is debug_new_value
        assert settings.NEW_SETTINGS == 'new_value'

    assert_override()

    assert settings.DEBUG is debug_orig_value
    assert not hasattr(settings, 'NEW_SETTING')


class TestRPCAPI(object):
    def test_ping(self, quizapi):
        assert quizapi.ping("Hello there!") == "Hello there!"

    def test_format_error_in_plugin(self, quizapi, free_answer_ctxt):
        with patch('stepic_plugins.quizzes.free_answer.FreeAnswerQuiz.generate',
                   return_value=("not a dict", None)):
            with pytest.raises(FormatError) as excinfo:
                quizapi.generate(free_answer_ctxt)

            assert "Expected dict" in excinfo.value.args[0]

    def test_plugin_error_in_plugin(self, quizapi, free_answer_ctxt):
        with patch('stepic_plugins.quizzes.free_answer.FreeAnswerQuiz.generate',
                   side_effect=PluginError("Generate failed")):
            with pytest.raises(PluginError) as excinfo:
                quizapi.generate(free_answer_ctxt)

            assert excinfo.value.args[0] == "Generate failed"

    def test_unexpected_exception_in_plugin(self, quizapi, free_answer_ctxt):
        with patch('stepic_plugins.quizzes.free_answer.FreeAnswerQuiz.generate',
                   side_effect=TimeoutError("Something timed out")):
            with pytest.raises(PluginError) as excinfo:
                quizapi.generate(free_answer_ctxt)

        exc_msg = excinfo.value.args[0]
        assert "RPC method failed badly" in exc_msg
        assert "TimeoutError" in exc_msg
        assert "Something timed out" in exc_msg


class TestQuizWrapper(object):
    def setup_method(self, method):
        self.reply = {
            'text': "42",
            'attachments': [],
        }

    def test_clean_reply_no_modification_by_default(self, free_answer_quiz):
        # noinspection PyUnresolvedReferences
        with patch.object(free_answer_quiz.wrapped_class, 'clean_reply', BaseQuiz.clean_reply):
            assert free_answer_quiz.clean_reply(self.reply)._original is self.reply

    def test_clean_reply_invalid_return_value(self, free_answer_quiz):
        def clean_reply(self_, reply, clue):
            reply._original['text'] = 42
            return reply._original

        # noinspection PyUnresolvedReferences
        with patch.object(free_answer_quiz.wrapped_class, 'clean_reply', clean_reply):
            with pytest.raises(FormatError):
                free_answer_quiz.clean_reply(self.reply)

    @override_settings(OLD_STYLE_CLEAN_REPLY_QUIZZES=['free-answer'])
    def test_old_style_clean_reply_returns_reply_by_default(self, free_answer_quiz):
        # noinspection PyUnresolvedReferences
        with patch.object(free_answer_quiz.wrapped_class, 'clean_reply', BaseQuiz.clean_reply):
            assert free_answer_quiz.clean_reply(self.reply)._original is self.reply

    @override_settings(OLD_STYLE_CLEAN_REPLY_QUIZZES=['free-answer'])
    def test_old_style_clean_reply_arbitrary_return_value(self, free_answer_quiz):
        cleaned_reply = {
            'text': 42,
        }

        def clean_reply(self_, reply, clue):
            return cleaned_reply

        # noinspection PyUnresolvedReferences
        with patch.object(free_answer_quiz.wrapped_class, 'clean_reply', clean_reply):
            assert free_answer_quiz.clean_reply(self.reply) == cleaned_reply

    def test_check_success(self, free_answer_quiz):
        with patch.object(free_answer_quiz.wrapped_class, 'check', return_value=(1, "")):
            free_answer_quiz.check({})

    def test_check_dict_feedback(self, free_answer_quiz):
        with patch.object(free_answer_quiz.wrapped_class, 'check',
                          return_value=(1, {'foo': 'bar'})):
            free_answer_quiz.check({})

    def test_check_invalid_feedback(self, free_answer_quiz):
        for feedback in [42, None, b'feedback', (), {'message': 42}]:
            with patch.object(free_answer_quiz.wrapped_class, 'check',
                              return_value=(1, feedback)):
                with pytest.raises(AssertionError):
                    free_answer_quiz.check({})
