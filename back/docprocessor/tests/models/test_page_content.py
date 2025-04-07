import pytest

def test_importable():
    from src.models.page_content import (
        PageContent, # noqa: F401
    )

@pytest.mark.parametrize("attr", [
    "content",
    "title"
])
def test_has_attributes(attr):
    from src.models.page_content import PageContent
    page_content = PageContent(content="Sample content")
    assert hasattr(page_content, attr)

def test_init():
    from src.models.page_content import PageContent
    content = "This is a sample content."
    title = "Sample Title"
    page_content = PageContent(content=content, title=title)

    assert page_content.content == content
    assert page_content.title == title