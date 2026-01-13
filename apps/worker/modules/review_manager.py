"""
Review queue management module
"""
import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict
from modules.database import Database

logger = logging.getLogger(__name__)


class ReviewManager:
    """Manages review queue and auto-approvals"""
    
    def __init__(self):
        self.db = Database()
        self.auto_approve_minutes = self._get_auto_approve_minutes()
    
    def _get_auto_approve_minutes(self) -> int:
        """Get auto-approve timeout from settings"""
        setting = self.db.get_setting('auto_approve_minutes')
        if setting and isinstance(setting, dict):
            return setting.get('value', 60)
        return 60
    
    def check_auto_approvals(self):
        """Check for pending reviews that should be auto-approved"""
        pending_items = self.db.get_pending_review_items()
        logger.debug(f"Checking {len(pending_items)} pending review items")
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=self.auto_approve_minutes)
        
        for item in pending_items:
            created_at = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
            
            if created_at < cutoff_time:
                # Auto-approve
                self.db.update_review_item(item['id'], {
                    'status': 'APPROVED',
                    'reviewed_at': datetime.now(timezone.utc).isoformat()
                })
                
                # Update story status
                self.db.update_story(item['story_id'], {'status': 'APPROVED'})
                
                logger.info(f"Auto-approved review item: {item['id']}")

