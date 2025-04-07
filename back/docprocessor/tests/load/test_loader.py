import pytest
from pathlib import Path

def test_importable():
    from src.load.loader import (
        doc_loader, # noqa: F401
        download_file, # noqa: F401
    )

@pytest.mark.parametrize("url", [
    "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
])
def test_download_file(url):
    from src.load.loader import download_file
    file_content = download_file(url=url)
    assert isinstance(file_content, bytes)

@pytest.mark.parametrize("mime_type, file_content", [
    ("text/plain", b"This is a sample text document.")
])
def test_doc_loader_text(mime_type, file_content):
    from src.load.loader import doc_loader
    from src.models.page_content import PageContent

    result = doc_loader(
        tenant_id="ptbdnr",
        doc_id="123",
        label="test_label",
        file_content=file_content, 
        mime_type=mime_type,
    )
    assert isinstance(result, dict)
    assert "page_contents" in result
    assert isinstance(result["page_contents"], list)
    for page_content in result["page_contents"]:
        assert isinstance(page_content, PageContent)

@pytest.mark.parametrize("mime_type, filepath", [
    ("application/pdf", "tests/fixtures/dummy.pdf"),
])
def test_doc_loader_pdf(mime_type, filepath):
    from src.load.loader import doc_loader
    from src.models.page_content import PageContent

    with Path(filepath).open("rb") as f:
        file_content = f.read()

    result = doc_loader(
        tenant_id="ptbdnr",
        doc_id="123",
        label="test_label",
        file_content=file_content, 
        mime_type=mime_type,
    )
    assert isinstance(result, list)
    for page_content in result:
        assert isinstance(page_content, PageContent)