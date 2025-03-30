from abc import ABC, abstractmethod
from typing import List, Dict

class GmailClientInterface(ABC):
    """
    Interface definition for a Gmail-based email assistant client.
    This interface outlines the core functionalities such as reading,
    sending, deleting, and marking emails.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish a connection to the Gmail server or service.
        
        Returns:
            bool: True if connection is successful, False otherwise.
        """
        pass
        
    @abstractmethod
    def login(self, username: str, password: str) -> bool:
        """
        Login to the Gmail account using username and password.
        
        Args:
            username (str): User's email address.
            password (str): User's password.
        
        Returns:
            bool: True if login is successful, False otherwise.
        """
        pass
        
    @abstractmethod
    def authenticate(self, username: str, access_token: str) -> bool:
        """
        Authenticate using OAuth token instead of password.
        
        Args:
            username (str): User's email address.
            access_token (str): OAuth access token.
        
        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        pass
        
    @abstractmethod
    def logout(self) -> None:
        """
        Logout from the Gmail session.
        """
        pass
        
    @abstractmethod
    def fetch_mailboxes(self) -> list[str]:
        """
        Retrieve a list of available mailboxes/labels.
        
        Returns:
            List[str]: List of mailbox names.
        """
        pass
        
    @abstractmethod
    def use_mailbox(self, mailbox: str) -> bool:
        """
        Select the mailbox to operate on.
        
        Args:
            mailbox (str): The name of the mailbox to use.
        
        Returns:
            bool: True if mailbox was selected successfully, False otherwise.
        """
        pass
        


    @abstractmethod
    def get_emails_list(self) -> List[Dict]:
        """
        Fetch a list of emails.

        Returns:
            List[Dict]: A list of email metadata, each represented as a dictionary
                        containing fields such as 'subject', 'sender', 'snippet', etc.
        """
        pass
    
    @abstractmethod
    def get_email_content(self, email_id: str) -> Dict:
        """
        Fetch the full content of a specific email.

        Args:
            email_id (str): Unique identifier of the email.

        Returns:
            Dict[str, Any]: Dictionary containing detailed email content.
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