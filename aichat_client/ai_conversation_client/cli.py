#!/usr/bin/env python3
"""
Command-line interface for the AI Conversation Client.

Provides tools for interacting with the AI assistant via terminal,
including starting a chat, showing message history, and managing sessions.
"""

import argparse
import asyncio

from .client import AIConversationClient

async def interactive_chat(client: AIConversationClient, user_id: str) -> None:
    """
    Start an interactive chat loop with the AI assistant for a given user.

    Args:
        client (AIConversationClient): The conversation client instance.
        user_id (str): Unique identifier for the user.
    """
    session_id = client.start_new_session(user_id)
    print(f"New session started. Session ID: {session_id}")
    print("Type 'exit' to quit.\n")

    # Event loop needed for non-blocking input
    loop = asyncio.get_event_loop()

    while True:
        user_input = await loop.run_in_executor(None, input, "You: ")
        user_input = user_input.strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Ending session...")
            client.end_session(session_id)
            break

        try:
            response = client.send_message(session_id, user_input)
            print(f"AI: {response['content']}")
        except Exception as e:
            print(f"Error: {e}")

def list_sessions(client: AIConversationClient) -> None:
    """
    Placeholder function to list sessions.

    Args:
        client (AIConversationClient): The conversation client instance.
    """
    print("Session listing is not implemented for the generic interface.")

def show_history(client: AIConversationClient, session_id: str) -> None:
    """
    Display the message history for a given session.

    Args:
        client (AIConversationClient): The conversation client instance.
        session_id (str): The ID of the session to show.
    """
    try:
        history = client.get_chat_history(session_id)
        if not history:
            print("No messages yet.")
            return

        for msg in history:
            print(f"[{msg['timestamp']}] {msg['role'].capitalize()}: {msg['content']}")
    except Exception as e:
        print(f"Error: {e}")

async def run_cli(client: AIConversationClient) -> None:
    """
    Parse command-line arguments and dispatch to appropriate handlers.

    Args:
        client (AIConversationClient): The conversation client instance.
    """
    parser = argparse.ArgumentParser(description="AI Conversation CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand for starting a new chat
    chat_parser = subparsers.add_parser("chat", help="Start a new chat")
    chat_parser.add_argument("--user-id", required=True, help="User ID for the session")

    # Subcommand for showing history
    history_parser = subparsers.add_parser("history", help="Show chat history")
    history_parser.add_argument("session_id", help="Session ID to view")

    # Placeholder for listing sessions
    subparsers.add_parser("list", help="List active session IDs")

    args = parser.parse_args()

    # Command dispatch
    if args.command == "chat":
        await interactive_chat(client, args.user_id)
    elif args.command == "history":
        show_history(client, args.session_id)
    elif args.command == "list":
        list_sessions(client)
    else:
        parser.print_help()

if __name__ == "__main__":
    import asyncio
    # from ai_conversation_client.client import AIConversationClient # No longer needed here
    from .gemini_api_client import GeminiAPIClient

    # Create the backend Gemini client and wrap it in a high-level interface
    api_client = GeminiAPIClient()
    client = AIConversationClient(api_client)

    # Start CLI
    asyncio.run(run_cli(client))
