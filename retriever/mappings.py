INDEX_NAME = "rag_docs_v1"

MAPPING = {
  "mappings": {
    "properties": {
      "text":       {"type": "text"},
      "text_vec":   {"type": "dense_vector", "dims": 384, "index": True, "similarity":"cosine"},
      "filename":   {"type": "keyword"},
      "drive_url":  {"type": "keyword"},
      "chunk_id":   {"type": "keyword"},
      "metadata":   {"type": "object"}
    }
  }
}
