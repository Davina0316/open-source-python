"""Implementation of the Gmail interface."""

from . import GmailClientInterface
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

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
        """Establish a connection to the Gmail server or service.
        
        Call the auth api if token does not exist or is not valid.
        Otherwise, no additional actions needed.
        """
        creds = None
        root_dir = Path(__file__).resolve().parent.parent  # <- project root
        token_path = root_dir / "hw2_inbox" / "token.json"
        credentials_path = root_dir / "hw2_inbox" / "resources" / "credentials.json"
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, "w") as token:
               token.write(creds.to_json())
        self.__connected = True
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
