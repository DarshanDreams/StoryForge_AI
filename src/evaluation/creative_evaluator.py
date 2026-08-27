from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class CreativeEvaluation:
    story_consistency: float
    character_consistency: float
    groundedness: float
    dialogue_quality: float
    continuity: float
    overall_score: float

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", value.lower()))


def evaluate_creative_output(
    brief: str,
    output: str,
    context: str,
) -> CreativeEvaluation:
    brief_tokens = _tokens(brief)
    output_tokens = _tokens(output)
    context_tokens = _tokens(context)

    alignment = (
        len(brief_tokens & output_tokens) / len(brief_tokens)
        if brief_tokens
        else 0.0
    )
    groundedness = (
        len(output_tokens & context_tokens) / len(output_tokens)
        if output_tokens and context_tokens
        else 0.0
    )
    has_dialogue = '"' in output or "dialogue" in output.lower()
    has_structure = any(
        marker in output.lower()
        for marker in ("scene", "character", "conflict", "setting")
    )
    dialogue_quality = 1.0 if has_dialogue else 0.5 if output else 0.0
    continuity = 1.0 if has_structure else 0.5 if output else 0.0
    story_consistency = round((groundedness + alignment) / 2, 4)
    character_consistency = round(groundedness, 4)
    overall = round(
        sum(
            (
                story_consistency,
                character_consistency,
                groundedness,
                dialogue_quality,
                continuity,
            )
        )
        / 5,
        4,
    )
    return CreativeEvaluation(
        story_consistency=round(story_consistency, 4),
        character_consistency=character_consistency,
        groundedness=round(groundedness, 4),
        dialogue_quality=dialogue_quality,
        continuity=continuity,
        overall_score=overall,
    )