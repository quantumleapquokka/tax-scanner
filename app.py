from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/")
def index(request: Request):
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
    fake_tax_data = {
        "taxpayer_name": "Jane Doe",
        "filing_status": "Single",
        "wages": 72000,
        "adjusted_gross_income": 68500,
        "total_tax": 8250,
        "refund_amount": 1100,
    }

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "tax_data": fake_tax_data,
            "saved": False,
            "error": None,
        },
    )