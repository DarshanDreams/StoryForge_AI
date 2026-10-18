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


def test_story_analysis_skips_incomplete_relationships():
    analysis = StoryAnalysis.from_json(
        '{"story_summary":"A story.","relationships":[{},'
        '{"from_character":"Mara","to_character":"Ilan",'
        '"relationship_type":"siblings"}]}'
    )

    assert len(analysis.relationships) == 1
    assert analysis.relationships[0].from_character == "Mara"
    assert analysis.relationships[0].relationship_type == "siblings"