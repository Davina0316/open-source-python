# Open Source Python Project

## Description

This repository is the final integration project for **CS-GY 9223 Open Source Development**.  
It implements a spam detection pipeline that connects:

- **Gmail Inbox via OAuth**
- **LLM-powered AI spam scoring via Gemini API**
- **CSV report generation for spam probability**

The project uses components provided by other teams and integrates them with our own `GmailClient` implementation.

---

## ⚠️ API Key Setup

Before running the application, please **create a `.env` file** in the project root:

```
GEMINI_API_KEY=your_google_gemini_api_key_here
```

You can get a Gemini API key from:  
https://makersuite.google.com/app/apikey  
_or_ set up via Google Cloud Console:  
https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com

---

## Prerequisites

- Python **3.11 or higher**
- Gmail account with developer access
- Google Gemini API Key
- `uv` for dependency management (or use `pip` if you prefer)

---

## Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Davina0316/open-source-python.git
```

### 2. Navigate to the Project Directory

```bash
cd open-source-python
```

### 3. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 4. Create virtual environment using uv

```bash
uv venv --python 3.11
```

### 5. Activate virtual environment

```bash
.venv\Scripts\activate
```

### 6. Install Project Dependencies

```bash
uv sync
```

---

## Running the Application

The main integration logic is in:

```
hw4_integration/src/main.py
```

To run the spam detection:

```bash
cd hw4_integration/src
python main.py
```

This will:

- Connect to your Gmail  
- Fetch up to 10 emails  
- Analyze them with Gemini LLM  
- Output results to `spam_results.csv`

---

## Output Format

The `spam_results.csv` file will contain results like:

```
mail_id,Pct_spam
1856bd7b24e9e132,0.87
f87dfc8880df19bd,0.12
```

---

## Testing

Run unit tests with:

```bash
pytest --cov=src
```

---

## Static Analysis & Code Formatting

Run static checks and type validation:

```bash
ruff check src --fix
mypy src
```

---

## Notes on AI Integration

The Gemini-based AI conversation component was adapted from another team's implementation, located under:

```
hw4_integration/src/aichat_client/ai_conversation_client/
```

The component uses `GeminiAPIClient` to call Google's Generative Language API for spam probability scoring.

---

## .gitignore Notes

The `.gitignore` excludes:

```
.env
__pycache__/
.venv/
```

To avoid exposing API secrets and unnecessary files.

---

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

