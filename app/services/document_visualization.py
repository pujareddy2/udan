from typing import Dict, Any

# Mock Database of Document Visuals (To be replaced with SQL DB queries)
DOCUMENT_VISUALS_DB = {
    "Income Certificate": {
        "description": "An official proof of your annual family income issued by the state revenue department. Required for almost all scholarships and fee reimbursement schemes.",
        "issuing_authority": "Revenue Department (Tehsildar/Mandal Revenue Officer)",
        "validity": "Usually 1 Year from date of issue",
        "templates": {
            "en": {
                "sample_image_url": "https://cdn.udaan.ai/samples/income_cert_en.png",
                "sample_pdf_url": "https://cdn.udaan.ai/templates/income_cert_blank_en.pdf"
            },
            "te": {
                "sample_image_url": "https://cdn.udaan.ai/samples/income_cert_te.png",
                "sample_pdf_url": "https://cdn.udaan.ai/templates/income_cert_blank_te.pdf"
            },
            "hi": {
                "sample_image_url": "https://cdn.udaan.ai/samples/income_cert_hi.png",
                "sample_pdf_url": "https://cdn.udaan.ai/templates/income_cert_blank_hi.pdf"
            }
        }
    },
    "Caste Certificate": {
        "description": "A documentary proof of a person belonging to a specific caste (SC/ST/OBC). Essential for reservation quotas in education and jobs.",
        "issuing_authority": "Revenue Department",
        "validity": "Usually Lifetime (OBC Non-Creamy Layer may require annual renewal)",
        "templates": {
            "en": {
                "sample_image_url": "https://cdn.udaan.ai/samples/caste_cert_en.png",
                "sample_pdf_url": "https://cdn.udaan.ai/templates/caste_cert_blank.pdf"
            }
        }
    },
    "Land Passbook": {
        "description": "A booklet containing ownership details of agricultural land. Mandatory for farmer subsidies like PM-KISAN.",
        "issuing_authority": "Revenue Department",
        "validity": "Valid until land ownership changes",
        "templates": {
            "en": {
                "sample_image_url": "https://cdn.udaan.ai/samples/pattadar_passbook.png",
                "sample_pdf_url": "https://cdn.udaan.ai/templates/pattadar_passbook.pdf"
            }
        }
    }
}

def get_document_visualization(document_name: str, language_preference: str = "en") -> Dict[str, Any]:
    """
    Returns localized sample images and PDFs for a requested document.
    """
    # Simple matching
    doc_data = None
    for key, data in DOCUMENT_VISUALS_DB.items():
        if key.lower() in document_name.lower():
            doc_data = data
            break
            
    if not doc_data:
        return {
            "document_name": document_name,
            "error": "Visualization not currently available for this document."
        }
        
    templates = doc_data.get("templates", {})
    lang_data = templates.get(language_preference)
    
    # Fallback to english if preferred language template doesn't exist
    if not lang_data and "en" in templates:
        lang_data = templates["en"]
        
    return {
        "document_name": document_name,
        "description": doc_data.get("description", ""),
        "issuing_authority": doc_data.get("issuing_authority", ""),
        "validity": doc_data.get("validity", ""),
        "sample_image_url": lang_data.get("sample_image_url", "") if lang_data else "",
        "sample_pdf_url": lang_data.get("sample_pdf_url", "") if lang_data else "",
        "language_support": list(templates.keys())
    }
