import random
from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError


class TableQuiz(BaseQuiz):
    name = 'table'

    class Schemas:
        source = {
            'description': str,
            'columns': [str],
            'rows': [{
                'name': str,
                'columns': [{'choice': bool}]
            }],
            'options': {
                'is_checkbox': bool,
                'is_randomize_rows': bool,
                'is_randomize_columns': bool,
                'sample_size': int
            }
        }
        reply = {
            'choices': [{
                'name_row': str,
                'columns': [{'name': str, 'answer': bool}]
            }]
        }
        dataset = {
            'description': str,
            'rows': [str],
            'columns': [str],
            'is_checkbox': bool
        }

    def __init__(self, source):
        super().__init__(source)
        self.columns = source.columns
        self.rows = source.rows
        self.description = source.description
        self.options = source.options
        for row in self.rows:
            possible_answer = 0
            for cell in row.columns:
                possible_answer += cell.choice

            if possible_answer > 1 and not self.options.is_checkbox:
                raise FormatError("Can't be multiple right answer in this mode")
            if possible_answer == 0:
                raise FormatError("There are no right answers")

        for i in range(len(self.rows)):
            for j in range(i + 1, len(self.rows)):
                if self.rows[i].name == self.rows[j].name:
                    raise FormatError("There are two equivalent rows: {} and {}".format(i + 1, j + 1))
        
        for i in range(len(self.columns)):
            for j in range(i + 1, len(self.columns)):
                if self.columns[i] == self.columns[j]:
                    raise FormatError("There are two equivalent columns: {} and {}".format(i + 1, j + 1))


    def generate(self):
        def permutate(array, permutation):
            return [array[i] for i in permutation]

        permutate_row = list(range(len(self.rows)))
        if self.options.is_randomize_rows:
            random.shuffle(permutate_row)

        permutate_column = list(range(len(self.columns)))
        if self.options.is_randomize_columns:
            random.shuffle(permutate_column)

        dataset = {'description': self.description,
                   'rows': [row.name for row in permutate(self.rows, permutate_row)],
                   'columns': permutate(self.columns, permutate_column),
                   'is_checkbox': self.options.is_checkbox}

        clue = [[column.choice for column in permutate(row.columns, permutate_column)]
                    for row in permutate(self.rows, permutate_row)]
        return dataset, clue

    def clean_reply(self, reply, dataset):
        return reply.choices

    def check(self, reply, clue):
        reply_plain = [[column['answer'] for column in row['columns']] for row in reply]
        return reply_plain == clue
