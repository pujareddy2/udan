import json
import re
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError

from backend.integrations.llm import call_gemini


class ProfileModel(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    category: Optional[str] = None
    state: Optional[str] = None
    qualification: Optional[str] = None
    income: Optional[int] = None
    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    documents: List[str] = Field(default_factory=list)
    module: str


def clean_and_parse_json(text: str) -> dict:
    """
    Cleans up LLM markdown block wrappers (if any) and parses the response as JSON.
    """
    if not text:
        raise ValueError("Empty text input")

    cleaned = text.strip()
    # Handle markdown code blocks
    pattern = r"```(?:json)?\s*(.*?)\s*```"
    match = re.search(pattern, cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1).strip()

    return json.loads(cleaned)


def parse_profile(text: str, module: str, lang: str = "en") -> Optional[dict]:
    """
    Calls Gemini to extract the profile from input text, parses it, and validates it.
    Returns None on any failure.
    """
    prompt = (
        "You extract a user profile as JSON. Output ONLY valid JSON with keys: name, age (int), gender, "
        "category (general/OBC/SC/ST/EWS/PwD/women), state, qualification, income (int annual rupees), "
        "skills (array), interests (array). Use null if unknown. "
        f"User (language={lang}) said: {text}"
    )

    response_text = call_gemini(prompt)
    if not response_text:
        return None

    try:
        extracted_data = clean_and_parse_json(response_text)
        if not isinstance(extracted_data, dict):
            return None

        # Add module to the extracted dictionary
        extracted_data["module"] = module

        # Ensure array fields are not None
        if "skills" not in extracted_data or extracted_data["skills"] is None:
            extracted_data["skills"] = []
        if "interests" not in extracted_data or extracted_data["interests"] is None:
            extracted_data["interests"] = []
        if "documents" not in extracted_data or extracted_data["documents"] is None:
            extracted_data["documents"] = []

        # Validate with Pydantic
        model = ProfileModel(**extracted_data)

        if hasattr(model, "model_dump"):
            return model.model_dump()
        return model.dict()
    except Exception:
        return None


def profile_from_form(form: dict, module: str) -> dict:
    """
    Constructs and validates a Profile dict from raw form input dictionary.
    """
    skills = form.get("skills")
    if not isinstance(skills, list):
        skills = [skills] if skills else []

    interests = form.get("interests")
    if not isinstance(interests, list):
        interests = [interests] if interests else []

    documents = form.get("documents")
    if not isinstance(documents, list):
        documents = [documents] if documents else []

    age = form.get("age")
    if age is not None:
        try:
            age = int(age)
        except (ValueError, TypeError):
            age = None

    income = form.get("income")
    if income is not None:
        try:
            income = int(income)
        except (ValueError, TypeError):
            income = None

    profile_data = {
        "name": form.get("name"),
        "age": age,
        "gender": form.get("gender"),
        "category": form.get("category"),
        "state": form.get("state"),
        "qualification": form.get("qualification"),
        "income": income,
        "skills": skills,
        "interests": interests,
        "documents": documents,
        "module": module
    }

    model = ProfileModel(**profile_data)

    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
