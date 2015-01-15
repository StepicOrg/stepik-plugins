import pytest

from stepic_plugins import rpcapi


def pytest_addoption(parser):
    parser.addoption('--rpc-url', action='store', default=None,
                     help="Use real RPC server transport for QuizAPI tests")


@pytest.fixture
def quiz_rpcapi(request):
    rpc_transport_url = request.config.getoption('rpc_url')
    if rpc_transport_url:
        return rpcapi.QuizAPI(rpc_transport_url)
    return rpcapi.QuizAPI(None, fake_server=True)


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
