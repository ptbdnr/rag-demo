import logging
import json

import azure.durable_functions as df
import azure.functions as func

from src.api.load import api_handler as load_api_handler
from src.api.split import api_handler as split_api_handler
from src.api.encode import api_handler as encode_api_handler

std_app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
# dur_app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)
VERSION = "1.0.0"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(stdout_handler)


@std_app.route(route="load/{tenant_id}")
def load_entry(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP trigger function to process documents."""
    logger.info("Triggered %s ...", 'load_entry')
    tenant_id = req.route_params.get("tenant_id", 'unknown')
    return load_api_handler(req, tenant_id, VERSION)

@std_app.route(route="split/{tenant_id}")
def split_entry(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP trigger function to process documents."""
    logger.info("Triggered %s ...", 'split_entry')
    tenant_id = req.route_params.get("tenant_id", 'unknown')
    return split_api_handler(req, tenant_id, VERSION)

@std_app.route(route="encode/{tenant_id}")
def encode_entry(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP trigger function to process documents."""
    logger.info("Triggered %s ...", 'encode_entry')
    tenant_id = req.route_params.get("tenant_id", 'unknown')
    return encode_api_handler(req, tenant_id, VERSION)

# # An HTTP-triggered function with a Durable Functions client binding
# @dur_app.route(route="doc_processing")
# @dur_app.durable_client_input(client_name="client")
# async def doc_processing_entry(req: func.HttpRequest, client):
#     """HTTP trigger function to start the orchestration."""
#     logger.info("Triggered %s ...", 'doc_processing_entry')
#     version = VERSION
#     logger.info("(%s) request: %s", version, json.dumps({
#         'method': req.method,
#         'url': req.url,
#         'headers': dict(req.headers),
#         'params': dict(req.params),
#         'get_body': req.get_body().decode()
#     }, indent=2))
#     orchestrator_name = "doc_processing_orchestrator"
#     logger.info("Orchestrator name: %s", orchestrator_name)
#     client_input = req.get_body.decode("utf-8") if req.get_body() else None
#     logger.info("Client input: %s", client_input)
#     instance_id = await client.start_new(
#         orchestration_function_name=orchestrator_name,
#         instance_id=None,
#         client_input=client_input,
#     )
#     logger.info("Starting orchestration with ID = '%s'", instance_id)
#     response = client.create_check_status_response(req, instance_id)
#     logger.info("Response: %s", response)
#     return response

# # Orchestrator
# @dur_app.orchestration_trigger(context_name="context")
# def doc_processing_orchestrator(context):
#     """Orchestrate the workflow."""
#     logger.info("Orchestrator (%s) started...", 'doc_processing_orchestrator')
#     result1 = yield context.call_activity("load", "Seattle")
#     logger.info("Result of load: %s", result1)
#     result2 = yield context.call_activity("split", "Tokyo")
#     logger.info("Result of split: %s", result2)
#     result3 = yield context.call_activity("encode", "London")
#     logger.info("Result of encode: %s", result3)
#     return {"content": "done"}

# # Activity
# @dur_app.activity_trigger(input_name="payload")
# def load(payload: str):
#     """Activity function to load documents."""
#     logger.info("Activity (%s) started...", 'load')
#     req = func.HttpRequest(
#         method="POST",
#         url="https://example.com",
#         route_params={"tenant_id": "unknown"},
#         body=payload.encode("utf-8"),
#         headers={},
#     )
#     tenant_id = req.route_params.get("tenant_id", 'unknown')
#     return load_api_handler(req, tenant_id, VERSION)

# @dur_app.activity_trigger(input_name="payload")
# def split(payload: str):
#     """Activity function to split documents."""
#     logger.info("Activity (%s) started...", 'split')
#     req = func.HttpRequest(
#         method="POST",
#         url="https://example.com",
#         route_params={"tenant_id": "unknown"},
#         body=payload.encode("utf-8"),
#         headers={},
#     )
#     tenant_id = req.route_params.get("tenant_id", 'unknown')
#     return split_api_handler(req, tenant_id, VERSION)

# @dur_app.activity_trigger(input_name="payload")
# def encode(payload: str):
#     """Activity function to encode documents."""
#     logger.info("Activity (%s) started...", 'encode')
#     req = func.HttpRequest(
#         method="POST",
#         url="https://example.com",
#         route_params={"tenant_id": "unknown"},
#         body=payload.encode("utf-8"),
#         headers={},
#     )
#     tenant_id = req.route_params.get("tenant_id", 'unknown')
#     return encode_api_handler(req, tenant_id, VERSION)
