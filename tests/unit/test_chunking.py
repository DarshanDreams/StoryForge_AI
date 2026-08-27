from src.retrieval.chunking import chunk_text


def test_chunk_text():

    text = "a" * 2500

    chunks = chunk_text(
        text,
        chunk_size=1000,
        overlap=100,
    )

    assert len(chunks) > 1
    assert chunks[0].index == 0