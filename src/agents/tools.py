from src.retrieval.retriever import StoryRetriever


class RetrievalTool:

    name = "story_retrieval"

    def __init__(
        self,
        retriever: StoryRetriever,
    ):
        self.retriever = retriever

    def run(
        self,
        query: str,
    ) -> list[str]:

        results = self.retriever.retrieve(
            query
        )

        return [
            result.text
            for result in results
        ]