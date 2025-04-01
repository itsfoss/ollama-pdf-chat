from setuptools import setup, find_packages

setup(
    name="ollama-pdf-chat",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "chromadb>=0.4.22",
        "streamlit>=1.24.0",
        "langchain>=0.1.5",
        "langchain-community>=0.0.20",
        "langchain-text-splitters>=0.0.1",  
        "unstructured[all-docs]>=0.12.3",
        "pypdf>=3.9.0",
        "werkzeug>=3.0.1",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "typing-extensions>=4.5.0",
        "pydantic>=2.0.0",
        "tiktoken>=0.5.2"
    ],
    python_requires=">=3.11",
)
