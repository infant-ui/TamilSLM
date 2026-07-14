import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

# Set UTF-8 encoding for stdout/stderr to prevent charmap encoding errors under Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from typing import Optional

class GenerateStreamRequest(BaseModel):
    query: str
    context: str
    language: str
    history_summary: str = ""
    system_prompt: Optional[str] = None

app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:7b-instruct-q4_k_m"

def get_system_prompt(lang: str, context: str, history_summary: str) -> str:
    if lang.lower() == "tamil":
        return (
            f"நீங்கள் TamilEdu-SLM, ஒரு புத்திசாலித்தனமான கல்வி கற்பிக்கும் AI ஆசிரியர். கொடுக்கப்பட்டுள்ள பாடப்புத்தகப் பகுதியின் அடிப்படையில் மட்டுமே மாணவரின் கேள்விக்கு எளிய தமிழில் விளக்கவும்.\n"
            f"உரையாடல் சுருக்கம்: {history_summary}\n"
            f"பாடப் புத்தகப் பகுதி:\n{context}\n\n"
            f"விதிமுறைகள்:\n"
            f"1. உனக்கு தெரிந்த பொது அறிவை பயன்படுத்தாமல், மேலே கொடுக்கப்பட்டுள்ள விவரங்களை மட்டுமே பயன்படுத்தி கேள்விக்குத் தமிழில் படிப்படியாக பதிலளிக்கவும்.\n"
            f"2. பதில் தமிழில் தெளிவாகவும், நேர்த்தியாகவும், பிழையின்றியும் இருக்க வேண்டும்."
        )
    else:
        return (
            f"You are TamilEdu-SLM, an intelligent educational AI tutor. Answer the student's question concisely using only the provided textbook context.\n"
            f"Conversation Summary: {history_summary}\n"
            f"Textbook Context:\n{context}\n\n"
            f"Rules:\n"
            f"1. Rely only on the textbook context provided above. Do not use outside knowledge.\n"
            f"2. Explain concepts step by step in simple, age-appropriate language."
        )

@app.post("/generate/stream")
async def generate_stream(req: GenerateStreamRequest):
    if req.system_prompt:
        system_prompt = req.system_prompt
        # Safe check: if context text is missing from the incoming system_prompt, append it
        if "Textbook Context" not in system_prompt and "பாடப் புத்தகப் பகுதி" not in system_prompt:
            if req.language.lower() == "tamil":
                system_prompt = f"{system_prompt}\n\nபாடப் புத்தகப் பகுதி (Textbook Context):\n{req.context}"
            else:
                system_prompt = f"{system_prompt}\n\nTextbook Context:\n{req.context}"
        
        # Append history summary if provided
        if req.history_summary:
            system_prompt = f"{system_prompt}\n\nConversation Summary:\n{req.history_summary}"
    else:
        system_prompt = get_system_prompt(req.language, req.context, req.history_summary)
    
    # Use unified Ollama model configured globally
    model = OLLAMA_MODEL
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": req.query}
        ],
        "options": {
            "temperature": 0.2,
            "num_predict": 1000,
            "num_ctx": 4096
        },
        "stream": True
    }
    
    def event_generator():
        try:
            # Set a connection timeout but allow infinite stream reading
            response = requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=(5, None))
            if response.status_code != 200:
                error_msg = f"Ollama returned status code {response.status_code}"
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
                return
                
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    try:
                        data = json.loads(decoded)
                        token = data.get("message", {}).get("content", "")
                        # Yield in standard Server-Sent Events structure
                        yield f"data: {json.dumps({'token': token})}\n\n"
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.RequestException as re:
            yield f"data: {json.dumps({'error': f'Failed to query local Ollama: {str(re)}'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/summarize-session")
async def summarize_session(history_text: str):
    # Endpoint to generate rolling summary of older conversation
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": "Summarize the key scientific questions and core concepts discussed in this student-teacher session. Keep the summary under 100 words."
            },
            {"role": "user", "content": history_text}
        ],
        "options": {"temperature": 0.1, "num_predict": 128},
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        if response.status_code == 200:
            return {"summary": response.json().get("message", {}).get("content", "").strip()}
        else:
            raise HTTPException(status_code=500, detail="Failed to call Ollama for summarization")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

# --- Image Generation Integration ---
import time
from image.db import get_cached_image, log_image_generation
from image.safety_checker import is_safe_prompt
from image.prompt_enhancer import enhance_prompt
from image.image_service import generate_image

GENERATION_ADMIN_KEYS = {
    os.environ.get("GENERATION_ADMIN_KEY", "dev-generation-secret-key-123"): "Admin"
}

