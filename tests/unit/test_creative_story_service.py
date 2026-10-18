from threading import Barrier
from types import SimpleNamespace

from src.observability.run_store import RunStore
from src.services.creative_story_service import CreativeStoryService


class FakeLLM:
    model = "test-model"

    def generate(self, system_prompt, user_prompt, max_tokens=None):
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


def test_full_pipeline_runs_independent_reviews_concurrently(tmp_path):
    barrier = Barrier(2)

    class ConcurrentLLM(FakeLLM):
        def generate(self, system_prompt, user_prompt, max_tokens=None):
            if (
                "Audit the proposed material" in user_prompt
                or "Critique the proposed material" in user_prompt
            ):
                barrier.wait(timeout=2)
            return "Generated creative output."

    service = CreativeStoryService(
        ConcurrentLLM(),
        FakeRetriever(),
        RunStore(tmp_path / "runs.jsonl"),
    )
    stages = []

    pipeline = service.run_pipeline(
        "Plan Mara's next episode.",
        story_id="story-1",
        on_stage=stages.append,
    )

    assert set(pipeline["steps"]) == {
        "plan",
        "scenes",
        "dialogue",
        "continuity",
        "critique",
        "rewrite",
        "video_prompt",
    }
    assert "Checking continuity and screenplay quality in parallel" in stages