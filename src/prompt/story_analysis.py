SYSTEM_PROMPT = """
You are StoryForge AI, a professional story analysis engine.

Your job is to analyze stories accurately and extract structured
narrative information.

You must:

1. Identify important characters.
2. Identify relationships between characters.
3. Identify major narrative events.
4. Identify themes.
5. Identify scene-level information.
6. Identify character motivations and arcs.
7. Ground every extracted fact in the provided story.

Rules:

- Never invent facts.
- Never introduce characters that do not exist.
- Never invent relationships.
- Include a relationship only when both character names and its type are known;
  otherwise omit that relationship from the array.
- Never assume information that is not explicitly supported.
- If something cannot be determined, return an empty value.
- Preserve names exactly as they appear in the story.
- Prefer concise, factual descriptions.
- Return only information supported by the input story.

The output must follow the application's structured schema.
"""


def build_story_analysis_prompt(
    story: str,
) -> str:

    return f"""
Analyze the following story and return structured JSON.

STORY
-----
{story}
-----

Return a JSON object with this exact structure:

{{
  "story_summary": "Brief 1-2 sentence summary of the story",
  "themes": ["theme1", "theme2"],
  "characters": [
    {{
      "name": "Character Name",
      "role": "protagonist/antagonist/supporting",
      "description": "Brief description",
      "personality_traits": ["trait1", "trait2"],
      "goals": ["goal1", "goal2"],
      "fears": ["fear1"],
      "motivations": ["motivation1"],
      "arc": "Character arc summary"
    }}
  ],
  "relationships": [
    {{
      "from_character": "Character A",
      "to_character": "Character B",
      "relationship_type": "ally/rival/family/other",
      "description": "How they interact"
    }}
  ],
  "narrative_events": [
    {{
      "title": "Event Title",
      "description": "What happens",
      "beat_type": "inciting_incident/turning_point/climax/resolution/other",
      "emotional_impact": "How it affects the story"
    }}
  ],
  "scene_outline": [
    {{
      "scene_number": 1,
      "title": "Scene Title",
      "scene_type": "exposition/rising_action/climax/falling_action/other",
      "location": "Where the scene takes place",
      "description": "What happens in this scene",
      "purpose": "Why this scene is important",
      "conflict": "What conflict appears here"
    }}
  ]
}}

Rules:

- Never invent facts or characters.
- Ground every extracted fact in the provided story.
- If information is unavailable, use empty strings or empty arrays.
- Preserve character names exactly as they appear.
- Return ONLY valid JSON, no markdown fences or extra text.
"""