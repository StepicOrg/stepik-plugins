import textwrap

from codejail import safe_exec

from stepic_plugins.base import BaseQuiz


class MathQuiz(BaseQuiz):
    name = 'math'

    class Schemas:
        source = {'answer': str}
        reply = {'formula': str}

    def __init__(self, source):
        super().__init__(source)
        self.answer = source.answer

    def clean_reply(self, reply, dataset):
        return reply.formula.strip()

    def check(self, reply, clue):
        global_dict = {'matched': False,
                       'hint': '',
                       'answer': self.answer,
                       'reply': reply}
        code = textwrap.dedent("""
        from sympy.parsing.sympy_parser import parse_expr
        from sympy.utilities.randtest import test_numerically
        from sympy import latex

        def compare(reply, answer):
            if (reply - answer).simplify() == 0:
                return True

            if reply.is_Number and answer.is_Number:
                return reply == answer

            n_tries = 3
            return all(test_numerically(reply, answer) for _ in range(n_tries))

        def to_expr(s):
            return parse_expr(s.replace("^", "**"))


        answer = to_expr(answer)
        try:
            reply = to_expr(reply)
        except Exception:
            matched = False
            hint = 'failed to parse expression'
        else:
            hint = "understood answer as ${}$".format(latex(reply))
            if not answer.free_symbols >= reply.free_symbols:
                matched = False
            else:
                matched = compare(reply, answer)
        """)
        try:
            safe_exec.safe_exec(code, global_dict)
        except safe_exec.SafeExecException:
            return False

        score = bool(global_dict['matched'])
        hint = ''
        if score == 0:
            hint = str(global_dict['hint'])
        return score, hint
