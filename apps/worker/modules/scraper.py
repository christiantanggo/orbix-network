"""
Scraper module for fetching news from RSS and HTML sources
"""
import hashlib
import logging
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import Dict, List
from modules.database import Database

logger = logging.getLogger(__name__)


class Scraper:
    """Handles scraping from RSS and HTML sources"""
    
    CATEGORIES = [
        'AI & Automation Takeovers',
        'Corporate Collapses & Reversals',
        'Tech Decisions With Massive Fallout',
        'Laws & Rules That Quietly Changed Everything',
        'Money & Market Shock'
    ]
    
    def __init__(self):
        self.db = Database()
    
    def run(self):
        """Main scraping loop"""
        sources = self.db.get_enabled_sources()
        logger.info(f"Processing {len(sources)} enabled sources")
        
        for source in sources:
            try:
                if source['type'] == 'RSS':
                    self._scrape_rss(source)
                elif source['type'] == 'HTML':
                    self._scrape_html(source)
                
                # Update last_fetched_at
                self.db.client.table('sources').update({
                    'last_fetched_at': datetime.now(timezone.utc).isoformat()
                }).eq('id', source['id']).execute()
                
            except Exception as e:
                logger.error(f"Error scraping source {source['name']}: {e}", exc_info=True)
    
    def _scrape_rss(self, source: Dict):
        """Scrape RSS feed"""
        try:
            feed = feedparser.parse(source['url'])
            logger.info(f"Parsed RSS feed: {len(feed.entries)} entries")
            
            for entry in feed.entries[:20]:  # Limit to 20 most recent
                self._process_entry(entry, source)
                
        except Exception as e:
            logger.error(f"Error parsing RSS feed {source['url']}: {e}")
    
    def _scrape_html(self, source: Dict):
        """Scrape HTML page (basic implementation)"""
        try:
            response = requests.get(source['url'], timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; OrbixBot/1.0)'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for common article patterns
            articles = soup.find_all(['article', 'div'], class_=lambda x: x and ('article' in x.lower() or 'post' in x.lower()))
            
            for article in articles[:20]:  # Limit to 20
                title_elem = article.find(['h1', 'h2', 'h3', 'a'])
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link_elem = article.find('a', href=True) or title_elem if title_elem.name == 'a' else None
                url = link_elem['href'] if link_elem else source['url']
                
                # Make absolute URL
                if url.startswith('/'):
                    from urllib.parse import urljoin
                    url = urljoin(source['url'], url)
                
                # Get snippet
                snippet_elem = article.find(['p', 'div'], class_=lambda x: x and ('summary' in x.lower() or 'excerpt' in x.lower()))
                snippet = snippet_elem.get_text(strip=True)[:500] if snippet_elem else ""
                
                # Get published date
                time_elem = article.find('time')
                published_at = None
                if time_elem and time_elem.get('datetime'):
                    try:
                        published_at = datetime.fromisoformat(time_elem['datetime'].replace('Z', '+00:00'))
                    except:
                        pass
                
                if title and url:
                    entry = {
                        'title': title,
                        'link': url,
                        'summary': snippet,
                        'published': published_at.isoformat() if published_at else None
                    }
                    self._process_entry(entry, source)
                    
        except Exception as e:
            logger.error(f"Error scraping HTML {source['url']}: {e}")
    
    def _process_entry(self, entry: Dict, source: Dict):
        """Process a single entry and store as raw_item"""
        url = entry.get('link') or entry.get('url', '')
        title = entry.get('title', '').strip()
        snippet = entry.get('summary') or entry.get('description', '').strip()
        
        if not url or not title:
            return
        
        # Generate hash for deduplication
        content_hash = hashlib.sha256(f"{url}{title}".encode()).hexdigest()
        
        # Parse published date
        published_at = None
        if entry.get('published'):
            try:
                # Handle feedparser time tuple
                if isinstance(entry['published'], tuple):
                    import time
                    published_at = datetime.fromtimestamp(time.mktime(entry['published']), tz=timezone.utc)
                else:
                    published_at = datetime.fromisoformat(str(entry['published']).replace('Z', '+00:00'))
            except:
                pass
        
        if not published_at:
            published_at = datetime.now(timezone.utc)
        
        # Store raw item
        raw_item = {
            'source_id': source['id'],
            'url': url,
            'title': title,
            'snippet': snippet[:1000] if snippet else None,  # Limit snippet length
            'published_at': published_at.isoformat(),
            'hash': content_hash,
            'status': 'NEW'
        }
        
        item_id = self.db.insert_raw_item(raw_item)
        if item_id:
            logger.debug(f"Stored new raw item: {title[:50]}...")

