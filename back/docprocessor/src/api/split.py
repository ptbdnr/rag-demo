import json
import logging

import azure.functions as func

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

    response_body = {
        'content': [
            {
                "_id": "foo",
                "content": 'This is a sample document content.'
            }
        ],
    }

    return func.HttpResponse(
        body=json.dumps(response_body, indent=2),
        status_code=200,
    )