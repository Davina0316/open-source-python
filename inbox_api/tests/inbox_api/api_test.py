"""Tests for the Gmail client interface."""

import pytest
from pytest_mock import MockerFixture
from typing import List, Dict, Any

from inbox_api.src.inbox_api import GmailClientInterface

class TestGmailClientInterface:
    """Test cases for the Gmail client interface."""

    def test_connect(self, mocker: MockerFixture) -> None:
        mock_client = mocker.create_autospec(GmailClientInterface, instance=True)
        mock_client.connect.return_value = True

        result = mock_client.connect()

        assert result is True
        mock_client.connect.assert_called_once()

    def test_login(self, mocker: MockerFixture) -> None:
        mock_client = mocker.create_autospec(GmailClientInterface, instance=True)
        mock_client.login.return_value = True
        result = mock_client.login("user@example.com", "password")
        assert result is True
        mock_client.login.assert_called_once_with("user@example.com", "password")

    def test_authenticate(self, mocker: MockerFixture) -> None:
        mock_client = mocker.create_autospec(GmailClientInterface, instance=True)
        mock_client.authenticate.return_value = True
        result = mock_client.authenticate("user@example.com", "access_token_123")
        assert result is True
        mock_client.authenticate.assert_called_once_with("user@example.com", "access_token_123")

    def test_logout(self, mocker: MockerFixture) -> None:
        mock_client = mocker.create_autospec(GmailClientInterface, instance=True)
        mock_client.logout.return_value = None
        mock_client.logout()
        mock_client.logout.assert_called_once()

    def test_fetch_mailboxes(self, mocker: MockerFixture) -> None:
        mock_client = mocker.create_autospec(GmailClientInterface, instance=True)
        expected_mailboxes = ["Inbox", "Sent", "Trash"]
        mock_client.fetch_mailboxes.return_value = expected_mailboxes
        mailboxes = mock_client.fetch_mailboxes()
        assert mailboxes == expected_mailboxes
        mock_client.fetch_mailboxes.assert_called_once()

    def test_use_mailbox(self, mocker: MockerFixture) -> None:
        mock_client = mocker.create_autospec(GmailClientInterface, instance=True)
        mock_client.use_mailbox.return_value = True
        result = mock_client.use_mailbox("Inbox")
        assert result is True
        mock_client.use_mailbox.assert_called_once_with("Inbox")

    def test_get_emails_list(self, mocker: MockerFixture) -> None:
        mock_client = mocker.create_autospec(GmailClientInterface, instance=True)
        emails: List[Dict[str, Any]] = [
            {"id": "1", "subject": "Hello", "sender": "a@example.com", "snippet": "Hi there"},
            {"id": "2", "subject": "World", "sender": "b@example.com", "snippet": "Greetings"},
        ]
        mock_client.get_emails_list.return_value = emails
        result = mock_client.get_emails_list()
        assert result == emails
        mock_client.get_emails_list.assert_called_once()

    def test_get_email_content(self, mocker: MockerFixture) -> None:
        mock_client = mocker.create_autospec(GmailClientInterface, instance=True)
        email_content = {"id": "1", "subject": "Hello", "body": "This is a test email."}
        mock_client.get_email_content.return_value = email_content
        result = mock_client.get_email_content("1")
        assert result == email_content
        mock_client.get_email_content.assert_called_once_with("1")

    def test_send_email(self, mocker: MockerFixture) -> None:
        mock_client = mocker.create_autospec(GmailClientInterface, instance=True)
        mock_client.send_email.return_value = True
        result = mock_client.send_email("recipient@example.com", "Test Subject", "Test Body")
        assert result is True
        mock_client.send_email.assert_called_once_with("recipient@example.com", "Test Subject", "Test Body")

    def test_delete_email(self, mocker: MockerFixture) -> None:
        mock_client = mocker.create_autospec(GmailClientInterface, instance=True)
        mock_client.delete_email.return_value = True
        result = mock_client.delete_email("1")
        assert result is True
        mock_client.delete_email.assert_called_once_with("1")

    def test_modify_email_labels(self, mocker: MockerFixture) -> None:
        mock_client_add = mocker.create_autospec(GmailClientInterface, instance=True)
        mock_client_add.modify_email_labels.return_value = True
        result_add = mock_client_add.modify_email_labels("1", add_labels=["UNREAD", "STARRED"])
        assert result_add is True
        mock_client_add.modify_email_labels.assert_called_with("1", add_labels=["UNREAD", "STARRED"])

        mock_client_remove = mocker.create_autospec(GmailClientInterface, instance=True)
        mock_client_remove.modify_email_labels.return_value = True
        result_remove = mock_client_remove.modify_email_labels("2", remove_labels=["IMPORTANT"])
        assert result_remove is True
        mock_client_remove.modify_email_labels.assert_called_with("2", remove_labels=["IMPORTANT"])

        mock_client_both = mocker.create_autospec(GmailClientInterface, instance=True)
        mock_client_both.modify_email_labels.return_value = True
        result_both = mock_client_both.modify_email_labels("3", add_labels=["INBOX"], remove_labels=["UNREAD"])
        assert result_both is True
        mock_client_both.modify_email_labels.assert_called_with("3", add_labels=["INBOX"], remove_labels=["UNREAD"])

        mock_client_none = mocker.create_autospec(GmailClientInterface, instance=True)
        mock_client_none.modify_email_labels.return_value = True
        result_none = mock_client_none.modify_email_labels("4")
        assert result_none is True
        mock_client_none.modify_email_labels.assert_called_with("4")


if __name__ == "__main__":
    pytest.main()
