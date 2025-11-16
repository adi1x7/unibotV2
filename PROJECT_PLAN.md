# UniBot Project Plan

## 🎯 Your Problem Statement

**Goal**: Build an Agentic AI college assistant that answers queries about:
- **Timetable** - Class schedules, exam schedules
- **Fees** - Tuition, hostel fees, payment details
- **Hostels** - Accommodation, facilities, rules
- **Academics** - Syllabus, course details, curriculum
- **Facilities** - Labs, library, sports, infrastructure

**How**: Web scraping + RAG pipeline to extract and use college website data (HTML + PDFs)

---

## ✅ What You Already Have

### 1. **Agentic AI System** ✓
- **LangGraph** - Multi-agent workflow system
- **UniBot** - Your AI assistant that can use tools and make decisions
- **Tools Available**:
  - RAG knowledge base query
  - Web scraping
  - Web browsing
  - Code execution
  - File management

### 2. **RAG Pipeline** ✓
- **ChromaDB** - Vector database to store scraped data
- **OpenAI Embeddings** - Converts text to vectors for search
- **Text Chunking** - Splits documents into searchable pieces
- **Semantic Search** - Finds relevant information from knowledge base

### 3. **Web Scraping** ✓
- **Playwright** - Scrapes HTML pages
- **PDF Processing** - Extracts text from PDFs (syllabi, documents)
- **Deep Crawling** - Goes 8 levels deep, 500 pages
- **Checkpoint System** - Can resume if interrupted

### 4. **Data Storage** ✓
- **HTML Pages** - Stored as text chunks
- **PDFs** - Extracted and stored (syllabi, course docs)
- **Metadata** - URLs, types, categories tracked

---

## 📋 What You Need to Do

### Step 1: **Scrape College Website** (One-time setup)

**Run this command:**
```bash
python fix_and_rescrape.py
```

**What it does:**
- Scrapes 500 HTML pages (depth 8)
- Finds and processes all PDFs
- Stores everything in ChromaDB vector database
- Takes 30-60 minutes depending on website size

**What gets scraped:**
- All HTML pages (homepage, departments, courses, facilities, etc.)
- All PDFs (syllabi, fee structures, hostel rules, timetables, etc.)

### Step 2: **Test the System**

**Start UniBot:**
```bash
python app.py
```

**Ask test questions:**
- "What courses are offered in Computer Science?"
- "What is the fee structure?"
- "Tell me about hostel facilities"
- "Show me the syllabus for Data Structures course"

### Step 3: **Verify Data Quality**

**Check what was scraped:**
```bash
python inspect_knowledge_base.py
```

**This shows:**
- How many documents stored
- How many PDFs found
- Sample content
- Unique sources

---

## 🔍 How It Works (Simple Explanation)

### **Data Collection Phase** (One-time)

```
College Website
    ↓
Web Scraper (Playwright)
    ↓
HTML Pages + PDFs
    ↓
Text Extraction
    ↓
Chunking (Split into pieces)
    ↓
Embedding (Convert to vectors)
    ↓
ChromaDB (Vector Database)
```

### **Query Answering Phase** (Every time user asks)

```
User Question
    ↓
UniBot (Agentic AI)
    ↓
Search Knowledge Base (RAG)
    ↓
Find Relevant Chunks
    ↓
LLM Generates Answer
    ↓
Response to User
```

---

## 📊 Data Coverage for Your Queries

### ✅ **Timetable**
- **Source**: HTML pages (academics section, notices)
- **PDFs**: Exam schedules, class timetables
- **Query Example**: "What is the exam schedule for semester 3?"

### ✅ **Fees**
- **Source**: HTML pages (admissions, fees section)
- **PDFs**: Fee structure documents, payment details
- **Query Example**: "What is the hostel fee for first year?"

### ✅ **Hostels**
- **Source**: HTML pages (hostel section, facilities)
- **PDFs**: Hostel rules, application forms
- **Query Example**: "What facilities are available in the hostel?"

