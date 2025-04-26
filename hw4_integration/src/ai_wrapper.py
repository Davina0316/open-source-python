from aichat_client.ai_conversation_client.gemini_api_client import GeminiAPIClient
from aichat_client.ai_conversation_client.client import AIConversationClient


_gemini_api = GeminiAPIClient()
_ai_client = AIConversationClient(api_client=_gemini_api)


def get_spam_probability(email_text: str) -> float:
    """
    Using Gemini AI to determin the probability of spam，return value is  0.0 to 1.0.
    """

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

        import re
        match = re.search(r"\d{1,3}", reply_text)
        if match:
            pct = int(match.group(0))
            return min(1.0, max(0.0, pct / 100.0))
        else:
            return 0.0
    except Exception as e:
        print(f"[Spam AI] Failed to analyze message: {e}")
        return 0.0
