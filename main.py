import asyncio
import json
import os

from fastapi import FastAPI, HTTPException, status, UploadFile, File, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from typing import List, Optional, Union

from pydantic import BaseModel

# agent imports
# from agent import QueueCallbackHandler, agent_executor
from agent_with_custom_history import QueueCallbackHandler, agent_executor

# doc and rag manager imports
from doc_manager import upload_doc
from rag_manager import ingest_all, ingest, delete_docs, summarize_chroma

# Log management
import logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger(__name__)

# initilizing our application
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class InvokeRequest(BaseModel):
    content: str
    session_id: str
    source: Optional[Union[str, List[str]]] = None  # Accept single source or list of sources

async def token_generator(content: str, streamer: QueueCallbackHandler, session_id: str, selected_source: Optional[str] = None):
    task = asyncio.create_task(agent_executor.invoke(
        input=content,
        streamer=streamer,
        session_id=session_id,
        selected_source=selected_source,
        verbose=True
    ))
    async for token in streamer:
        try:
            if token == "<<STEP_END>>":
                yield "</step>"
            elif tool_calls := token.message.additional_kwargs.get("tool_calls"):
                if tool_name := tool_calls[0]["function"]["name"]:
                    yield f"<step><step_name>{tool_name}</step_name>"
                if tool_args := tool_calls[0]["function"]["arguments"]:
                    yield tool_args
        except Exception as e:
            logging.error(f"Error streaming token: {e}")
            continue

    final_answer_dict, agent_scratchpad = await task
    # When everything is done, send the scratchpad
    scratchpad_summary = []
    for i in range(0, len(agent_scratchpad), 2):
        call = agent_scratchpad[i]
        result = agent_scratchpad[i+1] if i+1 < len(agent_scratchpad) else None
        if hasattr(call, "tool_calls") and call.tool_calls and result:
            tool_name = call.tool_calls[0]["name"]
            try:
                content = json.loads(result.content)
            except Exception:
                content = result.content
            scratchpad_summary.append({
                "name": tool_name,
                "result": content,
            })
    # Yield the scratchpad as a final message
    yield f"<scratchpad>{json.dumps(scratchpad_summary)}</scratchpad>"


@app.post("/invoke")
async def invoke(request: InvokeRequest):
    queue: asyncio.Queue = asyncio.Queue()
    streamer = QueueCallbackHandler(queue)
    return StreamingResponse(
        token_generator(request.content, streamer, request.session_id, request.source),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# RAG managing endpoint
@app.get("/rag/summary")
def api_rag_summary():
    return summarize_chroma()

@app.post("/rag/ingest-all")
def api_ingest_all():
    ingest_all()
    return {"message": "All docs ingested."}

@app.post("/rag/ingest")
def api_ingest(doc_names: list[str]):
    try:
        num_chunks = ingest(doc_names)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    return {"message": f"Ingested: {doc_names}", "chunks_ingested": num_chunks}

@app.delete("/rag/delete")
def api_delete(doc_names: List[str]):
    deleted_counts = delete_docs(doc_names)
    not_found = [doc for doc, count in deleted_counts.items() if count == 0]
    if not_found:
        # If ANY doc was not found, return 404 and list which ones
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No chunks found for: {not_found}"
        )
    return {
        "message": f"Deleted: {doc_names}",
        "deleted_counts": deleted_counts
    }

@app.post("/rag/upload")
async def upload_markdown(file: UploadFile = File(...)):
    # Only allow .md files
    if not file.filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="Only .md files are allowed")
    # Read file contents
    content = await file.read()
    try:
        path = upload_doc(file.filename, content)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    return {"message": f"File {file.filename} uploaded", "path": path}

DOCS_DIR = "docs"

@app.get("/rag/list")
def rag_list():
    # Step 1: List all .md files in docs/
    files = [
        f for f in os.listdir(DOCS_DIR)
        if os.path.isfile(os.path.join(DOCS_DIR, f)) and f.endswith(".md")
    ]
    # Step 2: Get Chroma summary (returns [{'source': filename, 'count': chunks}, ...])
    chroma_summary = summarize_chroma()
    chunk_map = {item['source']: item['count'] for item in chroma_summary}
    # Step 3: Build the results list
    results = []
    for fname in files:
        chunks = chunk_map.get(fname, 0)
        results.append({
            "filename": fname,
            "chunks": chunks,
            "ingested": chunks > 0
        })
    # Optional: Add files that are in vectorstore but no longer in docs (could be deleted from disk)
    for src, count in chunk_map.items():
        if src not in files:
            results.append({
                "filename": src,
                "chunks": count,
                "ingested": True,
                "note": "Ingested, but file missing in docs/"
            })
    return results

@app.get("/healthz")
def health_check():
    checks = {"status": "ok"}
    # Check OpenAI key loaded
    from os import getenv
    if not getenv("OPENAI_API_KEY"):
        checks["openaiKey"] = "missing"
        checks["status"] = "degraded"
    else:
        checks["openaiKey"] = "ok"

    # Check Chroma vectorstore dir exists
    import os
    if not os.path.isdir("chroma_db"):
        checks["vectorstore"] = "missing"
        checks["status"] = "degraded"
    else:
        checks["vectorstore"] = "ok"

    return checks
