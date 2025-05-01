import logging
import re

from dotenv import load_dotenv

from aichat_client.ai_conversation_client.client import AIConversationClient
from aichat_client.ai_conversation_client.gemini_api_client import GeminiAPIClient
from .constants import SPAM_PROBABILITY_PATTERN, SPAM_DETECTION_PROMPT

load_dotenv()


_gemini_api = GeminiAPIClient()
_ai_client = AIConversationClient(api_client=_gemini_api)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_spam_probability(email_text: str) -> float:
    """Use Gemini AI to determine the probability of spam; return value is 0.0 to 1.0."""
    try:
        prompt = SPAM_DETECTION_PROMPT + email_text.strip()

        session_id = _ai_client.start_new_session(user_id="spam-detector")
        response = _ai_client.send_message(session_id, prompt)
        _ai_client.end_session(session_id)

        reply_text = response["content"].strip()

        match = re.search(SPAM_PROBABILITY_PATTERN, reply_text)
        if match:
            pct = int(match.group(0))
            return min(1.0, max(0.0, pct / 100.0))
    except Exception:
        logging.exception("[Spam AI] Failed to analyze message")
        return 0.0

    return 0.0
