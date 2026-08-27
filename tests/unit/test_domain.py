from src.domain.models import StoryAnalysis


def test_story_analysis():

    analysis = StoryAnalysis(
        story_summary="A story.",
        themes=["hope"],
    )

    assert analysis.story_summary == "A story."
    assert analysis.themes == ["hope"]