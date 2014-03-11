from importlib import import_module
import os

from . import schema
from .exceptions import UnknownPluginError


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


def quiz_wrapper_factory(quiz_class):
    schemas = quiz_class.Schemas

    class QuizWrapper(object):
        wrapped_class = quiz_class

        def __init__(self, source, supplementary=None):
            source = schema.build(schemas.source, source)
            if supplementary is None:
                self.quiz = quiz_class(source)
            else:
                self.quiz = quiz_class(source, supplementary)

        def clean_reply(self, reply, dataset=None):
            reply = schema.build(schemas.reply, reply)
            if dataset:
                dataset = schema.build(schemas.dataset, dataset)
            return self.quiz.clean_reply(reply, dataset)

        def check(self, reply, clue=None):
            return self.quiz.check(reply, clue)

        def generate(self):
            ret = self.quiz.generate()
            if ret:
                dataset, clue = ret
                schema.build(schemas.dataset, dataset)
            return ret

        def extra(self):
            return self.quiz.extra()

        def async_init(self):
            return self.quiz.async_init()

        def set_supplementary(self, supplementary):
            self.quiz.set_supplementary(supplementary)

    return QuizWrapper


def load_by_name(name):
    """Dynamically loads plugin class by name"""

    base = os.path.join(os.path.dirname(__file__), 'quizzes')
    for directory in os.listdir(base):
        if os.path.isdir(os.path.join(base, directory)):
            package_name = os.path.basename(directory)
            qualified_name = 'stepic_plugins.quizzes.' + package_name
            module = import_module(qualified_name)
            for att in dir(module):
                val = getattr(module, att)
                if isinstance(val, type) and issubclass(val, BaseQuiz):
                    # noinspection PyUnresolvedReferences
                    if val.name == name:
                        return quiz_wrapper_factory(val)

    raise UnknownPluginError(name)
