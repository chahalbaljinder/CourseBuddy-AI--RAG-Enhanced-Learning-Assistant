# CourseBuddy AI: RAG-Enhanced Learning Assistant

A robust Retrieval-Augmented Generation (RAG) API for IIT Madras' Online Degree Program in Data Science, specifically designed to assist students in the Tools in Data Science (TDS) course.

![TDS Virtual Teaching Assistant](https://img.shields.io/badge/IIT%20Madras-TDS%20Virtual%20Assistant-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Overview

This API serves as a virtual teaching assistant for students taking the Tools in Data Science course. It leverages:

- **RAG Architecture**: Combines retrieval-based search with generative AI for accurate, contextual responses
- **Course Content**: Information from TDS Jan 2025 course materials
- **Discourse Integration**: Processes posts from the TDS Discourse forums (Jan-Apr 2025)
- **Google's Gemini 2.0 Flash**: State-of-the-art LLM for generating high-quality responses

The system is optimized for performance, with response times well under 30 seconds, typically answering queries in 2-5 seconds.

## Key Features

- **Fast and Accurate Responses**: Optimized RAG pipeline for quick, contextually accurate answers
- **Image Support**: Process screenshots of error messages or code through base64 encoded attachments
- **Source Attribution**: Every response includes links to relevant course materials and discourse posts
- **Asynchronous Initialization**: Server starts quickly with background model loading
- **Performance Monitoring**: Built-in performance tracking and metrics
- **Robust Error Handling**: Graceful handling of edge cases and rate limitations

## System Architecture

```
┌─────────────────┐     ┌───────────────┐     ┌────────────────┐
│                 │     │               │     │                │
│  FastAPI Server │◄────┤  RAG Engine   │◄────┤  Vector Store  │
│  (main.py)      │     │  (rag_engine) │     │  (FAISS)       │
│                 │     │               │     │                │
└────────┬────────┘     └───────┬───────┘     └────────────────┘
         │                      │                      ▲
         │                      │                      │
         │                      │                      │
         ▼                      ▼                      │
┌─────────────────┐     ┌───────────────┐     ┌────────────────┐
│                 │     │               │     │                │
│  Configuration  │     │  Gemini API   │     │  Preprocessed  │
│  (config.py)    │     │  (LLM)        │     │  Markdown Files│
│                 │     │               │     │                │
└─────────────────┘     └───────────────┘     └────────────────┘
```

## Installation

1. **Clone this repository**:
   ```bash
   git clone <repository-url>
   cd pratham_rag_project
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   Create a `.env` file in the project root with the following variables:
   ```
   # API settings
   HOST=0.0.0.0
   PORT=8000
   LOG_LEVEL=info
   MAX_RESPONSE_TIME=30

   # Google AI settings
   GOOGLE_API_KEY=your_google_api_key
   GEMINI_MODEL=gemini-2.0-flash

   # Data paths
   COURSE_DATA_PATH=./data/course_content
   DISCOURSE_DATA_PATH=./data/discourse_posts
   VECTOR_DB_PATH=./data/vector_store

   # Performance settings
   NUM_RETRIEVED_DOCS=3
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=100
   ```

4. **Preprocess the data**:
   ```bash
   python scripts/preprocess_data.py
   ```
   This script converts the discourse_posts.json file into individual markdown files for optimal processing.

## Usage

### Running the API

The main file to run is `main.py`, which starts the FastAPI server:

```bash
python main.py
```

The server will:
1. Start on http://localhost:8000 (or your configured HOST:PORT)
2. Begin loading models and initializing the vector store in the background
3. Be immediately available to handle requests (with initialization status provided through the health endpoint)

### API Endpoints

#### GET /health

Check the API health and initialization status:

**Request:**
```
GET /health
```

**Response:**
```json
{
  "status": "ready|initializing|error",
  "error": "Error message if status is error"
}
```

#### POST /

Ask a question to the virtual teaching assistant.

**Request:**
```json
{
  "question": "What is the deadline for GA5?",
  "image": "optional_base64_encoded_image"
}
```

**Response:**
```json
{
  "answer": "Based on the discourse posts, the deadline for GA5 is April 15, 2025 at 11:59 PM IST.",
  "links": [
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/t/topic/post_id",
      "text": "Discourse Post #12345"
    }
  ]
}
```

## Testing

### Quick Test

To quickly test if the API is working:

```bash
python quick_test.py
```

This script checks if the API is healthy and tests a simple question.

### Performance Testing

To evaluate the performance of the API:

```bash
python test_performance.py
```

This script sends multiple questions to the API and measures response times. Results are saved to `performance_results.json`.

### Specific Question Testing

To test with a specific question:

```bash
python test_question.py
```

You can modify the question in the script to test different queries.

## Implementation Details

### Components

- **main.py**: The main FastAPI application with API endpoints and middleware
- **app/config.py**: Configuration settings loaded from environment variables
- **app/rag_engine.py**: Core RAG implementation with vector storage and retrieval logic
- **scripts/preprocess_data.py**: Script to process discourse posts into markdown files
- **tests/**: Test scripts for the API and RAG engine

### Optimizations

1. **Singleton Model Loading**: Models are loaded only once and reused across requests
2. **Asynchronous Initialization**: Background loading of models and vector store
3. **FAISS Vector Store**: Efficient similarity search for fast document retrieval
4. **Reduced Document Retrieval**: Only retrieve the most relevant documents (configurable)
5. **Preprocessed Markdown Files**: Convert JSON to markdown files for faster processing

## Performance

In our tests, the API typically responds in 2-5 seconds for most queries, well under the 30-second requirement. Performance metrics include:

- **Average response time**: ~3.5 seconds
- **Minimum response time**: ~2 seconds
- **Maximum response time**: ~10 seconds (for complex queries with many documents)

## Troubleshooting

### Common Issues

1. **API Not Starting**: Check if the port is already in use or if there are permission issues
2. **Slow Responses**: Adjust NUM_RETRIEVED_DOCS in the .env file to balance between quality and speed
3. **Missing Google API Key**: Ensure your GOOGLE_API_KEY is valid and has access to the Gemini API

### Logs

Check the console logs for detailed information about:
- Model initialization status
- Document retrieval times
- Answer generation times
- Any errors that occur during processing

## Future Improvements

- Integration with course LMS for real-time updates
- Personalized responses based on student progress
- Multi-language support for international students
- Enhanced handling of code snippets and technical questions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- IIT Madras Online Degree Program in Data Science
- Google Gemini API for providing the generative AI capabilities
- FastAPI for the high-performance web framework
- LangChain for the RAG implementation tools

Ask a question to the virtual teaching assistant.

**Request Body:**

```json
{
  "question": "Your question here",
  "image": "Optional base64-encoded image data"
}
```

**Response:**

```json
{
  "answer": "The answer to your question",
  "links": [
    {
      "url": "https://source-url.com",
      "text": "Source description"
    }
  ]
}
```

#### GET /health

Check if the API is running.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": 1623456789.123
}
```

## Running Tests

To test the API:

```
python -m tests.test_api
```

To run unit tests:

```
pytest tests/
```

## Performance Optimization

The API is optimized for performance through:

1. Singleton pattern for model loading
2. Model caching to avoid repeated downloads
3. Efficient vector store initialization with FAISS
4. Limited number of retrieved documents
5. Multithreading for parallel processing
6. Adjustable chunk size and overlap for better document splitting

## License

MIT
