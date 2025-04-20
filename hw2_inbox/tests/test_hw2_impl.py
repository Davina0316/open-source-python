import pytest
from typing import Optional, Dict, Any, List
import pathlib

from ..main import GmailClientImpl
from .. import GmailClientInterface
from unittest.mock import patch, MagicMock, mock_open, PropertyMock
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path


@pytest.fixture
def client() -> GmailClientImpl:
    return GmailClientImpl()


@patch("pathlib.Path.open") 
@patch("hw2_inbox.main.InstalledAppFlow.from_client_secrets_file")  
@patch("hw2_inbox.main.build")  
@patch("hw2_inbox.main.Path.exists")
def test_should_connect_with_new_credentials(
    mock_path_exists: MagicMock, mock_build: MagicMock, mock_flow_factory: MagicMock, mock_path_open: MagicMock, client: GmailClientImpl # <-- Change signature back
) -> None:
    mock_path_exists.side_effect = [False, True]

    # Setup mock flow
    mock_flow = MagicMock()
    mock_creds = MagicMock(spec=Credentials, valid=True)
    mock_creds.to_json.return_value = '{"token": "test_token", "refresh_token": "test_refresh", "client_id": "test_client_id", "client_secret": "test_client_secret"}'
    mock_flow.run_local_server.return_value = mock_creds
    mock_flow_factory.return_value = mock_flow

    mock_service = MagicMock()
    mock_build.return_value = mock_service

    mock_file_handle = MagicMock()
    mock_path_open.return_value.__enter__.return_value = mock_file_handle

    connected = client.connect()

    assert connected is True
    assert client.is_connected()
    mock_flow_factory.assert_called_once()
    mock_flow.run_local_server.assert_called_once()
    mock_path_open.assert_called_once_with("w")
    mock_file_handle.write.assert_called_once_with(
        '{"token": "test_token", "refresh_token": "test_refresh", "client_id": "test_client_id", "client_secret": "test_client_secret"}'
    )


