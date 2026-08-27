from src.prompt.story_agents import (
    SYSTEM_PROMPT,
    build_agent_prompt,
)


def retrieve_node(
    state,
    retriever,
):

    query = state.get(
        "user_query",
        "",
    )

    if not query.strip():

        return {
            "retrieved_context": [],
            "error": "Query is empty.",
        }

    try:

        results = retriever.retrieve(
            query=query,
            limit=5,
        )

        return {
            "retrieved_context": results,
            "error": "",
        }

    except Exception as exc:

        return {
            "retrieved_context": [],
            "error": (
                f"Retrieval failed: {exc}"
            ),
        }


def generate_node(
    state,
    llm_gateway,
):

    if state.get("error"):

        return state

    question = state.get(
        "user_query",
        "",
    )

    context_items = state.get(
        "retrieved_context",
        [],
    )

    context = "\n\n".join(
        item.text
        for item in context_items
    )

    if not context.strip():

        return {
            **state,
            "answer": (
                "I could not find enough "
                "information in the story "
                "to answer that question."
            ),
        }

    prompt = build_agent_prompt(
        question=question,
        context=context,
    )

    try:

        answer = (
            llm_gateway.generate(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=prompt,
            )
        )

        return {
            **state,
            "answer": answer,
            "error": "",
        }

    except Exception as exc:

        return {
            **state,
            "answer": "",
            "error": (
                f"Generation failed: {exc}"
            ),
        }