def verify_generation_admin_key(x_generation_service_admin_key: str = Header(None)):
    if not x_generation_service_admin_key or x_generation_service_admin_key not in GENERATION_ADMIN_KEYS:
        raise HTTPException(status_code=401, detail="Unauthorized - Invalid or missing admin key")
    return GENERATION_ADMIN_KEYS[x_generation_service_admin_key]

class ImageGenerateRequest(BaseModel):
    prompt: str
    medium: str = "english"

@app.post("/generate/image")
async def generate_image_endpoint(req: ImageGenerateRequest, user: str = Depends(verify_generation_admin_key)):
    start_time = time.time()
    
    # 1. Safety Check
    if not is_safe_prompt(req.prompt):
        log_image_generation(req.prompt, "", req.medium, "", int((time.time() - start_time) * 1000), "rejected_safety")
        raise HTTPException(status_code=400, detail="Prompt rejected for safety or irrelevance.")
        
    # 2. Check Cache
    cached_path = get_cached_image(req.prompt, req.medium)
    if cached_path:
        log_image_generation(req.prompt, "", req.medium, cached_path, int((time.time() - start_time) * 1000), "cache_hit")
        return {"success": True, "image_path": cached_path, "cached": True}
        
    # 3. Enhance Prompt
    enhanced, labels = enhance_prompt(req.prompt, req.medium)
    
    # 4. Generate Image
    try:
        # Placeholder for actual generation which is pending NVIDIA schema
        image_path = generate_image(enhanced, labels)
        log_image_generation(req.prompt, enhanced, req.medium, image_path, int((time.time() - start_time) * 1000), "success")
        return {"success": True, "image_path": image_path, "cached": False, "enhanced_prompt": enhanced, "labels": labels}
    except NotImplementedError as e:
        log_image_generation(req.prompt, enhanced, req.medium, "", int((time.time() - start_time) * 1000), "pending_schema")
        return {"success": False, "message": str(e), "enhanced_prompt": enhanced}
    except Exception as e:
        import traceback
        traceback.print_exc()
        log_image_generation(req.prompt, enhanced, req.medium, "", int((time.time() - start_time) * 1000), "error")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")

@app.get("/images/{year}/{month}/{day}/{filename}")
async def serve_generated_image(year: str, month: str, day: str, filename: str):
    file_path = os.path.join(os.path.dirname(__file__), "generated-images", year, month, day, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from typing import Optional

class GenerateStreamRequest(BaseModel):
    query: str
    context: str
    language: str
    history_summary: str = ""
    system_prompt: Optional[str] = None

app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:7b-instruct-q4_k_m"

def get_system_prompt(lang: str, context: str, history_summary: str) -> str:
    if lang.lower() == "tamil":
        return (
            f"நீங்கள் TamilEdu-SLM, ஒரு புத்திசாலித்தனமான கல்வி கற்பிக்கும் AI ஆசிரியர். கொடுக்கப்பட்டுள்ள பாடப்புத்தகப் பகுதியின் அடிப்படையில் மட்டுமே மாணவரின் கேள்விக்கு எளிய தமிழில் விளக்கவும்.\n"
            f"உரையாடல் சுருக்கம்: {history_summary}\n"
            f"பாடப் புத்தகப் பகுதி:\n{context}\n\n"
            f"விதிமுறைகள்:\n"
            f"1. உனக்கு தெரிந்த பொது அறிவை பயன்படுத்தாமல், மேலே கொடுக்கப்பட்டுள்ள விவரங்களை மட்டுமே பயன்படுத்தி கேள்விக்குத் தமிழில் படிப்படியாக பதிலளிக்கவும்.\n"
            f"2. பதில் தமிழில் தெளிவாகவும், நேர்த்தியாகவும், பிழையின்றியும் இருக்க வேண்டும்."
        )
    else:
        return (
            f"You are TamilEdu-SLM, an intelligent educational AI tutor. Answer the student's question concisely using only the provided textbook context.\n"
            f"Conversation Summary: {history_summary}\n"
            f"Textbook Context:\n{context}\n\n"
            f"Rules:\n"
            f"1. Rely only on the textbook context provided above. Do not use outside knowledge.\n"
            f"2. Explain concepts step by step in simple, age-appropriate language."
        )

@app.post("/generate/stream")
async def generate_stream(req: GenerateStreamRequest):
    if req.system_prompt:
        system_prompt = req.system_prompt
        # Safe check: if context text is missing from the incoming system_prompt, append it
        if "Textbook Context" not in system_prompt and "பாடப் புத்தகப் பகுதி" not in system_prompt:
            if req.language.lower() == "tamil":
                system_prompt = f"{system_prompt}\n\nபாடப் புத்தகப் பகுதி (Textbook Context):\n{req.context}"
            else:
                system_prompt = f"{system_prompt}\n\nTextbook Context:\n{req.context}"
        
        # Append history summary if provided
        if req.history_summary:
            system_prompt = f"{system_prompt}\n\nConversation Summary:\n{req.history_summary}"
    else:
        system_prompt = get_system_prompt(req.language, req.context, req.history_summary)
    
    # Use unified Ollama model configured globally
    model = OLLAMA_MODEL
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": req.query}
        ],
        "options": {
            "temperature": 0.2,
            "num_predict": 1000,
            "num_ctx": 4096
        },
        "stream": True
    }
    
    def event_generator():
        try:
            # Set a connection timeout but allow infinite stream reading
            response = requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=(5, None))
            if response.status_code != 200:
                error_msg = f"Ollama returned status code {response.status_code}"
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
                return
                
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    try:
                        data = json.loads(decoded)
                        token = data.get("message", {}).get("content", "")
                        # Yield in standard Server-Sent Events structure
                        yield f"data: {json.dumps({'token': token})}\n\n"
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.RequestException as re:
            yield f"data: {json.dumps({'error': f'Failed to query local Ollama: {str(re)}'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/summarize-session")
