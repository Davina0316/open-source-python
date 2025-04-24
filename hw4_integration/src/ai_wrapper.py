import sys
import re
from pathlib import Path

# Add ai_conversation_client/src to sys.path
client_module_root = Path(__file__).resolve().parent / "ai_conversation_client"
sys.path.insert(0, str(client_module_root))

from src.components.ai_conversation_client.factory import AIClientFactory

client = AIClientFactory.create_client("mock")
session_id = client.start_new_session("spam_checker")

def get_spam_probability(email_body: str) -> float:
    prompt = (
        "Please read the following email and return a number representing the "
        "probability that it is a spam email (0 to 100). "
        "Only return the number, without explanation.\n\n"
        f"Email content:\n{email_body}"
    )
    response = client.send_message(session_id, prompt)["response"]
    match = re.search(r"(\d+(\.\d+)?)", response)
    if match:
        return float(match.group(1))
    else:
        raise ValueError(f"AI response did not contain a valid number: {response}")
