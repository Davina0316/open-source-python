import uuid
from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional, Any

class MessageRole(Enum):
    """
    Enum representing the role of a message sender.
    """
    USER = "user"
    SYSTEM = "system"
    FUNCTION = "function"
    ASSISTANT = "assistant"

class Message:
    """
    Represents a single message in a conversation.
    
    Attributes:
        content (str): The message content.
        role (MessageRole): The sender's role.
        id (str): Unique identifier for the message.
        timestamp (datetime): Time when the message was created.
    """

    def __init__(
        self,
        content: str,
        role: MessageRole = MessageRole.USER,
        message_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initializes a Message object.

        Args:
            content (str): The message text.
            role (MessageRole, optional): The sender's role. Defaults to USER.
            message_id (str, optional): Unique message ID. Auto-generated if not provided.
            timestamp (datetime, optional): Time of message creation. Defaults to current time.
        """
        self._content = content
        self._role = role
        self._id = message_id or f"msg_{uuid.uuid4().hex[:8]}"
        self._timestamp = timestamp or datetime.now()

    @property
    def id(self) -> str:
        """
        Returns the unique ID of the message.
        """
        return self._id

    @property
    def content(self) -> str:
        """
        Returns the content of the message.
        """
        return self._content

    @property
    def role(self) -> MessageRole:
        """
        Returns the role of the sender.
        """
        return self._role

    @property
    def timestamp(self) -> datetime:
        """
        Returns the timestamp of the message.
        """
        return self._timestamp

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the message to a dictionary format.
        Only includes role and content.

        Returns:
            dict: A dictionary representation of the message.
        """
        return {
            "role": self._role.value,
            "content": self._content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        Deserializes a message object from a dictionary.

        Args:
            data (dict): Dictionary containing message data.

        Returns:
            Message: A reconstructed Message object.
        """
        timestamp_str = data.get("timestamp")
        try:
            timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None
        except ValueError:
            timestamp = datetime.now()

        return cls(
            content=data.get("content", ""),
            role=MessageRole(data.get("role", "user")),
            message_id=data.get("id"),
            timestamp=timestamp
        )

class Conversation:
    """
    Represents a full conversation consisting of multiple messages.
    
    Attributes:
        id (str): Unique identifier for the conversation.
        title (str): Title of the conversation.
        messages (List[Message]): List of messages in the conversation.
    """

    def __init__(
        self,
        conversation_id: Optional[str] = None,
        title: Optional[str] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Initializes a new Conversation instance.

        Args:
            conversation_id (str, optional): Custom ID for the conversation.
            title (str, optional): Optional title of the conversation.
            system_prompt (str, optional): Initial system prompt message.
        """
        self._id = conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
        self._title = title or f"Conversation {self._id}"
        self._messages: List[Message] = []

        if system_prompt:
            self.add_message(Message(system_prompt, MessageRole.SYSTEM))

    @property
    def id(self) -> str:
        """
        Returns the conversation ID.
        """
        return self._id

    @property
    def title(self) -> str:
        """
        Returns the conversation title.
        """
        return self._title

    @property
    def messages(self) -> List[Message]:
        """
        Returns a copy of the list of messages in the conversation.
        """
        return self._messages.copy()

    def add_message(self, message: Message) -> None:
        """
        Adds a message to the conversation.

        Args:
            message (Message): The message object to add.
        """
        self._messages.append(message)

    def get_latest_messages(self, count: int = 5) -> List[Message]:
        """
        Returns the most recent messages in the conversation.

        Args:
            count (int, optional): Number of latest messages to retrieve. Defaults to 5.

        Returns:
            List[Message]: The latest messages.
        """
        return self._messages[-count:] if self._messages else []

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the conversation to a dictionary format.

        Returns:
            dict: Dictionary containing the conversation data.
        """
        return {
            "id": self._id,
            "title": self._title,
            "messages": [
                {
                    "id": msg.id,
                    "content": msg.content,
                    "role": msg.role.value,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in self._messages
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """
        Deserializes a conversation from dictionary data.

        Args:
            data (dict): The dictionary containing conversation details.

        Returns:
            Conversation: The reconstructed Conversation object.
        """
        conversation = cls(
            conversation_id=data.get("id"),
            title=data.get("title")
        )

        for msg_data in data.get("messages", []):
            conversation.add_message(Message.from_dict(msg_data))

        return conversation