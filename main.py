import asyncio


from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from typing import List

# agent imports
from agent import QueueCallbackHandler, agent_executor

# rag manager imports
from rag_manager import ingest_all, ingest, delete_docs, summarize_chroma

# initilizing our application
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# streaming function
async def token_generator(content: str, streamer: QueueCallbackHandler):
    task = asyncio.create_task(agent_executor.invoke(
        input=content,
        streamer=streamer,
        verbose=True  # set to True to see verbose output in console
    ))
    # initialize various components to stream
    async for token in streamer:
        try:
            if token == "<<STEP_END>>":
                # send end of step token
                yield "</step>"
            elif tool_calls := token.message.additional_kwargs.get("tool_calls"):
                if tool_name := tool_calls[0]["function"]["name"]:
                    # send start of step token followed by step name tokens
                    yield f"<step><step_name>{tool_name}</step_name>"
                if tool_args := tool_calls[0]["function"]["arguments"]:
                    # tool args are streamed directly, ensure it's properly encoded
                    yield tool_args
        except Exception as e:
            print(f"Error streaming token: {e}")
            continue
    await task

# invoke function
@app.post("/invoke")
async def invoke(content: str):
    queue: asyncio.Queue = asyncio.Queue()
    streamer = QueueCallbackHandler(queue)
    # return the streaming response
    return StreamingResponse(
        token_generator(content, streamer),
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
