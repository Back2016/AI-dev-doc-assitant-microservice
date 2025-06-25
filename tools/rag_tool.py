# tools/rag_tool.py

from typing import List, Tuple, Union
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

import logging

def build_filter(source):
    if isinstance(source, list) and source:
        return {"source": {"$in": source}}
    elif isinstance(source, str) and source:
        return {"source": source}
    else:
        return None


@tool
async def retrieval_tool(query: str, source: str = None) -> str:
    """
    Use this tool to answer any programming or Python-related questions,
    including definitions, usage, and language concepts. This tool searches
    an extensive internal documentation database (including official Python documentation).
    Use this tool for ANY question about Python, programming, or technical topics.
    """

    CHROMA_DIR = "chroma_db"
    EMBEDDING_MODEL = OpenAIEmbeddings()
    K = 3 # Number of chunks to return
    THRESHOLD = 0.7 # Minimum score threshold for relevance

    # Filter by source if provided
    filter_val = build_filter(source)

    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=EMBEDDING_MODEL
    )
    logging.info(f"Filter used in retrieval_tool: {filter_val}")

    results: List[Tuple[Union[Document, str], float]] = vectorstore.similarity_search_with_relevance_scores(
        query,
        k=K,
        filter=filter_val,
    )

    for i, (chunk_obj, score) in enumerate(results):
        text = chunk_obj.page_content if isinstance(chunk_obj, Document) else str(chunk_obj)
        # Print the first 80 characters so you can see what chunk we’re talking about
        src = getattr(chunk_obj, "metadata", {}).get("source", "unknown")
        snippet = text.replace("\n", " ")[:80] + "…"
        logging.info(f"Candidate #{i+1}: source={src} score = {score:.3f}, text starts with -> {snippet}")

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
            logging.info(f"Candidate#{i}: score = {score:.3f}, Skipping (below threshold {THRESHOLD})")
            continue

        if isinstance(chunk_obj, Document):
            top_texts.append(chunk_obj.page_content)
        else:
            top_texts.append(str(chunk_obj))

    if not top_texts:
        # If ALL candidates fell below threshold, fall back
        return "No relevant documents found."

    return "\n\n---NEXT-CHUNK---\n\n".join(top_texts).join(f"Retrieving documents for query: {query}")
