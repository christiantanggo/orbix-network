"""
Database module for Supabase interactions
"""
import os
from supabase import create_client, Client
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class Database:
    """Wrapper for Supabase database operations"""
    
    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    def get_setting(self, key: str) -> Any:
        """Get a setting value"""
        result = self.client.table('settings').select('value').eq('key', key).execute()
        if result.data:
            return result.data[0]['value']
        return None
    
    def get_enabled_sources(self) -> List[Dict]:
        """Get all enabled sources"""
        result = self.client.table('sources').select('*').eq('enabled', True).execute()
        return result.data
    
    def insert_raw_item(self, item: Dict) -> Optional[str]:
        """Insert a raw item, returns id if successful"""
        try:
            result = self.client.table('raw_items').insert(item).execute()
            if result.data:
                return result.data[0]['id']
        except Exception as e:
            if 'duplicate key' in str(e).lower():
                logger.debug(f"Duplicate raw item: {item.get('url')}")
            else:
                logger.error(f"Error inserting raw item: {e}")
        return None
    
    def get_new_raw_items(self) -> List[Dict]:
        """Get raw items with status NEW"""
        result = self.client.table('raw_items').select('*').eq('status', 'NEW').execute()
        return result.data
    
    def update_raw_item(self, item_id: str, updates: Dict):
        """Update a raw item"""
        self.client.table('raw_items').update(updates).eq('id', item_id).execute()
    
    def insert_story(self, story: Dict) -> Optional[str]:
        """Insert a story, returns id if successful"""
        result = self.client.table('stories').insert(story).execute()
        if result.data:
            return result.data[0]['id']
        return None
    
    def get_queued_stories(self) -> List[Dict]:
        """Get stories with status QUEUED"""
        result = self.client.table('stories').select('*').eq('status', 'QUEUED').execute()
        return result.data
    
    def update_story(self, story_id: str, updates: Dict):
        """Update a story"""
        self.client.table('stories').update(updates).eq('id', story_id).execute()
    
    def insert_script(self, script: Dict) -> Optional[str]:
        """Insert a script, returns id if successful"""
        result = self.client.table('scripts').insert(script).execute()
        if result.data:
            return result.data[0]['id']
        return None
    
    def get_pending_review_items(self) -> List[Dict]:
        """Get review queue items with status PENDING"""
        result = self.client.table('review_queue').select('*, stories(*), scripts(*)').eq('status', 'PENDING').execute()
        return result.data
    
    def update_review_item(self, review_id: str, updates: Dict):
        """Update a review queue item"""
        self.client.table('review_queue').update(updates).eq('id', review_id).execute()
    
    def get_approved_scripts_for_rendering(self) -> List[Dict]:
        """Get scripts that are approved and ready for rendering"""
        # Get all scripts with their stories
        result = self.client.table('scripts').select('*, stories(*)').execute()
        approved_scripts = []
        
        for script in result.data:
            story = script.get('stories', {})
            if not story or story.get('status') != 'APPROVED':
                continue
            
            # Check if review is approved or doesn't exist
            review_check = self.client.table('review_queue').select('*').eq('script_id', script['id']).execute()
            if review_check.data and review_check.data[0].get('status') != 'APPROVED':
                continue
            
            # Check if render already exists
            render_check = self.client.table('renders').select('id').eq('script_id', script['id']).execute()
            if render_check.data:
                continue
            
            # Add story_id to script dict for convenience
            script['story_id'] = story['id']
            approved_scripts.append(script)
        
        return approved_scripts
    
    def insert_render(self, render: Dict) -> Optional[str]:
        """Insert a render record"""
        result = self.client.table('renders').insert(render).execute()
        if result.data:
            return result.data[0]['id']
        return None
    
    def get_pending_renders(self) -> List[Dict]:
        """Get renders with status PENDING"""
        result = self.client.table('renders').select('*, scripts(*), stories(*)').eq('render_status', 'PENDING').execute()
        return result.data
    
    def update_render(self, render_id: str, updates: Dict):
        """Update a render"""
        self.client.table('renders').update(updates).eq('id', render_id).execute()
    
    def get_completed_renders(self) -> List[Dict]:
        """Get renders that are completed but not published"""
        result = self.client.table('renders').select('*, scripts(*), stories(*)').eq('render_status', 'COMPLETED').execute()
        # Filter out already published
        unpublished = []
        for render in result.data:
            publish_check = self.client.table('publishes').select('*').eq('render_id', render['id']).execute()
            if not publish_check.data:
                unpublished.append(render)
        return unpublished
    
    def insert_publish(self, publish: Dict) -> Optional[str]:
        """Insert a publish record"""
        result = self.client.table('publishes').insert(publish).execute()
        if result.data:
            return result.data[0]['id']
        return None
    
    def get_published_videos(self) -> List[Dict]:
        """Get all published videos for analytics"""
        result = self.client.table('publishes').select('*').eq('publish_status', 'PUBLISHED').execute()
        return result.data
    
    def upsert_analytics(self, analytics: Dict):
        """Upsert analytics data"""
        self.client.table('analytics_daily').upsert(analytics, on_conflict='platform_video_id,date').execute()
    
    def upload_file(self, bucket: str, path: str, file_data: bytes, content_type: str = 'video/mp4'):
        """Upload file to Supabase Storage"""
        self.client.storage.from_(bucket).upload(path, file_data, file_options={"content-type": content_type})
    
    def get_public_url(self, bucket: str, path: str) -> str:
        """Get public URL for a file in storage"""
        return self.client.storage.from_(bucket).get_public_url(path)

