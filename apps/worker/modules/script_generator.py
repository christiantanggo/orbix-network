"""
Script generation module
"""
import os
import logging
import json
from typing import Dict, Optional
from openai import OpenAI
from modules.database import Database

logger = logging.getLogger(__name__)


class ScriptGenerator:
    """Generates scripts for stories"""
    
    def __init__(self):
        self.db = Database()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set")
        self.client = OpenAI(api_key=api_key)
        self.review_mode = self._get_review_mode()
    
    def _get_review_mode(self) -> bool:
        """Check if review mode is enabled"""
        setting = self.db.get_setting('review_mode')
        if setting and isinstance(setting, dict):
            return setting.get('enabled', False)
        return False
    
    def process_queued_stories(self):
        """Process queued stories and generate scripts"""
        stories = self.db.get_queued_stories()
        logger.info(f"Processing {len(stories)} queued stories")
        
        for story in stories:
            try:
                # Get raw item for context
                raw_item_result = self.db.client.table('raw_items').select('*').eq('id', story['raw_item_id']).execute()
                if not raw_item_result.data:
                    logger.warning(f"Raw item not found for story {story['id']}")
                    continue
                
                raw_item = raw_item_result.data[0]
                script = self._generate_script(story, raw_item)
                
                if script:
                    script_id = self.db.insert_script(script)
                    
                    if script_id:
                        # Update story status
                        self.db.update_story(story['id'], {'status': 'APPROVED'})
                        
                        # If review mode is enabled, add to review queue
                        if self.review_mode:
                            self.db.client.table('review_queue').insert({
                                'story_id': story['id'],
                                'script_id': script_id,
                                'status': 'PENDING'
                            }).execute()
                            logger.info(f"Added script to review queue: {story['id']}")
                        else:
                            logger.info(f"Script generated and auto-approved: {story['id']}")
                else:
                    self.db.update_story(story['id'], {
                        'status': 'REJECTED',
                        'decision_reason': 'Failed to generate script'
                    })
                    
            except Exception as e:
                logger.error(f"Error processing story {story['id']}: {e}", exc_info=True)
    
    def _generate_script(self, story: Dict, raw_item: Dict) -> Optional[Dict]:
        """Generate script using AI"""
        prompt = f"""Generate a short-form video script (30-45 seconds) for this news story.

Story:
Title: {raw_item['title']}
Snippet: {raw_item.get('snippet', '')}
Category: {story['category']}
Shock Score: {story['shock_score']}

Script Structure (REQUIRED):
1. Hook (1-2 sentences, statement not question, attention-grabbing)
2. What Happened (2-3 sentences, factual)
3. Why It Matters (2-3 sentences, impact)
4. What Happens Next (1-2 sentences, implications)
5. CTA Line (soft utility, never "please subscribe")

Tone Requirements:
- Calm and observational
- Authoritative but not preachy
- No speculation language ("might", "could", "probably")
- No political rage framing
- No graphic descriptions

Return JSON format:
{{
    "hook": "hook text",
    "what_happened": "what happened text",
    "why_it_matters": "why it matters text",
    "what_happens_next": "what happens next text",
    "cta_line": "cta text",
    "duration_target_seconds": 35
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a script writer for Orbix Network. Return only valid JSON. Follow the exact structure."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate structure
            required_fields = ['hook', 'what_happened', 'why_it_matters', 'what_happens_next', 'cta_line']
            if not all(field in result for field in required_fields):
                logger.error("Script missing required fields")
                return None
            
            script = {
                'story_id': story['id'],
                'hook': result['hook'],
                'what_happened': result['what_happened'],
                'why_it_matters': result['why_it_matters'],
                'what_happens_next': result['what_happens_next'],
                'cta_line': result['cta_line'],
                'duration_target_seconds': result.get('duration_target_seconds', 35)
            }
            
            return script
            
        except Exception as e:
            logger.error(f"Error generating script: {e}", exc_info=True)
            return None

