from stepic_plugins.base import BaseQuiz


class UnityQuiz(BaseQuiz):
    name = 'unity'

    class Schemas:
        reply = {'score': str}
        source = {'file': str}

    def __init__(self, source):
        super().__init__(source)
        self.file = "abra_cadabra"

    def clean_reply(self, reply, dataset):
        return reply.score

    def check(self, reply, clue):
        if reply:
            return min(abs(float(reply)), 1), ''
        return False



