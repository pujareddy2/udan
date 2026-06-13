import json
from typing import List, Optional

from backend.integrations.llm import call_gemini
from backend.integrations.profile_agent import clean_and_parse_json


def explain(engine_result: dict, language: str = "en") -> dict:
    """
    Takes an EngineResult and rewrites each reason into ONE simple sentence
    in the specified language (te/hi/en) using Gemini.

    Returns a dictionary with:
    {verdict, reasons_plain[], missing_documents, missing_skills, readiness}

    If call_gemini fails or returns None, falls back to using original reasons.
    """
    # Extract original fields
    verdict = engine_result.get("verdict")
    reasons = engine_result.get("reasons", [])
    missing_documents = engine_result.get("missing_documents", [])
    missing_skills = engine_result.get("missing_skills", [])
    readiness = engine_result.get("readiness")

    # If no reasons to translate, return early
    if not reasons:
        return {
            "verdict": verdict,
            "reasons_plain": [],
            "missing_documents": missing_documents,
            "missing_skills": missing_skills,
            "readiness": readiness
        }

    # Language mapping for the prompt context
    lang_names = {
        "en": "English",
        "te": "Telugu",
        "hi": "Hindi"
    }
    target_lang_name = lang_names.get(language, "English")

    # Construct translation prompt
    prompt = (
        f"You are a translator. Translate and rewrite each sentence in the following input list "
        f"into exactly ONE simple sentence in {target_lang_name} (language code: {language}). "
        "Keep the meaning and any numbers exactly the same. Do not combine sentences.\n"
        f"Input list:\n{json.dumps(reasons)}\n\n"
        "Output ONLY a valid JSON array of strings containing the translated sentences in the same order. "
        "Do not output markdown code blocks unless it is json, and do not write any additional explanation or chat."
    )

    reasons_plain = list(reasons)  # Default fallback

    response_text = call_gemini(prompt)
    if response_text:
        try:
            parsed = clean_and_parse_json(response_text)
            if isinstance(parsed, list) and len(parsed) == len(reasons):
                # Ensure all items are strings
                reasons_plain = [str(item) for item in parsed]
        except Exception:
            # Fall back to original reasons on any error
            pass

    return {
        "verdict": verdict,
        "reasons_plain": reasons_plain,
        "missing_documents": missing_documents,
        "missing_skills": missing_skills,
        "readiness": readiness
    }
