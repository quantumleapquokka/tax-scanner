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