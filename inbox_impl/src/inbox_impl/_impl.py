"""Implementation of the Gmail interface."""

import base64
import binascii
import json
import logging
import os
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError
from inbox_api.src.inbox_api import GmailClientInterface

from .scopes import SCOPES

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

        self.__users: dict[str, str] = {
            "alice": "password123",
            "bob": "123456",
        }

        self.__valid_tokens: dict[str, str] = {
            "alice": "TOKEN123",
            "bob": "TOKEN456",
        }

    def is_connected(self) -> bool:
        """Return true if connected."""
        return self.__connected and self.__service is not None

    def _connect_with_service_account(self) -> bool:
        """Attempt connection using service account credentials from environment variables."""
        service_account_key_json = os.environ.get("GMAIL_SERVICE_ACCOUNT_KEY_JSON")
        if not service_account_key_json:
            return False

        logging.info("Attempting service account authentication from environment variable.")
        try:
            key_info: dict[str, Any] = json.loads(service_account_key_json)
            self.__creds = service_account.Credentials.from_service_account_info(
                key_info,
                scopes=SCOPES,
            ) # type: ignore[no-untyped-call]
            self.__service = build("gmail", "v1", credentials=self.__creds)
        except json.JSONDecodeError:
            logging.exception("Failed to parse GMAIL_SERVICE_ACCOUNT_KEY_JSON.")
            self.__service = None
            self.__connected = False
            return False
        except Exception:
            logging.exception("Service account authentication failed")
            self.__service = None
            self.__connected = False
            return False
        else:
            self.__connected = True
            logging.info("Service account authentication successful.")
            return True

    def _connect_with_oauth(self) -> bool:
        """Attempt connection using local OAuth flow (token.json/credentials.json)."""
        logging.info("Attempting local OAuth authentication (token/credentials files).")
        try:
            root_dir = Path(__file__).resolve().parent.parent
            token_path = root_dir / "hw2_inbox" / "token.json"
            credentials_path = root_dir / "hw2_inbox" / "resources" / "credentials.json"

            self.__creds = None

            if token_path.exists():
                self.__creds = Credentials.from_authorized_user_file(str(token_path), SCOPES) # type: ignore[no-untyped-call]

            if self.__creds is None or not self.__creds.valid:
                if self.__creds and self.__creds.expired and self.__creds.refresh_token:
                    self.__creds.refresh(Request()) # type: ignore[no-untyped-call]
                    with token_path.open("w") as token:
                        token.write(self.__creds.to_json())
                elif credentials_path.exists():
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_path),
                        SCOPES,
                    )
                    new_creds = flow.run_local_server(port=0)
                    if new_creds:
                        self.__creds = new_creds
                        with token_path.open("w") as token:
                            token.write(self.__creds.to_json()) # type: ignore[union-attr]
                    else:
                        self._handle_oauth_flow_failure()
                else:
                    logging.error("OAuth failed: No token.json, refresh_token, or credentials.json found.")
                    return False

            self.__service = build("gmail", "v1", credentials=self.__creds)

        except (OSError, RefreshError, HttpError, RuntimeError):
            logging.exception("Local OAuth connection/authentication failed")
            self.__service = None
            self.__connected = False
            self.__authenticated = False
            return False
        except Exception:
            logging.exception("An unexpected error occurred during local OAuth connect")
            self.__service = None
            self.__connected = False
            self.__authenticated = False
            return False
        else:
            self.__connected = True
            self.__authenticated = True
            logging.info("Local OAuth authentication successful.")
            return True

    def connect(self) -> bool:
        """Establish a connection to the Gmail service, trying Service Account then OAuth."""
        self.__service = None
        self.__creds = None
        self.__connected = False

        if self._connect_with_service_account():
            return True

        if self._connect_with_oauth():
            return True

        logging.error("Failed to connect using both service account and OAuth methods.")
        return False

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
            
            visible_labels = []
            important_system_labels = {"INBOX", "SENT", "DRAFT", "STARRED", "TRASH"}
            
            for label in labels:
                label_name = label.get("name", "")
                label_type = label.get("type", "")
                
                if label_name in important_system_labels:
                    visible_labels.append(label_name)
                    continue
                
                if (label_type == "user" or
                    (label_type == "system" and
                     label.get("labelListVisibility") != "labelHide")):
                    visible_labels.append(label_name)
            
            return sorted(visible_labels)

        except HttpError:
            logging.exception("Failed to fetch mailboxes")
            return []
        except Exception:
            logging.exception("An unexpected error occurred in fetch_mailboxes")
            return []

    def _get_email_metadata(self, message_id: str) -> dict[str, Any] | None:
        """Fetch metadata for a single email."""
        result_data: dict[str, Any] | None = None
        if self.__service is None:
            logging.error("Cannot fetch metadata: service not available")
            return None
        try:
            message = self.__service.users().messages().get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()

            headers = message.get("payload", {}).get("headers", [])
            email_data = {
                "id": message_id,
                "snippet": message.get("snippet", ""),
                "subject": "",
                "sender": "",
                "date": "",
            }

            for header in headers:
                name = header.get("name", "").lower()
                if name == "subject":
                    email_data["subject"] = header.get("value", "")
                elif name == "from":
                    email_data["sender"] = header.get("value", "")
                elif name == "date":
                    email_data["date"] = header.get("value", "")

            logging.debug(
                "Retrieved metadata: subject='%s', from='%s'",
                email_data["subject"],
                email_data["sender"],
            )
            result_data = email_data

        except HttpError as e:
            logging.warning("Failed to fetch details for message %s: %s", message_id, str(e))

        return result_data

    def get_emails_list(self, mailbox: str = "INBOX", limit: int = 10) -> list[dict[str, Any]]:
        """Fetch a list of emails from the specified mailbox."""
        if not self.__authenticated or not self.__service:
            logging.error("Cannot get emails: not authenticated or service not available")
            return []

        email_list: list[dict[str, Any]] = []
        try:
            labels = self.fetch_mailboxes()
            if mailbox not in labels and mailbox != "INBOX":
                logging.warning("Mailbox '%s' not found in available labels: %s", mailbox, labels)
                return []

            logging.info("Fetching up to %d messages from mailbox '%s'", limit, mailbox)
            query = self.__service.users().messages().list(
                userId="me",
                labelIds=[mailbox],
                maxResults=limit,
            )
            
            results = query.execute()
            messages = results.get("messages", [])

            if not messages:
                logging.info("No messages found in mailbox '%s' (this is normal for empty mailboxes)", mailbox)
                return []

            for msg in messages:
                email_metadata = self._get_email_metadata(msg["id"])
                if email_metadata:
                    email_list.append(email_metadata)

            logging.info("Successfully retrieved %d emails from mailbox '%s'", len(email_list), mailbox)

        except HttpError:
            logging.exception("Failed to get email list for mailbox '%s'", mailbox)
            return [] # Return empty list on HttpError
        except Exception:
            logging.exception("An unexpected error occurred in get_emails_list")
            return []
        else:
            return email_list

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
                    break
        elif "body" in payload:
            body_data = payload.get("body", {}).get("data")
            body = body_data if body_data else ""

        if body:
            try:
                body = base64.urlsafe_b64decode(body).decode("utf-8")
            except (binascii.Error, UnicodeDecodeError, ValueError) as e:
                logging.warning("Failed to decode base64 email body, returning raw data: %s", e)

        return body

    def get_email_content(self, email_id: str) -> dict[str, Any]:
        """Fetch the full content of a specific email."""
        if not self.__authenticated or not self.__service:
            return {}

        try:
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
            logging.error("Cannot send email: not authenticated or service not available")
            return False

        try:
            message = MIMEText(body, "plain", "utf-8")
            message["to"] = to
            message["from"] = "me"
            message["subject"] = subject

            raw = base64.urlsafe_b64encode(message.as_bytes())
            raw_string = raw.decode("utf-8")
            
            try:
                self.__service.users().messages().send(
                    userId="me",
                    body={"raw": raw_string},
                ).execute()
                logging.info("Successfully sent email to %s", to)
            except HttpError as error:
                error_details = error.error_details if hasattr(error, "error_details") else str(error)
                logging.exception("Failed to send email via Gmail API: %s", error_details)
                return False
            else:
                return True

        except Exception:
            logging.exception("Error preparing email message")
            return False

    def delete_email(self, email_id: str) -> bool:
        """Delete an email by its ID."""
        if not self.__authenticated or not self.__service:
            return False

        success = False
        try:
            self.__service.users().messages().trash(
                userId="me",
                id=email_id,
            ).execute()
            success = True
        except HttpError:
            logging.exception("Failed to delete email ID '%s'", email_id)
        except Exception:
            logging.exception("An unexpected error occurred in delete_email")

        return success

    def modify_email_labels(self, email_id: str, add_labels: list[str] | None = None, remove_labels: list[str] | None = None) -> bool:
        """Modify the labels of an email (e.g., mark as read/unread, starred, etc.)."""
        if not self.__authenticated or not self.__service:
            logging.warning("Cannot modify labels: Not authenticated or service not available.")
            return False

        modify_request: dict[str, Any] = {}
        if add_labels:
            modify_request["addLabelIds"] = add_labels
        if remove_labels:
            modify_request["removeLabelIds"] = remove_labels

        if not modify_request:
            logging.info("No labels specified to add or remove for email ID '%s'.", email_id)
            return True

        success = False
        try:
            self.__service.users().messages().modify(
                userId="me",
                id=email_id,
                body=modify_request,
            ).execute()
            logging.info(
                "Successfully modified labels for email ID '%s': Added=%s, Removed=%s",
                email_id,
                add_labels or "None",
                remove_labels or "None",
            )
            success = True
        except HttpError:
            logging.exception(
                "Failed to modify labels for email ID '%s'.", email_id,
            )
        except Exception:
            logging.exception(
                "An unexpected error occurred while modifying labels for email ID '%s'.", email_id,
            )

        return success
