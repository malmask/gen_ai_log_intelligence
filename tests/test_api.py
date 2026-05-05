import os
from unittest.mock import patch

from fastapi.testclient import TestClient

os.environ.setdefault("GEMINI_API_KEY", "test-key")

from app.chunker import chunk_log
from app.main import app

client = TestClient(app)


# chunker tests

def test_chunk_log_basic():
    lines = "\n".join([f"line {i}" for i in range(100)])
    chunks = chunk_log(lines)
    assert len(chunks) > 1
    assert all(isinstance(c, str) for c in chunks)


def test_chunk_log_empty():
    chunks = chunk_log("")
    assert chunks == []


def test_chunk_log_small():
    log = "line 1\nline 2\nline 3"
    chunks = chunk_log(log)
    assert len(chunks) == 1


# health endpoint

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ingest endpoint

@patch("app.routers.ingest.build_index", return_value=5)
def test_ingest_valid_log(mock_build):
    log_content = b"ERROR Something went wrong\nWARN High memory\nINFO Started"
    response = client.post(
        "/api/v1/ingest",
        files={"file": ("test.log", log_content, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["chunks_indexed"] == 5
    assert data["filename"] == "test.log"


def test_ingest_wrong_extension():
    response = client.post(
        "/api/v1/ingest",
        files={"file": ("test.csv", b"some,data", "text/csv")}
    )
    assert response.status_code == 400


def test_ingest_empty_file():
    response = client.post(
        "/api/v1/ingest",
        files={"file": ("empty.log", b"", "text/plain")}
    )
    assert response.status_code == 400


# analyze endpoint

@patch("app.routers.analyze.search")
@patch("app.routers.analyze.analyze_logs")
def test_analyze_success(mock_analyze, mock_search):
    mock_search.return_value = [{"text": "ERROR NullPointerException", "source": "app.log", "score": 0.1}]
    mock_analyze.return_value = {
        "query": "null pointer error",
        "analysis": "Root cause: user object is null",
        "retrieved_chunks": 1,
        "sources": ["app.log"]
    }
    response = client.post("/api/v1/analyze", json={"query": "null pointer error"})
    assert response.status_code == 200
    assert "analysis" in response.json()


@patch("app.routers.analyze.search", return_value=[])
def test_analyze_no_index(mock_search):
    response = client.post("/api/v1/analyze", json={"query": "any error"})
    assert response.status_code == 404


def test_analyze_empty_query():
    response = client.post("/api/v1/analyze", json={"query": "   "})
    assert response.status_code == 400
