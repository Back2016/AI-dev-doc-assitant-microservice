import os
import glob
from dotenv import load_dotenv

from typing import List, Dict

from langchain_community.document_loaders import TextLoader
from langchain.schema import Document

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Load environment variables
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("Missing OPENAI_API_KEY in .env")

DOCS_DIR = "docs"
CHROMA_DIR = "chroma_db"
EMBEDDING_MODEL = OpenAIEmbeddings()
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

# DB summary
def summarize_chroma():
    """
    Returns a summary of the Chroma DB: for each source document,
    the number of chunks present in the DB.
    Returns:
        List of dicts: [{ "source": <filename>, "count": <num_chunks> }, ...]
    """
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=EMBEDDING_MODEL
    )
    # Get all metadata
    all_metadatas = vectorstore.get(include=["metadatas"])["metadatas"]
    # Count by source
    from collections import Counter
    sources = [md.get("source", "UNKNOWN") for md in all_metadatas]
    counts = Counter(sources)
    summary = [{"source": src, "count": count} for src, count in counts.items()]
    return summary

# Ingest and delete functions
def _split_and_label(doc_path: str) -> list[Document]:
    loader = TextLoader(doc_path, encoding="utf-8")
    docs = loader.load()  # returns [Document(page_content=...)]
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n### ", "\n## ", "\n# ", "\n"],
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    # Split and add source filename as metadata
    split_docs = text_splitter.split_documents(docs)
    for d in split_docs:
        d.metadata = d.metadata or {}
        d.metadata["source"] = os.path.basename(doc_path)
    return split_docs

def ingest_all():
    """Ingest all .md files under DOCS_DIR, rebuilding the Chroma DB."""
    md_paths = glob.glob(os.path.join(DOCS_DIR, "**", "*.md"), recursive=True)
    all_chunks = []
    for path in md_paths:
        try:
            all_chunks.extend(_split_and_label(path))
        except Exception as e:
            print(f"Error loading file {path}: {e}")
    if not all_chunks:
        print("No markdown files found!")
        return
    # Overwrite DB with new content
    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=EMBEDDING_MODEL,
        persist_directory=CHROMA_DIR
    )
    print(f"✅ Ingested {len(all_chunks)} chunks from {len(md_paths)} files.")

def ingest(doc_names: list[str]) -> int:
    """Ingest just the specified docs into Chroma DB (additive, does not delete).
    Returns number of chunks ingested.
    Raises FileNotFoundError if none found.
    """
    chunks = []
    for doc_name in doc_names:
        path = os.path.join(DOCS_DIR, doc_name)
        if not os.path.isfile(path):
            print(f"File not found: {path}")
            continue
        try:
            chunks.extend(_split_and_label(path))
        except Exception as e:
            print(f"Error loading {path}: {e}")
    if not chunks:
        print("No valid files to ingest.")
        raise FileNotFoundError("No valid files to ingest.")
    # Append to existing vectorstore
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=EMBEDDING_MODEL
    )
    vectorstore.add_documents(chunks)
    print(f"✅ Ingested {len(chunks)} chunks from {len(doc_names)} docs.")
    return len(chunks)

def delete_docs(doc_names: List[str]) -> Dict[str, int]:
    """
    Delete all chunks in the DB that have a source in doc_names.
    Returns: dict mapping doc_name to number of deleted chunks.
    """
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=EMBEDDING_MODEL
    )
    deleted_counts = {}
    for doc_name in doc_names:
        n_before = len(vectorstore.get()['ids'])
        vectorstore.delete(where={"source": doc_name})
        n_after = len(vectorstore.get()['ids'])
        deleted = n_before - n_after
        deleted_counts[doc_name] = deleted
        print(f"✅ Deleted {deleted} chunks from {doc_name}.")
    return deleted_counts
