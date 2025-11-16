"""
Utility script to inspect what's stored in the UniBot knowledge base
"""
from rag_system import RAGSystem
import os

def inspect_knowledge_base():
    """Inspect and display what's in the knowledge base"""
    print("=" * 60)
    print("UniBot Knowledge Base Inspector")
    print("=" * 60)
    print()
    
    # Initialize RAG system
    rag = RAGSystem()
    
    # Get statistics
    stats = rag.get_stats()
    print(f"📊 Knowledge Base Statistics:")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Storage location: {stats['persist_directory']}")
    print(f"   Collection name: {stats['collection_name']}")
    print()
    
    if stats['total_documents'] == 0:
        print("⚠️  Knowledge base is empty. Scrape a website first!")
        return
    
    # Sample some documents
    print("🔍 Sample Queries to see what's stored:")
    print()
    
    sample_queries = [
        "courses",
        "admission",
        "faculty",
        "facilities",
        "department",
        "contact"
    ]
    
    for query in sample_queries:
        print(f"Query: '{query}'")
        docs = rag.search(query, k=2)
        if docs:
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('source', 'Unknown')
                title = doc.metadata.get('title', 'No title')
                content_preview = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                print(f"  {i}. Source: {source}")
                print(f"     Title: {title}")
                print(f"     Preview: {content_preview}")
                print()
        else:
            print(f"  No results found")
        print()
    
    # Get all unique sources - try to get more documents
    print("📄 All Sources in Knowledge Base:")
    print()
    
    # Try multiple queries to get diverse results
    all_sources = set()
    queries = ["college", "department", "admission", "course", "faculty", "facility"]
    
    for query in queries:
        docs = rag.search(query, k=min(20, stats['total_documents']))
        for doc in docs:
            source = doc.metadata.get('source', 'Unknown')
            all_sources.add(source)
    
    # If we still don't have many, try getting all documents directly from the collection
    if len(all_sources) <= 1 and stats['total_documents'] > 0:
        try:
            # Try to get documents directly from the collection
            collection = rag.vectorstore._collection
            if collection:
                # Get all documents from the collection
                results = collection.get(limit=min(100, stats['total_documents']))
                if results and 'metadatas' in results:
                    for metadata in results['metadatas']:
                        if metadata and 'source' in metadata:
                            all_sources.add(metadata['source'])
        except Exception as e:
            print(f"  (Could not retrieve all sources: {e})")
    
    if all_sources:
        for i, source in enumerate(sorted(all_sources), 1):
            print(f"  {i}. {source}")
    else:
        print("  (No sources found)")
    
    print()
    print(f"Total unique sources: {len(all_sources)}")
    print()
    
    # Show some sample content
    print("=" * 60)
    print("Sample Content (first 3 documents):")
    print("=" * 60)
    print()
    
    sample_docs = rag.search("", k=3) if stats['total_documents'] > 0 else []
    for i, doc in enumerate(sample_docs, 1):
        print(f"Document {i}:")
        print(f"  URL: {doc.metadata.get('source', 'Unknown')}")
        print(f"  Title: {doc.metadata.get('title', 'No title')}")
        print(f"  Content length: {len(doc.page_content)} characters")
        print(f"  Content preview:")
        print(f"  {doc.page_content[:300]}...")
        print()
        print("-" * 60)
        print()

def search_knowledge_base(query: str, k: int = 5):
    """Search the knowledge base for a specific query"""
    print(f"🔍 Searching for: '{query}'")
    print()
    
    rag = RAGSystem()
    docs = rag.search(query, k=k)
    
    if not docs:
        print("No results found.")
        return
    
    print(f"Found {len(docs)} result(s):")
    print()
    
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get('source', 'Unknown')
        title = doc.metadata.get('title', 'No title')
        
        print(f"Result {i}:")
        print(f"  Source: {source}")
        print(f"  Title: {title}")
        print(f"  Content:")
        print(f"  {doc.page_content}")
        print()
        print("-" * 60)
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # If query provided, search for it
        query = " ".join(sys.argv[1:])
        search_knowledge_base(query)
    else:
        # Otherwise, show overview
        inspect_knowledge_base()
        
        print()
        print("💡 Tip: To search for specific content, run:")
        print("   python inspect_knowledge_base.py 'your search query'")
        print()
        print("Example:")
        print("   python inspect_knowledge_base.py courses")
        print("   python inspect_knowledge_base.py admission requirements")

