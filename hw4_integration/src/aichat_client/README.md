# AI Conversation Client

## Overview
The AI Conversation Client is a lightweight Python module that enables structured interactions between users and an AI chatbot powered by **Google Gemini (gemini-2.0-flash)**. It supports session management, message exchange, chat history, and user preferences — all via a simple HTTP integration.

---

## Features
1. **Send and receive messages** using Gemini API (\`v1beta\`).
2. **Session management** to start and end conversations cleanly.
3. **Chat history retrieval** with timestamped messages.
4. **User preference support** for custom prompts or configurations.

---

## API Reference

### AIConversationClient Class

#### Initialization
```python
client = AIConversationClient()
```

#### 1. \`send_message(session_id: str, message: str) -> dict\`
Sends a message to the Gemini-powered AI and returns a structured response.

**Args:**
- \`session_id\`: Unique identifier for the session.
- \`message\`: User input.

**Returns:**
- A \`dict\` containing the assistant’s message, role, timestamp, and ID.

#### 2. \`get_chat_history(session_id: str) -> list\`
Retrieves all messages from a session.

**Returns:**
- A list of message dictionaries (user + assistant).

#### 3. \`set_user_preferences(user_id: str, preferences: dict) -> bool\`
Stores preferences such as system prompts for a user.

#### 4. \`start_new_session(user_id: str) -> str\`
Starts a new conversation session.

**Returns:**
- A new session ID.

#### 5. \`end_session(session_id: str) -> bool\`
Ends an active session and removes its history.

---

## Setup & Installation

**Setting PYTHONPATH**

For Windows use the following command:
```sh
set PYTHONPATH=%CD%
```

For MacOS use the following command:
```sh
export PYTHONPATH=$(pwd)
```

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/lkyuan233/python-template-repo.git
cd python-template-repo
git checkout hw3-implementation
```


### 2️⃣ Add your \`.env\` in the **project root**:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 3️⃣ Install dependencies and dev dependencies using [uv](https://github.com/astral-sh/uv)

```bash
uv pip install -r pyproject.toml
uv sync --group dev
```

---

## Usage

### 🧠 Start a Chat Session
```bash
uv run ai_conversation_client/cli.py chat --user-id <user_id>
```

### 📜 View Chat History
```bash
uv run ai_conversation_client/cli.py history <session_id>
```

### 📋 List Active Sessions
```bash
uv run ai_conversation_client/cli.py list
```

---

## Running Tests

Run all tests (if present) using:

```bash
uv run pytest
```

---

## Project Scope

### ✅ Minimum Viable Product (MVP)
- Send and receive messages via Gemini.
- Start and end sessions.
- View session history.
- Store user preferences.

### ❌ Out of Scope
- Real-time message streaming.
- Fine-grained personalization.
- Custom AI models or embeddings.

---

## Contributing

1. Fork the repo.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Make and commit your changes:
   ```bash
   git commit -m "Add feature"
   ```
4. Push and open a PR.

---

## License

MIT License © 2025