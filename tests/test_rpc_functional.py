import pytest

from stepic_plugins.exceptions import FormatError


class TestQuizApi(object):
    def test_ping(self, quiz_rpcapi):
        reply = quiz_rpcapi.ping("May the Force be with you")
        assert reply == "May the Force be with you"

    def test_validate_source(self, quiz_rpcapi, choice_quiz_ctxt):
        quiz_rpcapi.validate_source(choice_quiz_ctxt)

    def test_validate_source_format_error(self, quiz_rpcapi, choice_quiz_ctxt):
        choice_quiz_ctxt['source'] = {}

        with pytest.raises(FormatError):
            quiz_rpcapi.validate_source(choice_quiz_ctxt)

    def test_generate(self, quiz_rpcapi, choice_quiz_ctxt):
        dataset, clue = quiz_rpcapi.generate(choice_quiz_ctxt)

        assert sorted(dataset['options']) == ['one', 'two']
        assert clue == [x == 'one' for x in dataset['options']]

    def test_async_init(self, quiz_rpcapi):
        quiz_ctxt = {
            'name': 'dataset',
            'source': {
                'code': """
import random

def generate():
    a = random.randrange(10)
    b = random.randrange(10)
    return "{} {}".format(a, b)

def solve(dataset):
    a, b = dataset.split()
    return str(int(a)+int(b))

def check(reply, clue):
    return int(reply) == int(clue)

tests = [
    ("2 2", "4", "4"),
]
"""
            }
        }

        supplementary = quiz_rpcapi.async_init(quiz_ctxt)

        assert list(supplementary['options']['samples'][0]) == ['2 2', '4']
        assert supplementary['options']['time_limit']

    def test_clean_reply(self, quiz_rpcapi, choice_quiz_ctxt):
        dataset = {'options': ['one', 'two']}
        reply = {'choices': [True, False]}

        clean_reply = quiz_rpcapi.clean_reply(choice_quiz_ctxt, reply,
                                              dataset=dataset)

        assert clean_reply == reply['choices']

    def test_clean_reply_returns_serializable(self, quiz_rpcapi):
        quiz_ctxt = {
            'name': 'code',
            'source': {
                'code': '',
                'execution_time_limit': 1,
                'execution_memory_limit': 1,
                'samples_count': 0,
                'templates_data': '',
            }
        }
        reply = {
            'language': 'python3',
            'code': 'print(42)',
        }

        clean_reply = quiz_rpcapi.clean_reply(quiz_ctxt, reply)

        assert isinstance(clean_reply, dict)
        assert clean_reply == reply

    def test_clean_reply_format_error(self, quiz_rpcapi, choice_quiz_ctxt):
        dataset = {'options': ['one', 'two']}
        reply = {'choices': [True, False, False]}

        with pytest.raises(FormatError):
            quiz_rpcapi.clean_reply(choice_quiz_ctxt, reply, dataset=dataset)

    def test_check(self, quiz_rpcapi, choice_quiz_ctxt):
        reply = [True, False]
        clue = [True, False]

        assert quiz_rpcapi.check(choice_quiz_ctxt, reply, clue)

    def test_cleanup(self, quiz_rpcapi, choice_quiz_ctxt):
        clue = [True, False]

        assert quiz_rpcapi.cleanup(choice_quiz_ctxt, clue=clue) is None

    def test_list_computationally_hard_quizzes(self, quiz_rpcapi):
        hard_quizzes = quiz_rpcapi.list_computationally_hard_quizzes()

        assert 'code' in hard_quizzes
        assert 'dataset' in hard_quizzes
