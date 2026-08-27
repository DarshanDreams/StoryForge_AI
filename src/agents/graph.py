from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from src.agents.nodes import (
    generate_node,
    retrieve_node,
)

from src.agents.state import (
    AgentState,
)

from src.observability.logger import (
    get_logger,
)

from src.observability.tracing import (
    trace,
)


logger = get_logger(__name__)


class StoryAgent:
    """
    Story reasoning agent.

    Responsibilities:
    1. Receive user query.
    2. Retrieve relevant story context.
    3. Generate grounded answer.
    4. Expose execution state.
    5. Provide observability around execution.
    """

    def __init__(
        self,
        retriever,
        llm_gateway,
    ):

        self.retriever = retriever

        self.llm_gateway = llm_gateway

        self.graph = (
            self._build_graph()
        )

    def _build_graph(self):

        workflow = StateGraph(
            AgentState
        )

        workflow.add_node(
            "retrieve",
            lambda state:
                retrieve_node(
                    state,
                    self.retriever,
                ),
        )

        workflow.add_node(
            "generate",
            lambda state:
                generate_node(
                    state,
                    self.llm_gateway,
                ),
        )

        workflow.add_edge(
            START,
            "retrieve",
        )

        workflow.add_edge(
            "retrieve",
            "generate",
        )

        workflow.add_edge(
            "generate",
            END,
        )

        return workflow.compile()

    def run(
        self,
        query: str,
        story_id: str = "",
    ) -> AgentState:
        """
        Execute the complete agent workflow.
        """

        if not query.strip():

            raise ValueError(
                "Agent query cannot be empty."
            )

        with trace(
            "agent.run",
            metadata={
                "story_id": story_id,
                "query_length": len(
                    query
                ),
            },
        ):

            logger.info(
                "Agent execution started",
                extra={
                    "event": "agent_request",
                    "metadata": {
                        "story_id": story_id,
                    },
                },
            )

            state: AgentState = {
                "user_query": query,
                "story_id": story_id,
                "retrieved_context": [],
                "answer": "",
                "needs_retrieval": True,
                "error": "",
            }

            result = (
                self.graph.invoke(
                    state
                )
            )

            logger.info(
                "Agent execution completed",
                extra={
                    "event": "agent_response",
                    "metadata": {
                        "story_id": story_id,
                        "retrieval_count": len(
                            result.get(
                                "retrieved_context",
                                [],
                            )
                        ),
                        "has_answer": bool(
                            result.get(
                                "answer"
                            )
                        ),
                        "has_error": bool(
                            result.get(
                                "error"
                            )
                        ),
                    },
                },
            )

            return result