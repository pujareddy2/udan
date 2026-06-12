from fastapi import APIRouter

router = APIRouter()

@router.get("/{module}/documents/summary", tags=["Documents"])
def get_module_documents_summary(module: str):
    return {
        "success": True,
        "message": f"Document summary for {module}",
        "available_documents": 5,
        "missing_documents": 2,
        "expired_documents": 1,
        "required_documents": [
            "Income Certificate",
            "Aadhaar Card"
        ]
    }

@router.get("/documents/{document_name}", tags=["Documents"])
def get_document_details(document_name: str):
    return {
        "success": True,
        "message": "Document details retrieved",
        "name": document_name,
        "sample_image": "https://example.com/sample_income.jpg",
        "purpose": "Income Verification",
        "authority": "MeeSeva",
        "validity": "1 Year",
        "required_supporting_docs": [
            "Aadhaar Card",
            "Ration Card"
        ]
    }

@router.get("/documents/{document_name}/recovery-guide", tags=["Documents"])
def get_document_recovery_guide(document_name: str):
    return {
        "success": True,
        "message": "Recovery guide retrieved",
        "document": document_name,
        "authority": "MeeSeva",
        "apply_link": "https://ts.meeseva.telangana.gov.in/",
        "processing_time": "7 Days",
        "required_documents": [
            "Aadhaar Card"
        ],
        "steps": [
            "Visit MeeSeva portal",
            "Fill the application form",
            "Upload Aadhaar",
            "Pay fee",
            "Wait 7 days"
        ]
    }
