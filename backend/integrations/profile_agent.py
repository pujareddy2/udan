import json
import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ValidationError

# Absolute import as requested
from backend.integrations.llm import call_gemini

class ProfileModel(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    category: Optional[str] = None
    state: Optional[str] = None
    qualification: Optional[str] = None
    income: Optional[int] = None
    skills: List[str] = []
    interests: List[str] = []
    documents: List[str] = []
    module: str

def clean_json_string(raw: str) -> str:
    """Removes markdown wrappers like ```json and ```"""
    clean = raw.strip()
    if clean.startswith("```"):
        # Remove first line (e.g. ```json)
        clean = re.sub(r"^```[a-zA-Z]*\n", "", clean)
        # Remove trailing ```
        clean = re.sub(r"\n```$", "", clean)
    return clean.strip()

def parse_profile(text: str, module: str, lang: str = "en") -> Optional[Dict[str, Any]]:
    prompt = (
        f"You extract a user profile as JSON. Output ONLY valid JSON with keys: "
        f"name, age (int), gender, category (general/OBC/SC/ST/EWS/PwD/women), state, "
        f"qualification, income (int annual rupees), skills (array), interests (array). "
        f"Use null if unknown. User (language={lang}) said: {text}"
    )

    llm_response = call_gemini(prompt)
    if not llm_response:
        return None

    try:
        clean_text = clean_json_string(llm_response)
        parsed_dict = json.loads(clean_text)
        
        # Inject the strictly required module field
        parsed_dict["module"] = module
        
        # Validate through Pydantic to ensure types are strictly cast
        validated_profile = ProfileModel(**parsed_dict)
        return validated_profile.model_dump()
        
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Profile Parsing Failed: {e}")
        return None

def profile_from_form(form: Dict[str, Any], module: str) -> Dict[str, Any]:
    """
    Fallback method that extracts and validates raw form data into a strictly typed dictionary.
    """
    form_data = {
        "name": form.get("name"),
        "age": int(form.get("age")) if form.get("age") else None,
        "gender": form.get("gender"),
        "category": form.get("category"),
        "state": form.get("state"),
        "qualification": form.get("qualification"),
        "income": int(form.get("income")) if form.get("income") else None,
        "skills": form.get("skills", []),
        "interests": form.get("interests", []),
        "documents": form.get("documents", []),
        "module": module
    }
    
    # Ensure lists are actually lists
    for list_field in ["skills", "interests", "documents"]:
        if isinstance(form_data[list_field], str):
            # If comma-separated string, split it
            form_data[list_field] = [s.strip() for s in form_data[list_field].split(",") if s.strip()]
            
    try:
        validated_profile = ProfileModel(**form_data)
        return validated_profile.model_dump()
    except ValidationError as e:
        print(f"Form Validation Failed: {e}")
        # Return base model with just module if parsing completely fails
        return ProfileModel(module=module).model_dump()
