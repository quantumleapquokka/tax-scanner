import io
import json
import os
from typing import Any

from dotenv import load_dotenv
from google import genai
from PIL import Image


load_dotenv()


def extract_tax_data(image_bytes: bytes) -> dict[str, Any]:
    """
    Extracts relevant tax information from an uploaded IRS Form 1040 using
    the Gemini Vision API.

    The uploaded image is sent to Gemini along with a prompt requesting a
    predefined set of tax fields. Gemini returns the extracted information
    as JSON, which is parsed into a Python dictionary and returned to the
    caller.

    Args:
        image_bytes: Raw bytes of the uploaded image.

    Returns:
        A dictionary containing the extracted tax information.

    Raises:
        RuntimeError: If the Gemini API key is missing or Gemini returns
            an empty response.
        json.JSONDecodeError: If Gemini returns malformed JSON.
    """
    
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Copy .env.example to .env and add your API key."
        )

    image = Image.open(io.BytesIO(image_bytes))
    client = genai.Client(api_key=api_key)

    prompt = """
    Extract the following fields from this IRS Form 1040:

    - taxpayer_name
    - filing_status
    - wages
    - adjusted_gross_income
    - total_tax
    - refund_amount

    Return JSON only.

    Use null when a field cannot be confidently found.
    Monetary fields must be numbers without dollar signs or commas.
    Do not infer or invent missing values.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[prompt, image],
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    cleaned_text = response.text.strip()

    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.removeprefix("```json")
        cleaned_text = cleaned_text.removeprefix("```")
        cleaned_text = cleaned_text.removesuffix("```").strip()

    return json.loads(cleaned_text)