from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Character(BaseModel):
    name: str
    role: str = "unknown"
    description: str = ""
    personality_traits: list[str] = Field(
        default_factory=list
    )
    goals: list[str] = Field(
        default_factory=list
    )
    fears: list[str] = Field(
        default_factory=list
    )
    motivations: list[str] = Field(
        default_factory=list
    )
    arc: str = ""


class Relationship(BaseModel):
    from_character: str
    to_character: str
    relationship_type: str
    description: str = ""


class NarrativeEvent(BaseModel):
    title: str
    description: str
    beat_type: str = "event"
    emotional_impact: str = ""


class Scene(BaseModel):
    scene_number: int
    title: str = ""
    scene_type: str = "unknown"
    location: str = ""
    description: str = ""
    purpose: str = ""
    conflict: str = ""


class StoryAnalysis(BaseModel):
    story_summary: str
    themes: list[str] = Field(
        default_factory=list
    )
    characters: list[Character] = Field(
        default_factory=list
    )
    relationships: list[Relationship] = Field(
        default_factory=list
    )
    narrative_events: list[NarrativeEvent] = Field(
        default_factory=list
    )
    scene_outline: list[Scene] = Field(
        default_factory=list
    )


class StoryRecord(BaseModel):
    id: int
    title: str
    summary: str
    content: str
    created_at: datetime


class RetrievalResult(BaseModel):
    text: str
    score: float
    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class AgentState(BaseModel):
    user_query: str
    story_id: int | None = None
    retrieved_context: list[RetrievalResult] = Field(
        default_factory=list
    )
    tool_results: list[str] = Field(
        default_factory=list
    )
    answer: str = ""