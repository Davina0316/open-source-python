import pytest

from ..main import GmailClientImpl
from .. import GmailClientInterface


@pytest.fixture
def client() -> GmailClientInterface:
    return GmailClientImpl()

def test_should_connect(client: GmailClientInterface):
    assert client.connect()
    assert client.is_connected()

def test_login_success(client: GmailClientImpl):
    assert client.login("user", "pass")
    assert client.is_connected()

def test_login_failure(client: GmailClientImpl):
    assert not client.login("", "")
    assert not client.is_connected()

def test_authenticate_success(client: GmailClientImpl):
    assert client.authenticate("VALID_TOKEN")
    assert client.is_connected()

def test_authenticate_failure(client: GmailClientImpl):
    assert not client.authenticate("INVALID_TOKEN")
    assert not client.is_connected()

def test_logout(client: GmailClientImpl):
    client.login("user", "pass")
    assert client.is_connected()
    client.logout()
    assert not client.is_connected()

