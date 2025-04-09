"""Implementation of the Gmail interface."""

from . import GmailClientInterface


class GmailClientImpl(GmailClientInterface):
    """Implement the GmailClientInterface."""

    def __init__(self) -> None:
        """Initialize."""
        super().__init__()
        self.__connected = False
        self.__authenticated = False #To mark if authenticated
        self.__current_user = None

        #Test user name, password database
        self.__users = {
            "alice": "password123",
            "bob": "123456"
        }

        #Test token database
        self.__valid_tokens = {
            "alice": "TOKEN123",
            "bob": "TOKEN456"
        }

    def is_connected(self) -> bool:
        """Return true if connected."""
        return self.__connected

    def connect(self) -> bool:
        """Establish a connection to the Gmail server or service."""
        return self.__connected

    def login(self, username: str, password: str) -> bool:
        """Login with username and password."""
        if not self.__connected:
            return False
        if username in self.__users and self.__users[username] == password:
            self.__authenticated = True
            self.__current_user = username
            return True
        return False

    def logout(self) -> None:
        """Logout the user."""
        self.__connected = False
        self.__authenticated = False
        self.__current_user = None

    def authenticate(self, token: str) -> bool:
        """Authenticate with token."""
        if token in self.__valid_tokens.values():
            self.__connected = True
            self.__authenticated = True
            #Finding corresponding user
            for user, user_token in self.__valid_tokens.items():
                if user_token == token:
                    self.__current_user = user
                    break
            return True
        return False

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
