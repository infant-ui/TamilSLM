import os
import sys
import importlib
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

def load_service_app(service_dir, module_name):
    """
    Dynamically loads a microservice's FastAPI app.
    Clears sys.modules to prevent collisions between different microservices 
    that share module names like 'app' or 'main'.
    """
    service_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', service_dir))
    
    # Clear out previous conflicting modules
    to_delete = [k for k in sys.modules if k.split('.')[0] in ['app', 'main', module_name]]
    for k in to_delete:
        del sys.modules[k]
        
    sys.path.insert(0, service_path)
    module = importlib.import_module(module_name)
    app_instance = module.app
    sys.path.pop(0)
    return app_instance

def test_retrieve_happy_path():
    retrieval_app = load_service_app('retrieval-service', 'main')
    
    with patch('main.services_cache') as mock_cache:
        # Mock components to bypass actual ML loading/execution
        mock_retriever = MagicMock()
        
        async def mock_retrieve(*args, **kwargs):
            return [], False  # candidates, fallback_applied
        mock_retriever.retrieve = mock_retrieve
        
        mock_reranker = MagicMock()
        mock_reranker.rerank.return_value = []
        
        mock_prompt_builder = MagicMock()
        mock_prompt_builder.build_prompt.return_value = ("System Prompt", "User Msg")
        
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]]
        
        def mock_get(key, default=None):
            if key == "retriever": return mock_retriever
            if key == "reranker": return mock_reranker
            if key == "prompt_builder": return mock_prompt_builder
            if key == "ta_model": return mock_model
            if key == "en_model": return mock_model
            return default
            
        mock_cache.get.side_effect = mock_get
        
        client = TestClient(retrieval_app)
        response = client.post("/retrieve", json={
            "question": "What is gravity?",
            "preferred_medium": "english",
            "class_id": 6,
            "subject": "science"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "What is gravity?"

def test_generate_stream_happy_path():
    generation_app = load_service_app('generation-service', 'app')
    client = TestClient(generation_app)
    
    # Mock requests.post to bypass Ollama
    with patch('app.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Mock iter_lines to simulate SSE stream
        mock_response.iter_lines.return_value = [
            b'{"message": {"content": "Gravity "}}',
            b'{"message": {"content": "is "}}',
            b'{"message": {"content": "cool."}}'
        ]
        mock_post.return_value = mock_response
        
        response = client.post("/generate/stream", json={
            "query": "Explain gravity.",
            "context": "Gravity is a force.",
            "language": "english"
        })
        
        assert response.status_code == 200
        # Since it's a streaming response, we can read the text
        text = response.text
        assert "Gravity" in text

def test_corrections_report_happy_path():
    correction_app = load_service_app('correction-service', 'main')
    
    # We patch the database creation to not actually write
    with patch('main.db.create_report') as mock_create:
        mock_create.return_value = 123
        
        client = TestClient(correction_app)
        response = client.post("/corrections/report", json={
            "reported_issue_text": "The answer about gravity is wrong.",
            "reported_by": "Teacher A"
        })
        
        assert response.status_code == 200
        assert response.json()["report_id"] == 123
