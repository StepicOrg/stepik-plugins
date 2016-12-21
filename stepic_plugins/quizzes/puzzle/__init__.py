from stepic_plugins.base import BaseQuiz


class PuzzleQuiz(BaseQuiz):
    name = 'puzzle'

    class Schemas:
        source = {
            'image_src': str,
            'level': int,
        }
        dataset = {
            'image_src': str,
            'level': int,
        }
        reply = {
            'solved': bool,
        }

    def __init__(self, source):
        super().__init__(source)
        self.source = source

    def generate(self):
        dataset = {
            'image_src': self.source.image_src,
            'level': self.source.level,
        }
        return dataset, None

    def check(self, reply, clue):
        return reply['solved']
