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
            'is_checkbox': bool,
            'name_rows': str
        }
        reply = {
            'choices': [[bool]]
        }
        dataset = {
            'name_rows': str,
            'rows': [str],
            'columns': [str],
            'is_checkbox': bool
        }

    def __init__(self, source):
        super().__init__(source)
        self.name_columns = source.name_columns
        self.rows = source.rows
        self.name_rows = source.name_rows
        self.is_checkbox = source.is_checkbox

    def generate(self):
        dataset = {'name_rows': self.name_rows,
                   'rows': [row.name for row in self.rows],
                   'columns': self.name_columns,
                   'is_checkbox': self.is_checkbox}
        
        return dataset, [row.columns for row in self.rows]

    def clean_reply(self, reply, dataset):
        return reply.choices

    def check(self, reply, clue):
        return True