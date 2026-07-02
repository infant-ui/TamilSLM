import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger("correction_service.db")

# NOTE: SQLite is used here for the correction queue because this service handles rare, 
# human-paced correction reports and approvals — nowhere near the 1M-student transactional 
# load profile that the main application databases face. It is an appropriate choice for this specific workload.
DB_PATH = os.path.join(os.path.dirname(__file__), "corrections.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS correction_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reported_issue_text TEXT NOT NULL,
                reported_by TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending_review',
                reviewer_notes TEXT,
                reviewed_by TEXT,
                approved_correction_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP
            )
        """)
        conn.commit()
    logger.info("Database initialized.")

def create_report(reported_issue_text: str, reported_by: str) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO correction_queue (reported_issue_text, reported_by, status)
            VALUES (?, ?, 'pending_review')
        """, (reported_issue_text, reported_by))
        conn.commit()
        return cursor.lastrowid

def get_pending_reports():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM correction_queue WHERE status = 'pending_review'")
        return [dict(row) for row in cursor.fetchall()]

def review_report(report_id: int, status: str, reviewed_by: str, reviewer_notes: str, approved_correction_text: str = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        approved_at = datetime.utcnow() if status == 'approved' else None
        
        cursor.execute("""
            UPDATE correction_queue
            SET status = ?, reviewed_by = ?, reviewer_notes = ?, approved_correction_text = ?, approved_at = ?
            WHERE id = ?
        """, (status, reviewed_by, reviewer_notes, approved_correction_text, approved_at, report_id))
        conn.commit()
        
        # Log resolution time metric if approved
        if status == 'approved':
            cursor.execute("SELECT created_at, approved_at FROM correction_queue WHERE id = ?", (report_id,))
            row = cursor.fetchone()
            if row:
                created = datetime.fromisoformat(row[0])
                approved = datetime.fromisoformat(row[1]) if isinstance(row[1], str) else approved_at
                delta = (approved - created).total_seconds()
                # Extremely simple metric logging
                with open("correction_resolution_metrics.log", "a") as f:
                    f.write(f"ReportID: {report_id} | ResolutionTimeSecs: {delta} | ApprovedAt: {approved}\n")

def get_approved_corrections():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM correction_queue WHERE status = 'approved'")
        return [dict(row) for row in cursor.fetchall()]

# Initialize db on module load
init_db()
