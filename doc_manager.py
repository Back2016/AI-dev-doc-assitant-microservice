import os

DOCS_DIR = "docs"

def upload_doc(filename: str, file_content: bytes) -> str:
    """
    Saves the uploaded markdown file to the docs/ directory.
    Overwrites if file exists.
    Returns the path to the saved file.
    """
    # Sanitize filename (simple: no path traversal)
    if "/" in filename or "\\" in filename or filename.startswith("."):
        raise ValueError("Invalid filename.")
    os.makedirs(DOCS_DIR, exist_ok=True)
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "wb") as f:
        f.write(file_content)
    return path
