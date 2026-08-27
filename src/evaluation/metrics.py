from dataclasses import dataclass


@dataclass
class EvaluationMetrics:
    """
    Metrics for evaluating one agent response.
    """

    keyword_score: float = 0.0

    answer_similarity: float = 0.0

    groundedness: float = 0.0

    retrieval_hit: float = 0.0

    overall_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "keyword_score": self.keyword_score,
            "answer_similarity": self.answer_similarity,
            "groundedness": self.groundedness,
            "retrieval_hit": self.retrieval_hit,
            "overall_score": self.overall_score,
        }


def calculate_keyword_score(
    answer: str,
    expected_keywords: list[str],
) -> float:
    """
    Measure how many expected keywords
    appear in the generated answer.
    """

    if not expected_keywords:
        return 1.0

    normalized_answer = (
        answer.lower()
    )

    matched = 0

    for keyword in expected_keywords:

        if keyword.lower() in normalized_answer:
            matched += 1

    return round(
        matched / len(expected_keywords),
        4,
    )


def calculate_answer_similarity(
    answer: str,
    reference_answer: str,
) -> float:
    """
    Lightweight lexical similarity metric.

    This is intentionally deterministic and
    dependency-light for the demo.
    """

    if not answer.strip():
        return 0.0

    if not reference_answer.strip():
        return 0.0

    answer_words = set(
        answer.lower().split()
    )

    reference_words = set(
        reference_answer.lower().split()
    )

    if not reference_words:
        return 0.0

    intersection = (
        answer_words
        & reference_words
    )

    return round(
        len(intersection)
        / len(reference_words),
        4,
    )


def calculate_groundedness(
    answer: str,
    retrieved_context: list,
) -> float:
    """
    Estimate whether generated answer
    is grounded in retrieved context.

    Uses lexical overlap for the demo.
    """

    if not answer.strip():
        return 0.0

    if not retrieved_context:
        return 0.0

    context = " ".join(
        item.text
        for item in retrieved_context
        if getattr(item, "text", None)
    )

    if not context.strip():
        return 0.0

    answer_words = set(
        answer.lower().split()
    )

    context_words = set(
        context.lower().split()
    )

    if not answer_words:
        return 0.0

    overlap = (
        answer_words
        & context_words
    )

    return round(
        len(overlap)
        / len(answer_words),
        4,
    )


def calculate_retrieval_hit(
    retrieved_context: list,
    expected_keywords: list[str],
) -> float:
    """
    Determine whether retrieval returned
    context containing expected concepts.
    """

    if not expected_keywords:
        return 1.0

    if not retrieved_context:
        return 0.0

    context = " ".join(
        item.text
        for item in retrieved_context
        if getattr(item, "text", None)
    ).lower()

    matched = 0

    for keyword in expected_keywords:

        if keyword.lower() in context:
            matched += 1

    return round(
        matched / len(expected_keywords),
        4,
    )


def calculate_overall_score(
    metrics: EvaluationMetrics,
) -> float:
    """
    Weighted overall quality score.

    Retrieval and groundedness receive
    higher weights because this is a
    retrieval-grounded application.
    """

    score = (
        0.20
        * metrics.keyword_score
        + 0.20
        * metrics.answer_similarity
        + 0.35
        * metrics.groundedness
        + 0.25
        * metrics.retrieval_hit
    )

    return round(
        score,
        4,
    )