### ✅ **Academics (Syllabus, Courses)**
- **Source**: HTML pages (department pages, course pages)
- **PDFs**: **Syllabi PDFs** (most important!)
- **Query Example**: "What topics are covered in Database Management Systems course?"

### ✅ **Facilities**
- **Source**: HTML pages (infrastructure, labs, library)
- **PDFs**: Facility brochures, lab equipment lists
- **Query Example**: "What computer labs are available?"

---

## 🎯 Current Status

### ✅ **Working:**
- Web scraping (HTML + PDFs)
- RAG system (storage + retrieval)
- Agentic AI (UniBot with tools)
- PDF processing (syllabi extraction)
- Deep crawling (500 pages, 8 depth)

### ⚠️ **What to Verify:**
1. **Data Completeness**: Does scraping cover all needed pages?
   - Check: Run `inspect_knowledge_base.py` after scraping
   - Look for: Timetable pages, fee pages, hostel pages

2. **PDF Quality**: Are syllabi PDFs being extracted properly?
   - Check: Look for PDFs in knowledge base
   - Test: Ask "What is the syllabus for [course]?"

3. **Query Accuracy**: Can UniBot answer your specific queries?
   - Test: Ask questions about timetable, fees, hostels
   - Improve: If missing data, scrape more pages

---

## 🚀 Next Steps (Action Plan)

### **Immediate (Today):**
1. ✅ Run full scrape: `python fix_and_rescrape.py`
2. ✅ Verify data: `python inspect_knowledge_base.py`
3. ✅ Test queries: Start UniBot and ask questions

### **If Data is Missing:**
1. Check which pages weren't scraped
2. Manually add URLs to scrape more pages
3. Re-run scraper (it won't duplicate existing data)

### **If Queries Don't Work Well:**
1. Check if relevant data exists in knowledge base
2. Improve scraping to get missing pages
3. Test with different query phrasings

---

## 💡 Key Points for Your Project

### **Agentic AI:**
- UniBot uses **LangGraph** - it's an agent that can:
  - Decide which tool to use
  - Search knowledge base
  - Browse web if needed
  - Generate answers

### **RAG Pipeline:**
- **Retrieval**: Finds relevant chunks from knowledge base
- **Augmentation**: Adds context to LLM
- **Generation**: LLM creates answer from context

### **Efficiency:**
- **Vector Search**: Fast semantic search (not keyword)
- **Chunking**: Only retrieves relevant parts
- **Embeddings**: Understands meaning, not just words

---

## 📝 For Your Project Report

### **What to Document:**
1. **Problem Statement**: College assistant for timetable, fees, hostels, academics, facilities
2. **Solution**: Agentic AI + Web Scraping + RAG Pipeline
3. **Architecture**: 
   - Data Collection (Scraping)
   - Data Storage (ChromaDB)
   - Query Processing (RAG + LLM)
4. **Results**: 
   - Number of pages scraped
   - Number of PDFs processed
   - Query accuracy examples
5. **Technologies**: LangGraph, Playwright, ChromaDB, OpenAI, RAG

---

## ❓ Questions to Answer

1. **Does your college website have all this info?**
   - Check: Timetable pages, fee pages, hostel pages, syllabus PDFs
   - If not: You may need to supplement with manual data

2. **Are PDFs accessible?**
   - Some PDFs might be behind login
   - Some might be corrupted (we handle this)

3. **What's your success metric?**
   - Can answer X% of queries correctly?
   - Covers all 5 categories (timetable, fees, hostels, academics, facilities)?

---

## 🎓 Summary

**You have everything you need!** The system is:
- ✅ Built and working
- ✅ Scraping HTML + PDFs
- ✅ Storing in vector database
- ✅ Using RAG for queries
- ✅ Agentic AI making decisions

**Just need to:**
1. Run the full scrape
2. Test with your queries
3. Document the results

Good luck with your project! 🚀

