import pytest

from stepic_plugins import rpcapi


def pytest_addoption(parser):
    parser.addoption('--rpc-url', action='store', default=None,
                     help="Use real RPC server transport for QuizAPI tests")


@pytest.fixture
def rpc_transport_url(request):
    return request.config.getoption('rpc_url')


@pytest.fixture
def quiz_rpcapi(rpc_transport_url):
    if rpc_transport_url:
        return rpcapi.QuizAPI(rpc_transport_url)
    return rpcapi.QuizAPI(None, fake_server=True)


@pytest.fixture
def code_rpcapi(rpc_transport_url):
    if rpc_transport_url:
        return rpcapi.CodeJailAPI(rpc_transport_url)
    return rpcapi.CodeJailAPI(None, fake_server=True)


@pytest.fixture
def choice_quiz_ctxt():
    return {
        'name': 'choice',
        'source': {
            'is_multiple_choice': False,
            'is_always_correct': False,
            'sample_size': 2,
            'preserve_order': False,
            'is_html_enabled': True,
            'is_options_feedback': False,
            'options': [
                {'is_correct': True, 'text': 'one', 'feedback': ''},
                {'is_correct': False, 'text': 'two', 'feedback': ''},
            ],
        }
    }
