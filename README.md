# UniBot - College Query Assistant

A LangGraph-based AI assistant with RAG (Retrieval Augmented Generation) capabilities for answering college-related queries. UniBot can scrape college websites, store the data in a vector database, and use RAG to generate accurate responses to user questions.

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

After installing the requirements, you need to install Playwright browsers:

```bash
playwright install chromium
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory with the following variables:

**Required:**
- `GOOGLE_API_KEY` - Your Google Gemini API key (required for the LLM and embeddings)

**Optional:**
- `COLLEGE_WEBSITE_URL` - Base URL of your college website (e.g., "https://college.edu") - UniBot can scrape this automatically
- `SERPER_API_KEY` - API key for Google Search (optional, for web search functionality)
- `PUSHOVER_TOKEN` - Token for Pushover notifications (optional)
- `PUSHOVER_USER` - User key for Pushover notifications (optional)

Example `.env` file:
```
GOOGLE_API_KEY=your-google-gemini-api-key-here
COLLEGE_WEBSITE_URL=https://yourcollege.edu
SERPER_API_KEY=your-serper-api-key-here
PUSHOVER_TOKEN=your-pushover-token
PUSHOVER_USER=your-pushover-user
```

### 4. Verify Configuration (Optional but Recommended)

Before running the application, verify your setup:

```bash
python verify_gemini_setup.py
```

This will check:
- ✅ API key is set
- ✅ ChromaDB database exists
- ✅ Required packages are installed
- ✅ Models can be initialized

## Models Used

- **Chat Model**: `gemini-2.5-flash` - Fast, efficient response generation
- **Embedding Model**: `text-embedding-004` - High-quality embeddings for RAG

These models provide the best performance-to-cost ratio for the UniBot project.

### 5. Run the Application

**Option 1: Modern Web Frontend (Recommended)**
```bash
# Start the API server
cd frontend
python api_server.py

# In another terminal, start the frontend server
cd frontend
python -m http.server 8080

# Open http://localhost:8080 in your browser
```

**Or use the startup script:**
```bash
# Windows
frontend/start_frontend.bat

# Linux/Mac
frontend/start_frontend.sh
```

**Option 2: Gradio Interface (Alternative)**
```bash
python app.py
```

The Gradio application will launch in your default web browser.

## Features

### Core RAG Capabilities
- **Website Scraping**: Automatically scrape college website content using Playwright
- **Vector Database**: Store scraped content in ChromaDB for efficient retrieval
- **RAG Query System**: Search the knowledge base using semantic similarity
- **Intelligent Responses**: Generate accurate answers based on scraped college data

### Additional Tools
- **Web Browsing**: Navigate and retrieve information from web pages using Playwright
- **File Management**: Read and write files in the `sandbox/` directory
- **Code Execution**: Run Python code in a REPL environment
- **Web Search**: Search the internet using Google Search API
- **Wikipedia**: Query Wikipedia for information
- **Push Notifications**: Send push notifications (if configured)

## How It Works

1. **Initial Setup**: UniBot initializes with a RAG system using ChromaDB vector store
2. **Website Scraping** (Optional): You can ask UniBot to scrape your college website, or set `COLLEGE_WEBSITE_URL` in `.env`
3. **Data Storage**: Scraped content is chunked, embedded, and stored in the vector database
4. **Query Processing**: When users ask questions, UniBot:
   - Searches the knowledge base for relevant information
   - Retrieves the most relevant chunks
   - Uses the LLM to generate answers based on retrieved context
5. **Response Generation**: UniBot provides accurate, context-aware answers about the college

## Usage

### First Time Setup

1. **Scrape the College Website** (if not already done):
   - Ask UniBot: "Please scrape the college website at https://yourcollege.edu"
   - Or set `COLLEGE_WEBSITE_URL` in your `.env` file and UniBot can scrape it automatically

2. **Ask Questions**:
   - "What courses are offered?"
   - "What are the admission requirements?"
   - "Tell me about the faculty"
   - "What facilities are available?"
   - "What are the college policies?"

### Example Queries

- Course information: "What computer science courses are available?"
- Admissions: "What are the requirements for admission?"
- Faculty: "Who are the professors in the engineering department?"
- Facilities: "What labs and facilities does the college have?"
- Events: "What events are happening this semester?"

## Project Structure

### Core Files
- `sidekick.py` - Core UniBot class with LangGraph workflow and RAG integration
- `sidekick_tools.py` - Tool definitions including RAG tools
- `rag_system.py` - RAG system with vector store and retrieval
- `college_scraper.py` - Website scraper for college content
- `pdf_processor.py` - PDF extraction and quality filtering
- `scrape_checkpoint.py` - Checkpoint system for resuming scrapes
- `scrape_tracker.py` - URL tracking to avoid duplicate scraping

### Frontend
- `frontend/` - Modern web frontend (HTML/CSS/JS + FastAPI backend)
  - `index.html` - Main frontend UI
  - `api_server.py` - FastAPI backend server
  - `app.js` - Frontend logic
  - `styles.css` - Styling

### Utilities
- `fix_and_rescrape.py` - Complete re-scraping script with quality filtering
- `inspect_knowledge_base.py` - Utility to inspect knowledge base contents
- `app.py` - Gradio interface (alternative frontend)

### Data
- `chroma_db/` - Vector database storage (created automatically)
- `scrape_checkpoint.json` - Scraping progress checkpoint
- `scrape_tracker.json` - Tracked URLs to avoid duplicates

