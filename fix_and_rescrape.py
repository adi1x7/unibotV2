"""
Complete fix script: Clears database, re-scrapes, and verifies
Run this once to fix everything automatically
"""
import os
import shutil
import sys
import asyncio
from rag_system import RAGSystem
from college_scraper import CollegeScraper

def clear_database():
    """Clear the knowledge base and related files"""
    db_path = "./chroma_db"
    checkpoint_file = "scrape_checkpoint.json"
    tracker_file = "scrape_tracker.json"
    
    cleared_items = []
    
    # Clear database
    if os.path.exists(db_path):
        try:
            shutil.rmtree(db_path)
            cleared_items.append("knowledge base")
        except PermissionError:
            print("❌ Error: Cannot delete database - it's being used by another process.")
            print("\nPlease stop UniBot first (Ctrl+C), then run this script again.")
            return False
        except Exception as e:
            print(f"❌ Error clearing database: {e}")
            return False
    else:
        cleared_items.append("knowledge base (already empty)")
    
    # Keep checkpoint file (it has the PDF URLs list and HTML pages)
    # We'll just remove PDFs from tracker so they get re-processed
    # This way we don't have to re-crawl HTML pages
    
    # Remove PDF URLs from tracker (so PDFs get re-processed, but keep HTML pages)
    # This way we don't have to re-scrape all HTML pages (which takes hours)
    if os.path.exists(tracker_file):
        try:
            import json
            with open(tracker_file, 'r', encoding='utf-8') as f:
                tracker_data = json.load(f)
            
            urls = tracker_data.get('urls', [])
            # Remove only PDF URLs from tracker
            pdf_urls_removed = 0
            filtered_urls = []
            for url in urls:
                if url.lower().endswith('.pdf') or '.pdf' in url.lower():
                    pdf_urls_removed += 1
                else:
                    filtered_urls.append(url)  # Keep HTML pages
            
            # Save updated tracker (without PDF URLs)
            tracker_data['urls'] = filtered_urls
            tracker_data['total_urls'] = len(filtered_urls)
            with open(tracker_file, 'w', encoding='utf-8') as f:
                json.dump(tracker_data, f, indent=2, ensure_ascii=False)
            
            if pdf_urls_removed > 0:
                cleared_items.append(f"PDF URLs from tracker ({pdf_urls_removed} PDFs will be re-processed)")
        except Exception as e:
            print(f"⚠️  Warning: Could not update tracker file: {e}")
            print("   Will clear entire tracker file instead...")
            try:
                os.remove(tracker_file)
                cleared_items.append("tracker file (full clear)")
            except Exception as e2:
                print(f"⚠️  Warning: Could not delete tracker file: {e2}")
    
    if cleared_items:
        print(f"✅ Cleared: {', '.join(cleared_items)}")
        print("\n💡 Note: HTML pages are preserved in tracker (won't be re-scraped)")
        print("   Only PDFs will be re-processed with quality filtering")
    else:
        print("✅ Knowledge base is already empty!")
    
    return True

async def scrape_college(base_url: str):
    """Scrape the college website"""
    print(f"\n{'='*60}")
    print(f"Starting to scrape: {base_url}")
    print(f"{'='*60}\n")
    
    # Use deep scraping settings
    scraper = CollegeScraper(
        base_url=base_url, 
        max_pages=500,  # Deep comprehensive scraping
        max_depth=8,    # Much deeper crawling
        include_pdfs=True  # Include PDF processing
    )
    scraped_content = await scraper.scrape_website()
    
    return scraped_content

