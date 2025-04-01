import os
from datetime import datetime
from typing import Optional
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from get_vector_db import get_vector_db

TEMP_FOLDER = os.getenv('TEMP_FOLDER', './_temp')

def embed(file) -> bool:
    """Process and embed a PDF file."""
    temp_path = None
    try:
        # Create temp directory if it doesn't exist
        os.makedirs(TEMP_FOLDER, exist_ok=True)

        # Save uploaded file
        filename = secure_filename(file.name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_path = os.path.join(TEMP_FOLDER, f"{timestamp}_{filename}")
        
        with open(temp_path, 'wb') as f:
            f.write(file.read())

        # Load PDF with more granular page handling
        loader = PyPDFLoader(
            temp_path,
            extract_images=False  # Skip images for faster processing
        )
        pages = loader.load()
        
        if not pages:
            print(f"Warning: No content extracted from {filename}")
            return False

        # Split text into smaller chunks with more overlap for better context
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,  # Smaller chunks for better retrieval
            chunk_overlap=100,  # More overlap to maintain context
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""]  # More granular splitting
        )
        
        chunks = text_splitter.split_documents(pages)
        if not chunks:
            print(f"Warning: No chunks created from {filename}")
            return False

        print(f"Info: Created {len(chunks)} chunks from {filename}")

        # Update metadata with more context
        for i, chunk in enumerate(chunks):
            # Clean and normalize the text
            chunk.page_content = chunk.page_content.strip()
            
            # Enhanced metadata
            chunk.metadata.update({
                "source": filename,
                "chunk_id": i,
                "total_chunks": len(chunks),
                "timestamp": timestamp,
                "page": chunk.metadata.get("page", 1),
                "chunk_size": len(chunk.page_content),
                "position": "start" if i == 0 else "end" if i == len(chunks)-1 else "middle"
            })

        # Store in vector database with optimized settings
        db = get_vector_db()
        if db is None:
            print("Error: Vector database not initialized")
            return False

        db.add_documents(chunks)
        print(f"Success: Stored {len(chunks)} chunks in vector database")
        return True

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return False

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"Warning: Could not remove temporary file: {str(e)}")
