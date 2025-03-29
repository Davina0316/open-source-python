from abc import ABC, abstractmethod
from typing import List, Dict

class GmailClientInterface(ABC):
    """
    Interface definition for a Gmail-based email assistant client.
    This interface outlines the core functionalities such as reading,
    sending, deleting, and marking emails.
    """

    @abstractmethod
    def get_emails(self) -> List[Dict]:
        """
        Fetch a list of emails.

        Returns:
            List[Dict]: A list of email metadata, each represented as a dictionary
                        containing fields such as 'subject', 'sender', 'snippet', etc.
        """
        pass

    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send an email.

        Args:
            to (str): Recipient email address
            subject (str): Email subject
            body (str): Email body content

        Returns:
            bool: True if sent successfully, False otherwise
        """
        pass

    @abstractmethod
    def delete_email(self, email_id: str) -> bool:
        """
        Delete an email by its ID.

        Args:
            email_id (str): Unique identifier of the email

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    def mark_as_read(self, email_id: str) -> bool:
        """
        Mark an email as read.

        Args:
            email_id (str): Unique identifier of the email

        Returns:
            bool: True if marked as read successfully, False otherwise
        """
        pass
