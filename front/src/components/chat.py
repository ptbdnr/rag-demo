import time
import logging
from textwrap import dedent

import streamlit as st
from openai import OpenAI
from mistralai import Mistral
from langchain.schema import AIMessage
from langchain_openai.chat_models import ChatOpenAI

from src.store.cosmosdb import CosmosDB


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger.addHandler(handler)

STREAM = False
RAG_PROMPT_TEMPLATE = dedent("""
    Reply to the user based on the context provided.
    If the context does not contain enough information to answer the question, say "I don't know".
    Context: {context}
    Question: {question}
""".strip())


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

def search_knowledge(
        tenant_id: str,
        query_text: str,
        top_k: int = 5,
) -> str:
    """Search knowledge."""

    # encode the query text
    mistral_client = Mistral(api_key=st.session_state["MISTRAL_API_KEY"])
    embeddings_batch_response = mistral_client.embeddings.create(
        model=st.session_state["MISTRAL_MODEL_NAME"],
        inputs=[query_text],
    )
    query_vector = embeddings_batch_response.data[0].embedding

    # build the query
    query=dedent("""
        SELECT TOP @top_k c.text, VectorDistance(c.vector,@embedding) AS SimilarityScore
        FROM c1 c
        WHERE c.tenantId = "@tenant_id"
        ORDER BY VectorDistance(c.vector,@embedding)
    """.strip())
    parameters=[
        {"name": "@container_id", "value": st.session_state["COSMOSDB_CONTAINER_ID"]},
        {"name": "@top_k", "value": top_k},
        {"name": "@embedding", "value": query_vector},
        {"name": "@tenant_id", "value": tenant_id},
    ]
    logger.info(f"query_template: {query}")
    logger.info(f"query_parameters: {[str(p)[:100] for p in parameters]}")

    # query the knowledge base
    cosmosdb_client = CosmosDB()
    cosmosdb_client.create()
    query_results = cosmosdb_client.container.query_items(
        query=query,
        parameters=parameters,
    )
    return [str(qr) for qr in query_results]

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
            with st.status(label="Search knowledge"):
                st.write("query text:", prompt)
                tenant_id = st.session_state["TENANT_ID"]
                query_results = search_knowledge(
                    tenant_id=tenant_id,
                    query_text=prompt
                )
                st.write("query results:", query_results)
                prompt = RAG_PROMPT_TEMPLATE.format(
                    context=query_results,
                    question=prompt,
                )
            logger.info(f"Prompt: {prompt}")
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