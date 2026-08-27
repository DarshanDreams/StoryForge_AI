from __future__ import annotations

import streamlit as st

from src.ui.runtime import initialize_state
from src.ui.views import (
    render_agent,
    render_analysis,
    render_creative,
    render_evaluation,
    render_retrieval,
    render_sidebar,
    render_story_overview,
)


st.set_page_config(
    page_title="StoryForge AI",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_state()
render_sidebar()

st.title("StoryForge AI")
st.caption("Understand, retrieve, create, validate, and evaluate stories.")

if not st.session_state.story_text:
    st.info("Upload a story or paste story text from the sidebar.")
    st.stop()

render_story_overview()

analysis_tab, agent_tab, creative_tab, retrieval_tab, evaluation_tab = st.tabs(
    [
        "Story Analysis",
        "Ask StoryForge",
        "Creative Studio",
        "Retrieval",
        "Evaluation",
    ]
)

with analysis_tab:
    render_analysis()

with agent_tab:
    render_agent()

with creative_tab:
    render_creative()

with retrieval_tab:
    render_retrieval()

with evaluation_tab:
    render_evaluation()
