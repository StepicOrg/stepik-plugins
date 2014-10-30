from stepic_plugins.base import BaseQuiz
from stepic_plugins.quizzes.executable_base import JailedCodeFailed, run


class GeneralQuiz(BaseQuiz):
    name = 'general'

    class Schemas:
        source = {
            'code': str
        }
        reply = {
            'file': str
        }

    def __init__(self, source):
        super().__init__(source)
        self.code = source.code

    def clean_reply(self, reply, dataset):
        return reply.file.strip()

    def check(self, reply, clue, throw=False):
        try:
            score, hint = self.run_edyrun('score', data=(reply, clue))
            return score, hint
        except (JailedCodeFailed, ValueError, TypeError) as e:
            if throw:
                raise JailedCodeFailed(str(e))
            return False

    def run_edyrun(self, command, data=None, **kwargs):
        files = []
        return run(command, self.code, data, files, **kwargs)
