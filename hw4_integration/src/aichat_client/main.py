import asyncio
from ai_conversation_client.cli import run_cli
from ai_conversation_client.client import AIConversationClient
from ai_conversation_client.gemini_api_client import GeminiAPIClient

def main() -> None:
    gemini_backend = GeminiAPIClient()
    client = AIConversationClient(api_client=gemini_backend)
    asyncio.run(run_cli(client))

if __name__ == "__main__":
    main()
