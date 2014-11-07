import re
import textwrap

from codejail import safe_exec

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError
from stepic_plugins.quizzes.executable_base import JailedCodeFailed, run


class StringQuiz(BaseQuiz):
    name = 'string'

    class Schemas:
        source = {
            'pattern': str,
            'case_sensitive': bool,
            'use_re': bool,
            'match_substring': bool,
            'code': str  # TODO: make solve() optional
        }
        reply = {
            'text': str
        }

    def __init__(self, source):
        super().__init__(source)
        self.pattern = source.pattern
        self.case_sensitive = source.case_sensitive
        self.use_re = source.use_re
        self.match_substring = source.match_substring
        self.code = source.code
        self.use_code = bool(source.code.strip())
        if self.use_re:
            try:
                r = re.compile(self.pattern)
            # catching Exception and not re.error because compile can throw
            # not only re.error (ex pattern = '()'*100)
            except Exception:
                raise FormatError('Malformed regular expression')

            if r.match(''):
                raise FormatError('Pattern matches empty sting')

    def async_init(self):
        if self.use_code:
            try:
                reply = self.run_edyrun('solve', data={})
                score, hint = self.check(reply, '')
            except JailedCodeFailed as e:
                raise FormatError(str(e))
            if score != 1:
                hint = '\nHint: {}'.format(hint) if hint else ''
                raise FormatError('score of answer is {score} instead of 1.{hint}'.format(
                    score=score,
                    hint=hint))
        return None

    def clean_reply(self, reply, dataset):
        return reply.text

    def check(self, reply, clue):
        text = reply.strip()
        if self.use_code:
            return self.check_using_code(text, clue)
        elif self.use_re:
            return self.check_re(text)
        else:
            return self.check_simple(text)

    def check_using_code(self, text, clue, throw=False):
        try:
            score, hint = self.run_edyrun('score', data=(text, clue))
            return score, hint
        except (JailedCodeFailed, ValueError, TypeError) as e:
            if throw:
                raise JailedCodeFailed(str(e))
            return False

    def check_re(self, text):
        """Run re.match in sandbox, because re.match('(x+x+)+y', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        is to resource consuming.

        May be should use https://code.google.com/p/re2/ here.
        """
        if self.match_substring:
            pattern = "{0}({1}){0}".format(r"(.|\n)*", self.pattern)
        else:
            pattern = self.pattern
        global_dict = {'matched': False,
                       'pattern': pattern,
                       'text': text}
        code = textwrap.dedent("""
                import re
                match = re.match(pattern, text, {flags})
                matched = match.group() == text if match else False
                """).format(flags='' if self.case_sensitive else 'flags=re.I')
        try:
            safe_exec.safe_exec(code, global_dict)
        except safe_exec.SafeExecException:
            score = False
        else:
            score = bool(global_dict['matched'])
        return score

    def check_simple(self, text):
        if self.case_sensitive:
            pattern = self.pattern
        else:
            text = text.lower()
            pattern = self.pattern.lower()

        if self.match_substring:
            score = pattern in text
        else:
            score = pattern == text
        return score

    def run_edyrun(self, command, data=None, **kwargs):
        files = []
        return run(command, self.code, data, files, **kwargs)
