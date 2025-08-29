import fitz  # PyMuPDF
import re

def clean_text(text: str) -> str:
    #Removing URLs
    text = re.sub(r'http\S+', '', text)
    #Removing reference-style numbers at start of lines or in parentheses
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'\(\d+\)', '', text)
    # Removng extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text("text") + "\n"
    return clean_text(text)


