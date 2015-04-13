import textwrap

from codejail import safe_exec

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError
from stepic_plugins.utils import parse_decimal


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
        from sympy.parsing.sympy_parser import parse_expr

        def to_expr(s):
            return parse_expr(s.replace("^", "**"))

        answer = to_expr(answer)
        """)
        try:
            safe_exec.safe_exec(code, global_dict)
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
        code = textwrap.dedent("""
        from random import randint, uniform

        from sympy import I, Tuple, Symbol
        from sympy.parsing.sympy_parser import parse_expr
        from sympy.utilities.randtest import comp
        from sympy import latex

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
            if (reply - answer).simplify() == 0:
                return True

            if reply.is_Number and answer.is_Number:
                return abs(reply - answer) <= max_error

            n_tries = 10
            return all(test_numerically(reply, answer) for _ in range(n_tries))

        def to_expr(s):
            return parse_expr(s.replace("^", "**"))


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
        """)
        try:
            safe_exec.safe_exec(code, global_dict)
        except safe_exec.SafeExecException:
            return False, 'Cannot check answer. Perhaps syntax is wrong.'

        score = bool(global_dict['matched'])
        hint = ''
        if score == 0:
            hint = str(global_dict['hint'])
        return score, hint
