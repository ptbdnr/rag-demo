import streamlit as st


def component() -> None:
    st.header("Simple RAG Chatbot")

    st.markdown(
        """
        ### Instructions
        - **Step 1**: Enter your prompt in the chat input box.
        - **Step 2**: Click on the "Send" button to generate a response.
        """
    )
