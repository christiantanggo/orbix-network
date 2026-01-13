"""
Publishing module for YouTube and Rumble
"""
import os
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import requests
from modules.database import Database

logger = logging.getLogger(__name__)


class Publisher:
    """Handles publishing videos to platforms"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self):
        self.db = Database()
        self.youtube_service = self._get_youtube_service()
        self.enable_rumble = self._get_rumble_enabled()
    
    def _get_youtube_service(self):
        """Initialize YouTube API service"""
        try:
            client_id = os.getenv('YOUTUBE_CLIENT_ID')
            client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
            refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
            
            if not all([client_id, client_secret, refresh_token]):
                logger.warning("YouTube credentials not configured")
                return None
            
            creds = Credentials(
                None,
                refresh_token=refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=client_id,
                client_secret=client_secret
            )
            
            return build('youtube', 'v3', credentials=creds)
        except Exception as e:
            logger.error(f"Error initializing YouTube service: {e}")
            return None
    
    def _get_rumble_enabled(self) -> bool:
        """Check if Rumble is enabled"""
        setting = self.db.get_setting('enable_rumble')
        if setting and isinstance(setting, dict):
            return setting.get('enabled', False)
        return False
    
    def process_completed_renders(self):
        """Process completed renders and publish them"""
        renders = self.db.get_completed_renders()
        logger.info(f"Processing {len(renders)} completed renders")
        
        # Check daily cap
        daily_cap = self._get_daily_cap()
        today_published = self._get_today_published_count()
        
        if today_published >= daily_cap:
            logger.info(f"Daily cap reached: {today_published}/{daily_cap}")
            return
        
        for render in renders[:daily_cap - today_published]:
            try:
                # Publish to YouTube
                youtube_id = self._publish_to_youtube(render)
                
                if youtube_id:
                    # Create publish record
                    publish = {
                        'render_id': render['id'],
                        'platform': 'YOUTUBE',
                        'platform_video_id': youtube_id,
                        'title': self._generate_title(render),
                        'description': self._generate_description(render),
                        'publish_status': 'PUBLISHED',
                        'posted_at': datetime.now(timezone.utc).isoformat()
                    }
                    self.db.insert_publish(publish)
                    
                    # Update story status
                    self.db.update_story(render['stories']['id'], {'status': 'PUBLISHED'})
                    
                    logger.info(f"Published to YouTube: {youtube_id}")
                    
                    # Optionally publish to Rumble
                    if self.enable_rumble:
                        self._publish_to_rumble(render, youtube_id)
                        
            except Exception as e:
                logger.error(f"Error publishing render {render['id']}: {e}", exc_info=True)
    
    def _publish_to_youtube(self, render: Dict) -> Optional[str]:
        """Publish video to YouTube Shorts"""
        if not self.youtube_service:
            return None
        
        try:
            # Download video from storage
            video_url = render['output_url']
            video_response = requests.get(video_url, timeout=300)
            video_response.raise_for_status()
            
            # Save to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
                tmp_file.write(video_response.content)
                tmp_path = tmp_file.name
            
            # Upload to YouTube
            body = {
                'snippet': {
                    'title': self._generate_title(render),
                    'description': self._generate_description(render),
                    'tags': ['Orbix Network', render['stories']['category']],
                    'categoryId': '24'  # Entertainment
                },
                'status': {
                    'privacyStatus': self._get_youtube_visibility(),
                    'selfDeclaredMadeForKids': False
                }
            }
            
            media = MediaFileUpload(tmp_path, chunksize=-1, resumable=True, mimetype='video/mp4')
            
            request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            
            # Clean up temp file
            os.remove(tmp_path)
            
            return video_id
            
        except Exception as e:
            logger.error(f"Error uploading to YouTube: {e}", exc_info=True)
            return None
    
    def _publish_to_rumble(self, render: Dict, youtube_id: str):
        """Publish video to Rumble (placeholder)"""
        # Rumble API implementation would go here
        logger.info(f"Rumble publishing not yet implemented for {render['id']}")
    
    def _generate_title(self, render: Dict) -> str:
        """Generate YouTube title"""
        script = render['scripts']
        story = render['stories']
        return f"{script['hook']} | {story['category']}"
    
    def _generate_description(self, render: Dict) -> str:
        """Generate YouTube description"""
        script = render['scripts']
        story = render['stories']
        return f"""{script['what_happened']}

{script['why_it_matters']}

{script['what_happens_next']}

{script['cta_line']}

---
Orbix Network
Tracking sudden power shifts before they go mainstream.
"""
    
    def _get_youtube_visibility(self) -> str:
        """Get YouTube visibility setting"""
        setting = self.db.get_setting('youtube_visibility')
        if setting and isinstance(setting, dict):
            return setting.get('value', 'public')
        return 'public'
    
    def _get_daily_cap(self) -> int:
        """Get daily video cap"""
        setting = self.db.get_setting('daily_video_cap')
        if setting and isinstance(setting, dict):
            return setting.get('value', 10)
        return 10
    
    def _get_today_published_count(self) -> int:
        """Get count of videos published today"""
        from datetime import date
        today = date.today().isoformat()
        result = self.db.client.table('publishes').select('id', count='exact').eq('posted_at', today).execute()
        return result.count if hasattr(result, 'count') else 0

