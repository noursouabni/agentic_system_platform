import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


def generate_text(prompt: str) -> str:
    """
    Generates text using the Gemini API.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return (
            "ERROR: GEMINI_API_KEY is missing. "
            "Please add it to your .env file."
        )

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text