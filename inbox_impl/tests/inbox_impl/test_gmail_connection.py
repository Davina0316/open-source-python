import logging
import time
import traceback

from googleapiclient.errors import HttpError
from inbox_impl.src.inbox_impl._impl import GmailClientImpl


def test_gmail_features() -> None:
    gmail_client = GmailClientImpl()

    logging.info("\n1. Testing Gmail Connection...")
    connected = gmail_client.connect()

    if not connected:
        logging.error("Failed to connect to Gmail.")
        return

    logging.info("Successfully connected to Gmail!")

    logging.info("\n2. Testing Fetch Mailboxes...")
    mailboxes = []
    try:
        mailboxes = gmail_client.fetch_mailboxes()
        logging.info("Available mailboxes: %s", mailboxes)
        if not mailboxes:
            logging.warning("No mailboxes found. This is unusual for a Gmail account.")
    except HttpError as http_err:
        logging.error("HTTP error fetching mailboxes: %s", http_err)
        
    except Exception as e:
        logging.exception("Unexpected error fetching mailboxes: %s", e)

    logging.info("\n3. Testing INBOX access...")
    emails = [] 
    try:
        emails = gmail_client.get_emails_list(mailbox="INBOX", limit=1)
        if emails:
            logging.info("Successfully accessed INBOX!")
            logging.info("Found %d emails", len(emails))
        else:
            logging.warning("INBOX is empty or inaccessible")
            logging.info("Trying to list all labels to debug...")
            try:
                results = gmail_client._GmailClientImpl__service.users().labels().list(userId="me").execute() # type: ignore[attr-defined]
                logging.debug("Raw labels response: %s", results)
            except HttpError as label_http_err: 
                 logging.error("HTTP error getting raw labels: %s", label_http_err)
            except Exception as label_e: 
                logging.exception("Unexpected error getting raw labels: %s", label_e)
    except HttpError as inbox_http_err: 
        logging.error("HTTP error accessing INBOX: %s", inbox_http_err)
    except Exception as inbox_e: 
        logging.exception("Unexpected error accessing INBOX: %s", inbox_e)

    logging.info("\n4. Testing Send Email...")
    test_recipient = "racheltestingdev@gmail.com"  
    logging.info("Sending test email to %s...", test_recipient)
    try:
        success = gmail_client.send_email(
            to=test_recipient,
            subject="Test Email from Gmail API Client",
            body="This is a test email sent at " + time.strftime("%Y-%m-%d %H:%M:%S"),
        )
        if success:
            logging.info("Email sent successfully!")
        else:
            logging.error("Failed to send email (API returned False).")
    except HttpError as send_http_err: 
        logging.error("HTTP error sending email: %s", send_http_err)
    except Exception as send_e: 
        logging.exception("Unexpected error sending email: %s", send_e)

    logging.info("\n5. Testing Get Emails List...")
    logging.info("Fetching latest 5 emails from INBOX...")
    emails = [] 
    try:
        emails = gmail_client.get_emails_list(mailbox="INBOX", limit=5)
        if emails:
            for email in emails:
                logging.info("\nEmail ID: %s", email.get('id', 'N/A'))
                logging.info("Subject: %s", email.get('subject', 'N/A'))
                logging.info("From: %s", email.get('sender', 'N/A'))
                logging.info("Snippet: %s", email.get('snippet', 'N/A'))
        else:
            logging.info("No emails found in INBOX")
    except HttpError as list_http_err: 
        logging.error("HTTP error getting emails list: %s", list_http_err)
    except Exception as list_e: 
        logging.exception("Unexpected error getting emails list: %s", list_e)

    if emails:
        logging.info("\n6. Testing Get Email Content...")
        first_email_id = emails[0].get("id")
        if first_email_id:
            logging.info("Fetching content of email %s...", first_email_id)
            try:
                email_content = gmail_client.get_email_content(first_email_id)
                if email_content:
                    logging.info("\nSubject: %s", email_content.get('subject', 'N/A'))
                    logging.info("From: %s", email_content.get('sender', 'N/A'))
                    logging.info("To: %s", email_content.get('to', 'N/A'))
                    logging.info("Date: %s", email_content.get('date', 'N/A'))
                    body = email_content.get("body", "")
                    logging.info("\nBody preview: %s", body[:200] + "..." if len(body) > 200 else body)
                else:
                    logging.warning("Failed to get email content for ID %s", first_email_id)
            except HttpError as content_http_err: 
                logging.error("HTTP error getting email content for ID %s: %s", first_email_id, content_http_err)
            except Exception as content_e: 
                logging.exception("Unexpected error getting email content for ID %s: %s", first_email_id, content_e)
        else:
            logging.warning("Could not get ID from the first email in the list.")


def test_get_email_content() -> None:
    """Tests the get_email_content functionality of the GmailClientImpl."""
    gmail_client = GmailClientImpl()

    logging.info("1. Testing Gmail Connection...")
    connected = gmail_client.connect()

    if not connected:
        logging.error("Failed to connect to Gmail. Cannot proceed with testing get_email_content.")
        assert False, "Gmail connection failed" 

    logging.info("Successfully connected to Gmail!")

    logging.info("2. Fetching the latest email from INBOX to get an ID...")
    emails = []
    target_mailbox = "INBOX" 
    try:
        emails = gmail_client.get_emails_list(mailbox=target_mailbox, limit=1)
        if not emails:
            logging.warning(f"No emails found in {target_mailbox}. Cannot test get_email_content.")
            return 
        logging.info(f"Found {len(emails)} email(s) in {target_mailbox}.")

    except HttpError as list_http_err:
        logging.error(f"HTTP error getting emails list from {target_mailbox}: {list_http_err}")
        assert False, f"Failed to get email list: {list_http_err}"
    except Exception as list_e:
        logging.exception(f"Unexpected error getting emails list from {target_mailbox}: {list_e}")
        assert False, f"Unexpected error getting email list: {list_e}"

    if emails:
        first_email_id = emails[0].get("id")
        if not first_email_id:
            logging.error("Could not extract ID from the fetched email.")
            assert False, "Failed to get email ID"

        logging.info(f"3. Testing Get Email Content for ID: {first_email_id}...")
        try:
            email_content = gmail_client.get_email_content(first_email_id)

            # Assertions to validate the content
            assert email_content is not None, f"get_email_content returned None for ID {first_email_id}"
            logging.info("Successfully retrieved email content.")

            subject = email_content.get('subject')
            sender = email_content.get('sender')
            body = email_content.get('body')

            logging.info(f"   Subject: {subject}")
            logging.info(f"   From: {sender}")
            logging.info(f"   Body {body}")

            assert subject is not None, "Email subject is None"
            assert sender is not None, "Email sender is None"

            logging.info("get_email_content test completed successfully.")

        except HttpError as content_http_err:
            logging.error(f"HTTP error getting email content for ID {first_email_id}: {content_http_err}")
            assert False, f"HTTP error during get_email_content: {content_http_err}"
        except Exception as content_e:
            logging.exception(f"Unexpected error getting email content for ID {first_email_id}: {content_e}")
            assert False, f"Unexpected error during get_email_content: {content_e}"


if __name__ == "__main__":
    test_gmail_features()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    test_get_email_content() 
