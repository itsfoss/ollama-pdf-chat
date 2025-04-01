import os
from typing import Optional
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from get_vector_db import get_vector_db
from config import OllamaConfig

def query(question: str) -> str:
    """Query the vector database with a question."""
    try:
        config = OllamaConfig()
        if not config.is_configured():
            return "Error: Ollama is not configured. Please set up the server connection first."

        db = get_vector_db()
        if db is None:
            return "Error: Could not initialize vector database. Please check your configuration."

        # Verify documents exist
        docs = db.get()
        if not docs or len(docs.get('ids', [])) == 0:
            return "No documents found. Please upload a PDF first."

        # Initialize chat model with user's selected model
        chat = ChatOllama(
            base_url=config.get_base_url(),
            model=config.get_selected_model(),
            temperature=0.1
        )

        # Create memory for conversation context
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="answer",
            return_messages=True
        )

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant. Use the following pieces of context to answer the user's question. 
            If you don't find the answer in the context, say "I don't have enough information to answer this question."
            
            Context: {context}"""),
            ("human", "{question}")
        ])

        # Create retrieval chain
        chain = ConversationalRetrievalChain.from_llm(
            llm=chat,
            retriever=db.as_retriever(
                search_kwargs={"k": min(4, len(docs['ids']))}
            ),
            memory=memory,
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True,
            verbose=True
        )

        # Get response
        result = chain({"question": question})
        
        # Format response with sources
        answer = result["answer"]
        sources = result.get("source_documents", [])
        
        if sources:
            source_text = "\n\nSources:\n"
            for i, doc in enumerate(sources, 1):
                source = doc.metadata.get("source", "Unknown")
                page = doc.metadata.get("page", "Unknown")
                source_text += f"{i}. Document: {source}, Page: {page}\n"
            answer += source_text

        return answer

    except Exception as e:
        return f"Error processing query: {str(e)}"
