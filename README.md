# GenAI Log Intelligence Platform

A FastAPI backend that analyzes application logs with Retrieval-Augmented Generation (RAG), FAISS, and Google Gemini.

## Features

- `POST /api/v1/ingest` - Upload a `.log` or `.txt` file for indexing.
- `DELETE /api/v1/ingest` - Clear indexed log data.
- `POST /api/v1/analyze` - Ask a question about indexed logs.
- `POST /api/v1/summarize` - Summarize a raw log block without RAG.
- `GET /health` - Health check.

## Project Structure

```text
log-intelligence/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── chunker.py
│   ├── vector_store.py
│   ├── llm_service.py
│   └── routers/
│       ├── __init__.py
│       ├── ingest.py
│       └── analyze.py
├── logs/
│   └── sample_app.log
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## Run

```bash
uvicorn app.main:app --reload
```

API docs are available at `http://localhost:8000/docs`.

## Test

```bash
pytest -q
```

## Example Requests

Ingest a log file:

```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@logs/sample_app.log"
```

Analyze indexed logs:

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Why is the service throwing NullPointerException?"}'
```

Summarize a raw log block:

```bash
curl -X POST http://localhost:8000/api/v1/summarize \
  -H "Content-Type: application/json" \
  -d '{"log_text": "ERROR OutOfMemoryError: Java heap space\nWARN Memory at 87%"}'
```
