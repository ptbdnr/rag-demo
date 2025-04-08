import logging
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter 

from src.models.chunk import Chunk
from src.store.blob import load

MAX_CHUNK_SIZE = 800
MAX_OVERLAP = 200

def doc_splitter(
        tenant_id: str,
        document_id: str,
) -> dict:
    """Split the content into chunks based on the specified chunking strategy."""
    
    # load the content
    content = json.loads(load(filename=f"{tenant_id}/{document_id}.json"))
    logging.info("Loaded content: %s", content)
    chunking_strategy = content.get("chunkingStrategy", "auto")
    page_contents = content.get("pageContents", [])
    text_to_split = '\n'.join([p.get("page_content", "") for p in page_contents])

    if chunking_strategy in ["auto", "fix"]:
        # chunking strategy
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=MAX_CHUNK_SIZE, 
            chunk_overlap=MAX_OVERLAP
        )
        raw_chunks = text_splitter.split_text(text_to_split)
    
    elif chunking_strategy == "semantic":
        # semantic chunking strategy
        separators = infer_separators(text_to_split)    
        text_splitter = RecursiveCharacterTextSplitter(
            separators=separators,
            chunk_size=MAX_CHUNK_SIZE, 
            chunk_overlap=MAX_OVERLAP
        )
        raw_chunks = text_splitter.split_text(text_to_split)
    
    logging.info("Split content into %d chunks", len(raw_chunks))
    logging.info("Raw chunks: %s", [c for c in raw_chunks])

    chunks = [Chunk(text=c) for c in raw_chunks]

    return {
        "chunks": [c.to_dict() for c in chunks],
        "chunkingStrategy": chunking_strategy
    }

def infer_separators(content: str) -> list:
    """Infer the separators for semantic chunking."""
    # TODO: improve the logic to infer separators
    return [
        "\n\n", 
        "Section", "Chapter", "Title", "Subtitle", "Heading", "Subheading", 
        "Appendix", 
        "Figure", 
        "Table", 
        "List", "Item", "Point", "Step", 
        "Example", "Note", "Warning", "Tip",
    ]
