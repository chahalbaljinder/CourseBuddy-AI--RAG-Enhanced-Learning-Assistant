"""
RAG Engine Implementation for TDS Virtual Teaching Assistant

This module implements the Retrieval-Augmented Generation (RAG) engine
that powers the TDS Virtual Teaching Assistant. Optimized for performance.
"""

import os
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import base64
from io import BytesIO
from PIL import Image
import time
import threading
import sys

import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global model instances to avoid reloading
_embedding_model = None
_gemini_model = None
_vector_store = None
_initialization_complete = False
_initialization_error = None

def get_embedding_model():
    """Get or initialize the embedding model (singleton pattern)"""
    global _embedding_model
    if _embedding_model is None:
        start_time = time.time()
        logger.info("Starting embedding model download and initialization...")
        try:
            _embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                cache_folder="./model_cache"  # Cache the model locally
            )
            logger.info(f"Initialized HuggingFace embeddings in {time.time()-start_time:.2f}s")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {str(e)}")
            raise
    return _embedding_model

def get_gemini_model(api_key, model_name):
    """Get or initialize the Gemini model (singleton pattern)"""
    global _gemini_model
    if _gemini_model is None:
        start_time = time.time()
        try:
            genai.configure(api_key=api_key)
            _gemini_model = genai.GenerativeModel(model_name)
            logger.info(f"Initialized Gemini model: {model_name} in {time.time()-start_time:.2f}s")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise
    return _gemini_model

def get_vector_store(vector_store_path, embedding_model):
    """Get or initialize the vector store (singleton pattern)"""
    global _vector_store
    if _vector_store is None:
        start_time = time.time()
        if Path(vector_store_path).exists():
            try:
                logger.info(f"Loading vector store from {vector_store_path}...")
                _vector_store = FAISS.load_local(
                    folder_path=vector_store_path,
                    embeddings=embedding_model,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"Loaded vector store from {vector_store_path} in {time.time()-start_time:.2f}s")
            except Exception as e:
                logger.error(f"Error loading vector store: {str(e)}")
                # If vector store loading fails, create a new one
                _vector_store = None
        else:
            logger.warning(f"Vector store not found at {vector_store_path}")
            _vector_store = None
    return _vector_store

def initialize_in_background(settings):
    """Initialize the RAG engine in a background thread"""
    global _initialization_complete, _initialization_error
    
    try:
        # Initialize embedding model
        get_embedding_model()
        
        # Initialize Gemini model
        get_gemini_model(settings.GOOGLE_API_KEY, settings.GEMINI_MODEL)
        
        # Initialize vector store
        vector_store = get_vector_store(settings.VECTOR_DB_PATH, _embedding_model)
        
        # If vector store doesn't exist, create it
        if vector_store is None:
            logger.info("Creating new vector store...")
            # Create vector store by loading documents
            documents = _load_documents(settings)
            if documents:
                # Split documents into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=settings.CHUNK_SIZE,
                    chunk_overlap=settings.CHUNK_OVERLAP
                )
                splits = text_splitter.split_documents(documents)
                logger.info(f"Split {len(documents)} documents into {len(splits)} chunks")
                
                # Create vector store
                vector_store_path = Path(settings.VECTOR_DB_PATH)
                vector_store_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Use the embedding model to create the vector store
                _vector_store = FAISS.from_documents(
                    documents=splits,
                    embedding=_embedding_model
                )
                
                # Save the vector store locally
                _vector_store.save_local(folder_path=str(vector_store_path))
                logger.info(f"Created and saved vector store at {vector_store_path}")
        
        _initialization_complete = True
        logger.info("RAG engine initialization complete!")
    except Exception as e:
        _initialization_error = str(e)
        logger.error(f"RAG engine initialization failed: {str(e)}")

def _load_documents(settings):
    """Load documents from course content and discourse posts"""
    documents = []
    
    # Load discourse posts from processed files
    try:
        discourse_path = Path(settings.DISCOURSE_DATA_PATH)
        if discourse_path.exists():
            logger.info(f"Loading discourse posts from {discourse_path}")
            start_time = time.time()
            
            # Get all markdown files in the discourse posts directory
            md_files = list(discourse_path.glob("*.md"))
            
            for file_path in md_files:
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract URL from the content (third line contains the URL)
                    lines = content.split("\n")
                    url = ""
                    for line in lines:
                        if "**URL:**" in line:
                            url = line.replace("**URL:**", "").strip()
                            break
                    
                    # Create document
                    document = Document(
                        page_content=content,
                        metadata={
                            "source": url,
                            "filename": file_path.name
                        }
                    )
                    documents.append(document)
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
            
            logger.info(f"Loaded {len(documents)} discourse posts in {time.time()-start_time:.2f}s")
    except Exception as e:
        logger.error(f"Error loading discourse posts: {str(e)}")
    
    return documents

