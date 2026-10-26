
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load the .env file from the project root.
project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env")


def analyze_resume(resume_text, job_role=""):
    """Analyze resume text using the Gemini API."""

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "Google API key not found. Check your .env file."
        )

    client = genai.Client(api_key=api_key)

    target_role = job_role.strip() or "general job applications"

    prompt = f"""
    Analyze the following resume for {target_role}.

    Review these areas:
    1. Content clarity and impact
    2. Skills and relevant qualifications
    3. Experience descriptions
    4. Grammar and formatting suggestions
    5. Specific, practical improvements

    Be constructive and explain how the candidate can improve.
    Do not invent experience or qualifications.

    Resume:
    {resume_text}
    """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are an experienced resume reviewer. "
                "Give honest, specific and constructive feedback."
            ),
            max_output_tokens=3000,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return response.text
