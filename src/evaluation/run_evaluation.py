import json
from pathlib import Path

from src.config.settings import get_settings
from src.evaluation.evaluator import StoryEvaluator
from src.llm.gateway import LLMGateway
from src.services.story_analyzer import StoryAnalyzer


DATASET = Path(
    "evaluation/datasets/story_analysis.jsonl"
)


def main():

    settings = get_settings()

    gateway = LLMGateway(
        settings
    )

    analyzer = StoryAnalyzer(
        gateway
    )

    evaluator = StoryEvaluator()

    results = []

    with DATASET.open(
        encoding="utf-8"
    ) as file:

        for line in file:

            record = json.loads(
                line
            )

            analysis = analyzer.analyze(
                record["input"]
            )

            scores = {
                "has_summary": bool(
                    analysis.story_summary
                ),
                "characters": len(
                    analysis.characters
                ),
                "relationships": len(
                    analysis.relationships
                ),
                "narrative_events": len(
                    analysis.narrative_events
                ),
                "scenes": len(
                    analysis.scene_outline
                ),
                "themes": len(
                    analysis.themes
                ),
            }

            results.append(
                {
                    "input": record["input"],
                    "scores": scores,
                }
            )

    output = Path(
        "evaluation/results.json"
    )

    output.write_text(
        json.dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Evaluation saved to {output}"
    )


if __name__ == "__main__":
    main()