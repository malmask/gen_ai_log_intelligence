from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.vector_store import search
from app.llm_service import analyze_logs, summarize_logs

router = APIRouter()


class QueryRequest(BaseModel):
    query: str

    model_config = {"json_schema_extra": {"example": {"query": "Why is the service throwing NullPointerException?"}}}


class SummarizeRequest(BaseModel):
    log_text: str

    model_config = {"json_schema_extra": {"example": {"log_text": "ERROR 2024-01-01 ...\nWARN ..."}}}


@router.post("/analyze", summary="Query logs for root-cause analysis")
def analyze(request: QueryRequest):
    """
    Retrieves relevant log chunks via RAG and asks Gemini to
    identify root cause, issue type, affected component, and fix suggestion.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    chunks = search(request.query)
    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No logs indexed yet. Please ingest a log file first."
        )

    result = analyze_logs(request.query, chunks)
    return result


@router.post("/summarize", summary="Summarize a raw log block directly")
def summarize(request: SummarizeRequest):
    """
    Directly summarize a raw log snippet without RAG.
    Useful for quick triage of a pasted log block.
    """
    if not request.log_text.strip():
        raise HTTPException(status_code=400, detail="log_text cannot be empty.")

    summary = summarize_logs(request.log_text)
    return {"summary": summary}
