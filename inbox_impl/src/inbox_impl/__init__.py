"""Gmail Client API implementation package."""

from typing import Protocol

from ._impl import GmailClientImpl


class GmailClientInterface(Protocol):
    """Interface for Gmail client operations."""

    def connect(self) -> bool:
        """Establish connection to Gmail service.
        
        Returns:
            bool: True if connection successful, False otherwise.

        """
        ...

    def login(self, username: str, password: str) -> bool:
        """Login with username and password.
        
        Args:
            username: The username to login with
            password: The password for authentication
            
        Returns:
            bool: True if login successful, False otherwise.

        """
        ...

    def authenticate(self, username: str, token: str) -> bool:
        """Authenticate with username and access token.
        
        Args:
            username: The username to authenticate
            token: The access token for authentication
            
        Returns:
            bool: True if authentication successful, False otherwise.

        """
        ...

    def logout(self) -> None:
        """Logout the current user and clear session."""
        ...

    def is_connected(self) -> bool:
        """Check if client is currently connected.
        
        Returns:
            bool: True if connected, False otherwise.

        """
        ...

def get_client() -> GmailClientInterface:
    """Get a factory that returns a *fresh instance* each call."""
    return GmailClientImpl()

__all__: list[str] = ["GmailClientImpl", "GmailClientInterface", "get_client"]
