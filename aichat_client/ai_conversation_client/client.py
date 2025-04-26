from typing import Any
from .interface import IAIConversationClient

class AIConversationClient(IAIConversationClient):
    """
    A concrete conversation client that delegates all conversation logic to a backend API client.

    This class follows the Adapter pattern, allowing flexibility to switch backend providers
    (e.g., Gemini, OpenAI, local models) without changing the consumer-facing interface.
    """

    def __init__(self, api_client: IAIConversationClient) -> None:
        """
        Initialize the conversation client with an injected API client.

        Args:
            api_client (IAIConversationClient): The backend API client responsible for handling
                                                AI interaction, session management, and preferences.
        """
        self.api_client = api_client

    def send_message(self, session_id: str, message: str) -> dict[str, Any]:
        """
        Send a user message in the context of an existing conversation session.

        Args:
            session_id (str): The ID of the active session.
            message (str): The message content to send.

        Returns:
            dict[str, Any]: The assistant's response message with metadata.
        """
        return self.api_client.send_message(session_id, message)

    def get_chat_history(self, session_id: str) -> list[dict[str, Any]]:
        """
        Retrieve the complete chat history for the given session.

        Args:
            session_id (str): The session ID to retrieve messages for.

        Returns:
            list[dict[str, Any]]: List of messages (user and assistant) in chronological order.
        """
        return self.api_client.get_chat_history(session_id)

    def set_user_preferences(self, user_id: str, preferences: dict[str, Any]) -> bool:
        """
        Store user-specific preferences such as system prompts or context settings.

        Args:
            user_id (str): The unique ID of the user.
            preferences (dict[str, Any]): A dictionary of user preferences.

        Returns:
            bool: True if preferences were successfully stored.
        """
        return self.api_client.set_user_preferences(user_id, preferences)

    def start_new_session(self, user_id: str) -> str:
        """
        Start a new conversation session for the specified user.

        Args:
            user_id (str): The unique ID of the user starting a new session.

        Returns:
            str: The unique session ID generated for the conversation.
        """
        return self.api_client.start_new_session(user_id)

    def end_session(self, session_id: str) -> bool:
        """
        Terminate an ongoing conversation session and clean up resources.

        Args:
            session_id (str): The ID of the session to end.

        Returns:
            bool: True if the session was successfully terminated.
        """
        return self.api_client.end_session(session_id)