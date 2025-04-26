from typing import Any
from abc import ABC, abstractmethod

class IAIConversationClient(ABC):
    """
    Abstract base class for an AI conversation client.
    Defines the required interface for conversation clients.
    """

    @abstractmethod
    def send_message(self, session_id: str, message: str) -> dict[str, Any]:
        """
        Send a message to the AI conversation for the given session.

        Args:
            session_id (str): The session identifier.
            message (str): The user's message.

        Returns:
            dict[str, Any]: The AI's response message as a dictionary.
        """
        ...

    @abstractmethod
    def get_chat_history(self, session_id: str) -> list[dict[str, Any]]:
        """
        Retrieve the full chat history for a given session.

        Args:
            session_id (str): The session identifier.

        Returns:
            list[dict[str, Any]]: List of message dictionaries representing the chat history.
        """
        ...

    @abstractmethod
    def set_user_preferences(self, user_id: str, preferences: dict[str, Any]) -> bool:
        """
        Set or update preferences for a user.

        Args:
            user_id (str): The user's identifier.
            preferences (dict[str, Any]): A dictionary of user preference settings.

        Returns:
            bool: True if preferences were successfully set.
        """
        ...

    @abstractmethod
    def start_new_session(self, user_id: str) -> str:
        """
        Start a new chat session for the specified user.

        Args:
            user_id (str): The user's identifier.

        Returns:
            str: The new session's unique identifier.
        """
        ...

    @abstractmethod
    def end_session(self, session_id: str) -> bool:
        """
        End and clean up the specified chat session.

        Args:
            session_id (str): The identifier for the chat session.

        Returns:
            bool: True if the session was successfully ended.
        """
        ...