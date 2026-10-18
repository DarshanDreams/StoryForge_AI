import json
from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Any


@dataclass
class Character:
    name: str
    role: str = "unknown"
    description: str = ""
    personality_traits: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)
    fears: list[str] = field(default_factory=list)
    motivations: list[str] = field(default_factory=list)
    arc: str = ""


@dataclass
class Relationship:
    from_character: str
    to_character: str
    relationship_type: str
    description: str = ""


@dataclass
class NarrativeEvent:
    title: str
    description: str
    beat_type: str = "event"
    emotional_impact: str = ""


@dataclass
class Scene:
    scene_number: int
    title: str = ""
    scene_type: str = "unknown"
    location: str = ""
    description: str = ""
    purpose: str = ""
    conflict: str = ""


@dataclass
class StoryAnalysis:
    story_summary: str
    themes: list[str] = field(default_factory=list)
    characters: list[Character] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    narrative_events: list[NarrativeEvent] = field(default_factory=list)
    scene_outline: list[Scene] = field(default_factory=list)

    @classmethod
    def from_json(cls, raw_json: str) -> "StoryAnalysis":
        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            raise ValueError("Story analysis must be valid JSON.") from exc

        if not isinstance(payload, dict):
            raise ValueError("Story analysis JSON must contain an object.")

        payload = dict(payload)
        payload["characters"] = _parse_records(payload, "characters", Character)
        payload["relationships"] = _parse_records(
            payload, "relationships", Relationship
        )
        payload["narrative_events"] = _parse_records(
            payload, "narrative_events", NarrativeEvent
        )
        payload["scene_outline"] = _parse_records(payload, "scene_outline", Scene)

        valid_fields = {item.name for item in fields(cls)}
        try:
            values = {
                key: value
                for key, value in payload.items()
                if key in valid_fields
            }
            return cls(**values)
        except TypeError as exc:
            raise ValueError(f"Invalid story analysis data: {exc}") from exc


def _parse_records(
    payload: dict[str, Any],
    key: str,
    record_type: type[Any],
) -> list[Any]:
    records = payload.get(key, [])
    if not isinstance(records, list):
        raise ValueError(f"Story analysis field '{key}' must be a list.")

    valid_fields = {item.name for item in fields(record_type)}
    parsed = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(
                f"Story analysis field '{key}' item {index} must be an object."
            )
        values = {name: value for name, value in record.items() if name in valid_fields}
        try:
            parsed.append(record_type(**values))
        except TypeError as exc:
            raise ValueError(
                f"Invalid item {index} in story analysis field '{key}': {exc}"
            ) from exc
    return parsed


@dataclass
class StoryRecord:
    id: int
    title: str
    summary: str
    content: str
    created_at: datetime


@dataclass
class RetrievalResult:
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    user_query: str
    story_id: int | None = None
    retrieved_context: list[RetrievalResult] = field(default_factory=list)
    tool_results: list[str] = field(default_factory=list)
    answer: str = ""