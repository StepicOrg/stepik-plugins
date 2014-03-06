import decimal

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError


MAX_DIGITS = 50
DECIMAL_PLACES = 25


class NumberQuiz(BaseQuiz):
    name = 'number'

    class Schemas:
        source = {
            'answer': str,
            'max_error': str,
        }
        reply = {
            'number': str
        }

    def __init__(self, source):
        super().__init__(source)
        self.answer = parse_decimal(source.answer, 'answer')
        self.max_error = parse_decimal(source.max_error, 'max_error')
        if self.max_error < 0:
            raise FormatError("`max_error` should be non-negative")

    def clean_reply(self, reply, dataset):
        #TODO: add frontend validation and parse reply here ...
        return reply.number

    def check(self, reply, clue):
        with decimal.localcontext() as ctx:
            ctx.prec = MAX_DIGITS
            normalized = reply.replace(',', '.').replace(' ', '')
            try:
                # ... instead of here
                decimal_reply = parse_decimal(normalized, 'dummy')
            except FormatError:
                score = False
                hint = 'Only numbers, please'
            else:
                score = abs(decimal_reply - self.answer) <= self.max_error
                hint = ''

        return score, hint


def parse_decimal(s, filed_name):
    try:
        return decimal.Decimal(s)
    except decimal.DecimalException:
        raise FormatError("Field `{}` should be a number".format(filed_name))
