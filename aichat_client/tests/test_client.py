import pytest
from ai_conversation_client.client import AIConversationClient
from tests.dummy_api_client import DummyAPIClient

@pytest.fixture
def client() -> AIConversationClient:
    api = DummyAPIClient()
    return AIConversationClient(api_client=api)

def test_send_message(client: AIConversationClient) -> None:
    session_id = client.start_new_session("test_user")
    response = client.send_message(session_id, "Hello")
    assert isinstance(response, dict)
    assert "content" in response

def test_get_chat_history(client: AIConversationClient) -> None:
    session_id = client.start_new_session("test_user")
    client.send_message(session_id, "Hello")
    history = client.get_chat_history(session_id)
    assert isinstance(history, list)
    assert len(history) == 2  # user + assistant

def test_set_user_preferences(client: AIConversationClient) -> None:
    result = client.set_user_preferences("user_1", {"theme": "dark"})
    assert result is True

def test_start_new_session(client: AIConversationClient) -> None:
    session_id = client.start_new_session("user_2")
    assert session_id.startswith("session_")

def test_end_session(client: AIConversationClient) -> None:
    session_id = client.start_new_session("user_3")
    assert client.end_session(session_id) is True
