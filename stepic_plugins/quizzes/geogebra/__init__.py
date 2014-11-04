from stepic_plugins.base import BaseQuiz

class GeogebraQuiz(BaseQuiz):
    name = 'geogebra'

    class Schemas:
        source = {'ggbbase64': str}
        reply = {'answer': bool}
        dataset = {'ggbbase64': str}

    def __init__(self, source):
        super().__init__(source)
        self.ggbbase64 = source.ggbbase64

    def clean_reply(self, reply, dataset):
        return reply.answer

    def check(self, reply, clue):
        return reply

    def generate(self):
        return {'ggbbase64': self.ggbbase64}, False
