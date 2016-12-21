from voluptuous import ALLOW_EXTRA, Schema

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError


class PycharmQuiz(BaseQuiz):
    name = 'pycharm'

    class Schemas:
        source = Schema(dict, extra=ALLOW_EXTRA)
        reply = {
            'score': str,
            'solution': [{'name': str, 'text': str}],
        }

    def async_init(self):
        return {'options': self.source}

    def clean_reply(self, reply, dataset):
        try:
            float(reply.score)
        except ValueError:
            raise FormatError("score string is not convertible to float")
        return reply

    def check(self, reply, clue):
        return float(reply['score'])
