"""
Test suite for the TDS Virtual Teaching Assistant API

This module contains tests for the RAG engine and API endpoints.
"""

import os
import base64
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Settings
from app.rag_engine import RAGEngine
from main import app

# Configure test client
client = TestClient(app)

# Load settings
settings = Settings()

class TestRAGEngine:
    """Tests for the RAG Engine"""
    
    def test_initialization(self):
        """Test RAG engine initialization"""
        rag_engine = RAGEngine(settings)
        assert rag_engine is not None
        assert rag_engine.model is not None
    
    def test_load_documents(self):
        """Test document loading"""
        rag_engine = RAGEngine(settings)
        documents = rag_engine._load_documents()
        # This might be empty if no data has been scraped yet
        assert isinstance(documents, list)
    
    @pytest.mark.skipif(not os.path.exists(settings.VECTOR_DB_PATH), 
                        reason="Vector store not initialized")
    def test_answer_question(self):
        """Test question answering"""
        rag_engine = RAGEngine(settings)
        result = rag_engine.answer_question("Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?")
        assert "answer" in result
        assert "links" in result
        assert isinstance(result["answer"], str)
        assert isinstance(result["links"], list)

class TestAPI:
    """Tests for the API endpoints"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_question_endpoint_no_image(self):
        """Test question endpoint without image"""
        response = client.post(
            "/",
            json={"question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?"}
        )
        assert response.status_code == 200
        result = response.json()
        assert "answer" in result
        assert "links" in result
    
    @pytest.mark.skipif(not os.path.exists(Path(__file__).parent / "test_image.png"),
                        reason="Test image not found")
    def test_question_endpoint_with_image(self):
        """Test question endpoint with image"""
        # Load test image
        test_image_path = Path(__file__).parent / "test_image.png"
        with open(test_image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Send request
        response = client.post(
            "/",
            json={
                "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
                "image": image_data
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert "answer" in result
        assert "links" in result

if __name__ == "__main__":
    # Run a simple test
    test_api = TestAPI()
    test_api.test_health_endpoint()
    print("Health endpoint test passed!")
    
    test_api.test_question_endpoint_no_image()
    print("Question endpoint test (no image) passed!")
    
    # Create test image if it doesn't exist
    test_image_path = Path(__file__).parent / "test_image.png"
    if not test_image_path.exists():
        print("Test image not found. Run scripts/create_test_image.py first.")
    else:
        test_api.test_question_endpoint_with_image()
        print("Question endpoint test (with image) passed!")
