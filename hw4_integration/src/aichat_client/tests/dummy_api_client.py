from ai_conversation_client.interface import IAIConversationClient
from typing import Any

class DummyAPIClient(IAIConversationClient):
    def __init__(self) -> None:
        self.sessions: dict[str, list[dict[str, Any]]] = {}
        self.preferences: dict[str, dict[str, Any]] = {}

    def send_message(self, session_id: str, message: str) -> dict[str, Any]:
        reply = f"Echo: {message}"
        self.sessions.setdefault(session_id, []).append({"role": "user", "content": message})
        self.sessions[session_id].append({"role": "assistant", "content": reply})
        return {
            "message_id": "dummy_msg",
            "role": "assistant",
            "content": reply,
            "timestamp": "2025-01-01T00:00:00",
        }

    def get_chat_history(self, session_id: str) -> list[dict[str, Any]]:
        return self.sessions.get(session_id, [])

    def set_user_preferences(self, user_id: str, preferences: dict[str, Any]) -> bool:
        self.preferences[user_id] = preferences
        return True

    def start_new_session(self, user_id: str) -> str:
        session_id = f"session_{user_id}"
        self.sessions[session_id] = []
        return session_id

    def end_session(self, session_id: str) -> bool:
        return self.sessions.pop(session_id, None) is not None
