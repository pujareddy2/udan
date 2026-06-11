from typing import Dict, Any

# Hardcoded Knowledge Base (To be moved to SQL DB `document_master` and `resource_master`)
DOCUMENT_RECOVERY_KB = {
    "Income Certificate": {
        "apply_link": "https://edistrict.gov.in (Select your State)",
        "information_link": "https://www.india.gov.in/topics/certificates",
        "issuing_authority": "State Revenue Department / Tehsildar",
        "application_method": "Online via State e-District portal or physically at CSC/MeeSeva centers.",
        "processing_time_days": "7-15 Days",
        "required_documents": ["Aadhaar Card", "Ration Card", "Self-Declaration Form", "Salary Slip (if employed)"],
        "renewal_required": True
    },
    "Caste Certificate": {
        "apply_link": "https://edistrict.gov.in",
        "information_link": "https://www.india.gov.in/topics/certificates",
        "issuing_authority": "State Revenue Department",
        "application_method": "Online via e-District or offline at Tehsildar Office.",
        "processing_time_days": "15-30 Days",
        "required_documents": ["Aadhaar Card", "Proof of Caste (Ancestral property/parents cert)", "Address Proof"],
        "renewal_required": False # OBC Non-Creamy layer may differ
    },
    "UDYAM": {
        "apply_link": "https://udyamregistration.gov.in/",
        "information_link": "https://msme.gov.in/",
        "issuing_authority": "Ministry of MSME",
        "application_method": "100% Online, Paperless, and Free.",
        "processing_time_days": "Instant to 3 Days",
        "required_documents": ["Aadhaar Card linked to Mobile", "PAN Card", "Bank Account Details"],
        "renewal_required": False
    },
    "DPIIT Certificate": {
        "apply_link": "https://www.startupindia.gov.in/content/sih/en/startupgov/startup-recognition-page.html",
        "information_link": "https://www.startupindia.gov.in/",
        "issuing_authority": "Department for Promotion of Industry and Internal Trade (DPIIT)",
        "application_method": "Online via Startup India Portal.",
        "processing_time_days": "14-21 Days",
        "required_documents": ["Certificate of Incorporation", "Pitch Deck/Website Link", "Details of Directors/Founders"],
        "renewal_required": False # Valid up to 10 years from incorporation
    },
    "GST Certificate": {
        "apply_link": "https://reg.gst.gov.in/registration/",
        "information_link": "https://www.gst.gov.in/",
        "issuing_authority": "CBIC (Central Board of Indirect Taxes and Customs)",
        "application_method": "Online via GST Portal.",
        "processing_time_days": "3-7 Days",
        "required_documents": ["PAN", "Aadhaar", "Proof of Business Address", "Bank Statement/Cancelled Cheque"],
        "renewal_required": False
    }
}

def get_document_recovery_guide(document_name: str) -> Dict[str, Any]:
    """
    Transforms a missing document alert into an actionable Application Guide.
    """
    # Simple matching
    doc_data = None
    matched_name = document_name
    for key, data in DOCUMENT_RECOVERY_KB.items():
        if key.lower() in document_name.lower():
            doc_data = data
            matched_name = key
            break
            
    if not doc_data:
        return {
            "document_name": document_name,
            "error": "Recovery guide not currently available for this document."
        }
        
    return {
        "document_name": matched_name,
        "apply_link": doc_data.get("apply_link", ""),
        "information_link": doc_data.get("information_link", ""),
        "issuing_authority": doc_data.get("issuing_authority", ""),
        "application_method": doc_data.get("application_method", ""),
        "processing_time_days": doc_data.get("processing_time_days", ""),
        "required_documents": doc_data.get("required_documents", []),
        "renewal_required": doc_data.get("renewal_required", False)
    }
