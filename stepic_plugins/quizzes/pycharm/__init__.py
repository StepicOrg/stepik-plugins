from stepic_plugins.base import BaseQuiz


class PycharmQuiz(BaseQuiz):
    name = 'pycharm'

    class Schemas:
        source = {
            'files': [{'name': str,
                       'text': str,
                       'placeholders': [{
                                           'line': int,
                                           'start': int,
                                           'length': int,
                                           'hint': str,
                                           'possible_answer': str
                                       }]
                      }],
            'test': str,
        }
        reply = {
            'score': str
        }

    def __init__(self, source):
        super().__init__(source)
        self.files = source.files
        self.test = source.test

    def async_init(self):
        return {
            'options': {
                # 'files': self.files,
                'test': self.test
            }
        }

    def clean_reply(self, reply, dataset):
        return float(reply.score)

    def check(self, reply, clue, throw=False):
        return reply, ''

