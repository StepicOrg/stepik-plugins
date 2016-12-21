import random
import decimal
import re

import textwrap

from codejail import safe_exec

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError
from stepic_plugins.utils import parse_decimal


MAX_DIGITS = 50
PRECISION = 5


class RandomTasksQuiz(BaseQuiz):
    name = 'random-tasks'

    class Schemas:
        source = {
            'task': str,
            'solve': str,
            'max_error': str,
            'ranges': [{
                'variable': str,
                'num_from': str,
                'num_to': str,
                'num_step': str
            }]
        }
        reply = {
            'answer': str
        }
        dataset = {
            'task': str
        }

    def __init__(self, source):
        super().__init__(source)
        self.task = source.task
        self.solve = source.solve
        self.max_error = float(parse_decimal(source.max_error, 'max_error'))
        self.ranges = source.ranges
        self.variables = []

    def clean_reply(self, reply, dataset):
        return reply.answer

    def check(self, reply, clue):
        with decimal.localcontext() as ctx:
            ctx.prec = MAX_DIGITS
            try:
                float_reply = float(parse_decimal(reply, 'dummy'))
            except FormatError:
                score = False
                hint = 'Only numbers, please'
            else:
                score = abs(float_reply - clue) <= self.max_error
                hint = ''

        return score, hint

    def _random_context(self):
        for gr in re.findall(r'\{:([\w\|]*?)\}', self.task):  # find pattern groups {: }
            res = re.findall(r'\w+', gr)  # find all variables in group
            self.task = re.sub('\{:%s\}' % re.escape(gr),  # replace group by one variable
                               random.choice(res),
                               self.task, 1)
        for gr in re.finditer(r'\{:(\w+):([\w\|]*?)\}', self.task):  # find groups {:var: }
            if gr.group(2) is not '':
                res = re.findall(r'\w+', gr.group(2))
                self.task = re.sub('\{:%s:.*?\}' % gr.group(1),  # replace group by variable
                                   random.choice(res),
                                   self.task)

    def _randrange_float(self, start, stop, step):
        return random.randint(0, int((stop - start) / step)) * step + start

    def _random_variables(self):
        for var in self.ranges:
            try:
                start = float(var.num_from)
                stop = float(var.num_to)
                step = float(var.num_step)
            except ValueError:
                raise FormatError("Error in ranges.")
            random_value = round(self._randrange_float(start, stop, step), PRECISION)
            self.variables.append({'name': var.variable, 'value': str(random_value)})

        self.task = ' ' + self.task + ' '  # spaces helps regexp work fine
        for variable in self.variables:
            self.task = re.sub(r'(?P<l>\W)\\%s(?P<r>\W)' % variable['name'],  # variable between separator symbols
                               r'\g<l>%s\g<r>' % variable['value'],  # replace with saving separator symbols
                               self.task)
        self.task = self.task.strip()

    def generate(self):
        self._random_context()
        self._random_variables()
        dataset = {'task': self.task}

        global_dict = {'solve': self.solve,
                       'variables': self.variables,
                       'clue': ''
                       }
        code = textwrap.dedent("""
        from sympy import sympify
        import re

        str_exp = ' ' + str(solve) + ' '
        for variable in variables:
            replace_value = variable['value']
            if float(replace_value) < 0:
                replace_value = '({})'.format(replace_value)
            str_exp = re.sub(r'(?P<left>\W)%s(?P<right>\W)' % variable['name'],
                             r'\g<left>%s\g<right>' % replace_value,
                             str_exp)
        expr = sympify(str(str_exp))
        clue = str(expr.evalf())
        """)
        try:
            safe_exec.safe_exec(code, global_dict)
        except safe_exec.SafeExecException:
            return False, 'Cannot generate check function. Perhaps solve expression is wrong.'

        try:
            clue = float(parse_decimal(str(global_dict['clue']), 'dummy'))
        except FormatError:
            raise FormatError("Error in solve expression. Perhaps one or more variable is not declared")

        return dataset, clue
