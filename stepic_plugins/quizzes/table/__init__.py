from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError


class TableQuiz(BaseQuiz):
    name = 'table'

    class Schemas:
        source = {
            'name_columns': [str],
            'rows': [{
                'name': str,
                'columns': [{'name': str, 'answer': bool}]
            }],
            'is_multiple_choice': bool
        }
        reply = {
            'choices': [[bool]]
        }
        dataset = {
            'name_rows': [str],
            'name_columns': [str],
        }

    def __init__(self, source):
        super().__init__(source)
        self.name_columns = source.name_columns
        self.rows = source.rows
        self.is_multiple_choice = source.is_multiple_choice

    def generate(self):
        dataset = {'name_rows': [row.name for row in self.rows],
                   'name_columns': self.name_columns}

        return dataset, [row.columns for row in self.rows]

    def clean_reply(self, reply, dataset):
        return reply.choices

    def check(self, reply, clue):
        return True

