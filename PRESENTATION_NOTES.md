# UniBot - Presentation Notes

## Project Overview
UniBot is a RAG (Retrieval Augmented Generation) based AI assistant for answering college-related queries. It combines web scraping, vector databases, and LLM to provide accurate, source-cited answers.

## Key Technologies

### Backend Framework
- **LangGraph**: Workflow orchestration and agent framework
- **LangChain**: LLM integration and tool management
- **FastAPI**: REST API server

### AI/ML
- **Gemini 2.5 Flash**: Chat model for response generation
- **text-embedding-004**: Embedding model for RAG
- **ChromaDB**: Vector database for storing embeddings

### Web Technologies
- **Playwright**: Web scraping and browser automation
- **React**: Frontend framework (with Vite)
- **FastAPI**: Backend API

## Architecture Highlights

### 1. RAG System
- Scrapes college website content
- Chunks and embeds content using Google's embedding model
- Stores in ChromaDB vector database
- Performs semantic similarity search for relevant context

### 2. LangGraph Workflow
- **Worker Node**: LLM with tools, generates responses
- **Tools Node**: Executes tool calls (RAG search, web browsing, etc.)
- **Evaluator Node**: Validates responses against success criteria
- **Router**: Intelligently routes between nodes

### 3. Tool System
- `query_college_knowledge_base`: Semantic search in RAG system
- `scrape_college_website`: Scrape and index website content
- Web browsing tools (Playwright)
- File management tools
- Python REPL for code execution

## Project Structure

```
unibot_/
├── Core Components
│   ├── agents/unibot.py         # Main UniBot class with LangGraph
│   ├── agents/tools.py          # Tool definitions
│   ├── agents/intent_detector.py # Intent detection
│   ├── retrieval/rag_system.py  # RAG system with ChromaDB
│   ├── ingestion/scraper.py          # Website scraper
│   ├── ingestion/pdf_processor.py    # PDF processing with OCR
│   ├── ingestion/scrape_tracker.py   # URL tracking
│   └── ingestion/scrape_checkpoint.py # Checkpoint system
│
├── Frontend
│   ├── index.html               # UI
│   ├── src/App.jsx              # React frontend
│   ├── styles.css               # Styling
│   ├── api_server.py            # FastAPI backend
│   └── verify_setup.py          # Setup verification
│
└── Utils
    └── inspect_knowledge_base.py # Knowledge base inspector
```

## Key Features

1. **RAG-based Question Answering**
   - Searches knowledge base using semantic similarity
   - Retrieves relevant context
   - Generates accurate answers with source citations

2. **Website Scraping**
   - Automated scraping using Playwright
   - PDF processing and extraction
   - Duplicate detection and checkpoint system

3. **Modern Web Interface**
   - Clean, responsive UI
   - Real-time chat
   - Backend status monitoring
   - Source citation display

4. **Intelligent Workflow**
   - LangGraph-based agent system
   - Automatic tool selection
   - Response validation
   - Conversation history management

## Data Flow

```
User Query
    ↓
Frontend (React - src/App.jsx)
    ↓
API Server (api_server.py)
    ↓
UniBot (agents/unibot.py)
    ↓
LangGraph Workflow
    ↓
RAG System (retrieval/rag_system.py)
    ↓
ChromaDB Vector Search
    ↓
Retrieved Context
    ↓
LLM (Gemini 2.5 Flash)
    ↓
Final Answer + Sources
    ↓
Frontend Display
```

## Technical Achievements

1. **Efficient RAG Implementation**
   - 11,719+ documents indexed
   - Fast semantic search
   - Source citation tracking

2. **Robust Scraping System**
   - Handles dynamic content
   - PDF extraction
   - Checkpoint/resume capability
   - Duplicate prevention

3. **Clean Architecture**
   - Modular design
   - Separation of concerns
   - Easy to extend

## Demo Points

1. **Show the Interface**
   - Clean, modern UI
   - Real-time chat
   - Status indicators

2. **Demonstrate RAG**
   - Ask a question about college
   - Show it searches knowledge base
   - Display answer with sources

3. **Show Scraping Capability**
   - Explain how content is indexed
   - Show knowledge base stats
   - Demonstrate source citations

4. **Technical Deep Dive**
   - LangGraph workflow
   - RAG system architecture
   - Vector database usage

## Future Enhancements

- Multi-language support
- Advanced filtering and categorization
- User authentication
- Analytics dashboard
- Mobile app

## Questions to Prepare For

1. **Why RAG instead of fine-tuning?**
   - RAG allows dynamic knowledge updates without retraining
   - More cost-effective
   - Better for domain-specific information

2. **How does semantic search work?**
   - Content is embedded into vectors
   - Query is also embedded
   - Cosine similarity finds most relevant chunks

3. **What makes this different from ChatGPT?**
   - Domain-specific knowledge base
   - Source citations
   - Can scrape and update knowledge dynamically
   - No training required

4. **Scalability concerns?**
   - ChromaDB handles large datasets efficiently
   - Can add more documents without performance issues
   - Vector search is fast even with 10k+ documents

