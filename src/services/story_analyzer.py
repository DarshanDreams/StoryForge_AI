from src.domain.models import (
    StoryAnalysis,
)

from src.prompt.story_analysis import (
    SYSTEM_PROMPT,
    build_story_analysis_prompt,
)


class StoryAnalyzer:

    def __init__(
        self,
        llm_gateway,
    ):

        self.llm_gateway = (
            llm_gateway
        )

    def analyze(
        self,
        story: str,
    ) -> StoryAnalysis:

        if not story.strip():

            raise ValueError(
                "Story cannot be empty."
            )

        prompt = (
            build_story_analysis_prompt(
                story
            )
        )

        try:
            raw_response = self.llm_gateway.generate(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=prompt,
            )
        except TypeError:
            raw_response = self.llm_gateway.generate(prompt)

        if not isinstance(raw_response, str):
            raw_response = getattr(raw_response, "content", raw_response)

        return self._parse_response(
            raw_response
        )

    def _parse_response(
        self,
        raw_response: str,
    ) -> StoryAnalysis:

        cleaned = (
            raw_response.strip()
        )

        if cleaned.startswith(
            "```json"
        ):

            cleaned = (
                cleaned[7:]
                .replace(
                    "```",
                    "",
                )
                .strip()
            )

        elif cleaned.startswith(
            "```"
        ):

            cleaned = (
                cleaned[3:]
                .replace(
                    "```",
                    "",
                )
                .strip()
            )

        return StoryAnalysis.model_validate_json(
            cleaned
        )