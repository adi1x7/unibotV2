from playwright.async_api import async_playwright
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from dotenv import load_dotenv
import os
import requests
from langchain_core.tools import Tool
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_experimental.tools import PythonREPLTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from rag_system import RAGSystem
from college_scraper import CollegeScraper



load_dotenv(override=True)
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user = os.getenv("PUSHOVER_USER")
pushover_url = "https://api.pushover.net/1/messages.json"

# Initialize Serper only if API key is available (optional)
serper = None
serper_api_key = os.getenv("SERPER_API_KEY")
if serper_api_key:
    try:
        serper = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)
    except Exception:
        serper = None

async def playwright_tools():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
    return toolkit.get_tools(), browser, playwright


def push(text: str):
    """Send a push notification to the user"""
    requests.post(pushover_url, data = {"token": pushover_token, "user": pushover_user, "message": text})
    return "success"


def get_file_tools():
    toolkit = FileManagementToolkit(root_dir="sandbox")
    return toolkit.get_tools()


def get_rag_tools(rag_system: RAGSystem):
    """Get RAG-related tools for querying college information"""
    
    def query_college_knowledge_base(query: str, content_type: str = None) -> str:
        """
        Search the college knowledge base for information related to the query.
        Use this tool when the user asks questions about the college, courses, admissions, 
        faculty, facilities, or any college-related information.
        
        Args:
            query: The question or query about the college
            content_type: Optional filter for specific content type (e.g., "syllabus", "pdf", "course_info")
        """
        try:
            # Auto-detect content type from query
            query_lower = query.lower()
            detected_type = None
            detected_category = None
            
            if "syllabus" in query_lower or "syllabi" in query_lower:
                detected_type = "syllabus"
                detected_category = "academic"
            elif "course" in query_lower and ("structure" in query_lower or "curriculum" in query_lower):
                detected_type = "course_info"
                detected_category = "academic"
            elif "admission" in query_lower:
                detected_category = "admission"
            elif "faculty" in query_lower or "professor" in query_lower or "staff" in query_lower:
                detected_category = "academic"
            elif "placement" in query_lower:
                detected_category = "placement"
            elif "facility" in query_lower or "infrastructure" in query_lower:
                detected_category = "facilities"
            
            # Use provided type or detected type
            search_type = content_type or detected_type
            
            # Search with filters if available
            docs = rag_system.search(
                query, 
                k=6,  # Get more results for better context
                filter_type=search_type,
                filter_category=detected_category
            )
            
            # If filtered search returns no results, try without filters
            if not docs and (search_type or detected_category):
                docs = rag_system.search(query, k=6)
            
            # If still no results, try with just the query expanded
            if not docs:
                # Try a more general search
                expanded_query = query
                if "syllabus" in query.lower():
                    expanded_query = query + " course curriculum"
                elif "faculty" in query.lower() or "professor" in query.lower():
                    expanded_query = query + " staff department"
                elif "admission" in query.lower():
                    expanded_query = query + " requirements eligibility"
                
                if expanded_query != query:
                    docs = rag_system.search(expanded_query, k=6)
            
            if docs:
                context_parts = []
                sources_list = []  # Collect sources for easy reference
                for i, doc in enumerate(docs, 1):
                    source = doc.metadata.get("source", "Unknown")
                    title = doc.metadata.get("title", "")
                    doc_type = doc.metadata.get("type", "document")
                    content = doc.page_content
                    
                    # Format source as clickable markdown link - URL itself is the link text
                    if source != "Unknown":
                        source_link = f"[{source}]({source})"
                    else:
                        source_link = f"Source {i}: {source}"
                    
                    context_parts.append(f"Source {i}: {source_link} | Type: {doc_type}\n{title}\n{content}\n")
                    sources_list.append(source)
                
                # Add sources section at the end for easy reference - URLs as clickable links
                # Format as markdown links so they're clickable
                sources_section = "\n\n**SOURCES:**\n"
                for i, src in enumerate(sources_list, 1):
                    if src != "Unknown":
                        # Format as clickable markdown link - URL is both text and link
                        sources_section += f"{i}. [{src}]({src})\n"
                
                return f"Relevant information from college knowledge base:\n\n" + "\n---\n".join(context_parts) + sources_section
            else:
                return "No relevant information found in the knowledge base. You may need to scrape the website first or the information might not be available."
        except Exception as e:
            return f"Error querying knowledge base: {str(e)}"
    
    # Note: scrape_college_website needs to be synchronous for LangChain tools
    # So we create a sync wrapper that handles the async scraping
    import asyncio
    import nest_asyncio
    
    def scrape_college_website_sync(base_url: str) -> str:
        """Synchronous wrapper for scraping"""
        try:
            
            # Allow nested event loops
            try:
                nest_asyncio.apply()
            except:
                pass
            
            async def run_scrape():
                # Use deeper crawling settings for comprehensive knowledge base
                scraper = CollegeScraper(
                    base_url=base_url, 
                    max_pages=500,  # Increased for deep comprehensive scraping
                    max_depth=8,    # Much deeper crawling to get nested pages
                    include_pdfs=True  # Include PDF processing
                )
                return await scraper.scrape_website()
            
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, we need to run in a separate thread
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(lambda: asyncio.run(run_scrape()))
                        scraped_content = future.result(timeout=300)  # 5 minute timeout
                else:
                    scraped_content = asyncio.run(run_scrape())
            except RuntimeError:
                # No event loop, create one
                scraped_content = asyncio.run(run_scrape())
            
            if scraped_content:
                # Add all content in batch for better performance
                texts = []
                metadatas = []
                successful = 0
                failed = 0
                
                for content in scraped_content:
                    try:
                        url = content.get('url', 'Unknown')
                        text = content.get('content', '')
                        title = content.get('title', '')
                        content_type = content.get('type', 'scraped_content')
                        
                        if text and len(text) > 50:  # Only add if we have meaningful content
                            texts.append(text)
                            
                            # Enhanced metadata with content type detection
                            metadata = {
                                "source": url,
                                "type": content_type,
                                "title": title
                            }
                            
                            # Auto-detect content type from URL for better organization
                            url_lower = url.lower()
                            if "syllabus" in url_lower or "syllabi" in url_lower:
                                metadata["type"] = "syllabus"
                                metadata["category"] = "academic"
                            elif url_lower.endswith(".pdf") or content_type == "pdf":
                                metadata["type"] = "pdf"
                                if "syllabus" in url_lower:
                                    metadata["category"] = "academic"
                                    metadata["type"] = "syllabus"
                                elif "course" in url_lower or "curriculum" in url_lower:
                                    metadata["category"] = "academic"
                                else:
                                    metadata["category"] = "document"
                            elif "course" in url_lower or "curriculum" in url_lower:
                                metadata["type"] = "course_info"
                                metadata["category"] = "academic"
                            elif "admission" in url_lower:
                                metadata["type"] = "admission_info"
                                metadata["category"] = "admission"
                            elif "faculty" in url_lower or "staff" in url_lower:
                                metadata["type"] = "faculty_info"
                                metadata["category"] = "academic"
                            elif "placement" in url_lower:
                                metadata["category"] = "placement"
                            elif "facility" in url_lower or "infrastructure" in url_lower:
                                metadata["category"] = "facilities"
                            
                            metadatas.append(metadata)
                            successful += 1
                        else:
                            failed += 1
                    except Exception as e:
                        print(f"Error processing content: {e}")
                        failed += 1
                
                # Add all documents at once (with duplicate checking)
                if texts:
                    try:
                        print(f"\n📊 Adding {len(texts)} items to knowledge base (checking for duplicates)...")
                        rag_system.add_documents(texts, metadatas, skip_duplicates=True)
                        return f"Successfully scraped {len(scraped_content)} pages from {base_url}. Added {successful} pages to knowledge base ({failed} skipped)."
                    except Exception as e:
                        return f"Scraped {len(scraped_content)} pages but error adding to knowledge base: {str(e)}"
                else:
                    return f"Scraped {len(scraped_content)} pages but no valid content to add."
            else:
                return f"No content was scraped from {base_url}. Please check the URL and try again."
        except Exception as e:
            return f"Error scraping website: {str(e)}"
    
    rag_query_tool = Tool(
        name="query_college_knowledge_base",
        func=query_college_knowledge_base,
        description="Search the college knowledge base for information. Use this for questions about the college, courses, admissions, faculty, facilities, policies, events, or any college-related information."
    )
    
    scrape_tool = Tool(
        name="scrape_college_website",
        func=scrape_college_website_sync,
        description="Scrape the college website and add content to the knowledge base. Use this when you need to gather information from the college website. Provide the base URL of the college website."
    )
    
    return [rag_query_tool, scrape_tool]


async def other_tools(rag_system: RAGSystem = None):
    push_tool = Tool(name="send_push_notification", func=push, description="Use this tool when you want to send a push notification")
    file_tools = get_file_tools()

    base_tools = file_tools + [push_tool]
    
    # Add search tool only if Serper API key is available
    if serper:
        tool_search = Tool(
            name="search",
            func=serper.run,
            description="Use this tool when you want to get the results of an online web search"
        )
        base_tools.append(tool_search)

    python_repl = PythonREPLTool()
    base_tools.append(python_repl)
    
    # Add RAG tools if RAG system is provided
    if rag_system:
        rag_tools = get_rag_tools(rag_system)
        base_tools.extend(rag_tools)
    
    return base_tools