def add_to_knowledge_base(scraped_content, rag_system):
    """Add scraped content to knowledge base"""
    if not scraped_content:
        print("❌ No content to add!")
        return False
    
    print(f"\n{'='*60}")
    print(f"Adding {len(scraped_content)} pages to knowledge base...")
    print(f"{'='*60}\n")
    
    # Prepare batch data
    texts = []
    metadatas = []
    successful = 0
    failed = 0
    
    for content in scraped_content:
        try:
            url = content.get('url', 'Unknown')
            text = content.get('content', '')
            title = content.get('title', '')
            
            if text and len(text) > 50:
                texts.append(text)
                metadata = {
                    "source": url,
                    "type": "scraped_content",
                    "title": title
                }
                metadatas.append(metadata)
                successful += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ⚠ Error processing: {e}")
            failed += 1
    
    if texts:
        try:
            rag_system.add_documents(texts, metadatas)
            print(f"\n✅ Successfully added {successful} pages ({failed} skipped)")
            return True
        except Exception as e:
            print(f"\n❌ Error adding to knowledge base: {e}")
            return False
    else:
        print(f"\n❌ No valid content to add ({failed} pages had insufficient content)")
        return False

def verify_knowledge_base(rag_system):
    """Verify the knowledge base has content"""
    print(f"\n{'='*60}")
    print("Verifying knowledge base...")
    print(f"{'='*60}\n")
    
    stats = rag_system.get_stats()
    print(f"📊 Total documents: {stats['total_documents']}")
    
    if stats['total_documents'] == 0:
        print("❌ Knowledge base is empty!")
        return False
    
    # Get unique sources
    try:
        collection = rag_system.vectorstore._collection
        if collection:
            results = collection.get(limit=min(200, stats['total_documents']))
            if results and 'metadatas' in results:
                sources = set()
                for metadata in results['metadatas']:
                    if metadata and 'source' in metadata:
                        sources.add(metadata['source'])
                
                print(f"📄 Unique sources: {len(sources)}")
                if len(sources) > 1:
                    print(f"✅ Multiple sources found - looks good!")
                    print(f"\nSample sources:")
                    for i, source in enumerate(list(sources)[:5], 1):
                        print(f"  {i}. {source}")
                    if len(sources) > 5:
                        print(f"  ... and {len(sources) - 5} more")
                elif len(sources) == 1:
                    print(f"⚠️  Only 1 source found - might need to check")
                return True
    except Exception as e:
        print(f"⚠️  Could not verify sources: {e}")
    
    return True

async def main():
    """Main function"""
    print("="*60)
    print("UniBot Complete Fix & Re-scrape Script")
    print("="*60)
    print("\nThis script will:")
    print("1. Clear the existing knowledge base")
    print("2. Re-scrape your college website")
    print("3. Add all content to the knowledge base")
    print("4. Verify everything worked")
    print()
    
    # Get college URL
    college_url = os.getenv("COLLEGE_WEBSITE_URL", "https://bmsit.ac.in")
    print(f"College URL: {college_url}")
    print()
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    # Step 1: Clear database
    print("\n" + "="*60)
    print("Step 1: Clearing knowledge base...")
    print("="*60)
    if not clear_database():
        print("\n❌ Failed to clear database. Please stop UniBot and try again.")
        return
    
    # Step 2: Initialize RAG system
    print("\n" + "="*60)
    print("Step 2: Initializing RAG system...")
    print("="*60)
    rag_system = RAGSystem()
    print("✅ RAG system initialized")
    
    # Step 3: Scrape
    print("\n" + "="*60)
    print("Step 3: Scraping college website...")
    print("="*60)
    print("This may take 5-15 minutes...\n")
    
    try:
        scraped_content = await scrape_college(college_url)
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        return
    
    if not scraped_content:
        print("\n❌ No content was scraped!")
        return
    
    print(f"\n✅ Scraped {len(scraped_content)} pages")
    
    # Step 4: Add to knowledge base
    print("\n" + "="*60)
    print("Step 4: Adding to knowledge base...")
    print("="*60)
    
    if not add_to_knowledge_base(scraped_content, rag_system):
        print("\n❌ Failed to add content to knowledge base")
        return
    
    # Step 5: Verify
    if not verify_knowledge_base(rag_system):
        print("\n⚠️  Verification showed some issues, but content was added")
    
    print("\n" + "="*60)
    print("✅ COMPLETE!")
    print("="*60)
    print("\nYour knowledge base is now ready!")
    print("You can now:")
    print("1. Start UniBot: python app.py")
    print("2. Ask questions about your college")
    print("3. Check the knowledge base: python inspect_knowledge_base.py")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

