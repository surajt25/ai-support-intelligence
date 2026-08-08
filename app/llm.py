import os
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.models import TriageResponse

load_dotenv()

class GeminiClient:
    """Small wrapper around the Gemini API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        #self.api_key = api_key or os.getenv("GEMINI_API_KEY") # TO BE DELETED NOW
        self.api_key = (
            api_key
            if api_key is not None
            else os.getenv("GEMINI_API_KEY")
        )

        self.model = (
            model
            if model is not None
            else os.getenv(
                "GEMINI_MODEL",
                "gemini-3.5-flash-lite",
            )
        )

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Set it in the .env file."
            )

        self.client = genai.Client(api_key=self.api_key)

    #def generate_triage(
    def generate_triage(
        self,
        prompt: str,
    ) -> TriageResponse:
        """
        Generate and validate a structured triage response.
        """

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TriageResponse,
            ),
        )

        if not response.parsed:
            raise RuntimeError(
                "Gemini returned an empty or invalid structured response."
            )

        return response.parsed