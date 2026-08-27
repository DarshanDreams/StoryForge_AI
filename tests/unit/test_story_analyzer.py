from src.domain.models import StoryAnalysis
from src.services.story_analyzer import StoryAnalyzer


class FakeGateway:

    def generate(self, request):

        class Response:
            content = """
            {
                "story_summary": "A short story.",
                "themes": ["hope"],
                "characters": [],
                "relationships": [],
                "narrative_events": [],
                "scene_outline": []
            }
            """

        return Response()


def test_story_analyzer():

    analyzer = StoryAnalyzer(
        FakeGateway()
    )

    result = analyzer.analyze(
        "A short story about hope."
    )

    assert isinstance(
        result,
        StoryAnalysis,
    )

    assert result.story_summary == (
        "A short story."
    )