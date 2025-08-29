import os
import json
from .pdf_parse import extract_text_from_pdf
from .chunk import chunk_text
from retriever.indexer import ensure_index, index_documents
from utils.cache import clear_all_caches
from retriever.drive_loader import list_pdfs, download_pdf

def ingest_pdf(file_info):
    """
    Extract text from a PDF (from Google Drive), chunk it, and prepare docs.
    file_info: dict with 'id' and 'name'
    """
    file_id = file_info["id"]
    filename = file_info["name"]
    drive_url = f"https://drive.google.com/file/d/{file_id}/view"

    #Download PDF content from Drive
    text = download_pdf(file_id)
    chunks = chunk_text(text, chunk_size=500, overlap=50)

    docs = []
    for i, chunk in enumerate(chunks):
        doc = {
            "filename": filename,
            "chunk_id": f"{filename}_{i}",
            "text": chunk,
            "drive_url": drive_url  
        }
        docs.append(doc)

    print(f"Prepared {len(chunks)} chunks from {filename}")
    return docs

if __name__ == "__main__":
    all_docs = []

    
    ensure_index()

    # List all PDFs in Drive
    pdf_files = list_pdfs()
    print("PDF files found on Drive:", pdf_files)


    for file_info in pdf_files:
        docs = ingest_pdf(file_info)
        all_docs.extend(docs)

    if all_docs:
        index_documents(all_docs)

    with open("ingested_docs.json", "w") as f:
        json.dump(all_docs, f, indent=2)

    print(f"Finished ingestion. Total documents: {len(all_docs)}")
    clear_all_caches()
