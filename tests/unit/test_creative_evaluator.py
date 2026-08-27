from src.evaluation.creative_evaluator import evaluate_creative_output


def test_creative_evaluation_returns_bounded_scores():
    result = evaluate_creative_output(
        brief="Mara enters the observatory",
        output='Scene: Mara enters. "I am ready."',
        context="Mara enters the observatory.",
    )

    assert 0.0 <= result.overall_score <= 1.0
    assert result.dialogue_quality == 1.0
    assert result.continuity == 1.0
