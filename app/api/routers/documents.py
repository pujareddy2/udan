from fastapi import APIRouter, File, UploadFile
from typing import List

router = APIRouter()

@router.get("/documents", tags=["Document Intelligence"])
def list_documents():
    """List all documents for the user."""
    return {"documents": ["Aadhaar Card", "Income Certificate"]}

@router.post("/documents/upload", tags=["Document Intelligence"])
def upload_document(file: UploadFile = File(...)):
    """Upload a new document."""
    return {"message": f"Successfully uploaded {file.filename}", "document_name": file.filename}

@router.get("/documents/{document_name}", tags=["Document Intelligence"])
def get_document_details(document_name: str):
    """Get specific details, status, or extracted text of a document."""
    return {
        "document_name": document_name,
        "status": "Verified",
        "extracted_fields": {"name": "Test User", "id_number": "1234 5678 9012"}
    }

@router.get("/documents/recovery-guide/{document_name}", tags=["Document Intelligence"])
def get_document_recovery_guide(document_name: str):
    """Get offline/online instructions for obtaining a missing document."""
    return {
        "document_name": document_name,
        "online_process": "Visit the portal, login, and click apply.",
        "offline_process": "Visit the nearest Tehsil office with your ID proof.",
        "estimated_time": "15 days"
    }
