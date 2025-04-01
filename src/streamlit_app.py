import os
import streamlit as st
from tempfile import NamedTemporaryFile
import requests
from embed import embed
from query import query
from config import OllamaConfig

st.set_page_config(
    page_title="Ollama PDF Chat",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .title-container {
        display: flex;
        justify-content: center;
        padding: 1rem 0 2rem 0;
    }
    .title {
        color: #ff4c4c;
        font-size: 3rem !important;
        font-weight: 600;
        text-align: center;
        background: linear-gradient(90deg, #ff4c4c, #ff8f8f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 0.5rem 0;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: transparent;
        color: #808495;
        text-align: center;
        padding: 10px;
        font-size: 14px;
    }
    .footer a {
        color: #808495;
        text-decoration: none;
        border-bottom: 1px dotted #808495;
    }
    .footer a:hover {
        color: #ff4c4c;
        border-bottom-color: #ff4c4c;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def test_ollama_connection(url: str):
    """Test connection to Ollama server and return status and message."""
    try:
        # Ensure URL ends with /
        url = url.rstrip('/') + '/'
        
        # Test connection
        response = requests.get(f"{url}api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_count = len(models)
            return True, f"Successfully connected to Ollama. Found {model_count} models."
        
        return False, f"Failed to connect to Ollama. Status code: {response.status_code}"
        
    except Exception as e:
        return False, f"Error connecting to Ollama: {str(e)}"

def initialize_session_state():
    """Initialize session state variables."""
    if 'config' not in st.session_state:
        st.session_state.config = OllamaConfig()
    if 'connection_error' not in st.session_state:
        st.session_state.connection_error = None
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = set()

def configuration_ui():
    """Display and handle Ollama configuration UI."""
    st.header("Ollama Configuration")
    
    # URL Configuration
    current_url = st.session_state.config.get_base_url()
    url = st.text_input(
        "Ollama API URL",
        value=current_url if current_url else "http://localhost:11434",
        help="Enter the URL of your Ollama instance"
    )
    
    # Show current connection error if any
    if st.session_state.connection_error:
        st.error(st.session_state.connection_error)
    
    if st.button("Connect to Ollama"):
        success, message = test_ollama_connection(url)
        if success:
            if st.session_state.config.set_base_url(url):
                st.session_state.connection_error = None
                st.success(message)
                st.rerun()
            else:
                st.session_state.connection_error = "Failed to configure Ollama URL"
        else:
            st.session_state.connection_error = message
            st.error(message)
    
    # Model Selection
    if current_url:
        available_models = st.session_state.config.get_available_models()
        if available_models:
            current_model = st.session_state.config.get_selected_model()
            selected_model = st.selectbox(
                "Select Model",
                options=available_models,
                index=available_models.index(current_model) if current_model in available_models else 0
            )
            
            if st.button("Set Model"):
                if st.session_state.config.set_selected_model(selected_model):
                    st.success(f"Successfully set model to {selected_model}")
                    st.rerun()
                else:
                    st.error("Failed to set model")
        else:
            st.warning("No models found. Please ensure you have models installed in Ollama.")

def main():
    """Main application."""
    initialize_session_state()
    
    # Title
    st.markdown('<div class="title-container"><h1 class="title">Ollama PDF Chat</h1></div>', unsafe_allow_html=True)
    
    # Configuration Section
    with st.expander("⚙️ Configuration", expanded=not st.session_state.config.is_configured()):
        configuration_ui()
    
    # Main Interface
    if st.session_state.config.is_configured():
        # File upload
        uploaded_file = st.file_uploader("Upload a PDF document", type=['pdf'])
        
        if uploaded_file is not None:
            # Check if file was already processed
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            if file_id not in st.session_state.processed_files:
                with st.spinner("Processing document..."):
                    # Reset file pointer to start
                    uploaded_file.seek(0)
                    if embed(uploaded_file):
                        st.success(f"Successfully processed {uploaded_file.name}!")
                        st.session_state.processed_files.add(file_id)
                    else:
                        st.error(f"Failed to process {uploaded_file.name}")
        
        # Chat interface
        st.subheader("Ask Questions")
        user_question = st.text_input("Enter your question about the document")
        
        if user_question:
            with st.spinner("Thinking..."):
                response = query(user_question)
                st.write(response)
    
    # Footer
    st.markdown(
        '<div class="footer">Created with 💗 by <a href="https://abhishkkumar.com" target="_blank">Abhishek Kumar</a></div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
