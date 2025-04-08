import os
import logging

import streamlit as st
from dotenv import load_dotenv
from streamlit_theme import st_theme

from components.instruction import component as instruction_component
from components.knowledge import component as knowledge_component
from components.chat import component as chat_component

# Load environment variables
load_dotenv(".env.local")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger.addHandler(handler)

def initialize_session_state() -> None:
    """Initialize the session state variables if they are not already set."""
    env_vars = {
        "OPENAI_API_KEY": "OPENAI_API_KEY",
        "OPENAI_MODEL": "OPENAI_MODEL",
        "BACK_API_BASE": "BACK_API_BASE",
        "TENANT_ID": "TENANT_ID",
        "COSMOSDB_NOSQL_HOST": "COSMOSDB_NOSQL_HOST",
        "COSMOSDB_NOSQL_KEY": "COSMOSDB_NOSQL_KEY",
        "COSMOSDB_DATABASE_ID": "COSMOSDB_DATABASE_ID",
        "COSMOSDB_CONTAINER_ID": "COSMOSDB_CONTAINER_ID",
        "MISTRAL_API_KEY": "MISTRAL_API_KEY",
        "MISTRAL_MODEL_NAME": "MISTRAL_MODEL_NAME",
    }
    for var, env in env_vars.items():
        if var not in st.session_state:
            value = os.getenv(env)
            if value is None:
                message = "Missing env variable: " + env
                logger.exception(message)
                # raise ValueError(message)
            st.session_state[var] = value

# Set the page layout to wide
st.set_page_config(
    page_title="Snippets",
    page_icon="🔥",
    layout="wide",
)

# Initialize the session state variables
initialize_session_state()

theme = st_theme()
if theme and theme.get("base") == "dark":
    st.logo(
        image='media/avatar_clay_black.jpg',
        size='medium',
        link='https://github.com/ptbdnr',
    )
else:
    st.logo(
        image='media/avatar_clay_white.jpg',
        size='medium',
        link='https://github.com/ptbdnr',
    )

# Main Streamlit app starts here
with st.container():
    tab1, tab2, tab3 = st.tabs([
        "📙 Instruction",
        "📁 Knowledge",
        "💬 Chat"
    ])

    with tab1:
        instruction_component()

    with tab2:
        knowledge_component()

    with tab3:
        chat_component()

# Custom CSS
css = """
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:1.5rem;
    }
</style>
"""

st.markdown(css, unsafe_allow_html=True)
