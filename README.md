## Features

- Upload IRS Form 1040 (PDF or image)
- OCR using Gemini Vision
- Review extracted fields
- Save accepted data to SQLite
- Sample Form 1040 included for testing

## Installation

Clone the repository.

Install dependencies.

```bash
pip install -r requirements.txt
```

Copy the example environment file.

```bash
cp .env.example .env
```

Replace

```env
your_gemini_api_key_here
```

with your own Gemini API key.

Run

```bash
uvicorn app:app --reload
```