"""
Optional Gemini-backed response generation.

The app keeps working without Gemini credentials by treating this client as an
enhancement layer rather than a hard dependency.
"""

import os
from pathlib import Path

try:
    from google import genai
except ImportError:  # pragma: no cover - depends on local environment
    genai = None

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional in minimal environments
    load_dotenv = None

if load_dotenv:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class GeminiClient:
    """Thin wrapper around the Gemini API with safe fallback detection."""

    def __init__(self, model=None):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.enabled = bool(self.api_key and genai)
        self.client = genai.Client(api_key=self.api_key) if self.enabled else None

    def is_available(self):
        return self.enabled

    def generate_response(self, prompt):
        if not self.enabled:
            return None

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return (response.text or "").strip() or None
