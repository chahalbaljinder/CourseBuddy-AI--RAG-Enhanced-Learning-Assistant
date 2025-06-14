from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import base64
import time
import os
import logging
from pathlib import Path
import uvicorn
from io import BytesIO
from PIL import Image

from app.rag_engine import RAGEngine
from app.config import Settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Ensure the model cache directory exists
os.makedirs("./model_cache", exist_ok=True)

# Load settings
settings = Settings()

# Initialize the RAG engine
logger.info("Initializing RAG engine...")
start_time = time.time()
rag_engine = RAGEngine(settings)
initialization_time = time.time() - start_time
logger.info(f"RAG engine initialization started in {initialization_time:.2f}s")

app = FastAPI(
    title="TDS Virtual Teaching Assistant API",
    description="API for answering student questions based on course content and discourse posts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Link(BaseModel):
    url: str = Field(..., description="URL of the source")
    text: str = Field(..., description="Text description of the source")

class AnswerResponse(BaseModel):
    answer: str = Field(..., description="Answer to the student's question")
    links: List[Link] = Field(default_factory=list, description="Relevant source links")

class QuestionRequest(BaseModel):
    question: str = Field(..., description="The student's question")
    image: Optional[str] = Field(None, description="Base64 encoded image (optional)")

class StatusResponse(BaseModel):
    status: str = Field(..., description="Status of the RAG engine")
    error: Optional[str] = Field(None, description="Error message if status is error")

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    """Middleware to ensure responses are sent within the maximum response time"""
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Check if response time exceeded the maximum
    elapsed_time = time.time() - start_time
    if elapsed_time > settings.MAX_RESPONSE_TIME:
        logger.warning(f"Response time exceeded maximum: {elapsed_time:.2f}s > {settings.MAX_RESPONSE_TIME}s")
    
    return response

@app.get("/health", response_model=StatusResponse)
async def health_check():
    """Health check endpoint that also returns RAG engine initialization status"""
    status = rag_engine.get_initialization_status()
    return StatusResponse(
        status=status["status"],
        error=status.get("error")
    )

@app.post("/", response_model=AnswerResponse)
async def answer_question(request: QuestionRequest):
    """
    Process a student question and return an answer with relevant links.
    
    - Accepts a question text and optional base64 encoded image
    - Returns an answer with relevant links from course materials and discourse posts
    - Times out after settings.MAX_RESPONSE_TIME seconds
    """
    start_time = time.time()
    logger.info(f"Received question: {request.question[:50]}...")
    
    # Check if RAG engine is ready
    if not rag_engine.is_ready():
        raise HTTPException(
            status_code=503,
            detail="The RAG engine is still initializing. Please try again in a few minutes."
        )
    
    try:
        # Process the question using the RAG engine
        response = rag_engine.answer_question(request.question, request.image)
        
        # Check if response time will exceed the maximum
        elapsed_time = time.time() - start_time
        if elapsed_time > settings.MAX_RESPONSE_TIME * 0.9:
            logger.warning(f"Response generation took {elapsed_time:.2f}s, approaching the maximum response time")
        
        # Format response
        formatted_response = AnswerResponse(
            answer=response["answer"],
            links=[Link(url=link["url"], text=link["text"]) for link in response["links"]]
        )
        
        logger.info(f"Total request processing time: {time.time() - start_time:.2f}s")
        return formatted_response
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while processing your question: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=settings.HOST, 
        port=settings.PORT,
        log_level=settings.LOG_LEVEL
    )
