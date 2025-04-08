import logging
from datetime import datetime

import requests

from src.load.mistral_loader import MistralLoader
from src.load.text_loader import TextLoader
from src.models.page_content import PageContent
from src.store.blob import save

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def download_file(
        url: str
) -> bytes:
    """Download a file from the given URL."""

    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise ValueError(f"Failed to download file. Status code: {response.status_code}")

def doc_loader(
        document_id: str,
        tenant_id: str,
        label: str,
        file_content: bytes,
        mime_type: str = 'auto',
        created_at: datetime = None,
        chunking_strategy: str = 'auto',
        
) -> dict:
    """Load a document based on its mime type."""

    file_type_mappings = {
        'txt': [TextLoader],
        'text/plain': [TextLoader],
        'plain': [TextLoader],
        'text/markdown': [TextLoader],
        'markdown': [TextLoader],
        'pdf': [MistralLoader],
        'application/pdf': [MistralLoader],
        'image/png': [MistralLoader],
        'png': [MistralLoader],
        "octet-stream": [MistralLoader],
    }

    # iterate over the file type mappings
    page_contents: list[PageContent] = []
    for glob_pattern, list_of_loader_cls in file_type_mappings.items():
        if mime_type.split('/')[1] in glob_pattern:
            # iterate over the loader classes
            for loader_cls in list_of_loader_cls:
                loaded = False
                content = None
                try:
                    if loader_cls == TextLoader:
                        content = TextLoader().load(file_content)
                        page_contents.append(PageContent(page_content=content))
                        loaded = True
                    elif loader_cls == MistralLoader:
                        contents = MistralLoader().load(file_content)
                        for c in contents:
                            page_contents.append(PageContent(page_content=c))
                        loaded = True
                    else:
                        raise ValueError(f"Unsupported loader class: {loader_cls}")
                except Exception as e:
                    logger.exception(msg=str(e))
                
                if loaded:
                    data_object = {
                        "tenantId": tenant_id,
                        "documentId": document_id,
                        "label": label,
                        "mimeType": mime_type,
                        "pageContents": [pc.to_dict() for pc in page_contents],
                        "createdAt": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                        "chunkingStrategy": chunking_strategy,
                    }
                    try:
                        save(
                            filename=f"{tenant_id}/{document_id}.json",
                            data=data_object
                        )
                    except Exception as e:
                        logger.exception(msg=str(e))
                    return data_object
    
    
    raise ValueError(f"Unsupported mimeType: {mime_type}")
