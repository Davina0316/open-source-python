import unittest
from unittest.mock import create_autospec
from typing import List, Dict, Any

from .gmail_client_interface import GmailClientInterface

class TestGmailClientInterface(unittest.TestCase):
    def setUp(self):
        self.mock_client = create_autospec(GmailClientInterface, instance=True)

    def test_connect(self):
        self.mock_client.connect.return_value = True

        result = self.mock_client.connect()

        self.assertTrue(result)
        self.mock_client.connect.assert_called_once()

    def test_login(self):
        self.mock_client.login.return_value = True
        result = self.mock_client.login("user@example.com", "password")
        self.assertTrue(result)
        self.mock_client.login.assert_called_once_with("user@example.com", "password")

    def test_authenticate(self):
        self.mock_client.authenticate.return_value = True
        result = self.mock_client.authenticate("user@example.com", "access_token_123")
        self.assertTrue(result)
        self.mock_client.authenticate.assert_called_once_with("user@example.com", "access_token_123")

    def test_logout(self):
        self.mock_client.logout.return_value = None
        self.mock_client.logout()
        self.mock_client.logout.assert_called_once()

    def test_fetch_mailboxes(self):
        expected_mailboxes = ["Inbox", "Sent", "Trash"]
        self.mock_client.fetch_mailboxes.return_value = expected_mailboxes
        mailboxes = self.mock_client.fetch_mailboxes()
        self.assertEqual(mailboxes, expected_mailboxes)
        self.mock_client.fetch_mailboxes.assert_called_once()

    def test_use_mailbox(self):
        self.mock_client.use_mailbox.return_value = True
        result = self.mock_client.use_mailbox("Inbox")
        self.assertTrue(result)
        self.mock_client.use_mailbox.assert_called_once_with("Inbox")

    def test_get_emails_list(self):
        emails: List[Dict[str, Any]] = [
            {"id": "1", "subject": "Hello", "sender": "a@example.com", "snippet": "Hi there"},
            {"id": "2", "subject": "World", "sender": "b@example.com", "snippet": "Greetings"}
        ]
        self.mock_client.get_emails_list.return_value = emails
        result = self.mock_client.get_emails_list()
        self.assertEqual(result, emails)
        self.mock_client.get_emails_list.assert_called_once()

    def test_get_email_content(self):
        email_content = {"id": "1", "subject": "Hello", "body": "This is a test email."}
        self.mock_client.get_email_content.return_value = email_content
        result = self.mock_client.get_email_content("1")
        self.assertEqual(result, email_content)
        self.mock_client.get_email_content.assert_called_once_with("1")

    def test_send_email(self):
        self.mock_client.send_email.return_value = True
        result = self.mock_client.send_email("recipient@example.com", "Test Subject", "Test Body")
        self.assertTrue(result)
        self.mock_client.send_email.assert_called_once_with("recipient@example.com", "Test Subject", "Test Body")

    def test_delete_email(self):
        self.mock_client.delete_email.return_value = True
        result = self.mock_client.delete_email("1")
        self.assertTrue(result)
        self.mock_client.delete_email.assert_called_once_with("1")

    def test_mark_as_read(self):
        self.mock_client.mark_as_read.return_value = True
        result = self.mock_client.mark_as_read("1")
        self.assertTrue(result)
        self.mock_client.mark_as_read.assert_called_once_with("1")


if __name__ == "__main__":
    unittest.main()
