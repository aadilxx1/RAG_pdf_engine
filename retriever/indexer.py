# retriever/indexer.py
from elasticsearch import Elasticsearch, helpers
from retriever.mappings import INDEX_NAME, MAPPING
from models.dense_encoder import encode
import time
import os
from utils.cache import cached_search
from sentence_transformers import CrossEncoder
from retriever.drive_loader import list_pdfs, download_pdf
from ingest.chunk import chunk_text


reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
ES_URL = os.getenv("ES_URL", "http://localhost:9200")
es = Elasticsearch(ES_URL)

SIMILARITY_THRESHOLD = 0.7  # cosine similarity threshold for dense search

def ensure_index():
    """Create the Elasticsearch index if it doesn't exist."""
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=MAPPING)
        time.sleep(1)


def index_documents(docs):
    """Index documents into Elasticsearch."""
    texts = [d["text"] for d in docs]
    vecs = encode(texts)
    actions = []
    for d, vec in zip(docs, vecs):
        doc = {
            "text": d["text"],
            "text_vec": vec.tolist(),
            "filename": d["filename"],
            "drive_url": d.get("drive_url"),
            "chunk_id": d["chunk_id"],
            "metadata": d.get("metadata", {})
        }
        actions.append({"_op_type": "index", "_index": INDEX_NAME, "_id": d["chunk_id"], "_source": doc})
    helpers.bulk(es, actions)

@cached_search
def search_documents(query: str, top_k: int = 5, mode: str = "hybrid"):
    """
    Search documents with BM25 + Dense, deduplicate, rerank with cross-encoder,
    and return top_k chunk dicts.
    """
    if mode not in ("elser", "hybrid"):
        raise ValueError("mode must be 'elser' or 'hybrid'")

    relevant_hits = []

    # BM25 search
    bm25_resp = es.search(
        index=INDEX_NAME,
        size=top_k*5,  
        query={"match": {"text": {"query": query}}}
    )
    for hit in bm25_resp["hits"]["hits"]:
        if hit["_score"] > 0.5:
            relevant_hits.append(hit)

    if mode == "hybrid":
        # Dense vector search
        query_vec = encode([query])[0].tolist()
        dense_resp = es.search(
            index=INDEX_NAME,
            knn={
                "field": "text_vec",
                "query_vector": query_vec,
                "k": top_k*5,
                "num_candidates": top_k*10
            },
            _source=["chunk_id", "text", "filename", "drive_url", "metadata"]
        )
        for hit in dense_resp["hits"]["hits"]:
            if hit["_score"] >= SIMILARITY_THRESHOLD:
                relevant_hits.append(hit)

    # Deduplicate hits
    seen_ids = set()
    filtered_hits = []
    for h in relevant_hits:
        cid = h["_id"]
        if cid not in seen_ids:
            filtered_hits.append(h)
            seen_ids.add(cid)

    # If nothing is found
    if not filtered_hits:
        return []

    # --- Cross-encoder reranking ---
    #Preparing pairs of(query, chunk text)
    pairs = [(query, h["_source"]["text"]) for h in filtered_hits]
    scores = reranker.predict(pairs)

    # Attach scores and sort descending
    for h, score in zip(filtered_hits, scores):
        h["_cross_score"] = score
    filtered_hits.sort(key=lambda x: x["_cross_score"], reverse=True)

    # Keep only top_k after reranking
    filtered_hits = filtered_hits[:top_k]

    # Return as list of chunk dicts
    return [
        {
            "chunk_id": h["_source"]["chunk_id"],
            "text": h["_source"]["text"],
            "filename": h["_source"].get("filename", "unknown_file"),
            "drive_url": h["_source"].get("drive_url"),
            "metadata": h["_source"].get("metadata", {}),
        }
        for h in filtered_hits
    ]


