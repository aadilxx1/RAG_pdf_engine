import os
import json
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PyPDF2 import PdfReader

#Drive folder ID
FOLDER_ID = "1MbqteUjSkKTQ7NXIpLp5gzsEGrZwDBag"

#JSON service account key
SERVICE_ACCOUNT_FILE = "GD_service_creds.json"

def get_drive_service():
    """Authenticate with Google Drive using service account JSON file."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)

def list_pdfs():
    """List all PDFs in the given Drive folder."""
    service = get_drive_service()
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType='application/pdf'",
        fields="files(id, name, webViewLink)"
    ).execute()
    return results.get("files", [])

def download_pdf(file_id):
    """Download a PDF file and return its text."""
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)
    reader = PdfReader(fh)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text
