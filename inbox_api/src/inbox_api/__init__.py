"""Gmail Client interface defenition.

Including how the client should connect/disconnect to Gmail,
and the functionalities of the client such as reading, sending,
deleting, and marking emails.
"""

from abc import ABC, abstractmethod
from typing import Any


class GmailClientInterface(ABC):
    """Interface definition for a Gmail-based email assistant client.

    This interface outlines the core functionalities such as reading,
    sending, deleting, and marking emails.
    """

    @abstractmethod
    def is_connected(self) -> bool:
        """Return true if current status is connected."""

    @abstractmethod
    def connect(self) -> bool:
        """Establish a connection to the Gmail server or service.

        Returns:
            bool: True if connection is successful, False otherwise.

        """

    @abstractmethod
    def login(self, username: str, password: str) -> bool:
        """Login to the Gmail account using username and password.

        Args:
            username (str): User's email address.
            password (str): User's password.

        Returns:
            bool: True if login is successful, False otherwise.

        """

    @abstractmethod
    def authenticate(self, username: str, access_token: str) -> bool:
        """Authenticate using OAuth token instead of password.

        Args:
            username (str): User's email address.
            access_token (str): OAuth access token.

        Returns:
            bool: True if authentication is successful, False otherwise.

        """

    @abstractmethod
    def logout(self) -> None:
        """Logout from the Gmail session."""

    @abstractmethod
    def fetch_mailboxes(self) -> list[str]:
        """Retrieve a list of available mailboxes/labels.

        Returns:
            List[str]: List of mailbox names.

        """

    @abstractmethod
    def use_mailbox(self, mailbox: str) -> bool:
        """Select the mailbox to operate on.

        Args:
            mailbox (str): The name of the mailbox to use.

        Returns:
            bool: True if mailbox was selected successfully, False otherwise.

        """

    @abstractmethod
    def get_emails_list(self) -> list[dict[str, Any]]:
        """Fetch a list of emails.

        Returns:
            List[Dict]: A list of email metadata, each represented as a dictionary
                        containing fields such as 'id', 'threadId', 'subject', 'sender',
                        'date', and 'snippet'.

        """

    @abstractmethod
    def get_email_content(self, email_id: str) -> dict[str, Any]:
        """Fetch the full content of a specific email.

        Args:
            email_id (str): Unique identifier of the email.

        Returns:
            Dict[str, Any]: Dictionary containing detailed email content.

        """

    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email.

        Args:
            to (str): Recipient email address
            subject (str): Email subject
            body (str): Email body content

        Returns:
            bool: True if sent successfully, False otherwise

        """

    @abstractmethod
    def delete_email(self, email_id: str) -> bool:
        """Delete an email by its ID.

        Args:
            email_id (str): Unique identifier of the email

        Returns:
            bool: True if deleted successfully, False otherwise

        """

    @abstractmethod
    def modify_email_labels(self, email_id: str, add_labels: list[str] | None = None, remove_labels: list[str] | None = None) -> bool:
        """Modify the labels of an email (e.g., mark as read/unread, starred, etc.).

        Args:
            email_id (str): Unique identifier of the email.
            add_labels (List[str], optional): List of labels to add (e.g., ['UNREAD', 'STARRED']). Defaults to None.
            remove_labels (List[str], optional): List of labels to remove (e.g., ['READ']). Defaults to None.

        Returns:
            bool: True if labels were modified successfully, False otherwise.

        """

def get_client() -> GmailClientInterface:
    """Return an instance of a Mail Client."""
    raise NotImplementedError

__all__: list[str] = ["GmailClientInterface", "get_client"]
