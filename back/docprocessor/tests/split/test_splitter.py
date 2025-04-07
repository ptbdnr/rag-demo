import pytest
from pathlib import Path

def test_importable():
    from src.split.spliter import (
        doc_splitter, # noqa: F401
    )

class TestSplitter:
    from src.models.page_content import PageContent

    @pytest.mark.parametrize("pages, chunking_strategy, expected_chunk_count", [
        ([PageContent("fo bar bar")], "auto", 1),
        ([PageContent("fo bar bar")], "fix", 1),
        ([PageContent("fo bar bar")], "semantic", 1),
        ([PageContent("fo\n\nbar bar")], "semantic", 2),
    ])
    def test_doc_splitter(pages, chunking_strategy, expected_chunk_count):
        from src.split.spliter import doc_splitter
        result = doc_splitter(pages=pages, chunking_strategy=chunking_strategy)
        assert isinstance(result, dict)
        assert "chunks" in result
        assert "chunking_strategy" in result
        assert len(result["chunks"]) == expected_chunk_count
