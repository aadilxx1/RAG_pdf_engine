from fastapi import FastAPI
from pydantic import BaseModel
from retriever.indexer import search_documents  # function to query ES
from retriever.indexer import ensure_index

ensure_index()
app = FastAPI(title="RAG API")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.post("/query")
def query_docs(request: QueryRequest):
    results = search_documents(request.query, top_k=request.top_k)
    return {"query": request.query, "results": results}
