from src.evaluation.datasets import (
    GOLDEN_DATASET,
)

from src.evaluation.metrics import (
    EvaluationMetrics,
    calculate_answer_similarity,
    calculate_groundedness,
    calculate_keyword_score,
    calculate_overall_score,
    calculate_retrieval_hit,
)

from src.observability.logger import (
    get_logger,
)


logger = get_logger(
    __name__
)


def evaluate_case(
    agent,
    test_case: dict,
) -> dict:
    """
    Evaluate a single golden test case.
    """

    question = test_case[
        "question"
    ]

    expected_keywords = test_case.get(
        "expected_keywords",
        [],
    )

    reference_answer = test_case.get(
        "reference_answer",
        "",
    )

    try:

        result = agent.run(
            query=question,
            story_id="evaluation",
        )

        answer = result.get(
            "answer",
            "",
        )

        retrieved_context = result.get(
            "retrieved_context",
            [],
        )

        keyword_score = (
            calculate_keyword_score(
                answer,
                expected_keywords,
            )
        )

        answer_similarity = (
            calculate_answer_similarity(
                answer,
                reference_answer,
            )
        )

        groundedness = (
            calculate_groundedness(
                answer,
                retrieved_context,
            )
        )

        retrieval_hit = (
            calculate_retrieval_hit(
                retrieved_context,
                expected_keywords,
            )
        )

        metrics = EvaluationMetrics(
            keyword_score=keyword_score,
            answer_similarity=answer_similarity,
            groundedness=groundedness,
            retrieval_hit=retrieval_hit,
        )

        metrics.overall_score = (
            calculate_overall_score(
                metrics
            )
        )

        return {
            "case": test_case[
                "case"
            ],
            "question": question,
            "answer": answer,
            "metrics": metrics,
            "success": not bool(
                result.get("error")
            ),
            "error": result.get(
                "error",
                "",
            ),
        }

    except Exception as exc:

        logger.exception(
            "Evaluation case failed",
            extra={
                "event": (
                    "evaluation_case_failed"
                ),
                "metadata": {
                    "case": test_case[
                        "case"
                    ],
                },
            },
        )

        metrics = EvaluationMetrics()

        return {
            "case": test_case[
                "case"
            ],
            "question": question,
            "answer": "",
            "metrics": metrics,
            "success": False,
            "error": str(exc),
        }


def run_evaluation(
    agent,
    dataset=None,
) -> dict:
    """
    Run the complete evaluation suite.
    """

    dataset = (
        dataset
        if dataset is not None
        else GOLDEN_DATASET
    )

    results = []

    for test_case in dataset:

        result = evaluate_case(
            agent,
            test_case,
        )

        results.append(
            result
        )

    if not results:

        return {
            "summary": {
                "overall_score": 0.0,
                "retrieval_hit_rate": 0.0,
                "groundedness": 0.0,
                "keyword_score": 0.0,
                "answer_similarity": 0.0,
            },
            "results": [],
        }

    successful_results = [
        result
        for result in results
        if result["success"]
    ]

    if not successful_results:

        return {
            "summary": {
                "overall_score": 0.0,
                "retrieval_hit_rate": 0.0,
                "groundedness": 0.0,
                "keyword_score": 0.0,
                "answer_similarity": 0.0,
            },
            "results": results,
        }

    overall_score = sum(
        result[
            "metrics"
        ].overall_score
        for result in successful_results
    ) / len(
        successful_results
    )

    retrieval_hit_rate = sum(
        result[
            "metrics"
        ].retrieval_hit
        for result in successful_results
    ) / len(
        successful_results
    )

    groundedness = sum(
        result[
            "metrics"
        ].groundedness
        for result in successful_results
    ) / len(
        successful_results
    )

    keyword_score = sum(
        result[
            "metrics"
        ].keyword_score
        for result in successful_results
    ) / len(
        successful_results
    )

    answer_similarity = sum(
        result[
            "metrics"
        ].answer_similarity
        for result in successful_results
    ) / len(
        successful_results
    )

    summary = {
        "overall_score": round(
            overall_score,
            4,
        ),
        "retrieval_hit_rate": round(
            retrieval_hit_rate,
            4,
        ),
        "groundedness": round(
            groundedness,
            4,
        ),
        "keyword_score": round(
            keyword_score,
            4,
        ),
        "answer_similarity": round(
            answer_similarity,
            4,
        ),
    }

    logger.info(
        "Evaluation completed",
        extra={
            "event": (
                "evaluation_completed"
            ),
            "metadata": summary,
        },
    )

    return {
        "summary": summary,
        "results": results,
    }