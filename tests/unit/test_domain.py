from src.domain.models import Character, StoryAnalysis


def test_story_analysis():

    analysis = StoryAnalysis(
        story_summary="A story.",
        themes=["hope"],
    )

    assert analysis.story_summary == "A story."
    assert analysis.themes == ["hope"]


def test_story_analysis_parses_nested_records_without_pydantic():
    analysis = StoryAnalysis.from_json(
        '{"story_summary":"A story.","characters":[{"name":"Mara"}]}'
    )

    assert analysis.story_summary == "A story."
    assert len(analysis.characters) == 1
    assert isinstance(analysis.characters[0], Character)
    assert analysis.characters[0].role == "unknown"