"""
Video rendering module using FFmpeg
"""
import os
import logging
import random
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
from modules.database import Database

logger = logging.getLogger(__name__)


class Renderer:
    """Handles video rendering with FFmpeg"""
    
    # Background configuration
    STILL_BACKGROUNDS = ['bg_still_1.jpg', 'bg_still_2.jpg', 'bg_still_3.jpg', 
                         'bg_still_4.jpg', 'bg_still_5.jpg', 'bg_still_6.jpg']
    MOTION_BACKGROUNDS = ['bg_motion_1.mp4', 'bg_motion_2.mp4', 'bg_motion_3.mp4',
                          'bg_motion_4.mp4', 'bg_motion_5.mp4', 'bg_motion_6.mp4']
    
    TEMPLATES = ['A', 'B', 'C']
    
    def __init__(self):
        self.db = Database()
        self.assets_path = Path(__file__).parent.parent.parent / 'assets'
        self.storage_bucket = os.getenv('SUPABASE_STORAGE_BUCKET', 'renders')
    
    def process_pending_renders(self):
        """Process pending renders"""
        renders = self.db.get_pending_renders()
        logger.info(f"Processing {len(renders)} pending renders")
        
        for render in renders:
            try:
                self.db.update_render(render['id'], {'render_status': 'PROCESSING'})
                
                output_path = self._render_video(render)
                
                if output_path:
                    # Upload to Supabase Storage
                    with open(output_path, 'rb') as f:
                        file_data = f.read()
                    
                    storage_path = f"renders/{render['id']}.mp4"
                    self.db.upload_file(self.storage_bucket, storage_path, file_data)
                    
                    # Get public URL
                    public_url = self.db.get_public_url(self.storage_bucket, storage_path)
                    
                    # Update render record
                    self.db.update_render(render['id'], {
                        'render_status': 'COMPLETED',
                        'output_url': public_url,
                        'completed_at': datetime.now(timezone.utc).isoformat()
                    })
                    
                    # Update story status
                    self.db.update_story(render['stories']['id'], {'status': 'RENDERED'})
                    
                    # Clean up temp file
                    os.remove(output_path)
                    
                    logger.info(f"Completed render: {render['id']}")
                else:
                    self.db.update_render(render['id'], {
                        'render_status': 'FAILED',
                        'ffmpeg_log': 'Render failed'
                    })
                    
            except Exception as e:
                logger.error(f"Error rendering {render['id']}: {e}", exc_info=True)
                self.db.update_render(render['id'], {
                    'render_status': 'FAILED',
                    'ffmpeg_log': str(e)
                })
    
    def _render_video(self, render: Dict) -> Optional[str]:
        """Render video using FFmpeg"""
        script = render['scripts']
        story = render['stories']
        
        # Select background
        background_type, background_id = self._select_background()
        
        # Select template
        template = self._select_template()
        
        # Create temp output file
        output_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        output_path = output_file.name
        output_file.close()
        
        # Build FFmpeg command
        cmd = self._build_ffmpeg_command(script, story, background_type, background_id, template, output_path)
        
        try:
            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                # Update render with background info
                self.db.update_render(render['id'], {
                    'template': template,
                    'background_type': background_type,
                    'background_id': background_id
                })
                return output_path
            else:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout")
            return None
        except Exception as e:
            logger.error(f"FFmpeg error: {e}")
            return None
    
    def _select_background(self) -> tuple:
        """Randomly select background (50% still, 50% motion)"""
        if random.random() < 0.5:
            bg_type = 'STILL'
            bg_id = random.choice(self.STILL_BACKGROUNDS)
        else:
            bg_type = 'MOTION'
            bg_id = random.choice(self.MOTION_BACKGROUNDS)
        
        return bg_type, bg_id
    
    def _select_template(self) -> str:
        """Select template (A, B, or C)"""
        return random.choice(self.TEMPLATES)
    
    def _build_ffmpeg_command(self, script: Dict, story: Dict, bg_type: str, bg_id: str, template: str, output_path: str) -> list:
        """Build FFmpeg command for rendering"""
        bg_path = self.assets_path / 'backgrounds' / ('stills' if bg_type == 'STILL' else 'motion') / bg_id
        
        if not bg_path.exists():
            logger.warning(f"Background not found: {bg_path}, using default")
            # Use a solid color as fallback
            bg_input = ['-f', 'lavfi', '-i', f'color=c=0x1a1a1a:s=1080x1920:d=35']
        else:
            if bg_type == 'STILL':
                # Animate still with zoom
                bg_input = ['-loop', '1', '-i', str(bg_path), '-t', '35']
            else:
                # Loop motion video
                bg_input = ['-stream_loop', '-1', '-i', str(bg_path), '-t', '35']
        
        # Base FFmpeg command
        cmd = ['ffmpeg', '-y'] + bg_input
        
        # Add text overlays based on template
        if template == 'A':
            # Template A: headline + stat
            cmd.extend([
                '-vf', f"""
                scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,
                drawtext=text='{script['hook']}':fontfile=/path/to/font.ttf:fontsize=60:fontcolor=white:x=(w-text_w)/2:y=200,
                drawtext=text='{story['category']}':fontfile=/path/to/font.ttf:fontsize=40:fontcolor=#888888:x=(w-text_w)/2:y=300
                """
            ])
        elif template == 'B':
            # Template B: before/after
            cmd.extend([
                '-vf', f"""
                scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,
                drawtext=text='{script['what_happened']}':fontfile=/path/to/font.ttf:fontsize=50:fontcolor=white:x=(w-text_w)/2:y=400
                """
            ])
        else:
            # Template C: impact bullets
            cmd.extend([
                '-vf', f"""
                scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,
                drawtext=text='{script['why_it_matters']}':fontfile=/path/to/font.ttf:fontsize=45:fontcolor=white:x=(w-text_w)/2:y=500
                """
            ])
        
        # Add watermark
        # logo_path = self.assets_path / 'logos' / 'orbix_watermark.png'
        # if logo_path.exists():
        #     cmd.extend(['-i', str(logo_path)])
        
        # Output
        cmd.extend(['-c:v', 'libx264', '-preset', 'medium', '-crf', '23', output_path])
        
        return cmd

