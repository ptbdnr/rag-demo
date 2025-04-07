import pytest

def test_importable():
    from src.models.chunk import (
        Chunk, # noqa: F401
    )

@pytest.mark.parametrize("attr", [
    "text",
    "vector"
])
def test_has_attributes(attr):
    from src.models.chunk import Chunk
    chunk = Chunk(text="Sample content")
    assert hasattr(chunk, attr)

def test_init():
    from src.models.chunk import Chunk
    text = "This is a sample content."
    vector = [0.1, 0.2, 0.3]
    chunk = Chunk(
        text=text,
        vector=vector,
    )

    assert chunk.text == text
    assert chunk.vector == vector