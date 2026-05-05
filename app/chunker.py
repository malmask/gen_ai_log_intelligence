from app.config import settings


def chunk_log(log_text: str) -> list[str]:
    """
    Split a log file into overlapping chunks of N lines.
    Overlap of 5 lines ensures context isn't lost at boundaries.
    """
    lines = [l for l in log_text.splitlines() if l.strip()]
    chunk_size = settings.chunk_size
    overlap = 5
    chunks = []

    i = 0
    while i < len(lines):
        chunk = lines[i: i + chunk_size]
        chunks.append("\n".join(chunk))
        i += chunk_size - overlap

    return chunks
