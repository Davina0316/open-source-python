import pytest

from ..main import GmailClientImpl
from .. import GmailClientInterface


@pytest.fixture
def client() -> GmailClientInterface:
    return GmailClientImpl()

def test_should_connect(client: GmailClientInterface):
    assert client.connect()
    assert client.is_connected()
