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
        'get_body': req.get_body().decode()
    }, indent=2))

     # Parse request body
    file: Optional[str] = None
    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        file = req_body.get("url", req_body.get("content", None))
    
    if file is None:
        return func.HttpResponse(
            body="Invalid input",
            status_code=400,
        )
    
    if file.startswith("https://") or file.startswith("http://"):
        logger.info("(%s) download: %s ...", version, file)
        file_content = download_file(url=file)
    else:
        file_content = file

    created_at = datetime.now()
    label = req_body.get('label', created_at.strftime("%Y%m%dT%H%M%S"))
    mime_type = req_body.get('mimeType', 'auto')
    chunking_strategy = req_body.get('chunking_strategy', 'auto')
    doc_id = uuid.uuid4().hex

    logger.info("(%s) doc_id: %s", version, doc_id)
    logger.info("(%s) file_content: %s", version, file_content)
    logger.info("(%s) mime_type: %s", version, mime_type)
    logger.info("(%s) label: %s", version, label)
    logger.info("(%s) created_at: %s", version, created_at)
    logger.info("(%s) chunking_strategy: %s", version, chunking_strategy)

    # load the document and save to blob
    doc_loader(
        doc_id=doc_id,
        tenant_id=tenant_id,
        label=label,
        file_content=file_content,
        mime_type=mime_type,
        created_at=created_at,
        chunking_strategy=chunking_strategy,
    )

    response_body = {
        "docId": doc_id,
        "tenantId": tenant_id,
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