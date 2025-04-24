import pytest
from typing import Optional, Dict, Any, List
import pathlib
from pytest_mock import MockerFixture

from inbox_impl.src.inbox_impl._impl import GmailClientImpl
from inbox_impl.src.inbox_impl import GmailClientInterface, get_client
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path


@pytest.fixture
def client() -> GmailClientInterface:
    """Create a test client instance."""
    return get_client()


def test_should_connect_with_valid_token(mocker: MockerFixture, client: GmailClientImpl) -> None:
    """Test successful connection with valid token."""
    mocker.patch("inbox_impl.src.inbox_impl._impl.Path.exists", return_value=True)
    mock_creds = mocker.MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file = mocker.patch("inbox_impl.src.inbox_impl._impl.Credentials.from_authorized_user_file")
    mock_creds_from_file.return_value = mock_creds
    mock_service = mocker.MagicMock()
    mock_build = mocker.patch("inbox_impl.src.inbox_impl._impl.build")
    mock_build.return_value = mock_service

    connected = client.connect()

    assert connected is True
    assert client.is_connected()
    mock_creds.refresh.assert_not_called()


def test_login_success(mocker: MockerFixture, client: GmailClientImpl) -> None:
    """Test successful login."""
    mocker.patch("inbox_impl.src.inbox_impl._impl.Path.exists", return_value=True)

    mock_creds = mocker.MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file = mocker.patch("inbox_impl.src.inbox_impl._impl.Credentials.from_authorized_user_file")
    mock_creds_from_file.return_value = mock_creds

    mock_service = mocker.MagicMock()
    mock_build = mocker.patch("inbox_impl.src.inbox_impl._impl.build")
    mock_build.return_value = mock_service

    assert client.login("alice", "password123")
    assert client.is_connected()
    mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)


def test_login_failure(client: GmailClientImpl) -> None:
    """Test login failure."""
    assert not client.login("", "")
    assert not client.is_connected()
    
    # Also test with invalid credentials
    assert not client.login("invalid_user", "invalid_password")
    assert not client.is_connected()


def test_authenticate_success(mocker: MockerFixture, client: GmailClientImpl) -> None:
    """Test successful authentication."""
    mocker.patch("inbox_impl.src.inbox_impl._impl.Path.exists", return_value=True)

    mock_creds = mocker.MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file = mocker.patch("inbox_impl.src.inbox_impl._impl.Credentials.from_authorized_user_file")
    mock_creds_from_file.return_value = mock_creds

    mock_service = mocker.MagicMock()
    mock_build = mocker.patch("inbox_impl.src.inbox_impl._impl.build")
    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()
    mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)


def test_authenticate_failure(client: GmailClientImpl) -> None:
    """Test authentication failure."""
    assert not client.authenticate("invalid", "INVALID_TOKEN")
    assert not client.is_connected()


def test_logout(mocker: MockerFixture, client: GmailClientImpl) -> None:
    """Test logout functionality."""
    mocker.patch("inbox_impl.src.inbox_impl._impl.Path.exists", return_value=True)

    mock_creds = mocker.MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file = mocker.patch("inbox_impl.src.inbox_impl._impl.Credentials.from_authorized_user_file")
    mock_creds_from_file.return_value = mock_creds

    mock_service = mocker.MagicMock()
    mock_build = mocker.patch("inbox_impl.src.inbox_impl._impl.build")
    mock_build.return_value = mock_service

    assert client.login("alice", "password123")
    assert client.is_connected()

    client.logout()
    assert not client.is_connected()
    
    # Access internal state through getattr to avoid mypy errors
    assert getattr(client, "_GmailClientImpl__service") is None
    assert getattr(client, "_GmailClientImpl__creds") is None
    assert getattr(client, "_GmailClientImpl__current_user") is None
    assert not getattr(client, "_GmailClientImpl__authenticated")


def test_use_mailbox_success(mocker: MockerFixture, client: GmailClientImpl) -> None:
    """Test successful mailbox selection."""
    mocker.patch("inbox_impl.src.inbox_impl._impl.Path.exists", return_value=True)

    mock_creds = mocker.MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file = mocker.patch("inbox_impl.src.inbox_impl._impl.Credentials.from_authorized_user_file")
    mock_creds_from_file.return_value = mock_creds

    mock_service = mocker.MagicMock()
    mock_users = mocker.MagicMock()
    mock_labels = mocker.MagicMock()
    mock_list = mocker.MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.labels.return_value = mock_labels
    mock_labels.list.return_value = mock_list
    mock_list.execute.return_value = {"labels": [{"name": "INBOX"}, {"name": "SENT"}]}

    mock_build = mocker.patch("inbox_impl.src.inbox_impl._impl.build")
    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    assert client.use_mailbox("INBOX")
    assert getattr(client, "_GmailClientImpl__current_mailbox") == "INBOX"
    mock_labels.list.assert_called_once()


