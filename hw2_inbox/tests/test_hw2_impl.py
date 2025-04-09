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

def test_connect_then_login_success(client: GmailClientImpl):
    assert client.connect()
    assert client.login("alice", "password123")
    assert client.is_connected()

def test_login_failure_wrong_password(client: GmailClientImpl):
    client.connect()
    assert not client.login("alice", "wrongpassword")

def test_login_failure_not_connected(client: GmailClientImpl):
    assert not client.login("alice", "password123")

def test_authenticate_success(client: GmailClientImpl):
    assert client.authenticate("TOKEN123")
    assert client.is_connected()

def test_authenticate_failure(client: GmailClientImpl):
    assert not client.authenticate("INVALID_TOKEN")

def test_logout_clears_state(client: GmailClientImpl):
    client.connect()
    client.login("bob", "123456")
    assert client.is_connected()
    client.logout()
    assert not client.is_connected()
    assert client._GmailClientImpl__current_user is None