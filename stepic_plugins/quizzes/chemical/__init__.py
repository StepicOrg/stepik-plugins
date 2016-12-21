from chem.chemcalc import chemical_equations_equal, compare_chemical_expression, split_on_arrow
from pyparsing import ParseException

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError


RIGHTWARDS_ARROW = '->'
LEFT_RIGHT_ARROW = '<->'


class ChemicalQuiz(BaseQuiz):
    name = 'chemical'

    class Schemas:
        source = {
            'expression': str,
            'template': [str],  # allowed values: 'normal', 'sub', 'sup', 'subsup'
        }
        dataset = {
            'template': [str]
        }
        reply = {
            'slots': [{'normal': str, 'sub': str, 'sup': str}],
        }

    def __init__(self, source):
        super().__init__(source)
        self.is_equation = False
        left_expr, arrow, right_expr = split_on_arrow(self.source.expression)
        if arrow:
            self.is_equation = True
        if not self._is_valid_expression(self.source.expression, self.is_equation):
            raise FormatError("Chemical expression is invalid")
        if not self._is_valid_template(self.source.template):
            raise FormatError("Chemical template is invalid")

    def _is_valid_expression(self, expression, is_equation=False):
        try:
            if is_equation:
                left_expr, arrow, right_expr = split_on_arrow(expression)
                compare_chemical_expression(left_expr, 'H')
                compare_chemical_expression(right_expr, 'H')
            else:
                compare_chemical_expression(expression, 'H')
        except ParseException:
            return False
        return True

    def _is_valid_template(self, template):
        return all(v in ['normal', 'sub', 'sup', 'subsup'] for v in template)

    def generate(self):
        dataset = {
            'template': self.source.template,
        }
        return dataset, None

    def clean_reply(self, reply, dataset):
        if len(reply.slots) != len(self.source.template):
            raise FormatError("Reply has a wrong number of slots")
        reply_expr_parts = []
        for slot, slot_template in zip(reply.slots, self.source.template):
            if slot_template == 'normal' and slot.normal:
                reply_expr_parts.append(slot.normal)
            elif slot_template in ['sub', 'subsup'] and slot.sub:
                reply_expr_parts.append(slot.sub)
            if slot_template in ['sup', 'subsup'] and slot.sup:
                reply_expr_parts.append('^' + slot.sup)
        reply_expression = ''.join(reply_expr_parts)
        reply_expression = (reply_expression
                            .replace('\u2192', RIGHTWARDS_ARROW)
                            .replace('\u2194', LEFT_RIGHT_ARROW))
        return reply_expression

    def check(self, reply, clue):
        if not self._is_valid_expression(reply, self.is_equation):
            # Reply is not a valid chemical formula/equation
            if self.is_equation:
                return False, "Ответ не является корректным химическим уравнением"
            return False, "Ответ не является корректной химической формулой"
        if self.is_equation:
            return chemical_equations_equal(self.source.expression, reply)
        return compare_chemical_expression(self.source.expression, reply)
