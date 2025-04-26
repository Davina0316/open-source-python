import logging
import re

from aichat_client.ai_conversation_client.client import AIConversationClient
from aichat_client.ai_conversation_client.gemini_api_client import GeminiAPIClient

_gemini_api = GeminiAPIClient()
_ai_client = AIConversationClient(api_client=_gemini_api)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_spam_probability(email_text: str) -> float:
    """Use Gemini AI to determine the probability of spam; return value is 0.0 to 1.0."""
    try:
        prompt = (
            "Please analyze the following email content and return the probability "
            "that it is spam as a number between 0 and 100. Just return the number.\n\n"
            f"{email_text.strip()}"
        )

        session_id = _ai_client.start_new_session(user_id="spam-detector")
        response = _ai_client.send_message(session_id, prompt)
        _ai_client.end_session(session_id)

        reply_text = response["content"].strip()

        match = re.search(r"\d+", reply_text)
        if match:
            pct = int(match.group(0))
            return min(1.0, max(0.0, pct / 100.0))
    except Exception:
        logging.exception("[Spam AI] Failed to analyze message")
        return 0.0  # Default return on exception

    # Default return if no match is found or other issues occur within try block
    return 0.0
