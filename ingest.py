# ingest.py

import os
import glob
from dotenv import load_dotenv

# ─── Step 1: Imports ────────────────────────────────────────────────────────────

from langchain_community.document_loaders import TextLoader
from langchain.schema import Document

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# ─── Step 2: Load environment variables ──────────────────────────────────────────

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("Missing OPENAI_API_KEY in .env")

# ─── Step 3: Configuration ──────────────────────────────────────────────────────

DOCS_DIR = "docs"         # directory containing Markdown files
CHROMA_DIR = "chroma_db"  # where Chroma persists embeddings
EMBEDDING_MODEL = OpenAIEmbeddings()

# We will split on Markdown headers first, then enforce a character cap
CHUNK_SIZE = 1_000     # max 1,000 characters per chunk
CHUNK_OVERLAP = 100    # overlap 100 characters to preserve continuity


def main():
    # ─── Step 4: Find all .md files under docs/ ────────────────────────────────
    md_paths = glob.glob(os.path.join(DOCS_DIR, "**", "*.md"), recursive=True)
    if not md_paths:
        print(f"No Markdown files found in '{DOCS_DIR}/'.")
        return

    # ─── Step 5: Load each Markdown file as a single Document ───────────────────
    raw_documents: list[Document] = []
    for path in md_paths:
        try:
            loader = TextLoader(path, encoding="utf-8")
            docs_from_file = loader.load()  # returns [Document(page_content=...)]
            raw_documents.extend(docs_from_file)
        except Exception as e:
            print(f"Error loading file {path}: {e}")

    print(f"✅ Loaded {len(raw_documents)} document(s).")

    # ─── Step 6: Split each document using RecursiveCharacterTextSplitter ────────
    # We list header‐style separators first, so it splits on ##, ###, etc., before falling back to newline.
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n### ", "\n## ", "\n# ", "\n"],
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    split_docs = []
    for raw_doc in raw_documents:
        split_docs.extend(text_splitter.split_documents([raw_doc]))

    print(f"✅ Split into {len(split_docs)} chunks.")

    # ─── Step 7: Embed & Persist to Chroma ───────────────────────────────────────
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=EMBEDDING_MODEL,
        persist_directory=CHROMA_DIR
    )
    print(f"✅ Chroma DB persisted to {CHROMA_DIR}.")


if __name__ == "__main__":
    main()
