from __future__ import annotations

from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
import uuid

from src.observability.run_store import RunStore
from src.observability.tracing import trace
from src.evaluation.creative_evaluator import evaluate_creative_output
import json


CREATIVE_TASKS = {
    "Plan episode": (
        "Create a practical episode plan with a logline, objectives, "
        "turning points, scenes, and character arcs."
    ),
    "Generate scenes": (
        "Write a screenplay scene outline with setting, action, conflict, "
        "and emotional progression."
    ),
    "Generate dialogue": (
        "Write screenplay dialogue for the requested moment. Include only "
        "characters supported by the story context."
    ),
    "Validate continuity": (
        "Audit the proposed material for contradictions in characters, "
        "timeline, setting, relationships, and established facts."
    ),
    "Critique screenplay": (
        "Critique the proposed material for story consistency, character "
        "quality, pacing, conflict, dialogue, and clarity."
    ),
    "Rewrite weak sections": (
        "Rewrite the proposed material to address the critique while "
        "preserving established story facts and character identity."
    ),
    "Generate video prompt": (
        "Convert the proposed material into a structured video-generation "
        "prompt with shots, camera, lighting, motion, dialogue, sound, "
        "characters, setting, and negative constraints. Return valid JSON "
        "with keys: title, logline, visual_style, shots, characters, "
        "setting, action, dialogue, sound, negative_constraints."
    ),
}

CREATIVE_TOKEN_BUDGETS = {
    "Plan episode": 650,
    "Generate scenes": 700,
    "Generate dialogue": 700,
    "Validate continuity": 400,
    "Critique screenplay": 400,
    "Rewrite weak sections": 750,
    "Generate video prompt": 700,
}


