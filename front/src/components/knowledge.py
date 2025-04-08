import json
import logging

import streamlit as st
import requests

from src.store.cosmosdb import CosmosDB


def download_file(
        url: str
) -> bytes:
    """Download a file from the given URL."""

    response = requests.get(url)
    if response.status_code == 200:
        logging.info(f"File downloaded successfully from {url}")
        return response.content
    else:
        raise ValueError(f"Failed to download file. Status code: {response.status_code}")

def query_store(
        tenant_id: str
) -> dict:
    """Query the data store for a specific tenant ID."""
    cosmosdb_client = CosmosDB()
    cosmosdb_client.create()
    items = cosmosdb_client.find(filter={"tenantId": tenant_id})
    return [{
        "id": item["id"],
        "tenantId": item["tenantId"],
        "documentId": item["documentId"],
        "text": item["text"],
        "has_vector": True if "vector" in item else False,
    } for item in items]

def load_request(
        url: str,
        mime_type: str,
        data: str
) -> dict:
    """Post a request to the given URL."""
    logging.info(f"Posting request to {url}")
    response = requests.post(
        url=url,
        headers={
            "Content-Type": mime_type,
        },
        data=data
    )
    if response.status_code == 200:
        logging.info(f"Request posted successfully to {url}")
        return response.json()
    else:
        raise ValueError(f"Failed to post request. Status code: {response.status_code}")

def split_request(
        url: str,
        documentId: str
) -> dict:
    """Post a request to the given URL."""
    logging.info(f"Posting request to {url}")
    response = requests.post(
        url=url,
        json={
            "documentId": documentId,
        }
    )
    if response.status_code == 200:
        logging.info(f"Request posted successfully to {url}")
        return response.json()
    else:
        raise ValueError(f"Failed to post request. Status code: {response.status_code}")
    
def encode_request(
        url: str,
        documentId: str
) -> dict:
    """Post a request to the given URL."""
    logging.info(f"Posting request to {url}")
    response = requests.post(
        url=url,
        json={
            "documentId": documentId,
        }
    )
    if response.status_code == 200:
        logging.info(f"Request posted successfully to {url}")
        return response.json()
    else:
        raise ValueError(f"Failed to post request. Status code: {response.status_code}")

def component() -> None:
    """Main component for the tab."""
    
    with st.form(key='store') as f_input:
        
        st.header('View knowledge store')

        button = st.form_submit_button('Refresh')

        if button:
            try:
                st.toast('Start store query', icon="⏳")
                with st.spinner("Processing..."):
                    tenant_id = st.session_state["TENANT_ID"]
                    response = query_store(
                        tenant_id=tenant_id,
                    )
                if response:
                    st.toast('Processing done', icon="✅")
                    st.success("Processing completed successfully.")
                    with st.expander("See chunks", expanded=True):
                        st.table(response)
            except Exception as ex:
                st.toast(
                    body="An error occurred while processing the request.",
                    icon="⚠️",
                )
                logging.exception(msg=ex)
                st.exception(ex)



    with st.form(key='load') as f_input:

        st.header('Load document')

        text_input = st.text_area(
            label='source',
            value='https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
            height=40,
        )
        
        mime_type = st.selectbox(
            label='select one',
            options=[
                "application/pdf",
                "image/png",
                "text/plain",
                "text/markdown",
            ]
        )

        button = st.form_submit_button('Load')

        if button:
            try:
                st.toast('Start processing', icon="⏳")
                with st.spinner("Processing..."):
                    api_base = st.session_state["BACK_API_BASE"]
                    tenant_id = st.session_state["TENANT_ID"]
                    route = f"load/{tenant_id}?"
                    if mime_type in [
                        "url",
                        "application/pdf",
                        "image/png"
                    ]:
                        file_content = download_file(text_input)
                        response = load_request(
                            url=f"{api_base}/{route}",
                            mime_type="application/octet-stream",
                            data=file_content
                        )
                    else:
                        response = load_request(
                            url=f"{api_base}/{route}",
                            mime_type=mime_type,
                            data=text_input
                        )
                if response:
                    st.toast('Processing done', icon="✅")
                    st.success("Processing completed successfully.")
                    st.write(response)
            except Exception as ex:
                st.toast(
                    body="An error occurred while processing the request.",
                    icon="⚠️",
                )
                logging.exception(msg=ex)
                st.exception(ex) 

    with st.form(key='split') as f_input:

        st.header('Split document to chunks')

        text_input = st.text_input(
            label='documentId',
            value='45b9f7ecbaea456aa3de01e15373f12d',
        )

        button = st.form_submit_button('Split')

        if button:
            try:
                st.toast('Start processing', icon="⏳")
                with st.spinner("Processing..."):
                    api_base = st.session_state["BACK_API_BASE"]
                    tenant_id = st.session_state["TENANT_ID"]
                    route = f"split/{tenant_id}?"
                    response = split_request(
                        url=f"{api_base}/{route}",
                        documentId=text_input
                    )
                if response:
                    st.toast('Processing done', icon="✅")
                    st.success("Processing completed successfully.")
                    st.write(response)
            except Exception as ex:
                st.toast(
                    body="An error occurred while processing the request.",
                    icon="⚠️",
                )
                logging.exception(msg=ex)
                st.exception(ex) 

    with st.form(key='encode') as f_input:

        st.header('Encode document chunks')

        text_input = st.text_input(
            label='documentId',
            value='45b9f7ecbaea456aa3de01e15373f12d',
        )

        button = st.form_submit_button('Encode')

        if button:
            try:
                st.toast('Start processing', icon="⏳")
                with st.spinner("Processing..."):
                    api_base = st.session_state["BACK_API_BASE"]
                    tenant_id = st.session_state["TENANT_ID"]
                    route = f"encode/{tenant_id}?"
                    response = encode_request(
                        url=f"{api_base}/{route}",
                        documentId=text_input
                    )
                if response:
                    st.toast('Processing done', icon="✅")
                    st.success("Processing completed successfully.")
                    st.write(response)
            except Exception as ex:
                st.toast(
                    body="An error occurred while processing the request.",
                    icon="⚠️",
                )
                logging.exception(msg=ex)
                st.exception(ex) 