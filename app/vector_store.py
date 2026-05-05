import os
import json
import pickle
import numpy as np
import faiss
import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.gemini_api_key)


def _embed(texts: list[str]) -> np.ndarray:
    """Embed a list of texts using Gemini embedding model."""
    result = genai.embed_content(
        model=settings.embedding_model,
        content=texts,
        task_type="retrieval_document"
    )
    return np.array(result["embedding"], dtype="float32")


def _embed_query(text: str) -> np.ndarray:
    result = genai.embed_content(
        model=settings.embedding_model,
        content=text,
        task_type="retrieval_query"
    )
    return np.array(result["embedding"], dtype="float32").reshape(1, -1)


def build_index(chunks: list[str], source_name: str) -> int:
    """
    Embed chunks and add them to (or create) a persistent FAISS index.
    Returns number of chunks added.
    """
    embeddings = _embed(chunks)
    dim = embeddings.shape[1]

    index_file = f"{settings.faiss_index_path}.index"
    meta_file = f"{settings.faiss_index_path}.meta"

    # Load or create index
    if os.path.exists(index_file):
        index = faiss.read_index(index_file)
        with open(meta_file, "rb") as f:
            metadata = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(dim)
        metadata = []  # list of {"text": ..., "source": ...}

    index.add(embeddings)
    metadata.extend([{"text": c, "source": source_name} for c in chunks])

    faiss.write_index(index, index_file)
    with open(meta_file, "wb") as f:
        pickle.dump(metadata, f)

    return len(chunks)


def search(query: str) -> list[dict]:
    """Return top-k most relevant chunks for a query."""
    index_file = f"{settings.faiss_index_path}.index"
    meta_file = f"{settings.faiss_index_path}.meta"

    if not os.path.exists(index_file):
        return []

    index = faiss.read_index(index_file)
    with open(meta_file, "rb") as f:
        metadata = pickle.load(f)

    query_vec = _embed_query(query)
    distances, indices = index.search(query_vec, settings.top_k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        results.append({
            "text": metadata[idx]["text"],
            "source": metadata[idx]["source"],
            "score": float(dist)
        })
    return results


def clear_index():
    """Delete the FAISS index and metadata."""
    for ext in [".index", ".meta"]:
        path = f"{settings.faiss_index_path}{ext}"
        if os.path.exists(path):
            os.remove(path)
