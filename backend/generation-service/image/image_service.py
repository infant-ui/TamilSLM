import os
import requests
import time
import base64
import uuid
from datetime import datetime

from .text_overlay import add_legend_to_image

# Load env vars
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_API_URL = os.environ.get("NVIDIA_API_URL", "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.2-klein-4b")

# Path relative to backend/generation-service/
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
IMAGES_BASE_DIR = os.path.join(BASE_DIR, "generated-images")

def get_today_image_dir() -> str:
    """Returns the path to today's image directory (YYYY/MM/DD/), creating it if needed."""
    now = datetime.now()
    year_month_day = os.path.join(str(now.year), f"{now.month:02d}", f"{now.day:02d}")
    dir_path = os.path.join(IMAGES_BASE_DIR, year_month_day)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def generate_image(prompt: str, labels: list[str] = None) -> str:
    """
    Calls the NVIDIA API with exponential backoff (max 3 retries).
    Saves the image to the dated directory and returns the absolute path.
    Applies Tamil text overlay if labels are provided.
    """
    if not NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY environment variable is not set.")

    payload = {
        "prompt": prompt,
        "height": 1024,
        "width": 1024,
        "cfg_scale": 1.0,
        "samples": 1,
        "seed": 0,
        "steps": 4
    }
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Exponential backoff parameters
    max_retries = 3
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = requests.post(NVIDIA_API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            b64_data = data.get("artifacts", [])[0].get("base64", "")
            
            if not b64_data:
                raise ValueError("NIM API returned an empty or invalid base64 response")
                
            # Decode and save
            image_bytes = base64.b64decode(b64_data)
            filename = f"{uuid.uuid4().hex}.png"
            save_path = os.path.join(get_today_image_dir(), filename)
            
            with open(save_path, "wb") as f:
                f.write(image_bytes)
                
            # Add Tamil label overlay if labels exist
            if labels:
                save_path = add_legend_to_image(save_path, labels)
                
            return save_path
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed to generate image after {max_retries} attempts. Final error: {e}")
                raise e
            time.sleep(base_delay * (2 ** attempt))
