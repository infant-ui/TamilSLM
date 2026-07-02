import os
import csv
import json
import requests
from typing import Dict, List

GLOSSARY_PATH = r"d:\Project Assistan\glossary_all_classes.csv"
OLLAMA_API_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/api/chat"
OLLAMA_MODEL = "qwen2.5:7b-instruct-q4_k_m"

# Load glossary into memory on startup
glossary_en_to_ta: Dict[str, str] = {}
glossary_ta_to_en: Dict[str, str] = {}

def load_glossary():
    if not os.path.exists(GLOSSARY_PATH):
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

def enhance_prompt(user_prompt: str, medium: str) -> tuple[str, list[str]]:
    """
    Enhances the prompt for Education Mode using Ollama.
    medium: 'tamil' or 'english'
    Returns: (enhanced_prompt, list_of_labels)
    """
    
    prompt_words = user_prompt.lower().split()
    relevant_terms = []
    
    # Heuristic match
    if medium.lower() == "tamil":
        for en, ta in glossary_en_to_ta.items():
            if en in user_prompt.lower() or ta in user_prompt:
                relevant_terms.append(f"{ta} (Tamil for {en})")
    else:
        for ta, en in glossary_ta_to_en.items():
            if ta in user_prompt or en in user_prompt.lower():
                relevant_terms.append(f"{en}")
                
    glossary_context = ""
    if relevant_terms:
        glossary_context = "Relevant terminology for labels based on the prompt:\n" + "\n".join(relevant_terms)
        
    system_instruction = f"""
    You are an expert prompt engineer for an educational image generation model. 
    Your job is to take a student's brief request and expand it into a detailed, highly descriptive prompt 
    suitable for a diffusion model (like FLUX or Stable Diffusion).
    
    The image must be strictly educational:
    - Samacheer Kalvi (Tamil Nadu State Board) textbook style
    - Appropriate for Grades 6-8
    - Child-friendly, clean background (e.g., solid white or pastel)
    - Styled as a scientific diagram, math figure, or educational poster
    
    CRITICAL: 
    1. The diffusion model CANNOT render text or labels itself without garbling them.
    2. Therefore, your enhanced prompt MUST explicitly instruct the model to create an "unlabeled" or "blank" diagram without any text, letters, or labels.
    3. You will separately provide a list of labels in {medium.upper()} language that need to be overlaid later.
    
    {glossary_context}
    
    Output strictly as a JSON object with two keys:
    - "enhanced_prompt": The vivid image generation prompt in English, explicitly stating NO text/labels in the image.
    - "labels": A JSON array of strings containing the text labels in {medium.upper()} language.
    """

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Student request: {user_prompt}"}
        ],
        "options": {"temperature": 0.3},
        "format": "json",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "").strip()
        parsed = json.loads(content)
        
        enhanced = parsed.get("enhanced_prompt", user_prompt)
        labels = parsed.get("labels", [])
        return enhanced, labels
    except Exception as e:
        print(f"Error enhancing prompt: {e}")
        return user_prompt, [] # Fallback to original without labels
