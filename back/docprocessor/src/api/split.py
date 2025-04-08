from __future__ import annotations
import json
import logging
from typing import Optional

import azure.functions as func

from src.split.spliter import doc_splitter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
    import dotenv
    dotenv.load_dotenv(".env.local")
except Exception as e:
    logger.info("dotenv not loaded: %s", e)

def api_handler(
    req: func.HttpRequest,
    tenant_id: str,
    version: str,
) -> func.HttpResponse:
    """"HTTP triggered function to split doc content."""
    logger.info("(%s) Starting '%s' ...", version, __name__)
    logger.info("(%s) request: %s", version, json.dumps({
        'method': req.method,
        'url': req.url,
        'headers': dict(req.headers),
        'params': dict(req.params),
        'get_body': req.get_body().decode()
    }, indent=2))

    # Parse request body
    document_id: Optional[str] = None
    try:
        req_body = req.get_json()
    except ValueError:
        logger.info("(%s) Invalid JSON body", version)    
        document_id = req.get_body()
    else:
        document_id = req_body.get("documentId", None)
    
    # Validate input
    if document_id is None:
        return func.HttpResponse(
            body="Invalid input",
            status_code=400,
        )

    # Log the input
    logger.info("(%s) tenant_id: %s", version, tenant_id)
    logger.info("(%s) document_id: %s", version, document_id)
    
    # split the document and save in text db
    response_body = doc_splitter(
        tenant_id=tenant_id,
        document_id=document_id,
    )

    return func.HttpResponse(
        body=json.dumps(response_body, indent=2),
        status_code=200,
    )