import os
import sys
import json
import secrets
import requests
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.concurrency import run_in_threadpool
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

class GenerateVerifiedRequest(BaseModel):
    query: str
    context: str
    language: str
    history_summary: str = ""
    system_prompt: Optional[str] = None
    # Phase 4, step 3: post-generation verification as a live guardrail. False by default
    # -- see the module-level comment above generate_verified() for why this is NOT wired
    # into /generate/stream's default path.
    verify: bool = False
    key_facts: list = []
    judge_model: Optional[str] = None
    verify_threshold: float = 3.0
    # Next-best retrieved context (e.g. the retrieval-service caller's rank-4..6 chunks,
    # not used in the primary top_k) for the ONE allowed retry when verification scores low.
    alt_context: Optional[str] = None

app = FastAPI()

# ── CORS: restrict to configured origin(s) instead of allowing any origin ──
# Set ALLOWED_ORIGINS to a comma-separated list in production (e.g. the gateway's
# and/or frontend's URL). Defaults to local dev origins only.
_allowed_origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/api/chat")
# Overridable so the SAME pipeline (retrieval + prompt template + this service)
# can be re-run against a different generation model for comparison evals
# (e.g. OLLAMA_MODEL=tamil-llama-7b-instruct-v0.2 or OLLAMA_MODEL=sarvam-m),
# without touching code -- restart this service with the env var set.
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct-q4_k_m")
# Context window sent to Ollama. Default 4096 (unchanged). A prompt longer than this is SILENTLY
# truncated by Ollama's own engine (only the last ~half window is kept, dropping the instruction
# block at the start of the system prompt), so long Tamil-script prompts need it raised, e.g.
# OLLAMA_NUM_CTX=12000 for Qwen2.5 (Tamil-context prompts run to ~10.7K tokens with its tokenizer).
OLLAMA_NUM_CTX = int(os.environ.get("OLLAMA_NUM_CTX", "4096"))

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

def assemble_system_prompt(system_prompt: Optional[str], context: str, language: str, history_summary: str) -> str:
    """Single source of truth for system-prompt assembly, used by both /generate/stream
    and /generate/verified so the verified path is judging the SAME prompt a real request
    would get, not a reimplementation of it."""
    if system_prompt:
        out = system_prompt
        if "Textbook Context" not in out and "பாடப் புத்தகப் பகுதி" not in out:
            if language.lower() == "tamil":
                out = f"{out}\n\nபாடப் புத்தகப் பகுதி (Textbook Context):\n{context}"
            else:
                out = f"{out}\n\nTextbook Context:\n{context}"
        if history_summary:
            out = f"{out}\n\nConversation Summary:\n{history_summary}"
        return out
    return get_system_prompt(language, context, history_summary)


@app.post("/generate/stream")
async def generate_stream(req: GenerateStreamRequest):
    system_prompt = assemble_system_prompt(req.system_prompt, req.context, req.language, req.history_summary)

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
            "num_ctx": OLLAMA_NUM_CTX
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
                        event = {'token': token}
                        if data.get("done"):
                            # Final Ollama chunk: expose what was ACTUALLY evaluated so callers can
                            # detect silent prompt truncation (prompt_eval_count << true prompt length).
                            event.update({
                                'done': True,
                                'prompt_eval_count': data.get('prompt_eval_count'),
                                'eval_count': data.get('eval_count'),
                                'done_reason': data.get('done_reason'),
                                'num_ctx': OLLAMA_NUM_CTX,
                            })
                        # Yield in standard Server-Sent Events structure
                        yield f"data: {json.dumps(event)}\n\n"
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.RequestException as re:
            yield f"data: {json.dumps({'error': f'Failed to query local Ollama: {str(re)}'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# Phase 4, step 3: post-generation verification as a live guardrail.
#
# This is a NEW, separate, non-streaming endpoint -- NOT a change to /generate/stream's
# default behaviour. Verification needs the full answer text before it can be judged, which
# is fundamentally incompatible with token-by-token SSE streaming to the client; bolting it
# onto the streaming path would mean either buffering every answer before the user sees
# anything (defeating the point of streaming) or judging after the fact and being unable to
# act on a bad score. /generate/stream is therefore left exactly as it was. Whether THIS
# endpoint should become the gateway's default path is an open question gated on the
# latency numbers in evaluate_agentic.py -- see that script's docstring and the Phase 4
# report for the actual measured cost of verify=True before deciding.
#
# judge_answer() is imported directly from evaluate_generation.py (not reimplemented here),
# per the explicit Phase 4 instruction to reuse the SAME function used for offline eval --
# an online answer is judged by identical logic to an offline one, and a change to the
# rubric only ever needs to happen in one place.
# ---------------------------------------------------------------------------
import importlib.util as _importlib_util

_EVAL_GEN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                               "evaluation", "scripts", "evaluate_generation.py")
_judge_module = None


def _load_judge_module():
    global _judge_module
    if _judge_module is None:
        spec = _importlib_util.spec_from_file_location("evaluate_generation_judge", os.path.abspath(_EVAL_GEN_PATH))
        mod = _importlib_util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _judge_module = mod
    return _judge_module


