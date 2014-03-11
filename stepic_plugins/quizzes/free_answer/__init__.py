from stepic_plugins.base import BaseQuiz


class FreeAnswerQuiz(BaseQuiz):
    name = 'free-answer'

    class Schemas:
        source = {'manual_scoring': bool}
        reply = {'text': str}

    def __init__(self, source):
        super().__init__(source)
        self.manual_scoring = source.manual_scoring

    def check(self, reply, clue):
        if self.manual_scoring:
            return None  # will be scored manually later
        return 1, ''

