import requests
import os

OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/api/chat")
OLLAMA_MODEL = "qwen2.5:7b-instruct-q4_k_m"

# Basic keyword blocklist for immediate rejection (removed 'blood' for anatomy compatibility)
BLOCKLIST = ["violent", "kill", "naked", "porn", "weapon", "bomb", "hate"]

def is_safe_prompt(user_prompt: str) -> bool:
    """
    Validates if the user prompt is safe and educational.
    Returns True if safe, False if rejected.
    """
    prompt_lower = user_prompt.lower()
    
    # 1. Quick Keyword check
    if any(bad_word in prompt_lower for bad_word in BLOCKLIST):
        return False
        
    # 2. LLM-based Safety Check
    system_instruction = """
    You are an educational content moderator for a middle school platform (Grades 6-8).
    Your task is to determine if a student's image generation request is appropriate and educational.
    If the prompt asks for anything unsafe, harmful, sexually explicit, hateful, or completely off-topic from school subjects, reply with "REJECT".
    If it is a safe, educational, or harmless creative request (like a science diagram, math shape, historical figure, or cute animal), reply with "APPROVE".
    Reply ONLY with the word "APPROVE" or "REJECT". Do not provide explanations.
    """
    
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        "options": {"temperature": 0.0},
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json().get("message", {}).get("content", "").strip().upper()
        if "REJECT" in result:
            return False
        return True
    except Exception as e:
        # Fail closed or open? Since it's for minors, fail closed if API is unreachable,
        # but for robustness during testing we can just log.
        print(f"Safety check failed, defaulting to False: {e}")
        return False
