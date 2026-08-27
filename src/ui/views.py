from __future__ import annotations

import streamlit as st

from src.evaluation.runner import run_evaluation
from src.observability.run_store import RunStore
from src.services.creative_story_service import CREATIVE_TASKS
from src.ui.components import display_items, display_sources
from src.ui.runtime import (
    agent,
    analyzer,
    clear_story,
    creative_service,
    create_document_from_text,
    index_document,
    llm,
    parser,
    retriever,
    settings,
)


def render_sidebar() -> None:
    with st.sidebar:
        st.title("StoryForge AI")
        st.caption("Retrieval-grounded story intelligence")
        st.divider()
        st.subheader("Upload Story")
        uploaded_file = st.file_uploader("Choose a story", type=["txt", "pdf", "docx"])
        if st.button("Load & Index", use_container_width=True):
            if uploaded_file is None:
                st.warning("Please upload a file first.")
            else:
                try:
                    with st.spinner("Parsing, chunking and indexing..."):
                        index_document(parser().parse(uploaded_file))
                    st.success("Story indexed successfully.")
                except Exception as exc:
                    st.error(f"Failed to process document: {exc}")
        st.divider()
        st.subheader("Paste Story")
        pasted_text = st.text_area("Story", height=180, placeholder="Paste your story here...", label_visibility="collapsed")
        if st.button("Use Pasted Story", use_container_width=True):
            if not pasted_text.strip():
                st.warning("Please enter story text.")
            else:
                try:
                    with st.spinner("Chunking and indexing..."):
                        index_document(create_document_from_text(pasted_text))
                    st.success("Story indexed successfully.")
                except Exception as exc:
                    st.error(f"Failed to index story: {exc}")
        document = st.session_state.document
        if document:
            st.divider()
            st.subheader("Current Story")
            st.write(document.filename)
            st.caption(f"{document.metadata.get('word_count', 0):,} words")
            if st.button("Clear Story", use_container_width=True):
                clear_story()
                st.rerun()


def render_story_overview() -> None:
    document = st.session_state.document
    st.subheader("Story Overview")
    columns = st.columns(4)
    columns[0].metric("Words", f"{document.metadata.get('word_count', 0):,}")
    columns[1].metric("Characters", f"{document.metadata.get('character_count', 0):,}")
    columns[2].metric("Chunks", len(st.session_state.chunks))
    columns[3].metric("Indexed", "Yes" if st.session_state.indexed else "No")
    with st.expander("View Story"):
        st.text_area("Story content", value=st.session_state.story_text, height=300, disabled=True, label_visibility="collapsed")


def render_analysis() -> None:
    st.header("Story Analysis")
    st.write("Extract characters, relationships, scenes, narrative beats, and themes.")
    if st.button("Analyze Story", type="primary", use_container_width=True):
        try:
            with st.spinner("Analyzing story..."):
                st.session_state.analysis = analyzer().analyze(st.session_state.story_text)
            st.success("Analysis completed.")
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
    analysis = st.session_state.analysis
    if not analysis:
        return
    st.divider()
    st.subheader("Summary")
    st.write(getattr(analysis, "story_summary", "No summary returned."))
    for title, field in (("Characters", "characters"), ("Relationships", "relationships"), ("Narrative Beats", "narrative_events"), ("Scenes", "scene_outline"), ("Themes", "themes")):
        st.subheader(title)
        display_items(getattr(analysis, field, []))


