import json
import logging

import streamlit as st
import requests


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

def post_request(
        url: str,
        data: str
) -> dict:
    """Post a request to the given URL."""
    logging.info(f"Posting request to {url}")
    response = requests.post(url, data=data)
    if response.status_code == 200:
        logging.info(f"Request posted successfully to {url}")
        return response.json()
    else:
        raise ValueError(f"Failed to post request. Status code: {response.status_code}")

def component() -> None:
    """Main component for the tab."""
    st.write('TODO: list documents')

    with st.form(key='rows') as f_input:

        text_input = st.text_area(
            label='source',
            value='https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
            height=80,
        )
        
        mime_type = st.selectbox(
            label='select one',
            options=[
                "url",
                "application/pdf",
                "image/png"
                "text/plain",
                "text/markdown",
            ]
        )

        button = st.form_submit_button('Process')

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
                        data = {
                            "mime_type": mime_type,
                            "content": file_content
                        }
                        response = post_request(
                            url=f"{api_base}/{route}",
                            data=data
                        )
                    else:
                        data = {
                            "content": text_input,
                            "mime_type": mime_type
                        }
                        response = post_request(
                            url=f"{api_base}/{route}",
                            data=data
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