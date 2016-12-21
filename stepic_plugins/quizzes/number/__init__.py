import decimal

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError
from stepic_plugins.utils import parse_decimal


MAX_DIGITS = 50
DECIMAL_PLACES = 25


class NumberQuiz(BaseQuiz):
    name = 'number'

    class Schemas:
        source = {
            'options': [{
                'answer': str,
                'max_error': str,
            }]
        }
        reply = {
            'number': str
        }

    def __init__(self, source):
        super().__init__(source)
        if not source.options:
            raise FormatError("At least one answer option should be provided")
        self.options = [{'answer': parse_decimal(o.answer, 'answer'),
                         'max_error': parse_decimal(o.max_error, 'max_error')}
                        for o in source.options]
        if any(o['max_error'] < 0 for o in self.options):
            raise FormatError("`max_error` should be non-negative")

    def clean_reply(self, reply, dataset):
        #TODO: add frontend validation and parse reply here ...
        return reply.number

    def check(self, reply, clue):
        with decimal.localcontext() as ctx:
            ctx.prec = MAX_DIGITS
            try:
                # ... instead of here
                decimal_reply = parse_decimal(reply, 'dummy')
            except FormatError:
                score = False
                hint = 'Only numbers, please'
            else:
                score = any(abs(decimal_reply - o['answer']) <= o['max_error']
                            for o in self.options)
                hint = ''

        return score, hint