@patch("hw2_inbox.main.Path.exists", return_value=True) 
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")  
@patch("hw2_inbox.main.open", new_callable=mock_open)  
@patch("hw2_inbox.main.InstalledAppFlow.from_client_secrets_file") 
@patch("hw2_inbox.main.build") 
def test_should_connect_with_valid_token(
    mock_build: MagicMock,
    mock_flow_factory: MagicMock,
    mock_file_open: MagicMock,
    mock_creds_from_file: MagicMock,
    mock_path_exists: MagicMock,
    client: GmailClientImpl,
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_build.return_value = mock_service

    connected = client.connect()

    assert connected is True
    assert client.is_connected()
    mock_flow_factory.assert_not_called()
    mock_creds.refresh.assert_not_called()
    mock_file_open.assert_not_called()


@patch("hw2_inbox.main.InstalledAppFlow.from_client_secrets_file") 
@patch("pathlib.Path.open")  
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")  
@patch("hw2_inbox.main.Path.exists", return_value=True) 
@patch("hw2_inbox.main.build")  
def test_should_refresh_token_if_expired(
    mock_build: MagicMock,
    mock_file_exists: MagicMock,
    mock_creds_from_file: MagicMock,
    mock_path_open: MagicMock,
    mock_flow_factory: MagicMock,
    client: GmailClientImpl,
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=False, expired=True, refresh_token="123")
    mock_creds.to_json.return_value = '{"token": "refreshed_token", "refresh_token": "123", "client_id": "test_client_id", "client_secret": "test_client_secret"}'
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_build.return_value = mock_service

    mock_file_handle = MagicMock()
    mock_path_open.return_value.__enter__.return_value = mock_file_handle

    connected = client.connect()

    assert connected is True
    assert client.is_connected()
    mock_flow_factory.assert_not_called()
    mock_creds.refresh.assert_called_once()
    mock_path_open.assert_called_once_with("w")
    mock_file_handle.write.assert_called_once_with(
        '{"token": "refreshed_token", "refresh_token": "123", "client_id": "test_client_id", "client_secret": "test_client_secret"}'
    )


@patch("hw2_inbox.main.Path.exists", return_value=True)  
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")  
@patch("hw2_inbox.main.build") 
def test_login_success(mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_build.return_value = mock_service

    assert client.login("alice", "password123")
    assert client.is_connected() 

    mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)


def test_login_failure(client: GmailClientImpl) -> None:
    with patch.object(client, "connect", return_value=True):
        assert not client.login("", "")
        assert not client.is_connected()


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_authenticate_success(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)


def test_authenticate_failure(client: GmailClientImpl) -> None:
    assert not client.authenticate("invalid", "INVALID_TOKEN")
    assert not client.is_connected()


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_logout(mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl) -> None:

    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_build.return_value = mock_service

    assert client.login("alice", "password123")
    assert client.is_connected()

    client.logout()
    assert not client.is_connected()
    assert client._GmailClientImpl__service is None  # type: ignore[attr-defined]
    assert client._GmailClientImpl__creds is None # type: ignore[attr-defined]
    assert client._GmailClientImpl__current_user is None # type: ignore[attr-defined]
    assert not client._GmailClientImpl__authenticated # type: ignore[attr-defined]


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_connect_then_login_success(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_build.return_value = mock_service

    assert client.connect()
    assert client.login("alice", "password123")
    assert client.is_connected()


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_login_failure_wrong_password(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_build.return_value = mock_service

    assert client.connect()
    assert not client.login("alice", "wrongpassword")


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_logout_clears_state(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_build.return_value = mock_service

    client.connect()
    client.login("bob", "123456")
    assert client.is_connected()
    client.logout()
    assert not client.is_connected()
    assert client._GmailClientImpl__current_user is None # type: ignore[attr-defined]


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_use_mailbox_success(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_users = MagicMock()
    mock_labels = MagicMock()
    mock_list = MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.labels.return_value = mock_labels
    mock_labels.list.return_value = mock_list
    mock_list.execute.return_value = {"labels": [{"name": "INBOX"}, {"name": "SENT"}]}

    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    assert client.use_mailbox("INBOX")
    assert client._GmailClientImpl__current_mailbox == "INBOX" # type: ignore[attr-defined]
    mock_labels.list.assert_called_once()


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_use_mailbox_failure_invalid_mailbox(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_users = MagicMock()
    mock_labels = MagicMock()
    mock_list = MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.labels.return_value = mock_labels
    mock_labels.list.return_value = mock_list
    mock_list.execute.return_value = {"labels": [{"name": "INBOX"}, {"name": "SENT"}]}

    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    assert not client.use_mailbox("NONEXISTENT")
    assert client._GmailClientImpl__current_mailbox is None # type: ignore[attr-defined]
    mock_labels.list.assert_called_once()


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_fetch_mailboxes_success(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_users = MagicMock()
    mock_labels = MagicMock()
    mock_list = MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.labels.return_value = mock_labels
    mock_labels.list.return_value = mock_list
    mock_list.execute.return_value = {
        "labels": [{"name": "INBOX"}, {"name": "SENT"}, {"name": "TRASH"}]
    }

    mock_build.return_value = mock_service

    authenticated = client.authenticate("alice", "TOKEN123")
    assert authenticated is True
    assert client.is_connected()

    mailboxes = client.fetch_mailboxes()

    assert isinstance(mailboxes, list)
    assert mailboxes == ["INBOX", "SENT", "TRASH"]
    mock_labels.list.assert_called_once() 

    client.logout()


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_get_emails_list_success(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_users = MagicMock()
    mock_messages = MagicMock()
    mock_list = MagicMock()
    mock_get = MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.messages.return_value = mock_messages
    mock_messages.list.return_value = mock_list
    mock_list.execute.return_value = {"messages": [{"id": "1"}, {"id": "2"}]}

    mock_messages.get.return_value = mock_get
    mock_get.execute.side_effect = [
        {
            "id": "1",
            "snippet": "Email 1 snippet",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject 1"},
                    {"name": "From", "value": "sender1@example.com"},
                ]
            },
        },
        {
            "id": "2",
            "snippet": "Email 2 snippet",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject 2"},
                    {"name": "From", "value": "sender2@example.com"},
                ]
            },
        },
    ]

    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    emails = client.get_emails_list() 
    assert len(emails) == 2
    assert emails[0]["id"] == "1"
    assert emails[0]["subject"] == "Test Subject 1"
    assert emails[0]["sender"] == "sender1@example.com"
    assert emails[1]["id"] == "2"
    assert emails[1]["subject"] == "Test Subject 2"
    assert emails[1]["sender"] == "sender2@example.com"

    mock_messages.list.assert_called_once_with(userId="me", labelIds=["INBOX"], maxResults=10)
    assert mock_messages.get.call_count == 2


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_get_email_content_success(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_users = MagicMock()
    mock_messages = MagicMock()
    mock_get = MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.messages.return_value = mock_messages
    mock_messages.get.return_value = mock_get
    mock_get.execute.return_value = {
        "id": "123",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Test Subject"},
                {"name": "From", "value": "sender@example.com"},
                {"name": "To", "value": "recipient@example.com"},
                {"name": "Date", "value": "Tue, 25 Jun 2024 10:00:00 +0000"},
            ],
            "parts": [
                {"mimeType": "text/plain", "body": {"data": "VGVzdCBlbWFpbCBib2R5"}}
            ],
        },
    }

    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    email = client.get_email_content("123")
    assert email["id"] == "123"
    assert email["subject"] == "Test Subject"
    assert email["sender"] == "sender@example.com"
    assert email["date"] == "Tue, 25 Jun 2024 10:00:00 +0000"
    assert email["to"] == "recipient@example.com"
    assert email["body"] == "Test email body"

    mock_messages.get.assert_called_once_with(userId="me", id="123", format="full")


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_send_email_success(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_users = MagicMock()
    mock_messages = MagicMock()
    mock_send = MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.messages.return_value = mock_messages
    mock_messages.send.return_value = mock_send
    mock_send.execute.return_value = {"id": "send_receipt_1"}

    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    assert client.send_email("recipient@example.com", "Test Subject", "Test Body")
    mock_messages.send.assert_called_once()


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_delete_email_success(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_users = MagicMock()
    mock_messages = MagicMock()
    mock_trash = MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.messages.return_value = mock_messages
    mock_messages.trash.return_value = mock_trash
    mock_trash.execute.return_value = {"id": "trashed_1"}

    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    assert client.delete_email("1")
    mock_messages.trash.assert_called_once_with(userId="me", id="1")


def test_operations_fail_when_not_authenticated(client: GmailClientImpl) -> None:
    assert not client.use_mailbox("INBOX")
    assert client.fetch_mailboxes() == []
    assert client.get_emails_list() == []
    assert client.get_email_content("1") == {}
    assert not client.send_email("to@example.com", "subject", "body")
    assert not client.delete_email("1")


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_operations_handle_api_errors(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_service.users().labels().list.side_effect = Exception("API Error")
    mock_service.users().messages().list.side_effect = Exception("API Error")
    mock_service.users().messages().get.side_effect = Exception("API Error")
    mock_service.users().messages().send.side_effect = Exception("API Error")
    mock_service.users().messages().trash.side_effect = Exception("API Error")
    mock_service.users().messages().modify.side_effect = Exception("API Error")
    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    assert not client.use_mailbox("INBOX") 
    assert client.fetch_mailboxes() == []
    assert client.get_emails_list() == []
    assert client.get_email_content("1") == {}
    assert not client.send_email("to@example.com", "subject", "body")
    assert not client.delete_email("1")


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_modify_email_labels_success(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_users = MagicMock()
    mock_messages = MagicMock()
    mock_modify = MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.messages.return_value = mock_messages
    mock_messages.modify.return_value = mock_modify
    mock_modify.execute.return_value = {"id": "modified_1"} 

    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    email_id = "email_to_modify"
    add_labels = ["STARRED", "IMPORTANT"]
    remove_labels = ["UNREAD"]

    assert client.modify_email_labels(email_id, add_labels=add_labels, remove_labels=remove_labels)

    mock_messages.modify.assert_called_once_with(
        userId="me",
        id=email_id,
        body={
            "addLabelIds": add_labels,
            "removeLabelIds": remove_labels,
        }
    )


@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_modify_email_labels_no_action(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_messages = MagicMock()
    mock_service.users().messages.return_value = mock_messages
    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")

    assert client.modify_email_labels("email_no_modify") 

    mock_messages.modify.assert_not_called()


def test_modify_email_labels_fail_when_not_authenticated(client: GmailClientImpl) -> None:
    assert not client.modify_email_labels("any_id", add_labels=["STARRED"])

@patch("hw2_inbox.main.Path.exists", return_value=True)
@patch("hw2_inbox.main.Credentials.from_authorized_user_file")
@patch("hw2_inbox.main.build")
def test_modify_email_labels_api_error(
    mock_build: MagicMock, mock_creds_from_file: MagicMock, mock_path_exists: MagicMock, client: GmailClientImpl
) -> None:
    mock_creds = MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_messages = MagicMock()
    mock_messages.modify.side_effect = Exception("API Modify Error")
    mock_service.users().messages.return_value = mock_messages
    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")

    assert not client.modify_email_labels("fail_id", add_labels=["INBOX"])

    mock_messages.modify.assert_called_once()

