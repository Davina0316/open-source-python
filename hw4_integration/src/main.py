import logging
import sys
from pathlib import Path
from typing import Any

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from inbox_impl.src.inbox_impl._impl import GmailClientImpl  # noqa: E402

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
)


class MailAiIntegration:
    """Integrates Gmail functionalities."""

    def __init__(self) -> None:
        """Initialize the MailAiIntegration."""
        self.gmail_client = GmailClientImpl()

    def connect(self) -> bool:
        """Connect to the Gmail service.

        Returns:
            bool: True if connection is successful, False otherwise.

        """
        return self.gmail_client.connect()

    def crawl_get_email_content(
        self,
        mailbox: str = "INBOX",
        limit: int = 10,
    ) -> list[str] | None:
        """Crawl and retrieve the body content of the latest emails.

        Args:
            mailbox: The mailbox to crawl (default: "INBOX").
            limit: The maximum number of emails to retrieve (default: 10).

        Returns:
            A list of email bodies (strings), or None if the initial list fetch fails.
            Errors fetching individual emails are logged but don't cause a None return.

        """
        email_bodies: list[str] = []
        try:
            logging.info("Fetching the latest %d emails from %s...", limit, mailbox)
            email_list = self.gmail_client.get_emails_list(mailbox=mailbox, limit=limit)

            if not email_list:
                logging.warning("No emails found in %s.", mailbox)
                return []
            logging.info("Found %d email(s) in %s.", len(email_list), mailbox)

        except Exception:
            logging.exception("Failed to get email list from %s", mailbox)
            return None
        else:
            for email_summary in email_list:
                email_id = email_summary.get("id")
                if not email_id:
                    logging.warning("Found an email summary without an ID, skipping.")
                    continue

                try:
                    logging.debug("Fetching content for email ID: %s", email_id)
                    content: dict[str, Any] | None = (
                        self.gmail_client.get_email_content(email_id)
                    )
                    if content:
                        body = content.get("body")
                        if body:
                            email_bodies.append(body)
                            logging.debug("Successfully fetched body for ID: %s", email_id)
                        else:
                            logging.warning(
                                "Email content found for ID %s, but body was missing.",
                                email_id,
                            )
                    else:
                        logging.warning(
                            "get_email_content returned None or empty for ID %s", email_id,
                        )
                except Exception:
                    logging.exception("Error fetching content for email ID %s", email_id)

            logging.info(
                "Successfully processed %d emails, retrieved %d bodies.",
                len(email_list),
                len(email_bodies),
            )
            return email_bodies

    def ai_client_detect_email_type(self, email_content: str) -> None:
        """Detect the type of email based on the content (Placeholder)."""
        logging.info("AI detection called for content: %s...", email_content[:100])


if __name__ == "__main__":
    integration = MailAiIntegration()
    if integration.connect():
        logging.info("Successfully connected to Gmail.")
        retrieved_bodies = integration.crawl_get_email_content()
        if retrieved_bodies is not None:
            logging.info("Retrieved %d email bodies.", len(retrieved_bodies))
            if retrieved_bodies:
                integration.ai_client_detect_email_type(retrieved_bodies[0])
        else:
            logging.error("Failed to retrieve email content.")

    else:
        logging.error("Failed to connect to Gmail.")

