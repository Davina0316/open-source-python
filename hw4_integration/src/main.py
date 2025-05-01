import logging
import sys
from pathlib import Path
from typing import Any

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from hw4_integration.src.ai_wrapper import get_spam_probability  # noqa: E402
from hw4_integration.src.write_spam_csv import write_spam_results  # noqa: E402
from inbox_impl.src.inbox_impl._impl import GmailClientImpl  # noqa: E402

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
)


class MailAiIntegration:
    """Integrates Gmail and AI spam detection."""

    def __init__(self) -> None:
        """Initialize the MailAiIntegration class."""
        self.gmail_client = GmailClientImpl()

    def connect(self) -> bool:
        """Connect to the Gmail service."""
        return self.gmail_client.connect()

    def crawl_get_email_content(self, mailbox: str = "INBOX", limit: int = 10) -> tuple[list[str], list[str]]:
        """Crawl Gmail inbox, retrieve email bodies and their IDs."""
        email_bodies = []
        mail_ids = []

        try:
            logging.info("Fetching emails from %s...", mailbox)
            email_list = self.gmail_client.get_emails_list(mailbox=mailbox, limit=limit)
            if not email_list:
                logging.warning("No emails found in %s.", mailbox)
                return [], []

            for email in email_list:
                mail_id = email.get("id", "")
                if not mail_id:
                    continue

                content: dict[str, Any] = self.gmail_client.get_email_content(mail_id)
                body = content.get("body", "") if content else ""
                if body.strip():
                    email_bodies.append(body)
                    mail_ids.append(mail_id)

            logging.info("Retrieved %d valid email bodies.", len(email_bodies))
            result = (email_bodies, mail_ids)

        except Exception:
            logging.exception("Failed to crawl Gmail.")
            result = ([], [])
        return result

    def analyze_and_write_csv(self, email_bodies: list[str], mail_ids: list[str]) -> None:
        """Analyze email bodies for spam probability and write results to CSV."""
        results = []
        for body, mail_id in zip(email_bodies, mail_ids, strict=False):
            try:
                pct_spam = get_spam_probability(body)
                results.append({"mail_id": mail_id, "Pct_spam": round(pct_spam, 2)})
            except Exception:
                logging.exception("AI detection failed for email %s", mail_id)

        write_spam_results(results)


if __name__ == "__main__":
    integration = MailAiIntegration()

    if integration.connect():
        logging.info("Connected to Gmail successfully.")

        email_bodies, mail_ids = integration.crawl_get_email_content(limit=10)

        if email_bodies:
            integration.analyze_and_write_csv(email_bodies, mail_ids)
            logging.info("Spam analysis completed and written to CSV.")
        else:
            logging.warning("No valid emails to process.")

    else:
        logging.error("Failed to connect to Gmail.")