class CreativeStoryService:
    """Orchestrate creative story actions around retrieved story evidence."""

    def __init__(self, llm, retriever, run_store: RunStore | None = None):
        self.llm = llm
        self.retriever = retriever
        self.run_store = run_store or RunStore()

    def retrieve_context(self, query: str, limit: int = 5) -> list:
        return self.retriever.retrieve(query=query, limit=limit)

    def run_action(
        self,
        action: str,
        brief: str,
        prior_output: str = "",
        limit: int = 5,
        story_id: str = "",
        prompt_version: str = "creative-v1",
        retrieved_context: list | None = None,
    ) -> dict:
        if action not in CREATIVE_TASKS:
            raise ValueError(f"Unsupported creative action: {action}")
        if not brief.strip():
            raise ValueError("A creative brief is required.")

        run_id = str(uuid.uuid4())
        started = perf_counter()
        retrieved = (
            retrieved_context
            if retrieved_context is not None
            else self.retrieve_context(brief, limit=limit)
        )
        context = "\n\n".join(
            f"[Source {index}] {result.chunk.text}"
            for index, result in enumerate(retrieved, start=1)
        )
        if not context:
            context = "No relevant story context was retrieved."

        user_prompt = self._build_prompt(
            action=action,
            brief=brief,
            context=context,
            prior_output=prior_output,
        )

        with trace(
            "creative_story.run",
            request_id=run_id,
            metadata={
                "action": action,
                "story_id": story_id,
                "retrieved_chunks": len(retrieved),
            },
        ):
            output = self.llm.generate(
                system_prompt=(
                    "You are StoryForge AI's creative story agent. "
                    "Use only the supplied story context. Never invent "
                    "facts, characters, or continuity. Return clear "
                    "production-ready text."
                ),
                user_prompt=user_prompt,
                max_tokens=CREATIVE_TOKEN_BUDGETS[action],
            )

        structured_output = self._structure_output(action, output)
        usage = getattr(self.llm, "last_usage", {}) or {}
        evaluation = evaluate_creative_output(
            brief,
            self._output_text(structured_output),
            context,
        ).to_dict()
        record = {
            "run_id": run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "story_id": story_id,
            "agent_selected": "creative_story_agent",
            "action": action,
            "prompt_version": prompt_version,
            "model": getattr(
                self.llm,
                "last_model",
                getattr(self.llm, "model", "unknown"),
            ),
            "provider": getattr(self.llm, "last_provider", "unknown"),
            "input": brief,
            "retrieval_context": [result.to_dict() for result in retrieved],
            "retrieved_chunks": len(retrieved),
            "prompt": user_prompt,
            "output": structured_output,
            "validation": "pending" if action != "Validate continuity" else output,
            "critique": output if action == "Critique screenplay" else "",
            "rewrite": output if action == "Rewrite weak sections" else "",
            "latency_ms": round((perf_counter() - started) * 1000, 2),
            "tool_calls": ["retrieve_context", "llm.generate"],
            "input_tokens": usage.get("prompt_tokens"),
            "output_tokens": usage.get("completion_tokens"),
            "evaluation_scores": evaluation,
        }
        self.run_store.append(record)
        return record

    def _structure_output(self, action: str, output: str):
        if action != "Generate video prompt":
            return output
        cleaned = output.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:].replace("```", "").strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:].replace("```", "").strip()
        try:
            parsed = json.loads(cleaned)
            return parsed if isinstance(parsed, dict) else {"prompt": output}
        except json.JSONDecodeError:
            return {
                "prompt": output,
                "shots": [],
                "characters": [],
                "setting": "",
                "sound": "",
                "negative_constraints": [],
            }

    @staticmethod
    def _output_text(output) -> str:
        return json.dumps(output) if isinstance(output, dict) else str(output)

    def run_pipeline(
        self,
        brief: str,
        story_id: str = "",
        limit: int = 5,
        on_stage=None,
    ) -> dict:
        def report(stage: str) -> None:
            if on_stage is not None:
                on_stage(stage)

        retrieved = self.retrieve_context(brief, limit=limit)
        report("Creating episode plan")
        plan = self.run_action(
            "Plan episode", brief, limit=limit, story_id=story_id,
            retrieved_context=retrieved,
        )
        report("Generating scenes")
        scene = self.run_action(
            "Generate scenes", brief, prior_output=plan["output"],
            limit=limit, story_id=story_id, retrieved_context=retrieved,
        )
        report("Generating dialogue")
        dialogue = self.run_action(
            "Generate dialogue", brief, prior_output=scene["output"],
            limit=limit, story_id=story_id, retrieved_context=retrieved,
        )
        report("Checking continuity and screenplay quality in parallel")
        with ThreadPoolExecutor(max_workers=2) as executor:
            continuity_future = executor.submit(
                self.run_action,
                "Validate continuity",
                brief,
                dialogue["output"],
                limit,
                story_id,
                "creative-v1",
                retrieved,
            )
            critique_future = executor.submit(
                self.run_action,
                "Critique screenplay",
                brief,
                dialogue["output"],
                limit,
                story_id,
                "creative-v1",
                retrieved,
            )
            continuity = continuity_future.result()
            critique = critique_future.result()
        report("Rewriting from the reviews")
        rewrite = self.run_action(
            "Rewrite weak sections", brief,
            prior_output=(
                f"DRAFT:\n{dialogue['output']}\n\n"
                f"CONTINUITY AUDIT:\n{continuity['output']}\n\n"
                f"CRITIQUE:\n{critique['output']}"
            ),
            limit=limit, story_id=story_id, retrieved_context=retrieved,
        )
        report("Preparing video prompt")
        video = self.run_action(
            "Generate video prompt", brief, prior_output=rewrite["output"],
            limit=limit, story_id=story_id, retrieved_context=retrieved,
        )
        return {
            "run_id": video["run_id"],
            "steps": {
                "plan": plan,
                "scenes": scene,
                "dialogue": dialogue,
                "continuity": continuity,
                "critique": critique,
                "rewrite": rewrite,
                "video_prompt": video,
            },
        }

    def _build_prompt(
        self,
        action: str,
        brief: str,
        context: str,
        prior_output: str,
    ) -> str:
        previous = prior_output or "No previous creative output."
        return f"""TASK
{CREATIVE_TASKS[action]}

CREATIVE BRIEF
{brief}

ESTABLISHED STORY CONTEXT
{context}

PREVIOUS OUTPUT
{previous}

Return the requested result. Mark uncertainty instead of inventing facts.
"""