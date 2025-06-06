# vectorstore.py

import os
from dotenv import load_dotenv

# ─── Step 1: Imports ────────────────────────────────────────────────────────────

# `Chroma` now lives in the `langchain_chroma` package (v0.3+).
from langchain_chroma import Chroma

# We continue to use `OpenAIEmbeddings` from `langchain_openai`
from langchain_openai import OpenAIEmbeddings


# ─── Step 2: Load environment variables ──────────────────────────────────────────

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("Missing OPENAI_API_KEY in .env")


# ─── Step 3: Instantiate the Embedding Model ─────────────────────────────────────

# Use the same embeddings class you used during ingestion so that vectors align.
embeddings = OpenAIEmbeddings()


# ─── Step 4: Function to Load Chroma Vector Store ────────────────────────────────

def load_vectorstore(persist_dir: str = "chroma_db"):
    """
    Load an existing Chroma vector store from disk and return a Retriever.
    Raises:
        FileNotFoundError: if the directory does not exist.
    """
    if not os.path.isdir(persist_dir):
        raise FileNotFoundError(
            f"Chroma directory '{persist_dir}' not found. Run `ingest.py` first."
        )

    # Pass `embedding_function=embeddings` so that any new queries are embedded identically.
    vectorstore = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings
    )

    # Wrap as a Retriever. By default, this uses cosine similarity.
    retriever = vectorstore.as_retriever()
    return retriever


# ─── Step 5: Convenience Function to Query Chroma ────────────────────────────────

def query_chroma(question: str, k: int = 3):
    """
    Given a text question, return the top-k most relevant document chunks from Chroma.

    Args:
      question: The user’s question as a plain string.
      k: How many top results to return.

    Returns:
      A list of strings, each being the `.page_content` of a retrieved chunk.
    """
    retriever = load_vectorstore()

    # Instead of `get_relevant_documents(...)`, use `invoke(...)` (or `__call__`)
    docs = retriever.invoke(question)

    # If you want only k results, slice the returned list:
    top_chunks = [doc.page_content for doc in docs[:k]]
    return top_chunks
