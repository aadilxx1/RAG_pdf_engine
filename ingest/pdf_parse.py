import fitz  # PyMuPDF
import re

def clean_text(text: str) -> str:
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove reference-style numbers at start of lines or in parentheses
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'\(\d+\)', '', text)
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text("text") + "\n"
    return clean_text(text)


