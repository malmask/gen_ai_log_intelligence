from fastapi import APIRouter, UploadFile, File, HTTPException
from app.chunker import chunk_log
from app.vector_store import build_index, clear_index

router = APIRouter()


@router.post("/ingest", summary="Upload a log file for indexing")
async def ingest_log(file: UploadFile = File(...)):
    """
    Upload a .log or .txt file.
    The file is chunked and embedded into the FAISS vector store.
    """
    if not file.filename.endswith((".log", ".txt")):
        raise HTTPException(status_code=400, detail="Only .log or .txt files are supported.")

    content = await file.read()
    try:
        log_text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded.")

    if not log_text.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    chunks = chunk_log(log_text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No log lines found in file.")

    indexed = build_index(chunks, source_name=file.filename)

    return {
        "message": "Log file ingested successfully.",
        "filename": file.filename,
        "chunks_indexed": indexed
    }


@router.delete("/ingest", summary="Clear the FAISS index")
def clear():
    """Delete all indexed log data."""
    clear_index()
    return {"message": "Index cleared."}
