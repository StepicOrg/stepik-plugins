from . import schema


class BaseQuiz(object):
    name = None

    class Schemas:
        source = None
        reply = None
        dataset = None

    def __init__(self, source):
        pass

    def clean_reply(self, reply, dataset):
        raise NotImplementedError

    def check(self, reply, clue):
        raise NotImplementedError

    def generate(self):
        return None

    def extra(self):
        return None

    def get_supplementary(self):
        return None

    def set_supplementary(self, supplementary):
        pass


def quiz_wrapper_factory(quiz_class):
    schemas = quiz_class.Schemas

    class QuizWrapper(object):

        def __init__(self, source):
            source = schema.build(schemas.source, source)
            self.quiz = quiz_class(source)

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

        def get_supplementary(self):
            return self.quiz.get_supplementary()

        def set_supplementary(self, supplementary):
            self.quiz.set_supplementary(supplementary)

    return QuizWrapper
