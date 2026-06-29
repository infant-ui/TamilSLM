# services/retrieval-service/app/ingestion/book_scanner.py
import os
import hashlib
import json
from typing import Dict, List, Tuple
from pydantic import BaseModel
from app.ingestion.metadata_parser import MetadataParser, BookMetadata

class ScanSummary(BaseModel):
    new_files: List[BookMetadata] = []
    modified_files: List[BookMetadata] = []
    unchanged_files: List[str] = []
    invalid_files: List[Tuple[str, str]] = []

class BookScanner:
    def __init__(self, data_root: str, registry_path: str):
        self.data_root = os.path.abspath(data_root)
        self.books_dir = os.path.join(self.data_root, "books")
        self.registry_path = os.path.abspath(registry_path)
        self.parser = MetadataParser()

    def get_file_sha256(self, filepath: str) -> str:
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    def load_manifest(self) -> dict:
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_updated": None, "total_documents": 0, "documents": {}}

    def scan(self) -> ScanSummary:
        manifest = self.load_manifest()
        registered_docs = manifest.get("documents", {})
        summary = ScanSummary()

        if not os.path.exists(self.books_dir):
            os.makedirs(self.books_dir, exist_ok=True)

        for root, _, files in os.walk(self.books_dir):
            for file in files:
                if not file.lower().endswith(".pdf"):
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.data_root)
                
                # 1. Parse metadata
                meta = self.parser.parse_from_filename(file, rel_path)
                if not meta:
                    err_desc = f"Filename '{file}' does not match any naming pattern (term, fullyear, or prev-year)."
                    summary.invalid_files.append((rel_path, err_desc))
                    continue

                # 2. Hash check
                file_hash = self.get_file_sha256(full_path)
                
                # Check manifest records
                if file_hash in registered_docs:
                    summary.unchanged_files.append(file_hash)
                else:
                    # Check if modified (same path, different hash)
                    is_modified = False
                    for doc_id, doc in registered_docs.items():
                        if doc.get("file_path") == rel_path:
                            is_modified = True
                            break
                    
                    if is_modified:
                        summary.modified_files.append(meta)
                    else:
                        summary.new_files.append(meta)

        return summary
