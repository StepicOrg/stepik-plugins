import itertools
import random

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError


class TableQuiz(BaseQuiz):
    name = 'table'

    class Schemas:
        source = {
            'description': str,
            'columns': [{'name': str}],
            'rows': [{
                'name': str,
                'columns': [{'choice': bool}]
            }],
            'options': {
                'is_checkbox': bool,
                'is_randomize_rows': bool,
                'is_randomize_columns': bool,
                'sample_size': int
            },
            'is_always_correct': bool
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
        self.is_always_correct = source.is_always_correct
        for row in self.rows:
            possible_answer = 0
            for cell in row.columns:
                possible_answer += cell.choice

            if possible_answer > 1 and not self.options.is_checkbox:
                raise FormatError(
                    "There cannot be multiple right answers in this mode")
            if possible_answer == 0 and not self.options.is_checkbox \
                    and not self.is_always_correct:
                raise FormatError("There are no right answers for '{0}'"
                                  .format(row.name))

        for i, j in itertools.combinations(range(len(self.rows)), 2):
            if self.rows[i].name == self.rows[j].name:
                raise FormatError("There are two rows with the same name "
                                  "'{0}'".format(self.rows[i].name))

        for i, j in itertools.combinations(range(len(self.columns)), 2):
            if self.columns[i].name == self.columns[j].name:
                raise FormatError("There are two columns with the same name "
                                  "'{0}'".format(self.columns[i].name))

    def generate(self):
        def permutate(array, permutation):
            return [array[i] for i in permutation]

        row_perm = list(range(len(self.rows)))
        if self.options.is_randomize_rows:
            random.shuffle(row_perm)
        column_perm = list(range(len(self.columns)))
        if self.options.is_randomize_columns:
            random.shuffle(column_perm)

        rows = [row.name for row in permutate(self.rows, row_perm)]
        columns = [col.name for col in permutate(self.columns, column_perm)]
        dataset = {'description': self.description,
                   'rows': rows,
                   'columns': columns,
                   'is_checkbox': self.options.is_checkbox}
        clue = [[col.choice for col in permutate(row.columns, column_perm)]
                for row in permutate(self.rows, row_perm)]
        return dataset, clue

    def clean_reply(self, reply, dataset):
        return reply.choices

    def check(self, reply, clue):
        if self.is_always_correct:
            return True
        reply_plain = [[column['answer'] for column in row['columns']]
                       for row in reply]
        return reply_plain == clue
