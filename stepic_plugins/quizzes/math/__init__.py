import re
import textwrap

from codejail import safe_exec

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError
from stepic_plugins.utils import parse_decimal


SYMPY_NOTATION_MAP = {
    'e': 'E',
    'tg': 'tan',
    'ctg': 'cot',
    'arccos': 'acos',
    'arcsin': 'asin',
    'arctg': 'atan',
    'atg': 'atan',
    'arcctg': 'acot',
    'actg': 'acot',
}


def is_math_quiz_enabled():
    code = textwrap.dedent("""
        import sympy
        """)
    try:
        safe_exec.safe_exec(code, {})
    except safe_exec.SafeExecException:
        return False
    return True


class MathQuiz(BaseQuiz):
    name = 'math'

    class Schemas:
        source = {
            'answer': str,
            'numerical_test': {
                'z_re_min': str,
                'z_re_max': str,
                'z_im_min': str,
                'z_im_max': str,
                'max_error': str,
                'integer_only': bool,
            }
        }
        reply = {'formula': str}

    LIMITS = {
        'TIME': 120,
    }

    def __init__(self, source):
        super().__init__(source)
        self.answer = source.answer
        if not self.answer.strip():
            raise FormatError('Correct answer should be non-empty')

        parse_float = lambda name: float(parse_decimal(getattr(source.numerical_test, name),
                                                       'numerical_test.{}'.format(name)))
        self.z_re_min = parse_float('z_re_min')
        self.z_re_max = parse_float('z_re_max')
        self.z_im_min = parse_float('z_im_min')
        self.z_im_max = parse_float('z_im_max')
        self.max_error = parse_float('max_error')
        self.integer_only = source.numerical_test.integer_only

        if self.z_re_min > self.z_re_max:
            raise FormatError('Incorrect Re z')
        if self.z_im_min > self.z_im_max:
            raise FormatError('Incorrect Im z')
        if self.max_error < 0:
            raise FormatError('Incorrect tolerated absolute error')

    def async_init(self):
        global_dict = {'answer': self.answer}
        code = textwrap.dedent("""
        from sympy.core.compatibility import exec_
        from sympy.parsing.sympy_parser import parse_expr

        exclude_symbols = ['N']

        def to_expr(s):
            global_dict = {}
            exec_('from sympy import *', global_dict)
            for symbol in exclude_symbols:
                global_dict.pop(symbol)
            return parse_expr(s.replace("^", "**"), global_dict=global_dict)

        answer = to_expr(answer)
        """)
        try:
            safe_exec.safe_exec(code, global_dict, limits=self.LIMITS)
        except safe_exec.SafeExecException:
            raise FormatError('Failed to parse correct answer.')

    def clean_reply(self, reply, dataset):
        return reply.formula.strip()

    def check(self, reply, clue):
        global_dict = {'matched': False,
                       'hint': '',
                       'answer': self.answer,
                       'z_re_min': self.z_re_min,
                       'z_re_max': self.z_re_max,
                       'z_im_min': self.z_im_min,
                       'z_im_max': self.z_im_max,
                       'max_error': self.max_error,
                       'integer_only': self.integer_only,
                       'reply': reply}

        # Below we use our own test_numerically function, because the original function
        # sympy.utilities.randtest.test_numerically has the following problems:
        # (1) it uses the relative error for comparison, that does not work well for very large values;
        # (2) it uses random real numbers, that does not work well some formulas.
        # see https://vyahhi.myjetbrains.com/youtrack/issue/EDY-4078 for more details.

        code = textwrap.dedent("""
        from random import randint, uniform

        from sympy import I, Tuple, Symbol, latex
        from sympy.core.compatibility import exec_
        from sympy.parsing.sympy_parser import parse_expr
        from sympy.utilities.randtest import comp

        exclude_symbols = ['N']

        def random_number():
            if integer_only:
                A, B = randint(z_re_min, z_re_max), randint(z_im_min, z_im_max)
            else:
                A, B = uniform(z_re_min, z_re_max), uniform(z_im_min, z_im_max)
            return A + I*B

        def test_numerically(f, g, z=None):
            f, g, z = Tuple(f, g, z)
            z = [z] if isinstance(z, Symbol) else (f.free_symbols | g.free_symbols)
            reps = list(zip(z, [random_number() for zi in z]))
            z1 = f.subs(reps).n()
            z2 = g.subs(reps).n()
            return comp(z1 - z2, 0, max_error)

        def compare(reply, answer):
            if answer.is_Relational:
                if not reply.is_Relational:
                    return False, "The answer must be an inequality"
                return compare_inequalities(reply, answer)
            if reply.is_Relational:
                return False, "The answer must not be an inequality"
            return compare_expressions(reply, answer)

        def compare_expressions(reply, answer):
            if (reply - answer).simplify() == 0:
                return True

            if reply.is_Number and answer.is_Number:
                return bool(abs(reply - answer) <= max_error)

            n_tries = 10
            return all(test_numerically(reply, answer) for _ in range(n_tries))

        def compare_inequalities(reply, answer):
            # Compare two single inequalities
            reversed_rel_op = {'<': '>', '<=': '>=', '>': '<', '>=': '<='}
            if reply.rel_op == answer.rel_op:
                return compare_expressions(reply.lhs - reply.rhs, answer.lhs - answer.rhs)
            elif reversed_rel_op.get(reply.rel_op) == answer.rel_op:
                return compare_expressions(reply.rhs - reply.lhs, answer.lhs - answer.rhs)
            return False

        def to_expr(s):
            global_dict = {}
            exec_('from sympy import *', global_dict)
            for symbol in exclude_symbols:
                global_dict.pop(symbol)
            return parse_expr(s.replace("^", "**"), global_dict=global_dict)


        answer = to_expr(answer)
        try:
            reply = to_expr(reply)
        except Exception:
            matched = False
            hint = 'Failed to parse expression.'
        else:
            hint = "Understood answer as ${}$.".format(latex(reply))
            if not answer.free_symbols >= reply.free_symbols:
                matched = False
            else:
                try:
                    matched = compare(reply, answer)
                except Exception:
                    matched = False
                    hint += '\\nCannot check answer. Perhaps syntax is wrong.'
                else:
                    if isinstance(matched, tuple):
                        matched, feedback = matched
                        hint += '\\n' + feedback
        """)
        try:
            safe_exec.safe_exec(code, global_dict, limits=self.LIMITS)
        except safe_exec.SafeExecException:
            return False, ('Timed out while checking the answer. '
                           'Perhaps it is wrong or too complex.')

        score = bool(global_dict['matched'])
        hint = ''
        if score == 0:
            hint = str(global_dict['hint'])
            notation_feedback = []
            for symbol, correct_symbol in SYMPY_NOTATION_MAP.items():
                if re.search(r'\b{symbol}\b'.format(symbol=symbol), reply):
                    notation_feedback.append('You wrote "{}", maybe you meant to write "{}".'
                                             .format(symbol, correct_symbol))
            if hint and notation_feedback:
                hint += '\n'
            hint += '\n'.join(notation_feedback)
        return score, hint
