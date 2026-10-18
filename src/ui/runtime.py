from __future__ import annotations

import uuid

import streamlit as st

from src.agents.agent import StoryAgent
from src.config.settings import get_settings
from src.documents.models import Document
from src.documents.parser import DocumentParser
from src.llm.gateway import LLMGateway
from src.observability.run_store import RunStore
from src.retrieval.chunking import TextChunker
from src.retrieval.factory import create_retriever
from src.services.creative_story_service import CreativeStoryService
from src.services.story_analyzer import StoryAnalyzer


@st.cache_resource
def settings():
    return get_settings()


@st.cache_resource
def llm():
    return LLMGateway(settings())


@st.cache_resource
def parser():
    return DocumentParser()


def retriever():
    if st.session_state.get("_retriever") is None:
        st.session_state["_retriever"] = create_retriever()
    return st.session_state["_retriever"]


@st.cache_resource
def analyzer():
    return StoryAnalyzer(llm())


def agent():
    if st.session_state.get("_agent") is None:
        st.session_state["_agent"] = StoryAgent(
            llm=llm(),
            retriever=retriever(),
            retrieval_top_k=settings().retrieval_top_k,
        )
    return st.session_state["_agent"]


def creative_service():
    if st.session_state.get("_creative_service") is None:
        st.session_state["_creative_service"] = CreativeStoryService(
            llm(), retriever(), RunStore()
        )
    return st.session_state["_creative_service"]


SESSION_DEFAULTS = {
    "document": None,
    "story_text": "",
    "chunks": [],
    "analysis": None,
    "agent_result": None,
    "retrieval_results": [],
    "indexed": False,
    "evaluation_result": None,
    "creative_result": None,
    "creative_pipeline": None,
}


def initialize_state() -> None:
    for key, value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def create_document_from_text(text: str) -> Document:
    return Document(
        document_id=str(uuid.uuid4()),
        filename="pasted_story.txt",
        content=text,
        content_type="text/plain",
        metadata={
            "filename": "pasted_story.txt",
            "content_type": "text/plain",
            "character_count": len(text),
            "word_count": len(text.split()),
        },
    )


def index_document(document: Document) -> None:
    chunks = TextChunker(
        chunk_size=settings().chunk_size,
        chunk_overlap=settings().chunk_overlap,
    ).chunk_document(document)
    retriever().clear()
    retriever().add_chunks(chunks)
    st.session_state.document = document
    st.session_state.story_text = document.content
    st.session_state.chunks = chunks
    st.session_state.indexed = bool(chunks)
    reset_outputs()


def reset_outputs() -> None:
    st.session_state.analysis = None
    st.session_state.agent_result = None
    st.session_state.retrieval_results = []
    st.session_state.evaluation_result = None
    st.session_state.creative_result = None
    st.session_state.creative_pipeline = None


def clear_story() -> None:
    retriever().clear()
    st.session_state.document = None
    st.session_state.story_text = ""
    st.session_state.chunks = []
    st.session_state.indexed = False
    reset_outputs()