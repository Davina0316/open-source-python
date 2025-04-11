"""Implementation of the Gmail interface."""

from pathlib import Path
from typing import Dict, List, Any, Optional
from base64 import urlsafe_b64encode

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText

from . import GmailClientInterface

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify"
]

class GmailClientImpl(GmailClientInterface):
    """Implement the GmailClientInterface."""

    def __init__(self) -> None:
        """Initialize."""
        super().__init__()
        self.__connected = False
        self.__authenticated = False
        self.__current_user = None
        self.__current_mailbox = None
        self.__service = None
        self.__creds = None

        # Test user name, password database
        self.__users = {
            "alice": "password123",
            "bob": "123456",
        }

        # Test token database
        self.__valid_tokens = {
            "alice": "TOKEN123",
            "bob": "TOKEN456",
        }

    def is_connected(self) -> bool:
        """Return true if connected."""
        return self.__connected and self.__service is not None

    def connect(self) -> bool:
        """Establish a connection to the Gmail server or service."""
        try:
            root_dir = Path(__file__).resolve().parent.parent
            token_path = root_dir / "hw2_inbox" / "token.json"
            credentials_path = root_dir / "hw2_inbox" / "resources" / "credentials.json"

            if token_path.exists():
                self.__creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

            if not self.__creds or not self.__creds.valid:
                if self.__creds and self.__creds.expired and self.__creds.refresh_token:
                    self.__creds.refresh(Request())
                    with open(str(token_path), "w") as token:
                        token.write(self.__creds.to_json())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_path), SCOPES,
                    )
                    self.__creds = flow.run_local_server(port=0)
                    with open(str(token_path), "w") as token:
                        token.write(self.__creds.to_json())

            self.__service = build('gmail', 'v1', credentials=self.__creds)
            self.__connected = True
            return True
        except Exception:
            self.__service = None
            self.__connected = False
            self.__authenticated = False
            return False

    def login(self, username: str, password: str) -> bool:
        """Login with username and password."""
        if username in self.__users and self.__users[username] == password:
            try:
                if not self.connect():
                    return False
                self.__authenticated = True
                self.__current_user = username
                return True
            except Exception:
                self.__service = None
                self.__connected = False
                self.__authenticated = False
                self.__current_user = None
                return False
        return False

    def logout(self) -> None:
        """Logout the user."""
        self.__connected = False
        self.__authenticated = False
        self.__current_user = None
        self.__current_mailbox = None
        self.__service = None
        self.__creds = None

    def authenticate(self, username: str, access_token: str) -> bool:
        """Authenticate with username and token."""
        if username in self.__valid_tokens and self.__valid_tokens[username] == access_token:
            try:
                if not self.connect():
                    return False
                self.__authenticated = True
                self.__current_user = username
                return True
            except Exception:
                self.__service = None
                self.__connected = False
                self.__authenticated = False
                self.__current_user = None
                return False
        return False

    def use_mailbox(self, mailbox: str) -> bool:
        """Select a mailbox to operate on."""
        if not self.__authenticated or not self.__service:
            return False
        
        try:
            # Verify mailbox exists
            labels = self.fetch_mailboxes()
            if mailbox in labels:
                self.__current_mailbox = mailbox
                return True
            return False
        except Exception:
            return False

    def fetch_mailboxes(self) -> List[str]:
        """Retrieve a list of available mailboxes/labels."""
        if not self.__authenticated or not self.__service:
            return []
        
        try:
            results = self.__service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            return [label['name'] for label in labels]
        except Exception:
            return []

    def get_emails_list(self, mailbox: str = 'INBOX', limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch a list of emails from the specified mailbox."""
        if not self.__authenticated or not self.__service:
            return []
        
        try:
            # Get messages in the mailbox
            results = self.__service.users().messages().list(
                userId='me',
                labelIds=[mailbox],
                maxResults=limit
            ).execute()

            messages = results.get('messages', [])
            email_list = []

            for msg in messages:
                # Get the full message details
                message = self.__service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject']
                ).execute()

                headers = message['payload']['headers']
                email_data = {
                    'id': msg['id'],
                    'snippet': message.get('snippet', ''),
                    'subject': '',
                    'sender': ''
                }

                # Extract subject and sender from headers
                for header in headers:
                    if header['name'] == 'Subject':
                        email_data['subject'] = header['value']
                    elif header['name'] == 'From':
                        email_data['sender'] = header['value']

                email_list.append(email_data)

            return email_list
        except Exception:
            return []

    def get_email_content(self, email_id: str) -> Dict[str, Any]:
        """Fetch the full content of a specific email."""
        if not self.__authenticated or not self.__service:
            return {}
        
        try:
            # Get the full message
            message = self.__service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']
            email_content = {
                'id': email_id,
                'subject': '',
                'sender': '',
                'body': '',
                'date': '',
                'to': ''
            }

            # Extract headers
            for header in headers:
                if header['name'] == 'Subject':
                    email_content['subject'] = header['value']
                elif header['name'] == 'From':
                    email_content['sender'] = header['value']
                elif header['name'] == 'Date':
                    email_content['date'] = header['value']
                elif header['name'] == 'To':
                    email_content['to'] = header['value']

            # Extract body
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        email_content['body'] = part['body'].get('data', '')
            else:
                email_content['body'] = message['payload']['body'].get('data', '')

            return email_content
        except Exception:
            return {}

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email to the specified recipient."""
        if not self.__authenticated or not self.__service:
            return False
        
        try:
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            # Encode the message
            encoded_message = urlsafe_b64encode(message.as_bytes()).decode()

            # Send the email
            self.__service.users().messages().send(
                userId='me',
                body={'raw': encoded_message}
            ).execute()
            return True
        except Exception:
            return False

    def delete_email(self, email_id: str) -> bool:
        """Delete an email by its ID."""
        if not self.__authenticated or not self.__service:
            return False
        
        try:
            self.__service.users().messages().trash(
                userId='me',
                id=email_id
            ).execute()
            return True
        except Exception:
            return False

    def mark_as_read(self, email_id: str) -> bool:
        """Mark an email as read."""
        if not self.__authenticated or not self.__service:
            return False
        
        try:
            self.__service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception:
            return False