class RAGEngine:
    """RAG Engine for answering student questions using course content and discourse posts"""
    
    def __init__(self, settings):
        """Initialize the RAG engine with settings"""
        self.settings = settings
        self.is_initialized = False
        
        # Start background initialization
        logger.info("Starting background initialization of RAG engine...")
        self.init_thread = threading.Thread(
            target=initialize_in_background,
            args=(settings,)
        )
        self.init_thread.daemon = True
        self.init_thread.start()
    
    def is_ready(self):
        """Check if the RAG engine is ready to answer questions"""
        global _initialization_complete, _initialization_error
        return _initialization_complete
    
    def get_initialization_status(self):
        """Get the initialization status of the RAG engine"""
        global _initialization_complete, _initialization_error
        
        if _initialization_error:
            return {
                "status": "error",
                "error": _initialization_error
            }
        elif _initialization_complete:
            return {
                "status": "ready"
            }
        else:
            return {
                "status": "initializing"
            }
    
    def answer_question(self, question: str, image_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Answer a student question using the RAG pipeline
        
        Args:
            question: The student's question
            image_data: Optional base64 encoded image
            
        Returns:
            Dictionary containing the answer and relevant links
        """
        # Check if engine is ready
        if not self.is_ready():
            raise Exception("RAG engine is not yet initialized. Please try again later.")
        
        global _embedding_model, _gemini_model, _vector_store
        
        start_time = time.time()
        try:
            # Process image if provided
            image = None
            if image_data:
                try:
                    # Decode base64 image
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                    logger.info("Processed image attachment")
                except Exception as e:
                    logger.error(f"Error processing image: {str(e)}")
            
            # Retrieve relevant documents if vector store exists
            relevant_docs = []
            if _vector_store:
                try:
                    # Use similarity search from the vector store with smaller k for faster response
                    search_start = time.time()
                    relevant_docs = _vector_store.similarity_search(
                        question, 
                        k=self.settings.NUM_RETRIEVED_DOCS
                    )
                    search_time = time.time() - search_start
                    logger.info(f"Retrieved {len(relevant_docs)} relevant documents in {search_time:.2f}s")
                except Exception as e:
                    logger.error(f"Error retrieving documents: {str(e)}")
            
            # Extract context from documents
            context = ""
            links = []
            
            for doc in relevant_docs:
                context += doc.page_content + "\n\n"
                
                # Extract source metadata for links
                source = doc.metadata.get("source", "")
                if source:
                    # Create a user-friendly link
                    link_text = self._format_source_as_link_text(source)
                    links.append({
                        "url": source,
                        "text": link_text
                    })
            
            # Generate answer using Gemini
            prompt = self._create_prompt(question, context)
            
            # Handle image if present
            generation_start = time.time()
            if image:
                response = _gemini_model.generate_content([prompt, image])
            else:
                response = _gemini_model.generate_content(prompt)
            
            answer = response.text
            generation_time = time.time() - generation_start
            logger.info(f"Generated answer using Gemini in {generation_time:.2f}s")
            
            total_time = time.time() - start_time
            logger.info(f"Total question answering time: {total_time:.2f}s")
            
            # Return formatted response
            return {
                "answer": answer,
                "links": links
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            # Return a graceful error response
            return {
                "answer": f"I'm sorry, I encountered an error while processing your question. Please try again or contact support if the issue persists. Error details: {str(e)}",
                "links": []
            }
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create a prompt for the Gemini model"""
        if context:
            return f"""You are a virtual teaching assistant for a Technical Data Science (TDS) class at IIT Madras' Online Degree in Data Science. 
Use the following context to answer the student's question.
If the information is not in the context, just say that you don't know but would be happy to help with other questions.
Do not make up answers that are not supported by the context.
Provide a clear, concise answer.

CONTEXT:
{context}

STUDENT QUESTION:
{question}

YOUR ANSWER:"""
        else:
            return f"""You are a virtual teaching assistant for a Technical Data Science (TDS) class at IIT Madras' Online Degree in Data Science.
Answer the student's question based on your knowledge.
If you don't know the answer, just say that you don't know but would be happy to help with other questions.
Do not make up answers.
Provide a clear, concise answer.

STUDENT QUESTION:
{question}

YOUR ANSWER:"""
    
    def _format_source_as_link_text(self, source: str) -> str:
        """Format a source path as a user-friendly link text"""
        try:
            path = Path(source)
            
            # Handle course content vs. discourse posts
            if "course_content" in source:
                return f"Course Material: {path.name}"
            elif "discourse_posts" in source or "onlinedegree.iitm.ac.in" in source:
                # If it's a discourse URL, extract the post ID
                if "onlinedegree.iitm.ac.in" in source:
                    # Try to extract post ID from URL
                    parts = source.split("/")
                    if len(parts) >= 2:
                        post_id = parts[-1]
                        topic_title = self._get_discourse_post_title(post_id)
                        if topic_title:
                            return f"Discussion: {topic_title}"
                    return f"Discussion Post: {source.split('/')[-1]}"
                else:
                    # If filename is just a number, try to find the topic title in metadata
                    if path.stem.isdigit():
                        post_id = path.stem
                        topic_title = self._get_discourse_post_title(post_id)
                        if topic_title:
                            return topic_title
                    return f"Discourse Post: {path.name}"
            else:
                return path.name
                
        except Exception:
            # Fall back to the original source if parsing fails
            return source
    
    def _get_discourse_post_title(self, post_id: str) -> str:
        """Get the title of a discourse post from its ID"""
        # This would normally look up the title in a database or cache
        # For now, return a generic title
        return f"Discourse Post #{post_id}"
