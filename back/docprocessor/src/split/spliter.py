from langchain.text_splitter import RecursiveCharacterTextSplitter 

from src.models.chunk import Chunk

MAX_CHUNK_SIZE = 800
MAX_OVERLAP = 200

def doc_splitter(
        page_contents: list[dict],
        chunking_strategy: str = "auto",
) -> dict:
    """Split the content into chunks based on the specified chunking strategy."""
    if chunking_strategy in ["auto", "fix"]:
        # chunking strategy
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=MAX_CHUNK_SIZE, 
            chunk_overlap=MAX_OVERLAP
        )
        chunks = text_splitter.split_documents(page_contents)
    
    elif chunking_strategy == "semantic":
        # semantic chunking strategy
        separators = infer_separators(page_contents)    
        text_splitter = RecursiveCharacterTextSplitter(
            separators=separators,
            chunk_size=MAX_CHUNK_SIZE, 
            chunk_overlap=MAX_OVERLAP
        )
        chunks = text_splitter.split_documents(page_contents)

    return {
        "chunks": [Chunk(text=chunk.page_content) for chunk in chunks],
        "chunking_strategy": chunking_strategy
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
