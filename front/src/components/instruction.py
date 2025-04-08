import streamlit as st
from textwrap import dedent


def component() -> None:
    """Main component for the tab."""
    st.header("Using the App")

    st.markdown(dedent(
        """
        This tab provides a brief overview of how operate the app:

        ## Knowledge Tab
        Use this tab to interact with the knowledge store:

        * Refresh Knowledge Store: Click the refresh button to query the backend store for available documents linked to your tenant ID.
        * Load Document: Provide a document URL or text input to load a new document into the system. The app supports various MIME types.
        * Split Document: Provide a document ID to split the document into manageable chunks.
        * Encode Document Chunks: After splitting, encode the document chunks for further processing.
        
        ## Chat Tab
        Engage with the chatbot:

        Your conversation (both your input and the assistant's responses) is maintained throughout your session.
        
        Use either batch processing or streaming responses to interact with the OpenAI-powered backend.
        
        Enjoy exploring the different features of the application!
        """
    ))
