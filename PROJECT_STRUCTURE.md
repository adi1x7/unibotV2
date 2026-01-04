# UniBot Project Structure

## Overview
UniBot is a RAG (Retrieval Augmented Generation) based AI assistant for college queries, built with LangGraph and ChromaDB.

## Technology Stack

### Backend
- **LangGraph**: Workflow orchestration and agent framework
- **LangChain**: LLM integration and tool management
- **ChromaDB**: Vector database for embeddings storage
- **FastAPI**: REST API server
- **Playwright**: Web scraping and browser automation

### Frontend
- **HTML/CSS/JavaScript**: Modern web interface
- **FastAPI**: Backend API server

### AI Models
- **Gemini 2.5 Flash**: Chat model for response generation
- **text-embedding-004**: Embedding model for RAG

## Directory Structure

```
unibot_/
│
├── agents/                       # Agent modules
│   ├── unibot.py                # Main UniBot class with LangGraph workflow
│   ├── tools.py                 # Tool definitions (RAG, web, file, code)
│   └── intent_detector.py       # Intent detection & validation
│
├── backend/                      # Backend API
│   └── api_server.py            # FastAPI backend server
│
├── ingestion/                    # Data ingestion
│   ├── scraper.py               # Website scraper using Playwright
│   ├── pdf_processor.py         # PDF extraction and processing (with OCR)
│   ├── scrape_tracker.py        # URL tracking (prevents duplicates)
│   └── scrape_checkpoint.py     # Checkpoint system (resume scraping)
│
├── retrieval/                    # RAG system
│   └── rag_system.py            # RAG system with ChromaDB & hybrid search
│
├── frontend/                     # React frontend
│   ├── src/                     # React source code
│   │   ├── App.jsx              # Main React component
│   │   ├── components/          # React components
│   │   └── utils/               # Utility functions
│   ├── index.html               # HTML template
│   ├── styles.css               # Styling
│   ├── package.json             # Node.js dependencies
│   ├── verify_setup.py          # Setup verification
│   ├── start_frontend.bat       # Windows startup
│   └── start_frontend.sh        # Linux/Mac startup
│
├── utils/                        # Utility scripts
│   └── inspect_knowledge_base.py # Knowledge base inspector
│
├── Configuration
│   ├── requirements.txt         # Python dependencies
│   ├── .gitignore              # Git exclusions
│   └── .env                     # Environment variables (not in repo)
│
└── Data (auto-generated, gitignored)
    ├── chroma_db/                # Vector database
    ├── scrape_tracker.json       # Scraping progress
    └── scrape_checkpoint.json    # Checkpoint data
```

## Key Components

### 1. RAG System (`retrieval/rag_system.py`)
- Manages ChromaDB vector store
- Handles document embedding and storage
- Performs hybrid search (semantic + keyword)
- Returns relevant context for LLM

### 2. LangGraph Workflow (`agents/unibot.py`)
- **Worker Node**: LLM with tools, generates responses
- **Tools Node**: Executes tool calls (RAG, web, file, etc.)
- **Evaluator Node**: Validates responses against success criteria
- **Router**: Routes between worker, tools, and evaluator

### 3. Tools (`agents/tools.py`)
- `query_college_knowledge_base`: Search RAG system
- `scrape_college_website`: Scrape and index website
- Web browsing tools (Playwright)
- File management tools
- Python REPL
- Web search (optional)

### 4. Intent Detection (`agents/intent_detector.py`)
- Validates queries are college-domain only
- Detects intent (fees, admissions, exams, etc.)
- Rejects out-of-scope queries

### 4. Frontend (`frontend/`)
- Modern, responsive UI
- Real-time chat interface
- Backend status monitoring
- Source citation display
- Suggested questions

## Workflow

1. **User Query** → Frontend sends to API server
2. **API Server** → Calls UniBot's `run_superstep()`
3. **LangGraph** → Routes to worker node
4. **Worker** → LLM decides to use `query_college_knowledge_base` tool
5. **RAG System** → Searches ChromaDB, returns relevant chunks
6. **LLM** → Generates answer using retrieved context
7. **Evaluator** → Validates response
8. **Response** → Returns to frontend with sources

## Data Flow

```
College Website
    ↓ (scraping)
Content Chunks
    ↓ (embedding)
ChromaDB Vector Store
    ↓ (query)
Semantic Search
    ↓ (retrieval)
Relevant Context
    ↓ (LLM)
Final Answer + Sources
```

## Features

### Core Features
- ✅ RAG-based question answering
- ✅ Website scraping and indexing
- ✅ PDF processing
- ✅ Source citation
- ✅ Conversation history

### Additional Capabilities
- Web browsing
- File operations
- Code execution
- Web search (optional)

## Security & Best Practices

- Environment variables in `.env` (not committed)
- Large data files excluded from Git
- CORS enabled for local development
- API key validation on startup
- Error handling and logging

