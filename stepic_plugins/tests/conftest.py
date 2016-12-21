import pytest

from stepic_plugins.base import load_by_name
from stepic_plugins.rpcapi import QuizAPI


@pytest.fixture(scope='session')
def quizapi():
    return QuizAPI(None, fake_server=True)


@pytest.fixture(scope='session')
def free_answer_ctxt():
    return {
        'name': 'free-answer',
        'source': {
            'is_attachments_enabled': True,
            'is_html_enabled': True,
            'manual_scoring': False,
        },
    }


@pytest.fixture(scope='session')
def free_answer_quiz():
    quiz_class = load_by_name('free-answer')
    source = {
        'is_attachments_enabled': True,
        'is_html_enabled': True,
        'manual_scoring': False,
    }
    return quiz_class(source)
