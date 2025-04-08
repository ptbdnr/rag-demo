import time
import logging

import streamlit as st
from openai import OpenAI
from langchain.schema import AIMessage
from langchain_openai.chat_models import ChatOpenAI


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger.addHandler(handler)

STREAM = False

def generate_response(messages) -> str:
    """Generate a response using the OpenAI API."""
    client = ChatOpenAI(
        temperature=0.1, 
        api_key=st.session_state["OPENAI_API_KEY"]  # TODO: use st.secrets['KEY'] instead
    )
    return client.invoke(input=messages)

def stream_response(messages) -> str:
    """Generate a response using the OpenAI API."""
    client = OpenAI(
        api_key=st.session_state["OPENAI_API_KEY"]  # TODO: use st.secrets['KEY'] instead
    )
    return client.chat.completions.create(
        model=st.session_state["OPENAI_MODEL"],
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ],
        stream=True,
    )

def component() -> None:
    """Main component for the tab."""
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Say something..."):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display assistant response in chat message container
        with st.chat_message(name="assistant"):
            with st.status(label="Backend task"):
                st.write("doing", prompt)
                time.sleep(0.5)
                st.write("done", prompt)
            if STREAM:
                st.toast("Streaming response...")
                response = st.write_stream(stream_response(messages=st.session_state.messages))
            else:
                st.toast("Batch response...")
                ai_message: AIMessage = generate_response(messages=st.session_state.messages)
                logger.debug(f"AI message: {ai_message}")
                response = ai_message.content
                st.markdown(response)
            
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})