import os
import time
import secrets
import logging
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import app.db.corrections_db as db

logger = logging.getLogger(__name__)

app = FastAPI(title="Correction Service")

# ── CORS: restrict to configured origin(s) instead of allowing any origin ──
_allowed_origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Admin keys configuration
# NOTE: CORRECTION_ADMIN_KEY is currently a single shared secret.
# The `reviewed_by` field should be understood as "approved using the admin key"
# rather than true per-person accountability.
#
# SECURITY: There is intentionally no hardcoded "test" key that's valid regardless
# of configuration, and no fixed fallback string -- if CORRECTION_ADMIN_KEY isn't
# set, a random per-process secret is generated instead, so nothing here is ever a
# fixed, publicly-known credential.
_env_admin_key = os.environ.get("CORRECTION_ADMIN_KEY", "").strip()
if not _env_admin_key:
    _env_admin_key = secrets.token_urlsafe(32)
    logger.warning(f"CORRECTION_ADMIN_KEY not set. Generated a random per-process admin key for this run: {_env_admin_key}")
    logger.warning("Set CORRECTION_ADMIN_KEY in the environment for a stable key across restarts/deployments.")

ADMIN_KEYS = {
    _env_admin_key: "Super Admin"
}

# Simple in-memory rate limiting for reports
# NOTE: This is in-memory and per-process. If correction-service is run with
# multiple worker processes, the effective rate limit multiplies accordingly.
# If deployed behind a reverse proxy, `request.client.host` will be the proxy's IP
# unless X-Forwarded-For is properly parsed.
report_rate_limits: Dict[str, List[float]] = {}
RATE_LIMIT_MAX_REQUESTS = 5
RATE_LIMIT_WINDOW_SECONDS = 60

class ReportRequest(BaseModel):
    reported_issue_text: str
    reported_by: str

class ReviewRequest(BaseModel):
    status: str # 'approved' or 'rejected'
    reviewer_notes: str
    approved_correction_text: Optional[str] = None

def verify_admin_key(x_correction_service_admin_key: Optional[str] = Header(None)) -> str:
    if not x_correction_service_admin_key:
        raise HTTPException(status_code=401, detail="Missing API Key")
    reviewer_name = ADMIN_KEYS.get(x_correction_service_admin_key)
    if not reviewer_name:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return reviewer_name

@app.post("/corrections/report")
def report_correction(req: ReportRequest, request: Request):
    client_ip = request.client.host
    now = time.time()
    
    # Clean up old timestamps
    if client_ip in report_rate_limits:
        report_rate_limits[client_ip] = [t for t in report_rate_limits[client_ip] if now - t < RATE_LIMIT_WINDOW_SECONDS]
        if len(report_rate_limits[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
        report_rate_limits[client_ip].append(now)
    else:
        report_rate_limits[client_ip] = [now]
        
    report_id = db.create_report(req.reported_issue_text, req.reported_by)
    return {"message": "Report submitted successfully.", "report_id": report_id}

@app.get("/corrections/pending")
def get_pending(reviewer_name: str = Depends(verify_admin_key)):
    return {"pending_reports": db.get_pending_reports()}

@app.post("/corrections/review/{report_id}")
def review_correction(report_id: int, req: ReviewRequest, reviewer_name: str = Depends(verify_admin_key)):
    if req.status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    if req.status == "approved" and not req.approved_correction_text:
        raise HTTPException(status_code=400, detail="Approval requires override text")
        
    db.review_report(
        report_id=report_id, 
        status=req.status, 
        reviewed_by=reviewer_name, 
        reviewer_notes=req.reviewer_notes, 
        approved_correction_text=req.approved_correction_text
    )
    return {"message": f"Report {report_id} {req.status} successfully."}

@app.get("/corrections/lookup")
def lookup_correction(query: str):
    """
    Given a query string, return any approved correction that textually matches it.
    Uses simple keyword/substring match as instructed (no embeddings).
    """
    if not query:
        return {"match": None}
        
    import re
    query_lower = query.lower()
    approved = db.get_approved_corrections()
    
    if len(approved) >= 1000:
        logger.warning(f"PERFORMANCE ALERT: Correction table has grown to {len(approved)} items. The current O(N) scan in /corrections/lookup should be refactored.")
        
    
    # Strip punctuation for keyword matching
    query_clean = re.sub(r'[^\w\s]', '', query_lower)
    query_words = set(query_clean.split())
    
    # Simple match: if there is a significant word overlap (e.g. > 3 matching words, excluding stop words)
    # or just split into words and check intersection
    stop_words = {"is", "the", "of", "a", "an", "what", "how", "why", "to", "in", "it", "should", "be", "wrong", "and"}
    query_keywords = query_words - stop_words
    
    for item in approved:
        issue_lower = item['reported_issue_text'].lower()
        issue_clean = re.sub(r'[^\w\s]', '', issue_lower)
        issue_words = set(issue_clean.split())
        issue_keywords = issue_words - stop_words
        
        # If they share at least 2 keywords, consider it a match
        overlap = query_keywords.intersection(issue_keywords)
        if len(overlap) >= 2 or (query_lower in issue_lower) or (issue_lower in query_lower):
            return {"match": item['approved_correction_text']}
            
    return {"match": None}

if __name__ == "__main__":
    import uvicorn
    # Standalone service on port 8002
    uvicorn.run(app, host="0.0.0.0", port=8002)