def _composite_judge_score(judgement: dict) -> Optional[float]:
    """Mean of the three dimensions most directly about 'is this answer trustworthy to
    show as-is': correctness, groundedness, faithfulness. (Not all 7 rubric dimensions --
    e.g. language_quality/educational_suitability are about polish, not whether the
    answer should be retried or flagged.) None if the judge call itself failed/was invalid
    (distinct from a low score: a failed judge call should not silently pass verification)."""
    if not isinstance(judgement, dict):
        return None
    if judgement.get("_judge_call_failed") or judgement.get("_judge_parse_error") or judgement.get("_judge_invalid"):
        return None
    keys = ("correctness", "groundedness", "faithfulness")
    if not all(k in judgement for k in keys):
        return None
    return sum(judgement[k] for k in keys) / len(keys)


def _call_ollama_chat_blocking(model: str, system_prompt: str, query: str) -> str:
    """Non-streaming equivalent of /generate/stream's Ollama call, for verification (which
    needs the complete answer text to judge, not a token stream)."""
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
        "options": {"temperature": 0.2, "num_predict": 1000, "num_ctx": OLLAMA_NUM_CTX},
        "stream": False,
    }
    # 1800s read timeout: this machine's concurrent unrelated load (other apps observed
    # competing for CPU during this eval) pushed single calls past even 900s intermittently
    # (see evaluate_agentic.py's hardware-load caveat), and unlike judge_answer() below, a
    # plain Ollama generation call has no built-in retry -- one timeout here is fatal.
    r = requests.post(OLLAMA_API_URL, json=payload, timeout=(5, 1800))
    r.raise_for_status()
    return r.json().get("message", {}).get("content", "")


@app.post("/generate/verified")
async def generate_verified(req: GenerateVerifiedRequest):
    import time
    t0 = time.time()
    system_prompt = assemble_system_prompt(req.system_prompt, req.context, req.language, req.history_summary)
    answer = await run_in_threadpool(_call_ollama_chat_blocking, OLLAMA_MODEL, system_prompt, req.query)
    gen_latency_ms = (time.time() - t0) * 1000

    out = {
        "answer": answer, "verify_used": req.verify,
        "gen_latency_ms": gen_latency_ms, "judge_latency_ms": None, "retry_latency_ms": None,
        "judge": None, "composite_score": None, "retried_with_alt_context": False,
        "low_confidence_flag": False,
    }
    if not req.verify or not answer.strip():
        out["total_latency_ms"] = gen_latency_ms
        return out

    judge_mod = _load_judge_module()
    judge_model = req.judge_model or judge_mod.pick_judge_model(None)
    t1 = time.time()
    # timeout_s=600, not judge_answer's own 240s default: under this machine's measured
    # load a single call often exceeds 240s on the first attempt anyway (see the
    # generation-timeout comment above), so the lower default just burns one guaranteed
    # retry instead of usually succeeding on the first attempt.
    judgement = await run_in_threadpool(judge_mod.judge_answer, judge_model, req.query, req.context, answer,
                                         req.key_facts, 2, 1800)
    judge_latency_ms = (time.time() - t1) * 1000
    score = _composite_judge_score(judgement)
    out.update(judge=judgement, judge_latency_ms=judge_latency_ms, composite_score=score)

    if score is not None and score < req.verify_threshold:
        if req.alt_context:
            t2 = time.time()
            alt_system_prompt = assemble_system_prompt(req.system_prompt, req.alt_context, req.language, req.history_summary)
            retry_answer = await run_in_threadpool(_call_ollama_chat_blocking, OLLAMA_MODEL, alt_system_prompt, req.query)
            retry_latency_ms = (time.time() - t2) * 1000
            out.update(answer=retry_answer, retried_with_alt_context=True, retry_latency_ms=retry_latency_ms)
            # Capped at ONE retry (explicit Phase 4 instruction): the retried answer is NOT
            # re-judged -- that would double the judge cost again for an open-ended loop.
            # It is served as-is, flagged so the caller knows a retry happened.
        else:
            out["low_confidence_flag"] = True

    out["total_latency_ms"] = (time.time() - t0) * 1000
    return out


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

# --- Image Generation Integration ---
import time
from image.db import get_cached_image, log_image_generation
from image.safety_checker import is_safe_prompt
from image.prompt_enhancer import enhance_prompt
from image.image_service import generate_image

# ── SECURITY: Admin key gating /generate/image ──
# No hardcoded fallback value. If GENERATION_ADMIN_KEY isn't set in the environment,
# we generate a random per-process secret instead of using a fixed, publicly-known
# string -- this keeps the service usable for ad-hoc local testing without ever
# shipping a "default" credential that would also work in someone else's deployment.
_env_admin_key = os.environ.get("GENERATION_ADMIN_KEY", "").strip()
if not _env_admin_key:
    _env_admin_key = secrets.token_urlsafe(32)
    print(f"⚠️ GENERATION_ADMIN_KEY not set. Generated a random per-process admin key for this run: {_env_admin_key}")
    print("⚠️ Set GENERATION_ADMIN_KEY in the environment for a stable key across restarts/deployments.")

GENERATION_ADMIN_KEYS = {
    _env_admin_key: "Admin"
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
    enhanced, labels, subject, language = enhance_prompt(req.prompt, req.medium)

    # 4. Generate Image
    # NOTE: generate_image() performs blocking network I/O (requests.post, up to 3
    # retries) -- run it in FastAPI's threadpool so it doesn't block the event loop
    # and stall every other concurrent request to this service.
    try:
        image_path = await run_in_threadpool(generate_image, enhanced, labels, subject, language)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
