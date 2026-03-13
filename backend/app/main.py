from fastapi import FastAPI
from pydantic import BaseModel
from app.rag_pipeline import process_query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="YouTube RAG Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    video_id: str
    question: str
    session_id: str

@app.post("/ask")
async def ask(request: QueryRequest):
    return process_query(
        video_id=request.video_id,
        question=request.question,
        session_id=request.session_id
    )