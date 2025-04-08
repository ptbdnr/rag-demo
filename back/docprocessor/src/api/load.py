from __future__ import annotations
import json
import uuid
import logging
from datetime import datetime
from typing import Optional

import azure.functions as func
from src.load.loader import download_file, doc_loader

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
    """"HTTP triggered function to load doc."""
    logger.info("(%s) Starting '%s' ...", version, __name__)
    logger.info("(%s) request: %s", version, json.dumps({
        'method': req.method,
        'url': req.url,
        'headers': dict(req.headers),
        'params': dict(req.params),
    }, indent=2))
    
    # Parse request body
    content_type: Optional[str] = None
    content_type = req.headers.get('Content-Type', 'application/json')
    logger.info("(%s) Content-Type: %s", version, content_type)

    file: Optional[str] = None
    created_at = datetime.now()
    label = created_at.strftime("%Y%m%dT%H%M%S")
    mime_type = "application/octet-stream"
    chunking_strategy = "auto"
    try:
        req_body = req.get_json()
    except ValueError:
        logger.info("(%s) Invalid JSON body", version)    
        file = req.get_body()
    else:
        file = req_body.get("url", req_body.get("content", None))
        label = req_body.get('label', label)
        mime_type = req_body.get('mime_type', mime_type)
        chunking_strategy = req_body.get('chunking_strategy', chunking_strategy)
    
    document_id = uuid.uuid4().hex
    
    # Validate input
    if file is None:
        return func.HttpResponse(
            body="Invalid input",
            status_code=400,
        )
    
    if (
        content_type != "application/octet-stream" 
        and (file.startswith("https://") or file.startswith("http://"))
    ):
        logger.info("(%s) download: %s ...", version, file)
        file_content = download_file(url=file)
    else:
        file_content = file

    # Log the input
    logger.info("(%s) tenant_id: %s", version, tenant_id)
    logger.info("(%s) document_id: %s", version, document_id)
    if content_type != "application/octet-stream":
        logger.info("(%s) file_content: %s", version, file_content)
    else:
        logger.info("(%s) file_content: %s", version, "binary content")
    logger.info("(%s) mime_type: %s", version, mime_type)
    logger.info("(%s) label: %s", version, label)
    logger.info("(%s) created_at: %s", version, created_at)
    logger.info("(%s) chunking_strategy: %s", version, chunking_strategy)

    # load the document and save to blob
    doc_loader(
        document_id=document_id,
        tenant_id=tenant_id,
        label=label,
        file_content=file_content,
        mime_type=mime_type,
        created_at=created_at,
        chunking_strategy=chunking_strategy,
    )

    response_body = {
        "tenantId": tenant_id,
        "documentId": document_id,
        "label": label,
        "mimeType": mime_type,
        "status": "pending",
        "createdAt": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        "updatedAt": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        "chunking_strategy": chunking_strategy
    }

    return func.HttpResponse(
        body=json.dumps(response_body, indent=2),
        status_code=200,
    )