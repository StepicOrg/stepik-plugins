import epicbox
import pytest

import structlog


def pytest_addoption(parser):
    parser.addoption('--docker-url', action='store', default=None,
                     help="Use this url to connect to a Docker backend server")


@pytest.fixture
def docker_url(request):
    return request.config.getoption('docker_url')


@pytest.fixture(autouse=True)
def configure(docker_url):
    epicbox.configure(
        profiles=[
            epicbox.Profile('python3', 'stepic/epicbox-python',
                            user='sandbox',
                            read_only=True),
            epicbox.Profile('gcc', 'stepik/epicbox-gcc:5.3.0'),
        ],
        docker_url=docker_url,
    )
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.KeyValueRenderer(key_order=['event']),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
    )