def test_fetch_mailboxes_success(mocker: MockerFixture, client: GmailClientImpl) -> None:
    """Test successful mailbox fetching."""
    mocker.patch("inbox_impl.src.inbox_impl._impl.Path.exists", return_value=True)

    mock_creds = mocker.MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file = mocker.patch("inbox_impl.src.inbox_impl._impl.Credentials.from_authorized_user_file")
    mock_creds_from_file.return_value = mock_creds

    mock_service = mocker.MagicMock()
    mock_users = mocker.MagicMock()
    mock_labels = mocker.MagicMock()
    mock_list = mocker.MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.labels.return_value = mock_labels
    mock_labels.list.return_value = mock_list
    mock_list.execute.return_value = {
        "labels": [{"name": "INBOX"}, {"name": "SENT"}, {"name": "TRASH"}]
    }

    mock_build = mocker.patch("inbox_impl.src.inbox_impl._impl.build")
    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    mailboxes = client.fetch_mailboxes()
    assert isinstance(mailboxes, list)
    assert mailboxes == ["INBOX", "SENT", "TRASH"]
    mock_labels.list.assert_called_once()


def test_get_emails_list_success(mocker: MockerFixture, client: GmailClientImpl) -> None:
    """Test successful email list retrieval."""
    mocker.patch("inbox_impl.src.inbox_impl._impl.Path.exists", return_value=True)

    mock_creds = mocker.MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file = mocker.patch("inbox_impl.src.inbox_impl._impl.Credentials.from_authorized_user_file")
    mock_creds_from_file.return_value = mock_creds

    mock_service = mocker.MagicMock()
    mock_users = mocker.MagicMock()
    mock_messages = mocker.MagicMock()
    mock_list = mocker.MagicMock()
    mock_get = mocker.MagicMock()

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

    mock_build = mocker.patch("inbox_impl.src.inbox_impl._impl.build")
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


def test_get_email_content_success(mocker: MockerFixture, client: GmailClientImpl) -> None:
    """Test successful email content retrieval."""
    mocker.patch("inbox_impl.src.inbox_impl._impl.Path.exists", return_value=True)

    mock_creds = mocker.MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file = mocker.patch("inbox_impl.src.inbox_impl._impl.Credentials.from_authorized_user_file")
    mock_creds_from_file.return_value = mock_creds

    mock_service = mocker.MagicMock()
    mock_users = mocker.MagicMock()
    mock_messages = mocker.MagicMock()
    mock_get = mocker.MagicMock()

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

    mock_build = mocker.patch("inbox_impl.src.inbox_impl._impl.build")
    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    email = client.get_email_content("123")
    assert email["id"] == "123"
    assert email["subject"] == "Test Subject"
    assert email["sender"] == "sender@example.com"
    assert email["date"] == "Tue, 25 Jun 2024 10:00:00 +0000"
    assert email["to"] == "recipient@example.com"
    assert "Test email body" in email["body"]

    mock_messages.get.assert_called_once_with(userId="me", id="123", format="full")


def test_send_email_success(mocker: MockerFixture, client: GmailClientImpl) -> None:
    """Test successful email sending."""
    mocker.patch("inbox_impl.src.inbox_impl._impl.Path.exists", return_value=True)

    mock_creds = mocker.MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file = mocker.patch("inbox_impl.src.inbox_impl._impl.Credentials.from_authorized_user_file")
    mock_creds_from_file.return_value = mock_creds

    mock_service = mocker.MagicMock()
    mock_users = mocker.MagicMock()
    mock_messages = mocker.MagicMock()
    mock_send = mocker.MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.messages.return_value = mock_messages
    mock_messages.send.return_value = mock_send
    mock_send.execute.return_value = {"id": "send_receipt_1"}

    mock_build = mocker.patch("inbox_impl.src.inbox_impl._impl.build")
    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    assert client.send_email("recipient@example.com", "Test Subject", "Test Body")
    mock_messages.send.assert_called_once()


def test_delete_email_success(mocker: MockerFixture, client: GmailClientImpl) -> None:
    """Test successful email deletion."""
    mocker.patch("inbox_impl.src.inbox_impl._impl.Path.exists", return_value=True)

    mock_creds = mocker.MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file = mocker.patch("inbox_impl.src.inbox_impl._impl.Credentials.from_authorized_user_file")
    mock_creds_from_file.return_value = mock_creds

    mock_service = mocker.MagicMock()
    mock_users = mocker.MagicMock()
    mock_messages = mocker.MagicMock()
    mock_trash = mocker.MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.messages.return_value = mock_messages
    mock_messages.trash.return_value = mock_trash
    mock_trash.execute.return_value = {"id": "trashed_1"}

    mock_build = mocker.patch("inbox_impl.src.inbox_impl._impl.build")
    mock_build.return_value = mock_service

    assert client.authenticate("alice", "TOKEN123")
    assert client.is_connected()

    assert client.delete_email("1")
    mock_messages.trash.assert_called_once_with(userId="me", id="1")


def test_modify_email_labels_success(mocker: MockerFixture, client: GmailClientImpl) -> None:
    """Test successful email label modification."""
    mocker.patch("inbox_impl.src.inbox_impl._impl.Path.exists", return_value=True)

    mock_creds = mocker.MagicMock(spec=Credentials, valid=True, expired=False)
    mock_creds_from_file = mocker.patch("inbox_impl.src.inbox_impl._impl.Credentials.from_authorized_user_file")
    mock_creds_from_file.return_value = mock_creds

    mock_service = mocker.MagicMock()
    mock_users = mocker.MagicMock()
    mock_messages = mocker.MagicMock()
    mock_modify = mocker.MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.messages.return_value = mock_messages
    mock_messages.modify.return_value = mock_modify
    mock_modify.execute.return_value = {"id": "modified_1"}

    mock_build = mocker.patch("inbox_impl.src.inbox_impl._impl.build")
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
