# tools/rag_tool.py

from typing import List, Tuple, Union
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

# ─── Load environment so OPENAI_API_KEY is available ─────────────────────────────────
# If you have a .env file with OPENAI_API_KEY, this line will read it into os.environ.
load_dotenv()

@tool
async def retrieval_tool(query: str) -> str:
    """
    Use this tool to answer any programming or Python-related questions,
    including definitions, usage, and language concepts. This tool searches
    an extensive internal documentation database (including official Python documentation).
    Use this tool for ANY question about Python, programming, or technical topics.
    """

    # ─── Configuration ─────────────────────────────────────────────────────────
    CHROMA_DIR = "chroma_db"
    EMBEDDING_MODEL = OpenAIEmbeddings()  # Will raise if OPENAI_API_KEY is missing
    K = 3            # Number of chunks to retrieve
    THRESHOLD = 0.7  # Minimum cosine‐similarity (0–1) to consider “relevant”

    # ─── Step 1: Load the Chroma vector store ───────────────────────────────────
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=EMBEDDING_MODEL
    )

    # ─── Step 2: Retrieve (chunk, score) pairs ──────────────────────────────────
    # `chunk` might be a Document or a plain string
    results: List[Tuple[Union[Document, str], float]] = vectorstore.similarity_search_with_relevance_scores(
        query,
        k=K
    )

    for i, (chunk_obj, score) in enumerate(results):
        text = chunk_obj.page_content if isinstance(chunk_obj, Document) else str(chunk_obj)
        # Print the first 80 characters so you can see what chunk we’re talking about
        snippet = text.replace("\n", " ")[:80] + "…"
        print(f"Candidate #{i+1}: score = {score:.3f}, text starts with -> {snippet}")

    # If nothing is in the index, return fallback immediately
    if not results:
        return "No relevant documents found."

    # ─── Step 3: Check top‐score vs. threshold ──────────────────────────────────
    top_texts: List[str] = []
    i = 0
    for chunk_obj, score in results:
        i += 1
        if score < THRESHOLD:
            # Skip any chunk scoring below threshold
            print(f"Candidate#{i}: score = {score:.3f}, Skipping (below threshold {THRESHOLD})")
            continue

        if isinstance(chunk_obj, Document):
            top_texts.append(chunk_obj.page_content)
        else:
            top_texts.append(str(chunk_obj))

    if not top_texts:
        # If ALL candidates fell below threshold, fall back
        return "No relevant documents found."

    return "\n\n---NEXT-CHUNK---\n\n".join(top_texts)
