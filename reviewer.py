import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from schemas import CodeReviewResult
from langfuse import get_client, observe
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor

load_dotenv()

# Turn on automatic tracing for all Gemini SDK calls
GoogleGenAIInstrumentor().instrument()

langfuse = get_client()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_INSTRUCTION = """You are a senior software engineer performing a code review.
Analyze the given code snippet across exactly three categories: Security, Performance, and Readability.

Rules:
- Be specific. Reference actual variable names, function names, or line numbers from the snippet.
- Do not invent issues that aren't present. If a category has no real issues, say so and score it highly.
- Scores must reflect severity: a single critical security flaw should pull that score below 4, even if everything else is clean.
- Suggestions must be actionable, not generic advice like "write better code."
"""


@observe()
def review_code(code: str) -> CodeReviewResult:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"Review this code:\n\n```\n{code}\n```",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=CodeReviewResult,
        ),
    )
    langfuse.flush()
    return response.parsed