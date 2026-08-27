import os
import csv
import json
import requests
from typing import Dict, List

# Configurable via GLOSSARY_PATH so this works both in local dev on this machine and
# inside the Linux Docker image, where the old hardcoded "d:\..." path never existed --
# it was silently failing to load (see load_glossary()) with no error or log line.
# Defaults to a path relative to the repo root (three levels up from this file:
# backend/generation-service/image/ -> repo root), matching where the file actually
# lives in this project.
_DEFAULT_GLOSSARY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "glossary_all_classes.csv"))
GLOSSARY_PATH = os.environ.get("GLOSSARY_PATH", _DEFAULT_GLOSSARY_PATH)
OLLAMA_API_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/api/chat"
OLLAMA_MODEL = "qwen2.5:7b-instruct-q4_k_m"

# Load glossary into memory on startup
glossary_en_to_ta: Dict[str, str] = {}
glossary_ta_to_en: Dict[str, str] = {}

def load_glossary():
    if not os.path.exists(GLOSSARY_PATH):
        print(f"⚠️ Glossary file not found at {GLOSSARY_PATH}. Image labels will fall back to English only. "
              f"Set the GLOSSARY_PATH environment variable if the CSV lives elsewhere.")
        return
    with open(GLOSSARY_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            en = row.get("English_Term", "").strip().lower()
            ta = row.get("Tamil_Term", "").strip()
            if en and ta:
                glossary_en_to_ta[en] = ta
                glossary_ta_to_en[ta] = en

load_glossary()

def enhance_prompt(user_prompt: str, medium: str) -> tuple[str, list[str], str, str]:
    """
    Enhances the prompt for Education Mode using Ollama.
    medium: 'tamil' or 'english'
    Returns: (enhanced_prompt, list_of_labels, subject, language)
    """
    
    system_instruction = f"""
    You are an expert intent extractor for an educational image generation model. 
    Your job is to analyze a student's brief request and extract:
    1. The core anatomical or scientific 'subject' (e.g., "human heart", "human eye", "plant cell"). This should be in English and standardized.
    2. The list of distinct anatomical labels to show on this diagram, in English.

    Output strictly as a JSON object with two keys:
    - "subject": The core subject in English (e.g., "human heart").
    - "labels": A JSON array of strings containing the text labels in English.
    """

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Student request: {user_prompt}"}
        ],
        "options": {"temperature": 0.1},
        "format": "json",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "").strip()
        parsed = json.loads(content)
        
        subject = parsed.get("subject", "educational diagram").lower()
        english_labels = parsed.get("labels", [])
        
        # Determine target language
        language = "bilingual" if medium.lower() not in ["tamil", "english"] else medium.lower()
        
        # Translate labels deterministically
        labels = []
        for eng in english_labels:
            eng_lower = eng.lower()
            tamil_term = glossary_en_to_ta.get(eng_lower)
            
            if not tamil_term:
                # Try partial match if exact match fails
                for e_key, t_val in glossary_en_to_ta.items():
                    if e_key in eng_lower or eng_lower in e_key:
                        tamil_term = t_val
                        break
                        
            if language == "tamil" and tamil_term:
                labels.append(tamil_term)
            elif language == "bilingual" and tamil_term:
                labels.append(f"{tamil_term} ({eng})")
            else:
                labels.append(eng)
        
        # Part B: Fix the "plant cell" subject prompt to avoid whole-plant ambiguity
        if subject == "plant cell":
            subject_prompt = "cross-section diagram of a single plant cell showing internal organelles, biology textbook microscope-view style"
        elif subject == "animal cell":
            # Flagging animal cell as another potential risk for similar ambiguity
            subject_prompt = "cross-section diagram of a single animal cell showing internal organelles, biology textbook microscope-view style"
        else:
            subject_prompt = subject

        # Format the explicit Flux template, removing the contradictory "labeled" word
        enhanced = f"Anatomical diagram of {subject_prompt}, clean line-art medical illustration style, clearly showing distinct regions and structures, NO TEXT, NO LABELS, NO WRITING, NO NUMBERS, plain white background, high contrast outlines suitable for adding external labels and leader lines"
        
        return enhanced, labels, subject, language
    except Exception as e:
        print(f"Error enhancing prompt: {e}")
        # Fallback to original without labels
        enhanced = f"Anatomical diagram based on {user_prompt}, clean line-art medical illustration style, NO TEXT, NO LABELS, NO WRITING, NO NUMBERS, plain white background"
        return enhanced, [], "unknown", "bilingual"
