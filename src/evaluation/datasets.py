"""
Small deterministic golden dataset for the
StoryForge demo.

In a real system this would normally live
outside application code, for example in:

- JSON
- CSV
- database
- evaluation platform
"""

GOLDEN_DATASET = [
    {
        "case": "protagonist_motivation",
        "question": (
            "Why does the protagonist leave home?"
        ),
        "expected_keywords": [
            "protagonist",
        ],
        "reference_answer": (
            "The protagonist leaves home because "
            "they want to pursue a new future."
        ),
    },
    {
        "case": "character_relationship",
        "question": (
            "What is the relationship between "
            "the protagonist and their family?"
        ),
        "expected_keywords": [
            "protagonist",
            "family",
        ],
        "reference_answer": (
            "The protagonist has an important "
            "relationship with their family."
        ),
    },
    {
        "case": "central_conflict",
        "question": (
            "What is the central conflict of the story?"
        ),
        "expected_keywords": [
            "conflict",
        ],
        "reference_answer": (
            "The central conflict involves the "
            "protagonist facing an important challenge."
        ),
    },
]