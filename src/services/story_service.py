from dataclasses import dataclass

from src.config.settings import Settings
from src.domain.models import StoryAnalysis
from src.repositories.database import (
    create_session_factory,
)
from src.repositories.story_repository import (
    StoryRepository,
)
from src.services.story_analyzer import StoryAnalyzer


@dataclass
class AnalysisResult:
    story_id: int
    analysis: StoryAnalysis


class StoryService:

    def __init__(
        self,
        analyzer: StoryAnalyzer,
        settings: Settings,
    ):
        self.analyzer = analyzer

        session_factory = (
            create_session_factory(
                settings.database_url
            )
        )

        self.repository = StoryRepository(
            session_factory
        )

    def analyze_and_save(
        self,
        story_text: str,
    ) -> AnalysisResult:

        analysis = self.analyzer.analyze(
            story_text
        )

        title = self._generate_title(
            analysis.story_summary
        )

        story = self.repository.create(
            title=title,
            summary=analysis.story_summary,
            content=story_text,
        )

        return AnalysisResult(
            story_id=story.id,
            analysis=analysis,
        )

    def list_stories(self):
        return self.repository.list_all()

    @staticmethod
    def _generate_title(
        summary: str,
    ) -> str:

        words = summary.split()

        if not words:
            return "Untitled Story"

        return " ".join(
            words[:8]
        ).rstrip(".") + "..."