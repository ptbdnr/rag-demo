import pytest
from pathlib import Path

def test_importable():
    from src.encode.encoder import doc_encoder # noqa: F401
    from src.models.chunk import Chunk # noqa: F401

class TestEncoder:

    from src.models.chunk import Chunk

    @pytest.mark.parametrize("chunks", [
        ([Chunk(text="This is a test chunk.")]),
    ])
    def test_doc_encoder(chunks):
        from src.encode.encoder import doc_encoder
        from src.models.chunk import Chunk

        result = doc_encoder(chunks=chunks)
        assert isinstance(result, dict)
        assert "chunks" in result
        assert isinstance(result["chunks"], list)
        for chunk in result["chunks"]:
            assert isinstance(chunk, Chunk)
            assert chunk.text == chunks[0].text
            assert chunk.vector is not None
        assert len(result["chunks"]) == len(chunks)
