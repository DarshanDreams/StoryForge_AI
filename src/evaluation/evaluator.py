from __future__ import annotations

from src.evaluation.runner import evaluate_case, run_evaluation


class StoryEvaluator:
    """Compatibility facade for the supported evaluation runner."""

    def __init__(self, agent=None):
        self.agent = agent

    def evaluate_case(self, case: dict) -> dict:
        if self.agent is None:
            raise ValueError("An agent is required for story evaluation.")
        return evaluate_case(self.agent, case)

    def evaluate(self, cases: list[dict]) -> dict:
        if self.agent is None:
            raise ValueError("An agent is required for story evaluation.")
        return run_evaluation(self.agent, cases)
