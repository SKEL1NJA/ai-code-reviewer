# AI Code Reviewer & Refactor Assistant

An API that automatically reviews source code snippets for **Security**, **Performance**, and **Readability** issues using Google's Gemini API, returning structured, schema-validated feedback. Every request is traced end-to-end with Langfuse, capturing token usage, cost, and latency for full observability into LLM behavior.

**Live demo:** https://ai-code-reviewer-jztc.onrender.com/docs

---

## Overview

Manual code review is slow and inconsistent. This project uses a large language model as a first-pass reviewer, constrained by a strict output schema so the results are predictable, structured, and easy to consume programmatically — not free-form text that needs to be parsed and guessed at.

Each submitted snippet is scored and analyzed across three categories:

| Category | What it checks |
|---|---|
| **Security** | Injection risks, unsafe input handling, credential exposure, and other vulnerabilities |
| **Performance** | Inefficient patterns, unnecessary complexity, resource usage |
| **Readability** | Naming, structure, and overall clarity |

Each category returns a 0–10 score, a short summary, and a list of specific issues with severity, location, and a concrete suggested fix.

## Architecture

```
Client Request
      │
      ▼
FastAPI (/review endpoint)
      │  • Validates input (non-empty, length limit)
      ▼
Gemini API (gemini-3.5-flash-lite)
      │  • Structured output enforced via Pydantic response_schema
      ▼
Langfuse (OpenTelemetry-based tracing)
      │  • Captures input/output, token usage, cost, latency
      ▼
Structured JSON Response
```

## Tech Stack

- **FastAPI** — API framework with automatic request validation and interactive docs
- **Google Gemini API** (`gemini-3.5-flash-lite`) — code analysis, called via the official `google-genai` SDK
- **Pydantic** — defines the structured output schema, enforced server-side by the Gemini SDK rather than parsed from free text
- **Langfuse** — LLM observability: traces every call with cost, latency, and token metrics
- **pytest** — automated tests for request validation logic
- **Render** — deployment (free tier, auto-deploys on push to `main`)

## API Reference

### `GET /`
Health check.

**Response**
```json
{ "status": "AI Code Reviewer is running" }
```

### `POST /review`
Submits a code snippet for review.

**Request body**
```json
{
  "code": "def get_user(user_id):\n    query = \"SELECT * FROM users WHERE id = \" + user_id\n    return db.execute(query)"
}
```

**Response**
```json
{
  "security": {
    "score": 0,
    "summary": "Critical SQL injection vulnerability due to string concatenation.",
    "issues": [
      {
        "severity": "critical",
        "description": "Unsanitized user_id is concatenated directly into the SQL query.",
        "line_reference": "query = \"SELECT * FROM users WHERE id = \" + user_id",
        "suggestion": "Use parameterized queries: db.execute(\"SELECT * FROM users WHERE id = %s\", (user_id,))"
      }
    ]
  },
  "performance": { "score": 8, "summary": "...", "issues": [] },
  "readability": { "score": 9, "summary": "...", "issues": [] },
  "overall_summary": "Concise and readable, but the SQL injection risk must be fixed immediately."
}
```

**Error responses**

| Status | Cause |
|---|---|
| `400` | Empty code field, or code exceeds the length limit |
| `502` | The upstream Gemini API call failed |

Full interactive documentation (request/response schemas, try-it-now UI) is available at `/docs`.

## Observability

Every call to `/review` is traced in Langfuse, capturing:

- Full input and output for the LLM call
- Token usage (input/output)
- Estimated cost per request
- End-to-end latency and time-to-first-token
- Model name actually used, pulled live from the SDK response

This makes cost and performance visible per-request rather than estimated after the fact — useful both for debugging and for monitoring usage against the Gemini free-tier quota.

## Running Locally

**Prerequisites:** Python 3.12+, a free [Gemini API key](https://aistudio.google.com/apikey), a free [Langfuse Cloud](https://cloud.langfuse.com) account.

```bash
# Clone and enter the project
git clone https://github.com/SKEL1NJA/ai-code-reviewer.git
cd ai-code-reviewer

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows PowerShell
# source venv/bin/activate       # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_key_here
LANGFUSE_PUBLIC_KEY=your_key_here
LANGFUSE_SECRET_KEY=your_key_here
LANGFUSE_BASE_URL=your_region_url_here
```

Run the server:
```bash
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to try it locally.

## Testing

```bash
pytest
```

Tests cover request validation logic (empty input, oversized input) without calling the live Gemini API, so they run instantly and don't consume API quota.

## Deployment

Deployed on [Render](https://render.com) as a persistent web service (not serverless), which better suits an API with outbound LLM calls than a short-lived function model:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment:** Free tier — spins down after 15 minutes of inactivity; first request after idle time may take 30–60s to respond while the instance wakes up

Every push to `main` triggers an automatic redeploy.

## Possible Next Steps

- Fetch code directly from a GitHub repository or pull request instead of requiring a pasted snippet
- Rate-limit the `/review` endpoint to protect the shared Gemini free-tier quota
- A minimal frontend for non-technical users to submit code without using `/docs`

## License

MIT