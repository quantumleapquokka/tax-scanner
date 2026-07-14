import io
import json
import os
import fitz
from typing import Any

from dotenv import load_dotenv
from google import genai
from PIL import Image


load_dotenv()

def pdf_to_images(pdf_bytes: bytes) -> list[Image.Image]:
    """
    Converts the every page of an uploaded PDF into a PIL Image.

    Args:
        pdf_bytes: Raw bytes of the uploaded PDF.

    Returns:
        The first page of the PDF as a PIL Image.
    """

    images: list[Image.Image] = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        for page_number in range(document.page_count):
            page = document.load_page(page_number)
            pixmap = page.get_pixmap(dpi=300)

            # Convert the rendered PNG bytes into a standalone PIL image.
            image = Image.open(
                io.BytesIO(pixmap.tobytes("png"))
            ).convert("RGB")

            images.append(image.copy())

    if not images:
        raise ValueError("The uploaded PDF does not contain any pages.")

    return images


def extract_tax_data(images: list[Image.Image]) -> dict[str, Any]:
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
    contents = [prompt, *images]

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=contents,
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    cleaned_text = response.text.strip()

    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.removeprefix("```json")
        cleaned_text = cleaned_text.removeprefix("```")
        cleaned_text = cleaned_text.removesuffix("```").strip()

    return json.loads(cleaned_text)