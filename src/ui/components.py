from __future__ import annotations

import streamlit as st


def display_sources(sources) -> None:
    if not sources:
        st.info("No supporting sources returned.")
        return
    for index, source in enumerate(sources, start=1):
        if isinstance(source, dict):
            filename = source.get("source", "Unknown")
            score = source.get("score", 0.0)
            chunk_index = source.get("chunk_index", 0)
            text = source.get("text", "")
        else:
            filename = getattr(source, "source", "Unknown")
            score = getattr(source, "score", 0.0)
            chunk_index = getattr(source, "chunk_index", 0)
            text = getattr(getattr(source, "chunk", None), "text", "")
        with st.expander(
            f"{index}. {filename} | Chunk {chunk_index} | Score {score:.3f}"
        ):
            st.write(text)


def display_items(items) -> None:
    if not items:
        st.info("No information available.")
        return
    for item in items:
        if isinstance(item, str):
            st.markdown(f"- {item}")
        elif isinstance(item, dict):
            st.json(item)
        else:
            name = getattr(item, "name", None)
            if name:
                st.markdown(f"**{name}**")
            for field in ("role", "description", "motivation", "goal", "traits", "relationship", "type"):
                value = getattr(item, field, None)
                if value:
                    st.write(f"**{field.title()}:** {value}")