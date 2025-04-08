import json
import os
from pathlib import Path
import logging

import dotenv
from mistralai import Mistral, OCRResponse

dotenv.load_dotenv(".env.local")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

API_KEY = os.environ["MISTRAL_API_KEY"]
MODEL_NAME = "mistral-ocr-latest"

class MistralLoader:
    """Load a PDF file using Mistral OCR."""

    def __init__(self):
        """Initialize with PDF file path."""
        pass

    def load(self, pdf_file_content: bytes) -> dict:
        """Load the PDF file and return the OCR response."""
        mistral_client = Mistral(api_key=API_KEY)
        uploaded_pdf = mistral_client.files.upload(
            file={
                "file_name": "uploaded_file.pdf",
                "content": pdf_file_content,
            },
            purpose="ocr",
        )

        logger.info(mistral_client.files.retrieve(file_id=uploaded_pdf.id))
        signed_url = mistral_client.files.get_signed_url(file_id=uploaded_pdf.id)

        ocr_response: OCRResponse = mistral_client.ocr.process(
            model=MODEL_NAME,
            document={
                "type": "document_url",
                "document_url": signed_url.url,
            },
        )
        ocr_dump = ocr_response.model_dump()
        logger.info(ocr_dump)
        contents = [p["markdown"] for p in ocr_dump["pages"]]

        return contents
