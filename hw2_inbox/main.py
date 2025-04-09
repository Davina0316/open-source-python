"""Implementation of the Gmail interface."""

from . import GmailClientInterface


class GmailClientImpl(GmailClientInterface):
    """Implement the GmailClientInterface."""

    def __init__(self) -> None:
        """Initialize."""
        super().__init__()
        self.__connected = False

    def is_connected(self) -> bool:
        """Return true if connected."""
        return self.__connected

    def connect(self) -> bool:
        """Establish a connection to the Gmail server or service."""
        return self.__connected

    def login(self, username: str, password: str) -> bool:
        raise NotImplementedError("login method not implemented")

    def logout(self) -> None:
        raise NotImplementedError("logout method not implemented")

    def authenticate(self, token: str) -> bool:
        raise NotImplementedError("authenticate method not implemented")

    def use_mailbox(self, mailbox: str) -> None:
        raise NotImplementedError("use_mailbox method not implemented")

    def fetch_mailboxes(self) -> list[str]:
        raise NotImplementedError("fetch_mailboxes method not implemented")

    def get_emails_list(self, mailbox: str, limit: int = 10) -> list[str]:
        raise NotImplementedError("get_emails_list method not implemented")

    def get_email_content(self, email_id: str) -> str:
        raise NotImplementedError("get_email_content method not implemented")

    def send_email(self, to: str, subject: str, body: str) -> bool:
        raise NotImplementedError("send_email method not implemented")

    def delete_email(self, email_id: str) -> bool:
        raise NotImplementedError("delete_email method not implemented")

    def mark_as_read(self, email_id: str) -> bool:
        raise NotImplementedError("mark_as_read method not implemented")
