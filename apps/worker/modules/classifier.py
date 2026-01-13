"""
AI Classification and Shock Scoring module
"""
import os
import logging
import json
from typing import Dict, List, Optional
from openai import OpenAI
from modules.database import Database

logger = logging.getLogger(__name__)


class Classifier:
    """Handles AI classification and shock scoring"""
    
    CATEGORIES = [
        'AI & Automation Takeovers',
        'Corporate Collapses & Reversals',
        'Tech Decisions With Massive Fallout',
        'Laws & Rules That Quietly Changed Everything',
        'Money & Market Shock'
    ]
    
    def __init__(self):
        self.db = Database()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set")
        self.client = OpenAI(api_key=api_key)
        self.threshold = self._get_threshold()
    
    def _get_threshold(self) -> int:
        """Get shock score threshold from settings"""
        setting = self.db.get_setting('shock_score_threshold')
        if setting and isinstance(setting, dict):
            return setting.get('value', 65)
        return 65
    
    def process_new_items(self):
        """Process new raw items for classification"""
        items = self.db.get_new_raw_items()
        logger.info(f"Processing {len(items)} new raw items")
        
        for item in items:
            try:
                result = self._classify_and_score(item)
                if result:
                    self._create_story(item, result)
                    self.db.update_raw_item(item['id'], {'status': 'PROCESSED'})
                else:
                    self.db.update_raw_item(item['id'], {
                        'status': 'DISCARDED',
                        'discard_reason': 'Failed classification or below threshold'
                    })
            except Exception as e:
                logger.error(f"Error processing item {item['id']}: {e}", exc_info=True)
                self.db.update_raw_item(item['id'], {
                    'status': 'DISCARDED',
                    'discard_reason': f'Error: {str(e)}'
                })
    
    def _classify_and_score(self, item: Dict) -> Optional[Dict]:
        """Classify item and calculate shock score"""
        prompt = f"""Analyze this news story and classify it into exactly ONE category, then score its "shock value" (0-100).

Story:
Title: {item['title']}
Snippet: {item.get('snippet', '')[:500]}

Categories (choose exactly ONE):
1. AI & Automation Takeovers
2. Corporate Collapses & Reversals
3. Tech Decisions With Massive Fallout
4. Laws & Rules That Quietly Changed Everything
5. Money & Market Shock

Shock Score Components (total 0-100):
- Scale (0-30): How many people/companies affected?
- Speed (0-20): How quickly did this happen?
- Power shift (0-25): How much did power/control change?
- Permanence (0-15): How permanent is this change?
- Explainability (0-10): How hard is this to explain to average person?

Rules:
- If story is unclear, political rage, graphic violence, or speculation-heavy, return "DISCARD"
- If shock score is below 65, return "DISCARD"
- Only return valid category if story clearly fits

Return JSON format:
{{
    "category": "category name or DISCARD",
    "shock_score": 0-100,
    "factors": {{
        "scale": 0-30,
        "speed": 0-20,
        "power_shift": 0-25,
        "permanence": 0-15,
        "explainability": 0-10
    }},
    "reasoning": "brief explanation"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a news classifier for Orbix Network. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate result
            if result.get('category') == 'DISCARD':
                return None
            
            if result.get('category') not in self.CATEGORIES:
                logger.warning(f"Invalid category returned: {result.get('category')}")
                return None
            
            shock_score = result.get('shock_score', 0)
            if shock_score < self.threshold:
                logger.debug(f"Item below threshold: {shock_score} < {self.threshold}")
                return None
            
            return result
            
        except Exception as e:
            logger.error(f"Error in AI classification: {e}", exc_info=True)
            return None
    
    def _create_story(self, item: Dict, classification: Dict):
        """Create a story record from classified item"""
        story = {
            'raw_item_id': item['id'],
            'category': classification['category'],
            'shock_score': classification['shock_score'],
            'factors_json': classification.get('factors', {}),
            'status': 'QUEUED',
            'decision_reason': classification.get('reasoning', '')
        }
        
        story_id = self.db.insert_story(story)
        if story_id:
            logger.info(f"Created story: {classification['category']} (score: {classification['shock_score']})")

