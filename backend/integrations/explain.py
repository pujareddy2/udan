import json
import re
from typing import Dict, Any

from backend.integrations.llm import call_gemini

# Language map
LANG_MAP = {
    "te": "Telugu",
    "hi": "Hindi",
    "en": "English"
}

def clean_json_array(raw: str) -> str:
    """Removes markdown wrappers like ```json and ```"""
    clean = raw.strip()
    clean = re.sub(r"^```(?:json)?\s*", "", clean)
    clean = re.sub(r"\s*```$", "", clean)
    return clean.strip()

def explain(engine_result: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
    """
    Translates the eligibility reasons into simple sentences in the target language.
    """
    # Create a copy to avoid mutating the original input dictionary
    result = engine_result.copy()
    original_reasons = result.get("reasons", [])
    
    # If there are no reasons or language is English (and we don't need translation), 
    # we can just pass through, though prompt asks to translate even to English for simplicity.
    if not original_reasons:
        result["reasons_plain"] = []
        return result

    lang_name = LANG_MAP.get(language, "English")
    
    prompt = (
        f"You are a translator. Translate and rewrite each sentence in the following input list "
        f"into exactly ONE simple sentence in {lang_name} (language code: {language}). "
        f"Keep the meaning and any numbers exactly the same. Do not combine sentences. "
        f"Output ONLY a valid JSON array of strings containing the translated sentences in the same order.\n\n"
        f"Input: {json.dumps(original_reasons)}"
    )

    llm_response = call_gemini(prompt)
    
    if llm_response:
        try:
            clean_text = clean_json_array(llm_response)
            translated_reasons = json.loads(clean_text)
            
            # Basic validation: ensure it's a list and matches the length
            if isinstance(translated_reasons, list) and len(translated_reasons) == len(original_reasons):
                result["reasons_plain"] = translated_reasons
                return result
        except json.JSONDecodeError as e:
            print(f"Explanation Translation Failed: {e}")

    # Fallback to the original reasons if LLM fails, network fails, or validation fails
    result["reasons_plain"] = original_reasons
    return result
