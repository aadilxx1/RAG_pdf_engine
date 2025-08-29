# RAG PDF Q&A

An interactive **PDF Question-Answering application** using **Retrieval-Augmented Generation (RAG)**. Users can ask questions about PDFs stored locally or on Google Drive, and the system retrieves relevant chunks, generates answers using a local LLM, and includes citations with links to the source PDFs.

---

## Features

- **Hybrid Retrieval**: Combines Elasticsearch BM25 search and dense embeddings with reranking.  
- **Google Drive Integration**: Fetch PDFs directly from a shared Drive folder.  
- **LLM-powered Answer Generation**: Uses a local LLaMA/Flan-T5 model to generate concise, evidence-based answers.  
- **Citations with Links**: Each answer includes clickable links to the source PDF chunks.
- **Caching**: Prevents repeated API calls and redundant model runs for faster responses.   
- **Guardrails**: Automatically refuses unsafe, harmful, or off-topic queries.  
- **Clean and Responsive UI**: Simple web interface with retrieved chunks and generated answers.

---

## Guardrails

- The system refuses unsafe or harmful queries (e.g., hacking, attacks, illegal instructions).

- Answers are grounded only in retrieved chunks—the model will reply "I don't know" if information is missing.

---

## Dependencies
- python -m venv env
- source env/bin/activate
- pip install -r req.txt
- python -m ingest.ingest_runner
- uvicorn api.main:app --reload

then in another terminal run cmnd - > python ui/app.py

- Open your browser at http://127.0.0.1:5000

---

## Requirements

- Python 3.10+
- Elasticsearch 8.x
- Google Drive service account credentials (JSON)

```bash
pip install flask requests transformers sentence-transformers elasticsearch PyPDF2 google-api-python-client google-auth google-auth-oauthlib
