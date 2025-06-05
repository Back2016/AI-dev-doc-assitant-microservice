from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "LangChain microservice is running"}