def render_agent() -> None:
    st.header("Ask StoryForge")
    st.write("Ask questions grounded in the uploaded story.")
    query = st.text_input("Question", placeholder="Why did the protagonist leave home?")
    if st.button("Ask StoryForge", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Please enter a question.")
        else:
            try:
                with st.spinner("Retrieving evidence and generating answer..."):
                    st.session_state.agent_result = agent().run(query=query, story_id=st.session_state.document.document_id)
            except Exception as exc:
                st.error(f"Agent failed: {exc}")
    result = st.session_state.agent_result
    if not result:
        return
    st.divider()
    st.subheader("Answer")
    st.write(result.get("answer", "No answer generated."))
    confidence = float(result.get("confidence", 0.0))
    st.subheader("Confidence")
    st.progress(min(max(confidence, 0.0), 1.0))
    st.caption(f"{confidence:.1%}")
    if result.get("blocked"):
        st.warning("The response was blocked by an agent guardrail.")
    st.subheader("Supporting Evidence")
    display_sources(result.get("sources", []))


def _show_creative_output(output) -> None:
    if isinstance(output, dict):
        st.json(output)
    else:
        st.write(output)


def render_creative() -> None:
    st.header("Creative Studio")
    st.write("Plan, generate, validate, critique, rewrite, and prepare video prompts.")
    brief = st.text_area("Creative brief", height=130, placeholder="Describe the episode, scene, or story moment...")
    action = st.selectbox("Creative action", list(CREATIVE_TASKS))
    limit = st.slider("Context chunks", 1, 10, min(max(settings().retrieval_top_k, 1), 10))
    action_col, pipeline_col = st.columns(2)
    run_action = action_col.button(f"Run: {action}", type="primary", use_container_width=True)
    run_pipeline = pipeline_col.button("Run Full Creative Workflow", use_container_width=True)
    if run_action or run_pipeline:
        if not brief.strip():
            st.warning("Enter a creative brief first.")
        else:
            try:
                with st.spinner("Running creative agent..."):
                    if run_pipeline:
                        st.session_state.creative_pipeline = creative_service().run_pipeline(brief, st.session_state.document.document_id, limit)
                        st.session_state.creative_result = None
                    else:
                        previous = st.session_state.creative_result or {}
                        st.session_state.creative_result = creative_service().run_action(action, brief, previous.get("output", ""), limit, st.session_state.document.document_id)
                        st.session_state.creative_pipeline = None
                st.success("Creative workflow completed.")
            except Exception as exc:
                st.error(f"Creative workflow failed: {exc}")
    pipeline = st.session_state.creative_pipeline
    result = st.session_state.creative_result
    if pipeline:
        st.subheader("Workflow Results")
        labels = {"plan": "Episode Plan", "scenes": "Scenes", "dialogue": "Dialogue", "continuity": "Continuity Validation", "critique": "Screenplay Critique", "rewrite": "Automatic Rewrite", "video_prompt": "Video Generation Prompt"}
        for key, label in labels.items():
            step = pipeline["steps"].get(key, {})
            with st.expander(label, expanded=key in {"plan", "rewrite", "video_prompt"}):
                _show_creative_output(step.get("output", "No output generated."))
                scores = step.get("evaluation_scores", {})
                if scores:
                    st.caption(f"Overall quality score: {scores.get('overall_score', 0):.1%}")
                st.caption(f"Run {step.get('run_id', 'unknown')} | {step.get('latency_ms', 0):.0f} ms | {step.get('retrieved_chunks', 0)} chunks")
    elif result:
        st.subheader(result["action"])
        _show_creative_output(result.get("output", "No output generated."))
        st.caption(f"Run {result['run_id']} | {result['latency_ms']:.0f} ms | {result['retrieved_chunks']} chunks")
        scores = result.get("evaluation_scores", {})
        if scores:
            st.subheader("Output Evaluation")
            st.json(scores)
        with st.expander("Retrieved context"):
            display_sources(result.get("retrieval_context", []))
        with st.expander("Prompt and trace metadata"):
            st.code(result.get("prompt", ""))
            st.json({key: result.get(key) for key in ("run_id", "model", "prompt_version", "timestamp", "tool_calls", "input_tokens", "output_tokens")})
    render_experiment_log()


def render_retrieval() -> None:
    st.header("Retrieval Inspector")
    query = st.text_input("Search query", placeholder="Search for information about a character...")
    top_k = st.slider("Top-K results", 1, 10, min(max(settings().retrieval_top_k, 1), 10))
    if st.button("Retrieve", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Enter a search query.")
        else:
            st.session_state.retrieval_results = retriever().retrieve(query=query, limit=top_k)
    results = st.session_state.retrieval_results
    if results:
        st.subheader(f"{len(results)} retrieved chunks")
        display_sources(results)
    elif query:
        st.info("No relevant results found.")


def render_evaluation() -> None:
    st.header("Evaluation")
    st.write("Evaluate retrieval, grounded answers, and creative output quality.")
    if st.button("Run Evaluation", type="primary", use_container_width=True):
        try:
            with st.spinner("Running evaluation..."):
                st.session_state.evaluation_result = run_evaluation(agent())
            st.success("Evaluation completed.")
        except Exception as exc:
            st.error(f"Evaluation failed: {exc}")
    evaluation = st.session_state.evaluation_result
    if evaluation:
        summary = evaluation.get("summary", {})
        cols = st.columns(5)
        for column, key, label in zip(cols, ("overall_score", "retrieval_hit_rate", "groundedness", "keyword_score", "answer_similarity"), ("Overall", "Retrieval", "Groundedness", "Keywords", "Similarity")):
            column.metric(label, f"{summary.get(key, 0):.1%}")
        for item in evaluation.get("results", []):
            with st.expander(item.get("case", "Evaluation case")):
                st.write(item.get("answer", ""))
                st.json(item.get("metrics").to_dict() if hasattr(item.get("metrics"), "to_dict") else item.get("metrics", {}))
                if item.get("error"):
                    st.error(item["error"])
    render_experiment_log()


def render_experiment_log() -> None:
    with st.expander("Execution history and regression experiments"):
        records = RunStore().recent(50)
        if not records:
            st.info("No creative runs have been stored yet.")
            return
        st.dataframe(
            [{"timestamp": r.get("timestamp", ""), "run_id": r.get("run_id", ""), "action": r.get("action", ""), "model": r.get("model", ""), "score": r.get("evaluation_scores", {}).get("overall_score", 0), "latency_ms": r.get("latency_ms", 0)} for r in records],
            use_container_width=True,
            hide_index=True,
        )
