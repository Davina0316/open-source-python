import pytest
from typing import Optional

from ..main import GmailClientImpl
from .. import GmailClientInterface
from unittest.mock import patch, MagicMock, mock_open
from google.oauth2.credentials import Credentials


@pytest.fixture
def client() -> GmailClientInterface:
    return GmailClientImpl()

@patch("hw2_inbox.main.Path.exists", return_value=False) # mock_path_exists
@patch("hw2_inbox.main.open", new_callable=mock_open) # mock_file_open
@patch("hw2_inbox.main.InstalledAppFlow.from_client_secrets_file") # mock_flow_factory
def test_should_connect_with_new_credentials(mock_flow_factory, mock_file_open, mock_path_exists, client: GmailClientInterface):
    mock_flow = MagicMock()
    mock_flow.run_local_server.return_value = MagicMock(spec=Credentials, valid=True)
    mock_flow_factory.return_value = mock_flow

    connected = client.connect()

    assert connected is True
    assert client.is_connected()
    # Ensure the flow was created (i.e., user had to log in)
    mock_flow_factory.assert_called_once()
    # Ensure run_local_server was called
    mock_flow.run_local_server.assert_called_once()
    # Ensure token file was written
    mock_file_open.assert_called_once()
    handle = mock_file_open()
    handle.write.assert_called_once()

@patch("hw2_inbox.main.Path.exists", return_value=True) # mock_path_exists
@patch("hw2_inbox.main.Credentials.from_authorized_user_file") # mock_creds_from_file
@patch("hw2_inbox.main.open", new_callable=mock_open) # mock_file_open
@patch("hw2_inbox.main.InstalledAppFlow.from_client_secrets_file") # mock_flow_factory
def test_should_connect_with_valid_token(mock_flow_factory, mock_file_open, mock_creds_from_file, mock_path_exists,client: GmailClientInterface):
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    connected = client.connect()

    assert connected is True
    assert client.is_connected()
    # If credentials are valid, we do NOT expect the OAuth flow
    mock_flow_factory.assert_not_called()
    # And no refresh()
    mock_creds.refresh.assert_not_called()
    # And no new token.json file is written
    mock_file_open.assert_not_called()

@patch("hw2_inbox.main.InstalledAppFlow.from_client_secrets_file") # mock_flow_factory
@patch("hw2_inbox.main.open", new_callable=mock_open) # mock_file_open
@patch("hw2_inbox.main.Credentials.from_authorized_user_file") # mock_creds_from_file
@patch("hw2_inbox.main.Path.exists", return_value=True) # mock_file_exists
def test_should_refresh_token_if_expired(mock_file_exists, mock_creds_from_file, mock_file_open, mock_flow_factory, client: GmailClientInterface):
    mock_creds = MagicMock(spec=Credentials, valid=False, expired=True, refresh_token="123")
    mock_creds_from_file.return_value = mock_creds

    connected = client.connect()

    assert connected is True
    assert client.is_connected() is True
    mock_flow_factory.assert_not_called()
    mock_creds.refresh.assert_called_once()
    mock_file_open.assert_called_once()



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