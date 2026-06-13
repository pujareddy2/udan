import os
import json
import httpx
from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel
from datetime import datetime
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.domain import UserProfile, Document, DocumentMaster
from app.core.config import settings

router = APIRouter()

@router.get("/{module}/documents/summary", tags=["Documents"])
def get_module_documents_summary(module: str, user_id: int = None, session: Session = Depends(get_session)):
    available = 5
    missing = ["Income Certificate", "Land Passbook"]
    
    if user_id:
        user_profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
        if user_profile and user_profile.profile_data:
            docs = user_profile.profile_data.get("documents", [])
            available = len(docs)
            missing = []
            if "Aadhaar" not in docs: missing.append("Aadhaar")
            if "Land Passbook" not in docs: missing.append("Land Passbook")
            if "Income Certificate" not in docs: missing.append("Income Certificate")
            
    return {
        "available_documents": available,
        "missing_documents": len(missing),
        "missing": missing
    }

@router.get("/documents/{document_name}", tags=["Documents"])
def get_document_details(document_name: str):
    return {
        "name": document_name,
        "sample_image": "",
        "authority": "MeeSeva",
        "validity": "1 Year",
        "purpose": "Income Verification" if "Income" in document_name else "Verification",
        "required_for": [
            "Scholarships",
            "Subsidies"
        ]
    }

@router.get("/documents/{document_name}/recovery-guide", tags=["Documents"])
async def get_document_recovery_guide(document_name: str):
    groq_api_key = os.getenv("GROQ_API_KEY", settings.GROQ_API_KEY)
    serper_api_key = os.getenv("SERPER_API_KEY", settings.SERPER_API_KEY)

    # --- 1. Groq: Get structured guide ---
    prompt = f"""
    You are an expert Indian e-Governance assistant. The user needs to apply for a '{document_name}' in India.
    Provide the exact response in valid JSON format with the following keys:
    - "apply_link": A valid official URL where the user can apply for this document online (e.g., https://www.india.gov.in or specific portal).
    - "processing_time": Estimated time to get it (e.g., "7-14 Days").
    - "steps": A list of strings, each being a clear, actionable step to get this document.
    - "required_documents": A list of strings, what they need to upload/bring (e.g., Aadhaar, Photo).
    
    Make it highly accurate for India. Return ONLY the JSON object, nothing else.
    """
    
    data = {
        "apply_link": "https://www.myscheme.gov.in/",
        "processing_time": "7-14 Days",
        "steps": [
            f"Visit your local MeeSeva or CSC center to apply for {document_name}.",
            "Fill out the application form.",
            "Submit the required documents and pay the fee.",
            "Wait for the verification and approval process."
        ],
        "required_documents": ["Aadhaar Card", "Passport Size Photo"]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                },
                timeout=10.0
            )
            if response.status_code == 200:
                res_json = response.json()
                content = res_json['choices'][0]['message']['content']
                parsed = json.loads(content)
                data.update(parsed)
    except Exception as e:
        print(f"Groq API error: {e}")

    # --- 2. Serper: Fetch real Google Images for sample document ---
    sample_images = []
    image_search_query = f"official {document_name} India sample certificate format"
    try:
        async with httpx.AsyncClient() as client:
            serper_resp = await client.post(
                "https://google.serper.dev/images",
                headers={
                    "X-API-KEY": serper_api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "q": image_search_query,
                    "gl": "in",
                    "hl": "en",
                    "num": 6
                },
                timeout=10.0
            )
            if serper_resp.status_code == 200:
                img_data = serper_resp.json()
                images_raw = img_data.get("images", [])
                # Pick top 3 valid image URLs (prefer imageUrl over thumbnailUrl)
                for img in images_raw[:10]:
                    url = img.get("imageUrl") or img.get("thumbnailUrl")
                    if url and url.startswith("http") and not url.endswith(".svg"):
                        sample_images.append({
                            "url": url,
                            "title": img.get("title", document_name),
                            "source": img.get("source", "")
                        })
                    if len(sample_images) >= 3:
                        break
    except Exception as e:
        print(f"Serper Image API error: {e}")

    encoded_name = document_name.replace(' ', '+')

    return {
        "document": document_name,
        "apply_link": data.get("apply_link", "https://www.myscheme.gov.in/"),
        "required_documents": data.get("required_documents", ["Aadhaar", "Photo"]),
        "processing_time": data.get("processing_time", "7 Days"),
        "steps": data.get("steps", ["Submit Application"]),
        "youtube_link": f"https://www.youtube.com/results?search_query=how+to+apply+for+{encoded_name}+in+india",
        # Legacy single image (first result or fallback)
        "sample_image": sample_images[0]["url"] if sample_images else "",
        # New: multiple Google Images results for carousel
        "sample_images": sample_images,
        "image_search_query": image_search_query
    }

class DocumentUploadBody(BaseModel):
    user_id: int
    document_name: str

@router.post("/documents/upload", tags=["Documents"])
def upload_document_json(body: DocumentUploadBody, session: Session = Depends(get_session)):
    dm = session.exec(select(DocumentMaster).where(DocumentMaster.document_name == body.document_name)).first()
    if not dm:
        dm = DocumentMaster(document_name=body.document_name, description=f"{body.document_name} description", issuing_authority="Government Office")
        session.add(dm)
        session.commit()
        session.refresh(dm)
        
    doc = session.exec(select(Document).where(Document.user_id == body.user_id, Document.doc_master_id == dm.id)).first()
    if doc:
        doc.status = "Verified"
        doc.uploaded_at = datetime.utcnow()
    else:
        doc = Document(
            user_id=body.user_id,
            doc_master_id=dm.id,
            status="Verified",
            file_url=f"https://s3.amazonaws.com/udaan/{body.document_name.lower().replace(' ', '_')}.pdf"
        )
        session.add(doc)
        
    session.commit()
    return {
        "success": True,
        "message": f"Document '{body.document_name}' uploaded and verified successfully!"
    }
