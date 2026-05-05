import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel(settings.gemini_model)


def analyze_logs(query: str, context_chunks: list[dict]) -> dict:
    """
    Given a user query and retrieved log chunks, ask Gemini to:
    - Identify the root cause
    - Classify the issue type
    - Suggest a fix
    """
    context_text = "\n\n---\n\n".join(
        [f"[Source: {c['source']}]\n{c['text']}" for c in context_chunks]
    )

    prompt = f"""You are an expert backend engineer analyzing application logs.

Below are relevant log excerpts retrieved for the following query:
Query: {query}

Log Context:
{context_text}

Based on the logs above, provide a structured analysis:

1. **Root Cause**: What is the most likely root cause of the issue?
2. **Issue Type**: Classify the issue (e.g. NullPointerException, DB timeout, Auth failure, OOM, Network error, etc.)
3. **Affected Component**: Which service or component is most likely responsible?
4. **Fix Suggestion**: What concrete steps should the engineer take to fix this?
5. **Severity**: Rate the severity as LOW / MEDIUM / HIGH / CRITICAL and briefly explain why.

Be concise and actionable. If the logs do not contain enough information, say so clearly.
"""

    response = model.generate_content(prompt)
    return {
        "query": query,
        "analysis": response.text,
        "retrieved_chunks": len(context_chunks),
        "sources": list({c["source"] for c in context_chunks})
    }


def summarize_logs(log_text: str) -> str:
    """Quick summary of a raw log block without RAG."""
    prompt = f"""Summarize the following application log in 3-5 bullet points.
Focus on: errors, warnings, anomalies, and any patterns that suggest system issues.

Log:
{log_text}
"""
    response = model.generate_content(prompt)
    return response.text
