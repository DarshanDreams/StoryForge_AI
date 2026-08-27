from __future__ import annotations


def validate_query(query: str) -> tuple[bool, str]:
    if not query or not query.strip():
        return False, "Query cannot be empty."
    return True, ""


def validate_retrieval(results: list) -> tuple[bool, str]:
    if not results:
        return False, "I could not find enough information in the story to answer that question."
    return True, ""


def calculate_confidence(results: list) -> float:
    if not results:
        return 0.0
    scores = [float(getattr(result, "score", 0.0)) for result in results]
    return round(min(max(sum(scores) / len(scores), 0.0), 1.0), 4)