import bleach

from stepic_plugins.base import BaseQuiz
from stepic_plugins.schema import attachment


class FreeAnswerQuiz(BaseQuiz):
    name = 'free-answer'

    class Schemas:
        source = {'manual_scoring': bool}
        reply = {
            'text': str,
            'attachments': [attachment]
        }

    def __init__(self, source):
        super().__init__(source)
        self.manual_scoring = source.manual_scoring

    def check(self, reply, clue):
        if not bleach.clean(reply['text'], tags=['img'], strip=True).strip() and not reply['attachments']:
            return False, 'Empty reply. Please write some text.'
        return True
