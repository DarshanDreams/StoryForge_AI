from types import SimpleNamespace

from src.observability.run_store import RunStore
from src.services.creative_story_service import CreativeStoryService


class FakeLLM:
    model = "test-model"

    def generate(self, system_prompt, user_prompt):
        return "Generated creative output."


class FakeRetriever:
    def retrieve(self, query, limit):
        result = SimpleNamespace(
            chunk=SimpleNamespace(text="Mara enters the observatory."),
            score=0.9,
            source="story.txt",
            chunk_index=0,
        )
        result.to_dict = lambda: {
            "text": result.chunk.text,
            "score": result.score,
            "source": result.source,
            "chunk_index": result.chunk_index,
        }
        return [result]


def test_creative_action_persists_trace(tmp_path):
    store = RunStore(tmp_path / "runs.jsonl")
    service = CreativeStoryService(FakeLLM(), FakeRetriever(), store)

    result = service.run_action(
        action="Plan episode",
        brief="Plan Mara's next episode.",
        story_id="story-1",
    )

    assert result["action"] == "Plan episode"
    assert result["retrieved_chunks"] == 1
    assert result["output"] == "Generated creative output."
    assert store.recent()[0]["run_id"] == result["run_id"]