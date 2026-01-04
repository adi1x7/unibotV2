# UniBot - College Query Assistant

A LangGraph-based AI assistant with RAG (Retrieval Augmented Generation) capabilities for answering college-related queries. UniBot can scrape college websites, store the data in a vector database, and use RAG to generate accurate responses to user questions.

## 🎯 Features

### Core RAG Capabilities
- **Website Scraping**: Automatically scrape college website content using Playwright
- **PDF Processing**: Extract text from PDFs with OCR support for scanned documents
- **Vector Database**: Store scraped content in ChromaDB for efficient retrieval
- **Hybrid Search**: Combines semantic similarity and keyword matching for better retrieval
- **Intent Detection**: Validates queries are college-domain only, rejects out-of-scope queries
- **Intelligent Responses**: Generate accurate answers based on scraped college data with source citations

### Additional Tools
- **Web Browsing**: Navigate and retrieve information from web pages
- **File Management**: Read and write files in the `sandbox/` directory
- **Code Execution**: Run Python code in a REPL environment
- **Web Search**: Search the internet using Google Search API (optional)

## 🏗️ Architecture

```
UniBot/
├── agents/                  # Agent modules
│   ├── unibot.py           # Main UniBot class with LangGraph workflow
│   ├── tools.py            # Tool definitions (RAG, web browsing, etc.)
│   └── intent_detector.py  # Intent detection and validation
│
├── backend/                 # Backend API
│   └── api_server.py       # FastAPI backend server
│
├── ingestion/               # Data ingestion
│   ├── scraper.py          # Website scraper
│   ├── pdf_processor.py    # PDF extraction and processing (with OCR)
│   ├── scrape_tracker.py   # URL tracking to avoid duplicates
│   └── scrape_checkpoint.py # Checkpoint system for resuming scrapes
│
├── retrieval/               # RAG system
│   └── rag_system.py       # RAG system with vector store and hybrid search
│
├── frontend/                # React frontend
│   ├── src/                # React source code
│   │   ├── App.jsx         # Main React component
│   │   ├── components/     # React components
│   │   └── utils/          # Utility functions
│   ├── index.html          # HTML template
│   ├── styles.css          # Styling
│   ├── package.json        # Node.js dependencies
│   └── verify_setup.py     # Setup verification script
│
├── utils/                   # Utility scripts
│   └── inspect_knowledge_base.py  # Inspect knowledge base contents
│
├── chroma_db/              # Vector database (auto-created, gitignored)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# For OCR support (optional, for scanned PDFs):
# Windows: Download Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract

# Install Node.js dependencies for React frontend
cd frontend
npm install
cd ..
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Required
GOOGLE_API_KEY=your-google-gemini-api-key-here

# Optional
COLLEGE_WEBSITE_URL=https://yourcollege.edu
SERPER_API_KEY=your-serper-api-key-here
PUSHOVER_TOKEN=your-pushover-token
PUSHOVER_USER=your-pushover-user
```

### 3. Start the Application

You need to start both the backend API server and the frontend development server in separate terminals.

#### Step 1: Start the Backend API Server

**⚠️ IMPORTANT: Run this from the PROJECT ROOT directory (not from the frontend folder)**

1. **Navigate to the project root directory:**
   ```powershell
   # If you're in C:\Users\novap\Desktop\unibot_\, go into the inner folder:
   cd unibot_
   
   # You should now be in: C:\Users\novap\Desktop\unibot_\unibot_\
   # This is where the venv, backend, frontend folders are located
   
   # Verify you're in the right place - you should see these folders:
   # - venv\
   # - backend\
   # - frontend\
   # - agents\
   # - requirements.txt
   ```

