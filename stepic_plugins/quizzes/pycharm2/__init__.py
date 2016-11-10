from stepic_plugins.base import BaseQuiz


class PycharmQuiz(BaseQuiz):
    name = 'pycharm2'

    class Schemas:
        source = {
            'title': str,
            'files': [{'name': str,
                       'text': str,
                       'placeholders':
                           [{
                               'offset': int,
                               'length': int,
                               "subtask_infos":
                                   [{
                                       "hints": [str],
                                       "possible_answer": str,
                                       "placeholder_text": str,
                                       "has_frame": bool,
                                       "need_insert_text": bool,
                                       "index": int
                                   }]
                           }]
                       }],
            'test': [{'name': str, 'text': str}],
            'format_version': int,
            'last_subtask_index': int
        }
        reply = {
            'score': str,
            'solution': [{'name': str, 'text': str}]
        }

    def __init__(self, source):
        super().__init__(source)
        self.title = source.title
        self.files = source.files
        self.test = source.test
        self.format_version = source.format_version
        self.last_subtask_index = source.last_subtask_index

    def async_init(self):
        return {
            'options': {
                'title': self.title,
                'files': self.files,
                'test': self.test,
                'format_version': self.format_version,
                'last_subtask_index': self.last_subtask_index
            }
        }

    def clean_reply(self, reply, dataset):
        return float(reply.score)

    def check(self, reply, clue, throw=False):
        return reply, ''
