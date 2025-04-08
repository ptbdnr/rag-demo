import logging
import os

import dotenv
from mistralai import Mistral

from src.models.chunk import Chunk
from src.store.cosmosdb import CosmosDB

dotenv.load_dotenv(".env.local")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]
MISTRAL_MODEL_NAME = os.environ["MISTRAL_MODEL_NAME"]

def doc_encoder(
        tenant_id: str,
        document_id: str,
 )-> dict:
    """Encode the content into a vector representation."""

    # load the content
    cosmos_db = CosmosDB()
    items = cosmos_db.find(filter={
        "tenantId": tenant_id,
        "documentId": document_id,
    })
    logger.info("Loaded %d items: %s", len(items), list(items))

    # encode the content
    text_chunks = [item['text'] for item in items]
    mistral_client = Mistral(api_key=MISTRAL_API_KEY)
    embeddings_batch_response = mistral_client.embeddings.create(
        model=MISTRAL_MODEL_NAME,
        inputs=text_chunks,
    )
    vector_chunks = [e.embedding for e in embeddings_batch_response.data]

    # pair the text with the vectors
    for idx, item in enumerate(items):
        item["vector"] = vector_chunks[idx]
        cosmos_db.upsert(item)

    chunks = [
        Chunk(text=item['text'], vector=item['vector'])
        for item in items
    ]

    return {
        "tenantId": tenant_id,
        "documentId": document_id,
        "embedding_model": MISTRAL_MODEL_NAME,
        "chunks": [chunk.to_dict() for chunk in chunks],
    }