2. **Activate your virtual environment (if using one):**

   Windows (PowerShell):
   ```powershell
   # If you get an execution policy error, run this first:
   # Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   
   .\venv\Scripts\Activate.ps1
   ```
   
   **Alternative for PowerShell (if activation script doesn't work):**
   ```powershell
   # Just use the venv's Python directly - no need to activate
   .\venv\Scripts\python.exe -m uvicorn backend.api_server:app --host 127.0.0.1 --port 8001
   ```

   Windows (CMD):
   ```cmd
   venv\Scripts\activate.bat
   ```

   Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

3. **Start the backend server:**
   ```bash
   python -m uvicorn backend.api_server:app --host 127.0.0.1 --port 8001
   ```

   Or if using the venv's Python directly (without activating):
   ```bash
   # Windows
   venv\Scripts\python.exe -m uvicorn backend.api_server:app --host 127.0.0.1 --port 8001

   # Linux/Mac
   venv/bin/python -m uvicorn backend.api_server:app --host 127.0.0.1 --port 8001
   ```

   The backend will start on `http://127.0.0.1:8001`
   
   **Keep this terminal window open!**

#### Step 2: Start the Frontend Development Server

**⚠️ IMPORTANT: Run this from the FRONTEND directory**

1. **Open a NEW terminal window** (keep the backend terminal running!)

2. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   # You should be in: C:\Users\novap\Desktop\unibot_\unibot_\frontend\
   ```

3. **Install dependencies (only needed the first time):**
   ```bash
   npm install
   ```

4. **Start the Vite development server:**
   ```bash
   npm run dev
   ```

   The frontend will start on `http://localhost:8080` and should automatically open in your browser.
   
   **Keep this terminal window open too!**

#### Summary

- **Backend API**: `http://127.0.0.1:8001`
- **Frontend**: `http://localhost:8080`

Keep both terminal windows open while using the application. Close them to stop the servers.

### 4. First Time Setup

1. **Scrape the College Website** (if not already done):
   - Ask UniBot: "Please scrape the college website at https://yourcollege.edu"
   - Or set `COLLEGE_WEBSITE_URL` in your `.env` file

2. **Ask Questions**:
   - "What courses are offered?"
   - "What are the admission requirements?"
   - "Tell me about the faculty"
   - "What facilities are available?"

## 🔧 How It Works

1. **Initialization**: UniBot initializes with a RAG system using ChromaDB vector store
2. **Website Scraping** (Optional): Scrapes college website content using Playwright
3. **Data Storage**: Scraped content is chunked, embedded using Google's `text-embedding-004`, and stored in ChromaDB
4. **Query Processing**: When users ask questions:
   - UniBot searches the knowledge base using semantic similarity
   - Retrieves the most relevant document chunks
   - Uses Gemini LLM (`gemini-2.5-flash`) to generate answers based on retrieved context
5. **Response Generation**: Provides accurate, context-aware answers with source citations

## 📊 Models Used

- **Chat Model**: `gemini-2.5-flash` - Fast, efficient response generation
- **Embedding Model**: `text-embedding-004` - High-quality embeddings for RAG

## 🛠️ Development

### Virtual Environment

**Activate virtual environment:**

Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

Windows (CMD):
```cmd
venv\Scripts\activate.bat
```

Linux/Mac:
```bash
source venv/bin/activate
```

### Utility Scripts

**Inspect Knowledge Base:**
```bash
python utils/inspect_knowledge_base.py
```

**Search Knowledge Base:**
```bash
python utils/inspect_knowledge_base.py "your search query"
```

## 📝 Example Queries

- Course information: "What computer science courses are available?"
- Admissions: "What are the requirements for admission?"
- Faculty: "Who are the professors in the engineering department?"
- Facilities: "What labs and facilities does the college have?"
- Events: "What events are happening this semester?"

## 🔒 Security Notes

- Never commit `.env` file (contains API keys)
- Never commit `chroma_db/` directory (large embeddings database)
- Never commit `venv/` directory (virtual environment)
- These are automatically excluded via `.gitignore`

## 📦 Project Structure

### Core Files
- `agents/unibot.py` - Core UniBot class with LangGraph workflow and RAG integration
- `agents/tools.py` - Tool definitions including RAG tools, web browsing, file management
- `agents/intent_detector.py` - Intent detection and out-of-scope query validation
- `retrieval/rag_system.py` - RAG system with ChromaDB vector store, hybrid search
- `ingestion/scraper.py` - Website scraper for college content
- `ingestion/pdf_processor.py` - PDF extraction and quality filtering (with OCR support)
- `ingestion/scrape_checkpoint.py` - Checkpoint system for resuming scrapes
- `ingestion/scrape_tracker.py` - URL tracking to avoid duplicate scraping

### Backend
- `backend/api_server.py` - FastAPI backend server with intent validation

### Frontend (React)
- `frontend/src/App.jsx` - Main React component
- `frontend/src/components/` - React components (Header, ChatContainer, InputArea, WelcomeScreen)
- `frontend/src/utils/` - Utility functions (API calls, message formatting)
- `frontend/index.html` - HTML template
- `frontend/styles.css` - Styling and layout
- `frontend/package.json` - Node.js dependencies
- `frontend/verify_setup.py` - Setup verification script

### Utilities
- `utils/inspect_knowledge_base.py` - Utility to inspect knowledge base contents

## 🐛 Troubleshooting

### Backend Not Starting
- Check if `GOOGLE_API_KEY` is set in `.env` file
- Verify Python dependencies are installed: `pip install -r requirements.txt`
- Check if port 8001 is already in use

### Frontend Not Connecting
- Ensure backend is running on `http://127.0.0.1:8001`
- Check browser console for errors (F12)
- Verify CORS is enabled in `api_server.py`

### Knowledge Base Empty
- Scrape the college website first
- Check `chroma_db/` directory exists and has data
- Use `python utils/inspect_knowledge_base.py` to verify

## 📄 License

This project is for educational purposes.

## 👨‍💻 Author

Created for 5th Semester External Project Presentation.
