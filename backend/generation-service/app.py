import os
import sys
import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Set UTF-8 encoding for stdout/stderr to prevent charmap encoding errors under Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

class GenerateStreamRequest(BaseModel):
    query: str
    context: str
    language: str
    history_summary: str = ""

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
            f"நீ ஒரு சிறந்த அறிவியல் ஆசிரியர். கொடுக்கப்பட்டுள்ள அறிவியல் பாடப் புத்தகப் பகுதியின் அடிப்படியில் மட்டுமே கேள்விக்கு பதில் அளிக்கவும்.\n"
            f"விவரங்களின் சுருக்கம்: {history_summary}\n"
            f"பாடப் புத்தகப் பகுதி:\n{context}\n\n"
            f"விதிமுறைகள்:\n"
            f"1. உனக்கு தெரிந்த பொது அறிவை பயன்படுத்தாமல், மேலே கொடுக்கப்பட்டுள்ள விவரங்களை மட்டுமே பயன்படுத்தி கேள்விக்கு தமிழில் சுருக்கமாக பதிலளிக்கவும்.\n"
            f"2. பதில் தமிழில் தெளிவாகவும் பிழையின்றியும் இருக்க வேண்டும்."
        )
    else:
        return (
            f"You are a science tutoring assistant. Answer the user's question concisely using only the provided textbook context.\n"
            f"Conversation Summary: {history_summary}\n"
            f"Textbook Context:\n{context}\n\n"
            f"Rules:\n"
            f"1. Rely only on the textbook context provided above. Do not use outside knowledge.\n"
            f"2. Answer the question directly and keep it concise. Use bullet points if helpful."
        )

@app.post("/generate/stream")
async def generate_stream(req: GenerateStreamRequest):
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
            "num_predict": 300,
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
