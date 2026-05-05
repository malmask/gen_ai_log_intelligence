from fastapi import FastAPI
from app.routers import ingest, analyze

app = FastAPI(
    title="GenAI Log Intelligence Platform",
    description="Upload application logs and get AI-powered root-cause analysis and fix suggestions.",
    version="1.0.0"
)

app.include_router(ingest.router, prefix="/api/v1", tags=["Ingest"])
app.include_router(analyze.router, prefix="/api/v1", tags=["Analyze"])


@app.get("/health")
def health():
    return {"status": "ok"}