async def summarize_session(history_text: str):
    # Endpoint to generate rolling summary of older conversation
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": "Summarize the key scientific questions and core concepts discussed in this student-teacher session. Keep the summary under 100 words."
            },
            {"role": "user", "content": history_text}
        ],
        "options": {"temperature": 0.1, "num_predict": 128},
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        if response.status_code == 200:
            return {"summary": response.json().get("message", {}).get("content", "").strip()}
        else:
            raise HTTPException(status_code=500, detail="Failed to call Ollama for summarization")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

# --- Image Generation Integration ---
import time
from image.db import get_cached_image, log_image_generation
from image.safety_checker import is_safe_prompt
from image.prompt_enhancer import enhance_prompt
from image.image_service import generate_image

GENERATION_ADMIN_KEYS = {
    os.environ.get("GENERATION_ADMIN_KEY", "dev-generation-secret-key-123"): "Admin"
}

def verify_generation_admin_key(x_generation_service_admin_key: str = Header(None)):
    if not x_generation_service_admin_key or x_generation_service_admin_key not in GENERATION_ADMIN_KEYS:
        raise HTTPException(status_code=401, detail="Unauthorized - Invalid or missing admin key")
    return GENERATION_ADMIN_KEYS[x_generation_service_admin_key]

class ImageGenerateRequest(BaseModel):
    prompt: str
    medium: str = "english"

@app.post("/generate/image")
async def generate_image_endpoint(req: ImageGenerateRequest, user: str = Depends(verify_generation_admin_key)):
    start_time = time.time()
    
    # 1. Safety Check
    if not is_safe_prompt(req.prompt):
        log_image_generation(req.prompt, "", req.medium, "", int((time.time() - start_time) * 1000), "rejected_safety")
        raise HTTPException(status_code=400, detail="Prompt rejected for safety or irrelevance.")
        
    # 2. Check Cache
    cached_path = get_cached_image(req.prompt, req.medium)
    if cached_path:
        log_image_generation(req.prompt, "", req.medium, cached_path, int((time.time() - start_time) * 1000), "cache_hit")
        return {"success": True, "image_path": cached_path, "cached": True}
        
    # 3. Enhance Prompt
    enhanced, labels = enhance_prompt(req.prompt, req.medium)
    
    # 4. Generate Image
    try:
        # Placeholder for actual generation which is pending NVIDIA schema
        image_path = generate_image(enhanced, labels)
        log_image_generation(req.prompt, enhanced, req.medium, image_path, int((time.time() - start_time) * 1000), "success")
        return {"success": True, "image_path": image_path, "cached": False, "enhanced_prompt": enhanced, "labels": labels}
    except NotImplementedError as e:
        log_image_generation(req.prompt, enhanced, req.medium, "", int((time.time() - start_time) * 1000), "pending_schema")
        return {"success": False, "message": str(e), "enhanced_prompt": enhanced}
    except Exception as e:
        import traceback
        traceback.print_exc()
        log_image_generation(req.prompt, enhanced, req.medium, "", int((time.time() - start_time) * 1000), "error")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")

@app.get("/images/{year}/{month}/{day}/{filename}")
async def serve_generated_image(year: str, month: str, day: str, filename: str):
    file_path = os.path.join(os.path.dirname(__file__), "generated-images", year, month, day, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Image not found")

class IntentRequest(BaseModel):
    query: str

@app.post("/router/intent")
async def route_intent(req: IntentRequest):
    # This endpoint is deprecated. Intent routing is now handled via deterministic 
    # keyword classification in the gateway (app.js).
    raise HTTPException(status_code=410, detail="Endpoint deprecated. Intent routing is now handled via deterministic keyword classification in the API Gateway.")
