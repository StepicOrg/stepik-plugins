from importlib import import_module
import os

from . import schema
from .exceptions import UnknownPluginError


QUIZZES_DIR = os.path.join(os.path.dirname(__file__), 'quizzes')


class BaseQuiz(object):
    name = None

    class Schemas:
        source = None
        reply = None
        dataset = None

    def __init__(self, source):
        assert self.name, '`name` attribute should be overridden in subclass'

    def clean_reply(self, reply, dataset):
        return reply

    def check(self, reply, clue):
        raise NotImplementedError

    def generate(self):
        return None

    def async_init(self):
        return None

    def cleanup(self, clue):
        pass

    @classmethod
    def Source(cls, source):
        return schema.build(cls.Schemas.source, source)

    @classmethod
    def Reply(cls, reply):
        return schema.build(cls.Schemas.reply, reply)

    @classmethod
    def Dataset(cls, dataset):
        assert cls.Schemas.dataset is not None
        return schema.build(cls.Schemas.dataset, dataset)


def quiz_wrapper_factory(quiz_class):

    class QuizWrapper(object):
        wrapped_class = quiz_class

        def __init__(self, source, supplementary=None):
            source = quiz_class.Source(source)
            if supplementary is None:
                self.quiz = quiz_class(source)
            else:
                self.quiz = quiz_class(source, supplementary)

        def clean_reply(self, reply, dataset=None):
            reply = quiz_class.Reply(reply)
            if dataset:
                dataset = quiz_class.Dataset(dataset)
            return self.quiz.clean_reply(reply, dataset)

        def check(self, reply, clue=None):
            ret = self.quiz.check(reply, clue)
            if isinstance(ret, bool):
                score = ret
                hint = ''
            else:
                score, hint = ret
            assert 0 <= score <= 1, 'Score should be True or False instead of {}'.format(score)
            assert isinstance(hint, str), 'hint should be a string instead of {}'.format(hint)
            return score, hint

        def generate(self):
            ret = self.quiz.generate()
            if ret:
                dataset, clue = ret
                quiz_class.Dataset(dataset)
            return ret

        def async_init(self):
            return self.quiz.async_init()

        def cleanup(self, clue=None):
            self.quiz.cleanup(clue)

    return QuizWrapper


# TODO: rewrite using mitsuhiko's PluginBase
def load_by_name(name):
    """Dynamically load plugin class by name."""

    package_name = name.replace('-', '_')
    qualified_name = 'stepic_plugins.quizzes.' + package_name
    try:
        module = import_module(qualified_name)
    except ImportError as e:
        raise UnknownPluginError("Failed to import {0} quiz: {1}"
                                 .format(name, e))

    for att in dir(module):
        val = getattr(module, att)
        if isinstance(val, type) and issubclass(val, BaseQuiz):
            # noinspection PyUnresolvedReferences
            if val.name == name:
                return quiz_wrapper_factory(val)

    raise UnknownPluginError(name)
