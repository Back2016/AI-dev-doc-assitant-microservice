# LangChain Microservice for RAG + Agents + Streaming

This is a standalone **LangChain microservice**, built with **FastAPI**, that provides:
- Retrieval-Augmented Generation (RAG)
- LangChain Agent with custom tools
- Real-time streaming responses (token-by-token)

This microservice is designed to be part of a full-stack AI application:
- **Frontend**: Next.js
- **Backend Gateway**: Spring Boot
- **LLM Engine**: This Python-based LangChain service

---

## Features

- **/chat/stream** endpoint for streaming LLM responses
- Easily integrates with any Java or TypeScript backend (e.g., Spring Boot)
- Document ingestion pipeline using `langchain`, `chromadb`, and `openai` embeddings
- Plug-and-play agent architecture: custom tools (e.g., RAG retriever, calculator) supported
- Ready for Dockerization and production deployment

---

## Run the API

* `source venv/bin/activate (if want to run with venv)
* `cd` into the `/api` directory
* execute `uv run uvicorn main:app --reload` to start the API
* you can find the API docs at `http://localhost:8000/docs`
* you can test the streaming by running the `streaming-test.ipynb` notebook

## Run the App

* `cd` into the `/app` directory
* execute `npm install` to install the dependencies
* execute `npm run dev` to start the app
* you can find the app at `http://localhost:3000`
