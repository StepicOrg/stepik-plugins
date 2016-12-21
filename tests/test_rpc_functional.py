import pytest
import tarfile

from stepic_plugins.exceptions import FormatError
from stepic_plugins.schema import ParsedJSON


class TestQuizApi(object):
    def test_ping(self, quiz_rpcapi):
        reply = quiz_rpcapi.ping("May the Force be with you")
        assert reply == "May the Force be with you"

    def test_ping_serialization(self, quiz_rpcapi):
        parsed_json = ParsedJSON({'code': str}, {'code': 'some code here'})
        complex_data = {
            'list': ['Use', b'the Force', 42],
            'dict': {'bin': b'data', 'float': 42.42},
            'bytes': b'The Force will be with you, always',
            'parsed_json': parsed_json,
        }

        reply = quiz_rpcapi.ping(complex_data)

        complex_data['parsed_json'] = parsed_json._original
        assert reply == complex_data

    def test_validate_source(self, quiz_rpcapi, choice_quiz_ctxt):
        quiz_rpcapi.validate_source(choice_quiz_ctxt)

    def test_validate_source_format_error(self, quiz_rpcapi, choice_quiz_ctxt):
        choice_quiz_ctxt['source'] = {}

        with pytest.raises(FormatError):
            quiz_rpcapi.validate_source(choice_quiz_ctxt)

    def test_generate(self, quiz_rpcapi, choice_quiz_ctxt):
        source_options = choice_quiz_ctxt['source']['options']
        options_index = {o['text']: i for i, o in enumerate(source_options)}

        dataset, clue = quiz_rpcapi.generate(choice_quiz_ctxt)

        assert sorted(dataset['options']) == ['one', 'two']
        assert clue == [options_index[o] for o in dataset['options']]

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
        dataset = {
            'is_multiple_choice': choice_quiz_ctxt['source']['is_multiple_choice'],
            'options': ['one', 'two'],
        }
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
                'execution_memory_limit': 32,
                'samples_count': 0,
                'templates_data': '',
                'is_time_limit_scaled': False,
                'is_memory_limit_scaled': False,
                'manual_time_limits': [],
                'manual_memory_limits': [],
                'test_archive': [],
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
        clue = [0, 1]

        assert quiz_rpcapi.check(choice_quiz_ctxt, reply, clue)

    def test_cleanup(self, quiz_rpcapi, choice_quiz_ctxt):
        clue = [True, False]

        assert quiz_rpcapi.cleanup(choice_quiz_ctxt, clue=clue) is None

    def test_list_computationally_hard_quizzes(self, quiz_rpcapi):
        hard_quizzes = quiz_rpcapi.list_computationally_hard_quizzes()

        assert 'code' in hard_quizzes
        assert 'dataset' in hard_quizzes

    def test_call_attribute(self, quiz_rpcapi, choice_quiz_ctxt):
        assert quiz_rpcapi.call(choice_quiz_ctxt, 'name') == 'choice'

    def test_call_method(self, quiz_rpcapi, choice_quiz_ctxt):
        reply = [True, False]
        clue = [True, False]

        assert quiz_rpcapi.call(choice_quiz_ctxt, 'check',
                                args=(reply,), kwargs=dict(clue=clue))


class TestCodeJailApi(object):
    def test_run_code(self, code_rpcapi):
        code = 'n = int(input().strip()); print("inc:", n + 1)'

        result = code_rpcapi.run_code('python', code=code, stdin='42')

        expected_result = {
            'status': 0,
            'stdout': b'inc: 43\n',
            'stderr': b'',
            'time_limit_exceeded': False,
        }
        assert result == expected_result
