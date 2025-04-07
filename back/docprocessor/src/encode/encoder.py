import logging
import os

import dotenv
from mistralai import Mistral

from src.models.chunk import Chunk

dotenv.load_dotenv(".env.local")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

API_KEY = os.environ["MISTRAL_API_KEY"]
MODEL_NAME = "mistral-embed"

def doc_encoder(
        chunks: list[Chunk],
 )-> dict:
    """Encode the content into a vector representation."""
    mistral_client = Mistral(api_key=API_KEY)

    text_chunks = [chunk.text for chunk in chunks]
    
    embeddings_batch_response = mistral_client.embeddings.create(
        model=MODEL_NAME,
        inputs=text_chunks,
    )

    vector_chunks = embeddings_batch_response.data
    text_vector_pairs = [
        Chunk(text=text_chunks[idx], vector=vector_chunks[idx])
        for idx in range(len(text_chunks))
    ]

    return {
        "chunks": chunks,
    }