"""
Checkpoint system for scraping - allows resuming interrupted scrapes
"""
import json
import os
from typing import List, Dict
from datetime import datetime

CHECKPOINT_FILE = "scrape_checkpoint.json"

class ScrapeCheckpoint:
    """Save and restore scraping progress"""
    
    def __init__(self):
        self.checkpoint_data = {
            'scraped_content': [],
            'pdf_urls': [],
            'visited_urls': [],
            'urls_to_visit': [],
            'scraped_count': 0,
            'last_updated': None
        }
        self.load()
    
    def load(self):
        """Load checkpoint if exists"""
        if os.path.exists(CHECKPOINT_FILE):
            try:
                with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                    self.checkpoint_data = json.load(f)
                print(f"Loaded checkpoint: {self.checkpoint_data['scraped_count']} pages, {len(self.checkpoint_data['pdf_urls'])} PDFs queued")
            except Exception as e:
                print(f"WARNING: Could not load checkpoint: {e}")
                self.checkpoint_data = {
                    'scraped_content': [],
                    'pdf_urls': [],
                    'visited_urls': [],
                    'urls_to_visit': [],
                    'scraped_count': 0,
                    'last_updated': None
                }
    
    def save(self, scraped_content: List[Dict], pdf_urls: List[str], 
             visited_urls: set, urls_to_visit: List[str], scraped_count: int):
        """Save checkpoint"""
        try:
            self.checkpoint_data = {
                'scraped_content': scraped_content,
                'pdf_urls': pdf_urls,
                'visited_urls': list(visited_urls),
                'urls_to_visit': urls_to_visit,
                'scraped_count': scraped_count,
                'last_updated': datetime.now().isoformat()
            }
            with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.checkpoint_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"WARNING: Could not save checkpoint: {e}")
    
    def get_checkpoint(self) -> Dict:
        """Get checkpoint data"""
        return self.checkpoint_data
    
    def clear(self):
        """Clear checkpoint"""
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
        self.checkpoint_data = {
            'scraped_content': [],
            'pdf_urls': [],
            'visited_urls': [],
            'urls_to_visit': [],
            'scraped_count': 0,
            'last_updated': None
        }
        print("Checkpoint cleared")

