"""Implementation of the Gmail interface."""

import base64
import binascii
import logging
from base64 import urlsafe_b64encode
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError

from . import GmailClientInterface

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class GmailClientImpl(GmailClientInterface):
    """Implement the GmailClientInterface."""

    def __init__(self) -> None:
        """Initialize."""
        super().__init__()
        self.__connected: bool = False
        self.__authenticated: bool = False
        self.__current_user: str | None = None
        self.__current_mailbox: str | None = None
        self.__service: Resource | None = None
        self.__creds: Credentials | None = None

        # Test user name, password database
        self.__users: dict[str, str] = {
            "alice": "password123",
            "bob": "123456",
        }

        # Test token database
        self.__valid_tokens: dict[str, str] = {
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
                self.__creds = Credentials.from_authorized_user_file(str(token_path), SCOPES) # type: ignore[no-untyped-call]

            # Check if credentials need to be refreshed or obtained
            if self.__creds is None or not self.__creds.valid:
                if self.__creds and self.__creds.expired and self.__creds.refresh_token:
                    self.__creds.refresh(Request()) # type: ignore[no-untyped-call]
                    # Save the refreshed credentials
                    with token_path.open("w") as token:
                        token.write(self.__creds.to_json()) # type: ignore[no-untyped-call]
                else:
                    # No valid credentials, initiate OAuth flow
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_path),
                        SCOPES,
                    )
                    new_creds = flow.run_local_server(port=0)
                    if new_creds:
                        self.__creds = new_creds
                        # Save the new credentials (Moved inside the 'if' block)
                        with token_path.open("w") as token:
                            token.write(self.__creds.to_json()) # type: ignore[union-attr]
                    else:
                        # Handle case where flow failed unexpectedly without raising
                        self._handle_oauth_flow_failure()


            # Build the Gmail service object
            self.__service = build("gmail", "v1", credentials=self.__creds)

        except (OSError, RefreshError, HttpError, RuntimeError): # Added RuntimeError
            logging.exception("Connection/Authentication failed")
            self.__service = None
            self.__connected = False
            self.__authenticated = False
            return False
        except Exception:
            logging.exception("An unexpected error occurred during connect")
            self.__service = None
            self.__connected = False
            self.__authenticated = False
            return False
        else:
            # Connection successful
            self.__connected = True
            return True

    def _handle_oauth_flow_failure(self) -> None:
        """Handle the specific case where OAuth flow fails to return credentials."""
        log_msg = "OAuth flow did not return credentials."
        logging.error(log_msg)
        error_msg = "OAuth flow failed to return credentials"
        raise RuntimeError(error_msg)

    def login(self, username: str, password: str) -> bool:
        """Login with username and password."""
        if username in self.__users and self.__users[username] == password:
            try:
                if not self.connect():
                    return False
            except (OSError, RefreshError, HttpError):
                logging.exception("Login failed during connection")
                self.__service = None
                self.__connected = False
                self.__authenticated = False
                self.__current_user = None
                return False
            except Exception:
                logging.exception("An unexpected error occurred during login")
                self.__service = None
                self.__connected = False
                self.__authenticated = False
                self.__current_user = None
                return False
            else:
                self.__authenticated = True
                self.__current_user = username
                return True
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
            except (OSError, RefreshError, HttpError):
                logging.exception("Authentication failed during connection")
                self.__service = None
                self.__connected = False
                self.__authenticated = False
                self.__current_user = None
                return False
            except Exception:
                logging.exception("An unexpected error occurred during authenticate")
                self.__service = None
                self.__connected = False
                self.__authenticated = False
                self.__current_user = None
                return False
            else:
                self.__authenticated = True
                self.__current_user = username
                return True
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
        except HttpError:
            logging.exception("Failed to use mailbox '%s'", mailbox)
            return False
        except Exception:
            logging.exception("An unexpected error occurred in use_mailbox")
            return False
        return False

    def fetch_mailboxes(self) -> list[str]:
        """Retrieve a list of available mailboxes/labels."""
        if not self.__authenticated or not self.__service:
            return []

        try:
            results = self.__service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
        except HttpError:
            logging.exception("Failed to fetch mailboxes")
            return []
        except Exception:
            logging.exception("An unexpected error occurred in fetch_mailboxes")
            return []
        else:
            return [label["name"] for label in labels]

    def get_emails_list(self, mailbox: str = "INBOX", limit: int = 10) -> list[dict[str, Any]]:
        """Fetch a list of emails from the specified mailbox."""
        if not self.__authenticated or not self.__service:
            return []

        email_list: list[dict[str, Any]] = [] # Ensure type hint for initialization
        try:
            # Get messages in the mailbox
            results = (
                self.__service.users()
                .messages()
                .list(
                    userId="me",
                    labelIds=[mailbox],
                    maxResults=limit,
                )
                .execute()
            )

            messages = results.get("messages", [])

            if not messages:
                pass # Let it return the initialized empty list at the end
            else:
                for msg in messages:
                    # Get the full message details
                    message = (
                        self.__service.users()
                        .messages()
                        .get(
                            userId="me",
                            id=msg["id"],
                            format="metadata",
                            metadataHeaders=["From", "Subject"],
                        )
                        .execute()
                    )

                    headers = message["payload"]["headers"]
                    email_data = {
                        "id": msg["id"],
                        "snippet": message.get("snippet", ""),
                        "subject": "",
                        "sender": "",
                    }

                    # Extract subject and sender from headers
                    for header in headers:
                        if header["name"] == "Subject":
                            email_data["subject"] = header["value"]
                        elif header["name"] == "From":
                            email_data["sender"] = header["value"]

                    email_list.append(email_data)

        except HttpError:
            logging.exception("Failed to get email list for mailbox '%s'", mailbox)
            # Return initial empty list at the end
        except Exception:
            logging.exception("An unexpected error occurred in get_emails_list")
            # Return initial empty list at the end
        # No else block needed, email_list is populated in try if successful

        return email_list # Single return point

    def _parse_email_headers(self, headers: list[dict[str, str]]) -> dict[str, str]:
        """Parse relevant fields from email headers."""
        parsed_headers = {"subject": "", "sender": "", "date": "", "to": ""}
        for header in headers:
            name = header.get("name", "").lower()
            value = header.get("value", "")
            if name == "subject":
                parsed_headers["subject"] = value
            elif name == "from":
                parsed_headers["sender"] = value
            elif name == "date":
                parsed_headers["date"] = value
            elif name == "to":
                parsed_headers["to"] = value
        return parsed_headers

    def _extract_email_body(self, payload: dict[str, Any]) -> str:
        """Extract the plain text body from the email payload."""
        body = ""
        if "parts" in payload:
            parts = payload.get("parts", [])
            for part in parts:
                if part.get("mimeType") == "text/plain":
                    body_data = part.get("body", {}).get("data")
                    body = body_data if body_data else ""
                    break  # Assume first text/plain part is the body
        elif "body" in payload:
            body_data = payload.get("body", {}).get("data")
            body = body_data if body_data else ""

        # Decode body from base64 if needed
        if body:
            try:
                # It's common for email bodies (especially non-ASCII) to be base64 encoded
                body = base64.urlsafe_b64decode(body).decode("utf-8")
            except (binascii.Error, UnicodeDecodeError, ValueError) as e:
                # Log a warning if decoding fails, but proceed with the raw data
                logging.warning("Failed to decode base64 email body, returning raw data: %s", e)
                # Keep original 'body' which is the raw base64 data

        return body

    def get_email_content(self, email_id: str) -> dict[str, Any]:
        """Fetch the full content of a specific email."""
        if not self.__authenticated or not self.__service:
            return {}

        try:
            # Get the full message
            message = (
                self.__service.users()
                .messages()
                .get(
                    userId="me",
                    id=email_id,
                    format="full",
                )
                .execute()
            )

            payload = message.get("payload", {})
            headers = payload.get("headers", [])

            parsed_headers = self._parse_email_headers(headers)
            body = self._extract_email_body(payload)

        except HttpError:
            logging.exception("Failed to get email content for ID '%s'", email_id)
            return {}
        except Exception:
            logging.exception("An unexpected error occurred in get_email_content")
            return {}
        else:
            # Construct and return dictionary in the else block
            return {
                "id": email_id,
                "subject": parsed_headers["subject"],
                "sender": parsed_headers["sender"],
                "date": parsed_headers["date"],
                "to": parsed_headers["to"],
                "body": body,
            }

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email to the specified recipient."""
        if not self.__authenticated or not self.__service:
            return False

        success = False # Initialize success flag
        try:
            # Create message
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject

            # Encode the message
            encoded_message = urlsafe_b64encode(message.as_bytes()).decode()

            # Send the email
            self.__service.users().messages().send(
                userId="me",
                body={"raw": encoded_message},
            ).execute()
            success = True # Set flag on success
        except HttpError:
            logging.exception("Failed to send email to '%s'", to)
            # Let it return False at the end
        except Exception:
            logging.exception("An unexpected error occurred in send_email")
            # Let it return False at the end
        # Remove else block

        return success # Single return point

    def delete_email(self, email_id: str) -> bool:
        """Delete an email by its ID."""
        if not self.__authenticated or not self.__service:
            return False

        success = False # Initialize success flag
        try:
            self.__service.users().messages().trash(
                userId="me",
                id=email_id,
            ).execute()
            success = True # Set flag on success
        except HttpError:
            logging.exception("Failed to delete email ID '%s'", email_id)
            # Let it return False at the end
        except Exception:
            logging.exception("An unexpected error occurred in delete_email")
            # Let it return False at the end
        # Remove else block

        return success # Single return point

    def mark_as_read(self, email_id: str) -> bool:
        """Mark an email as read."""
        if not self.__authenticated or not self.__service:
            return False

        success = False # Initialize success flag
        try:
            self.__service.users().messages().modify(
                userId="me",
                id=email_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
            success = True # Set flag on success
        except HttpError:
            logging.exception("Failed to mark email ID '%s' as read", email_id)
            # Let it return False at the end
        except Exception:
            logging.exception("An unexpected error occurred in mark_as_read")
            # Let it return False at the end
        # Remove else block

        return success # Single return point
