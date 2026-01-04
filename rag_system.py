"""
RAG (Retrieval Augmented Generation) system for UniBot
Handles document storage, embedding, and retrieval for college information
"""
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class RAGSystem:
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "college_data"):
        """
        Initialize the RAG system with vector store
        
        Args:
            persist_directory: Directory to persist the vector database
            collection_name: Name of the collection in Chroma
        """
        # Verify API key is set
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable is not set. "
                "Please set it in your .env file or environment variables."
            )
        
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize or load the existing vector store"""
        if os.path.exists(self.persist_directory):
            # Load existing vector store
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
        else:
            # Create new vector store
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
    
    def get_existing_sources(self) -> set:
        """Get set of all source URLs already in the knowledge base"""
        try:
            collection = self.vectorstore._collection
            if collection:
                results = collection.get(limit=10000)  # Get up to 10k documents
                if results and 'metadatas' in results:
                    sources = set()
                    for metadata in results['metadatas']:
                        if metadata and 'source' in metadata:
                            sources.add(metadata['source'])
                    return sources
        except Exception as e:
            print(f"⚠️  Could not check existing sources: {e}")
        return set()
    
    def add_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None, skip_duplicates: bool = True):
        """
        Add documents to the vector store with duplicate checking
        
        Args:
            texts: List of text documents to add
            metadatas: Optional list of metadata dictionaries for each document
            skip_duplicates: If True, skip documents with URLs already in knowledge base
        """
        if not texts:
            return
        
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        # Ensure metadatas list matches texts list length
        if len(metadatas) != len(texts):
            metadatas = metadatas[:len(texts)] + [{}] * (len(texts) - len(metadatas))
        
        # Check for existing sources if skip_duplicates is enabled
        existing_sources = set()
        if skip_duplicates:
            existing_sources = self.get_existing_sources()
        
        # Create Document objects, filtering duplicates
        documents = []
        skipped_count = 0
        for text, meta in zip(texts, metadatas):
            if text and len(text.strip()) > 0:  # Only add non-empty documents
                # Ensure source URL is in metadata
                if 'source' not in meta:
                    meta['source'] = 'Unknown'
                
                # Skip if URL already exists
                if skip_duplicates and meta['source'] in existing_sources:
                    skipped_count += 1
                    continue
                
                documents.append(Document(page_content=text, metadata=meta))
        
        if skipped_count > 0:
            print(f"  ⏭️  Skipped {skipped_count} duplicate(s) already in knowledge base")
        
        if not documents:
            if skipped_count > 0:
                print("  ℹ️  All documents were duplicates, nothing to add")
            else:
                print("Warning: No valid documents to add after filtering")
            return
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        if not chunks:
            print("Warning: No chunks created from documents")
            return
        
        # Add to vector store in batches (ChromaDB has batch size limit)
        batch_size = 5000  # Safe batch size for ChromaDB
        total_chunks = len(chunks)
        added_count = 0
        
        try:
            for i in range(0, total_chunks, batch_size):
                batch = chunks[i:i + batch_size]
                self.vectorstore.add_documents(batch)
                added_count += len(batch)
                # Show progress for large batches
                if total_chunks > batch_size:
                    print(f"  [BATCH] Added batch {i//batch_size + 1}: {added_count}/{total_chunks} chunks", flush=True)
            
            # ChromaDB automatically persists, no need to call persist() in newer versions
            print(f"[OK] Added {added_count} chunks from {len(documents)} documents to knowledge base")
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            raise
    
    def add_scraped_content(self, url: str, content: str, title: Optional[str] = None, content_type: str = "scraped_content"):
        """
        Add scraped content from a URL to the vector store
        
        Args:
            url: Source URL of the content
            content: Text content scraped from the URL
            title: Optional title of the page
            content_type: Type of content (e.g., "scraped_content", "pdf", "syllabus", "course_info")
        """
        metadata = {"source": url, "type": content_type}
        if title:
            metadata["title"] = title
        
        # Detect content type from URL if not specified
        if content_type == "scraped_content":
            url_lower = url.lower()
            if "syllabus" in url_lower or "syllabi" in url_lower:
                metadata["type"] = "syllabus"
            elif "pdf" in url_lower or url_lower.endswith(".pdf"):
                metadata["type"] = "pdf"
            elif "course" in url_lower or "curriculum" in url_lower:
                metadata["type"] = "course_info"
            elif "admission" in url_lower:
                metadata["type"] = "admission_info"
            elif "faculty" in url_lower or "staff" in url_lower:
                metadata["type"] = "faculty_info"
        
        self.add_documents([content], [metadata])
    
    def search(self, query: str, k: int = 4, filter_type: Optional[str] = None, filter_category: Optional[str] = None) -> List[Document]:
        """
        Search for relevant documents using similarity search
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            filter_type: Optional filter by content type (e.g., "syllabus", "pdf", "course_info")
            filter_category: Optional filter by category (e.g., "academic", "admission", "facilities")
            
        Returns:
            List of relevant Document objects
        """
        if self.vectorstore is None:
            return []
        
        # Build filter if needed
        # ChromaDB requires filters in a specific format - use only one filter at a time
        # If both are provided, prefer filter_type
        where_filter = None
        if filter_type:
            where_filter = {"type": filter_type}
        elif filter_category:
            where_filter = {"category": filter_category}
        
        if where_filter:
            try:
                return self.vectorstore.similarity_search(query, k=k, filter=where_filter)
            except Exception:
                # If filtered search fails, fall back to unfiltered search
                return self.vectorstore.similarity_search(query, k=k)
        else:
            return self.vectorstore.similarity_search(query, k=k)
    
    def search_with_scores(self, query: str, k: int = 4):
        """
        Search with similarity scores
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
        Returns:
            List of tuples (Document, score)
        """
        if self.vectorstore is None:
            return []
        
        return self.vectorstore.similarity_search_with_score(query, k=k)
    
    def get_relevant_context(self, query: str, k: int = 4) -> str:
        """
        Get formatted context string from relevant documents
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
        Returns:
            Formatted string with relevant context
        """
        docs = self.search(query, k=k)
        
        if not docs:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            title = doc.metadata.get("title", "")
            content = doc.page_content
            
            context_parts.append(f"[Source {i}: {source}]\n{title}\n{content}\n")
        
        return "\n---\n".join(context_parts)
    
    def clear_database(self):
        """Clear all documents from the vector store"""
        if os.path.exists(self.persist_directory):
            import shutil
            shutil.rmtree(self.persist_directory)
        self._initialize_vectorstore()
    
    def get_stats(self) -> dict:
        """Get statistics about the vector store"""
        if self.vectorstore is None:
            return {"total_documents": 0}
        
        # Get collection count
        collection = self.vectorstore._collection
        count = collection.count() if collection else 0
        
        return {
            "total_documents": count,
            "persist_directory": self.persist_directory,
            "collection_name": self.collection_name
        }

