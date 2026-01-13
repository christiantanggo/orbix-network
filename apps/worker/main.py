"""
Orbix Network Worker
Main entry point for the background worker system
"""
import os
import logging
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from modules.scraper import Scraper
from modules.classifier import Classifier
from modules.script_generator import ScriptGenerator
from modules.review_manager import ReviewManager
from modules.renderer import Renderer
from modules.publisher import Publisher
from modules.analytics import AnalyticsCollector
from modules.database import Database

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_scraping_job():
    """Scrape news sources and store raw items"""
    logger.info("Starting scraping job")
    try:
        scraper = Scraper()
        scraper.run()
        logger.info("Scraping job completed")
    except Exception as e:
        logger.error(f"Scraping job failed: {e}", exc_info=True)


def run_classification_job():
    """Classify and score new raw items"""
    logger.info("Starting classification job")
    try:
        classifier = Classifier()
        classifier.process_new_items()
        logger.info("Classification job completed")
    except Exception as e:
        logger.error(f"Classification job failed: {e}", exc_info=True)


def run_script_generation_job():
    """Generate scripts for approved stories"""
    logger.info("Starting script generation job")
    try:
        generator = ScriptGenerator()
        generator.process_queued_stories()
        logger.info("Script generation job completed")
    except Exception as e:
        logger.error(f"Script generation job failed: {e}", exc_info=True)


def run_review_check_job():
    """Check review queue for auto-approvals"""
    logger.info("Starting review check job")
    try:
        review_manager = ReviewManager()
        review_manager.check_auto_approvals()
        logger.info("Review check job completed")
    except Exception as e:
        logger.error(f"Review check job failed: {e}", exc_info=True)


def run_render_creation_job():
    """Create render records for approved scripts"""
    logger.info("Starting render creation job")
    try:
        db = Database()
        scripts = db.get_approved_scripts_for_rendering()
        logger.info(f"Found {len(scripts)} approved scripts ready for rendering")
        
        for script in scripts:
            # Check if render already exists
            existing = db.client.table('renders').select('id').eq('script_id', script['id']).execute()
            if existing.data:
                continue
            
            # Create render record
            render = {
                'story_id': script['story_id'],
                'script_id': script['id'],
                'template': 'A',  # Will be selected during rendering
                'background_type': 'STILL',  # Will be selected during rendering
                'background_id': 'bg_still_1.jpg',  # Will be selected during rendering
                'render_status': 'PENDING'
            }
            render_id = db.insert_render(render)
            if render_id:
                logger.info(f"Created render record: {render_id}")
        
        logger.info("Render creation job completed")
    except Exception as e:
        logger.error(f"Render creation job failed: {e}", exc_info=True)


def run_rendering_job():
    """Render videos for approved scripts"""
    logger.info("Starting rendering job")
    try:
        renderer = Renderer()
        renderer.process_pending_renders()
        logger.info("Rendering job completed")
    except Exception as e:
        logger.error(f"Rendering job failed: {e}", exc_info=True)


def run_publishing_job():
    """Publish completed renders to platforms"""
    logger.info("Starting publishing job")
    try:
        publisher = Publisher()
        publisher.process_completed_renders()
        logger.info("Publishing job completed")
    except Exception as e:
        logger.error(f"Publishing job failed: {e}", exc_info=True)


def run_analytics_job():
    """Collect analytics for published videos"""
    logger.info("Starting analytics job")
    try:
        collector = AnalyticsCollector()
        collector.collect_daily_metrics()
        logger.info("Analytics job completed")
    except Exception as e:
        logger.error(f"Analytics job failed: {e}", exc_info=True)


def main():
    """Main scheduler setup"""
    scheduler = BlockingScheduler()
    
    # Scraping: every 5 minutes
    scheduler.add_job(
        run_scraping_job,
        trigger=IntervalTrigger(minutes=5),
        id='scraping',
        max_instances=1
    )
    
    # Classification: every 2 minutes
    scheduler.add_job(
        run_classification_job,
        trigger=IntervalTrigger(minutes=2),
        id='classification',
        max_instances=1
    )
    
    # Script generation: every 3 minutes
    scheduler.add_job(
        run_script_generation_job,
        trigger=IntervalTrigger(minutes=3),
        id='script_generation',
        max_instances=1
    )
    
    # Review check: every 1 minute
    scheduler.add_job(
        run_review_check_job,
        trigger=IntervalTrigger(minutes=1),
        id='review_check',
        max_instances=1
    )
    
    # Render creation: every 3 minutes
    scheduler.add_job(
        run_render_creation_job,
        trigger=IntervalTrigger(minutes=3),
        id='render_creation',
        max_instances=1
    )
    
    # Rendering: every 5 minutes
    scheduler.add_job(
        run_rendering_job,
        trigger=IntervalTrigger(minutes=5),
        id='rendering',
        max_instances=1
    )
    
    # Publishing: every 10 minutes
    scheduler.add_job(
        run_publishing_job,
        trigger=IntervalTrigger(minutes=10),
        id='publishing',
        max_instances=1
    )
    
    # Analytics: daily at 2 AM
    scheduler.add_job(
        run_analytics_job,
        trigger='cron',
        hour=2,
        minute=0,
        id='analytics',
        max_instances=1
    )
    
    logger.info("Orbix Network Worker started")
    logger.info("Scheduler jobs configured")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler")
        scheduler.shutdown()


if __name__ == '__main__':
    main()

