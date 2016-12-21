import textwrap

from stepic_plugins.base import quiz_wrapper_factory
from stepic_plugins.quizzes.code import CodeQuiz


class BaseTestQuiz(object):
    quiz_class = quiz_wrapper_factory(CodeQuiz)
    default_source = {
        'code': textwrap.dedent("""
            def generate():
                return ['42']

            def solve(dataset):
                return '42'

            def check(reply, clue):
                return int(reply) == 42
            """),
        'execution_time_limit': 1,
        'execution_memory_limit': 32,
        'samples_count': 1,
        'templates_data': '',
        'is_time_limit_scaled': False,
        'is_memory_limit_scaled': False,
        'manual_time_limits': [],
        'manual_memory_limits': [],
        'test_archive': [],
    }
    default_code = textwrap.dedent("""
        #include <iostream>

        int main() {
            std::cout << 42 << std::endl;
        }
        """)

    def _generate_supplementary(self, source):
        quiz = self.quiz_class(source)
        supplementary = quiz.async_init()
        supplementary.pop('options')
        supplementary.pop('warnings')
        return supplementary

    def prepare_quiz(self, source):
        supplementary = self._generate_supplementary(source)
        return self.quiz_class(source, supplementary=supplementary)

    def submit(self, quiz, code, language=None):
        assert language is not None or hasattr(self, 'language'), \
            "You must specify the language of the submission"
        # noinspection PyUnresolvedReferences
        reply = {
            'language': language or self.language,
            'code': code,
        }
        # noinspection PyProtectedMember
        clean_reply = quiz.clean_reply(reply, None)._original
        return quiz.check(clean_reply, None)
