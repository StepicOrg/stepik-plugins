from stepic_plugins.base import BaseQuiz


class ManualScoreQuiz(BaseQuiz):
    name = 'manual-score'

    class Schemas:
        source = {}
        reply = {}

    def check(self, reply, clue):
        return False, "This step is scored manually by instructor(s)"
