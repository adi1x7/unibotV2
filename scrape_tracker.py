"""
Scrape tracker to remember what URLs have already been scraped
Prevents re-scraping the same URLs in future runs
"""
import json
import os
from typing import Set
from datetime import datetime

TRACKER_FILE = "scrape_tracker.json"

class ScrapeTracker:
    """Track scraped URLs to avoid re-scraping"""
    
    def __init__(self):
        self.scraped_urls: Set[str] = set()
        self.load()
    
    def load(self):
        """Load previously scraped URLs from file"""
        if os.path.exists(TRACKER_FILE):
            try:
                with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.scraped_urls = set(data.get('urls', []))
                    print(f"Loaded {len(self.scraped_urls)} previously scraped URLs")
            except Exception as e:
                print(f"WARNING: Could not load scrape tracker: {e}")
                self.scraped_urls = set()
        else:
            self.scraped_urls = set()
    
    def save(self):
        """Save scraped URLs to file"""
        try:
            data = {
                'urls': list(self.scraped_urls),
                'last_updated': datetime.now().isoformat(),
                'total_urls': len(self.scraped_urls)
            }
            with open(TRACKER_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"WARNING: Could not save scrape tracker: {e}")
    
    def is_scraped(self, url: str) -> bool:
        """Check if URL has been scraped before"""
        return url in self.scraped_urls
    
    def mark_scraped(self, url: str):
        """Mark URL as scraped"""
        self.scraped_urls.add(url)
    
    def mark_multiple_scraped(self, urls: list):
        """Mark multiple URLs as scraped"""
        self.scraped_urls.update(urls)
    
    def get_count(self) -> int:
        """Get count of tracked URLs"""
        return len(self.scraped_urls)
    
    def clear(self):
        """Clear all tracked URLs (for fresh start)"""
        self.scraped_urls.clear()
        if os.path.exists(TRACKER_FILE):
            os.remove(TRACKER_FILE)
        print("Scrape tracker cleared")

