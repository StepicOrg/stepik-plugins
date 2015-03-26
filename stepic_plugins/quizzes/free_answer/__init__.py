import bleach

from stepic_plugins.base import BaseQuiz


class FreeAnswerQuiz(BaseQuiz):
    name = 'free-answer'

    class Schemas:
        source = {'manual_scoring': bool}
        reply = {'text': str}

    def __init__(self, source):
        super().__init__(source)
        self.manual_scoring = source.manual_scoring

    def clean_reply(self, reply, dataset):
        return reply.text

    def check(self, reply, clue):
        if not bleach.clean(reply, tags=['img'], strip=True).strip():
            return False, 'Empty reply. Please write some text.'
        return True
