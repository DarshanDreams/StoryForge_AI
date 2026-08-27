from __future__ import annotations

from src.agents.prompts import (
    SYSTEM_PROMPT,
    build_user_prompt,
)

from src.agents.guardrails import (
    calculate_confidence,
    validate_query,
    validate_retrieval,
)

from src.agents.state import (
    AgentState,
)

from src.observability.logger import (
    get_logger,
)

from src.retrieval.retriever import (
    InMemoryRetriever,
)


logger = get_logger(
    __name__
)


class StoryAgent:
    """
    Retrieval-grounded StoryForge agent.

    Flow:

        Query
          ↓
        Validation
          ↓
        Retrieval
          ↓
        Evidence validation
          ↓
        LLM generation
          ↓
        Source attribution
          ↓
        Response
    """

    def __init__(
        self,
        llm,
        retriever: InMemoryRetriever,
        retrieval_top_k: int = 5,
    ):

        self.llm = llm

        self.retriever = (
            retriever
        )

        self.retrieval_top_k = (
            retrieval_top_k
        )

    def run(
        self,
        query: str,
        story_id: str = "default",
    ) -> dict:
        """
        Execute the complete agent pipeline.
        """

        state = AgentState(
            query=query
        )

        # -------------------------------------------------
        # 1. Query validation
        # -------------------------------------------------

        valid, error = (
            validate_query(
                query
            )
        )

        if not valid:

            state.blocked = True
            state.error = error
            state.answer = error

            return self._build_response(
                state
            )

        # -------------------------------------------------
        # 2. Retrieval
        # -------------------------------------------------

        try:

            results = (
                self.retriever.retrieve(
                    query=query,
                    limit=self.retrieval_top_k,
                )
            )

            state.retrieved_context = (
                results
            )

        except Exception as exc:

            logger.exception(
                "Retrieval failed",
                extra={
                    "event": (
                        "retrieval_failed"
                    ),
                    "metadata": {
                        "story_id": story_id,
                    },
                },
            )

            state.blocked = True

            state.error = (
                "Unable to retrieve story context."
            )

            state.answer = state.error

            return self._build_response(
                state
            )

        # -------------------------------------------------
        # 3. Retrieval guardrail
        # -------------------------------------------------

        valid, error = (
            validate_retrieval(
                state.retrieved_context
            )
        )

        if not valid:

            state.blocked = True

            state.error = error

            state.answer = error

            state.confidence = 0.0

            return self._build_response(
                state
            )

        # -------------------------------------------------
        # 4. Build context
        # -------------------------------------------------

        state.context_text = (
            self._build_context(
                state.retrieved_context
            )
        )

        # -------------------------------------------------
        # 5. Confidence
        # -------------------------------------------------

        state.confidence = (
            calculate_confidence(
                state.retrieved_context
            )
        )

        # -------------------------------------------------
        # 6. LLM generation
        # -------------------------------------------------

        try:

            user_prompt = (
                build_user_prompt(
                    query=query,
                    context=(
                        state.context_text
                    ),
                )
            )

            response = (
                self.llm.generate(
                    system_prompt=(
                        SYSTEM_PROMPT
                    ),
                    user_prompt=(
                        user_prompt
                    ),
                )
            )

            state.answer = (
                self._extract_answer(
                    response
                )
            )

        except Exception as exc:

            logger.exception(
                "Agent generation failed",
                extra={
                    "event": (
                        "agent_generation_failed"
                    ),
                    "metadata": {
                        "story_id": story_id,
                    },
                },
            )

            state.error = (
                "The AI model could not "
                "generate an answer."
            )

            state.answer = (
                state.error
            )

        # -------------------------------------------------
        # 7. Sources
        # -------------------------------------------------

        state.sources = [
            {
                "source": result.source,
                "chunk_index": (
                    result.chunk_index
                ),
                "score": result.score,
                "text": result.chunk.text,
            }
            for result in (
                state.retrieved_context
            )
        ]

        return self._build_response(
            state
        )

    def _build_context(
        self,
        results,
    ) -> str:

        context_parts = []

        for index, result in enumerate(
            results,
            start=1,
        ):

            context_parts.append(
                f"""
[Source {index}]
File: {result.source}
Chunk: {result.chunk_index}
Relevance: {result.score:.3f}

{result.chunk.text}
"""
            )

        return "\n".join(
            context_parts
        )

    def _extract_answer(
        self,
        response,
    ) -> str:

        if isinstance(
            response,
            str,
        ):

            return response.strip()

        if isinstance(
            response,
            dict,
        ):

            answer = response.get(
                "answer"
            )

            if answer:
                return str(
                    answer
                ).strip()

            content = response.get(
                "content"
            )

            if content:
                return str(
                    content
                ).strip()

        return str(
            response
        ).strip()

    def _build_response(
        self,
        state: AgentState,
    ) -> dict:

        return {
            "query": state.query,
            "answer": state.answer,
            "retrieved_context": (
                state.retrieved_context
            ),
            "context_text": (
                state.context_text
            ),
            "sources": state.sources,
            "confidence": (
                state.confidence
            ),
            "blocked": state.blocked,
            "error": state.error,
            "metadata": state.metadata,
        }