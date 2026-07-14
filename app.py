import io

from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from PIL import Image

from extraction import extract_tax_data, pdf_to_images
from database import Base, SessionLocal, engine
from models import TaxReturn


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

Base.metadata.create_all(bind=engine)

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

@app.post("/accept")
def accept_tax_return(
    request: Request,
    taxpayer_name: str = Form(...),
    filing_status: str | None = Form(None),
    wages: float | None = Form(None),
    adjusted_gross_income: float | None = Form(None),
    total_tax: float | None = Form(None),
    refund_amount: float | None = Form(None),
):
    """
    Saves the tax information reviewed and accepted by the user.

    The submitted values may differ from Gemini's original extraction
    because the review form allows the user to correct OCR errors before
    saving.

    Args:
        request: The incoming HTTP request.
        taxpayer_name: Reviewed taxpayer name.
        filing_status: Reviewed filing status.
        wages: Reviewed wage amount.
        adjusted_gross_income: Reviewed adjusted gross income.
        total_tax: Reviewed total tax.
        refund_amount: Reviewed refund amount.

    Returns:
        The main page with a confirmation message after the record has
        been saved successfully.
    """

    database = SessionLocal()

    try:
        tax_return = TaxReturn(
            taxpayer_name=taxpayer_name,
            filing_status=filing_status,
            wages=wages,
            adjusted_gross_income=adjusted_gross_income,
            total_tax=total_tax,
            refund_amount=refund_amount,
            status="accepted",
        )

        database.add(tax_return)
        database.commit()
        database.refresh(tax_return)

    except Exception as exc:
        database.rollback()

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "tax_data": None,
                "saved": False,
                "error": f"The tax return could not be saved: {exc}",
            },
            status_code=500,
        )

    finally:
        database.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "tax_data": None,
            "saved": True,
            "error": None,
        },
    )