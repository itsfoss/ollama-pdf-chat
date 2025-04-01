import os
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from config import OllamaConfig
import chromadb
from chromadb.config import Settings

# Configure ChromaDB with telemetry disabled
chromadb.Client(Settings(anonymized_telemetry=False))

def get_vector_db():
    """Initialize and return the ChromaDB vector database instance."""
    try:
        config = OllamaConfig()
        if not config.is_configured():
            return None

        persist_directory = os.getenv('PERSIST_DIRECTORY', './_vectors')
        os.makedirs(persist_directory, exist_ok=True)

        embeddings = OllamaEmbeddings(
            base_url=config.get_base_url(),
            model=config.get_selected_model()
        )

        db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
        )

        return db
    except Exception as e:
        print(f"Error initializing vector database: {str(e)}")
        return None
