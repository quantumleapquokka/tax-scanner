import io

from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from PIL import Image

from extraction import extract_tax_data, pdf_to_images


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/")
def index(request: Request):
    """
    Renders the application's home page.

    The page initially displays a file upload form where users can
    upload a completed IRS Form 1040 for processing.

    Args:
        request: The incoming HTTP request.

    Returns:
        The application's main HTML page.
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "tax_data": None,
            "saved": False,
            "error": None,
        },
    )

@app.post("/scan")
async def scan_tax_form(
    request: Request,
    file: UploadFile = File(...),
):
    """
    Processes an uploaded tax form image and extracts relevant tax
    information using the Gemini Vision API.

    The extracted information is returned to the user in an editable
    review form before being saved to the database.

    Args:
        request: The incoming HTTP request.
        file: The uploaded tax form image.

    Returns:
        The main page populated with either:
        - extracted tax data, or
        - an error message if processing fails.
    """

    allowed_types = {
        "image/png",
        "image/jpeg",
        "application/pdf",
    }

    if file.content_type not in allowed_types:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "tax_data": None,
                "saved": False,
                "error": "Upload a PDF, PNG, or JPEG image.",
            },
            status_code=400,
        )

    try:
        file_bytes = await file.read()

        if file.content_type == "application/pdf":
            images = pdf_to_images(file_bytes)
        else:
            # Wrap a single PNG or JPEG in a list so the extraction function always receives the same input type.
            image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            images = [image]

        tax_data = extract_tax_data(images)

    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "tax_data": None,
                "saved": False,
                "error": str(exc),
            },
            status_code=400,
        )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "tax_data": tax_data,
            "saved": False,
            "error": None,
        },
    )