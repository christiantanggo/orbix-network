"""
Analytics collection module
"""
import os
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from modules.database import Database

logger = logging.getLogger(__name__)


class AnalyticsCollector:
    """Collects analytics from published videos"""
    
    def __init__(self):
        self.db = Database()
        self.youtube_service = self._get_youtube_service()
    
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
    
    def collect_daily_metrics(self):
        """Collect daily analytics for all published videos"""
        if not self.youtube_service:
            logger.warning("YouTube service not available, skipping analytics")
            return
        
        # Get all published videos
        publishes = self.db.get_published_videos()
        logger.info(f"Collecting analytics for {len(publishes)} published videos")
        
        # Collect metrics for yesterday (analytics are typically delayed)
        target_date = date.today() - timedelta(days=1)
        
        for publish in publishes:
            try:
                video_id = publish['platform_video_id']
                if not video_id:
                    continue
                
                metrics = self._get_video_metrics(video_id)
                
                if metrics:
                    analytics = {
                        'platform_video_id': video_id,
                        'date': target_date.isoformat(),
                        'views': metrics.get('views', 0),
                        'avg_watch_time': metrics.get('avg_watch_time'),
                        'completion_rate': metrics.get('completion_rate'),
                        'likes': metrics.get('likes', 0),
                        'comments': metrics.get('comments', 0)
                    }
                    
                    self.db.upsert_analytics(analytics)
                    logger.debug(f"Updated analytics for {video_id}")
                    
            except Exception as e:
                logger.error(f"Error collecting analytics for {publish['id']}: {e}", exc_info=True)
    
    def _get_video_metrics(self, video_id: str) -> Dict:
        """Get metrics for a single video"""
        try:
            # Get video statistics
            video_response = self.youtube_service.videos().list(
                part='statistics',
                id=video_id
            ).execute()
            
            if not video_response.get('items'):
                return None
            
            stats = video_response['items'][0]['statistics']
            
            # Get analytics data (requires YouTube Analytics API)
            # For now, we'll use basic stats
            metrics = {
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0))
            }
            
            # Note: avg_watch_time and completion_rate require YouTube Analytics API
            # which needs additional setup. For now, these will be None.
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics for {video_id}: {e}")
            return None

