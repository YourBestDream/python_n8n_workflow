from app.vector import chunk_text


def test_chunk_text_creates_overlapping_chunks() -> None:
    text = " ".join([f"token{i}" for i in range(300)])
    chunks = chunk_text(text, size=120, overlap=30)
    assert len(chunks) > 1
    assert all(chunks)
    assert chunks[0] != chunks[1]

