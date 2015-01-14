import pytest

from stepic_plugins import rpcapi


@pytest.fixture
def quiz_rpcapi():
    #return rpcapi.QuizAPI(None, fake_server=True)
    return rpcapi.QuizAPI('rabbit://guest:guest@192.168.59.103:5672//')


@pytest.fixture
def choice_quiz_ctxt():
    return {
        'name': 'simple-choice',
        'source': {
            'options': [
                {'text': 'one', 'is_correct': True},
                {'text': 'two', 'is_correct': False},
            ]
        }
    }
