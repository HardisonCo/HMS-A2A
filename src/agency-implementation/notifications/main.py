"""
Unified Notification System Main Entry Point

This script initializes and runs the unified notification system.
"""

import asyncio
import logging
import json
import argparse
import os
import sys
from typing import Dict, Any
import traceback
from datetime import datetime

from core.unified_notification_system import UnifiedNotificationSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('notification_system.log')
    ]
)

logger = logging.getLogger(__name__)


async def run_system(config_path: str, run_once: bool = False) -> None:
    """
    Initialize and run the notification system.
    
    Args:
        config_path: Path to configuration file
        run_once: If True, process alerts once and exit
    """
    try:
        # Load configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        logger.info(f"Loaded configuration from {config_path}")
        
        # Create and initialize notification system
        notification_system = UnifiedNotificationSystem(config)
        
        initialization_successful = await notification_system.initialize()
        if not initialization_successful:
            logger.error("Failed to initialize notification system")
            return
            
        logger.info("Notification system initialized successfully")
        
        try:
            if run_once:
                # Run alert processing once
                logger.info("Running alert processing once")
                results = await notification_system.process_alert_lifecycle()
                logger.info(f"Alert processing results: {results}")
            else:
                # Run in continuous mode
                logger.info("Starting continuous alert processing")
                
                # Get processing interval from config (default: 5 minutes)
                interval_seconds = config.get("processing_interval_seconds", 300)
                
                while True:
                    try:
                        results = await notification_system.process_alert_lifecycle()
                        logger.info(f"Alert processing results: {results}")
                    except Exception as e:
                        logger.error(f"Error in alert processing cycle: {e}")
                        
                    # Wait for next cycle
                    logger.info(f"Waiting {interval_seconds} seconds until next processing cycle")
                    await asyncio.sleep(interval_seconds)
                    
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down")
        except Exception as e:
            logger.error(f"Error running notification system: {e}")
            traceback.print_exc()
        finally:
            # Shutdown notification system
            await notification_system.shutdown()
            logger.info("Notification system shutdown complete")
            
    except Exception as e:
        logger.error(f"Error in notification system: {e}")
        traceback.print_exc()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Unified Notification System")
    parser.add_argument(
        "--config", 
        "-c", 
        default="/Users/arionhardison/Desktop/Codify/agency-implementation/notifications/config/notification_config.json",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--once", 
        "-o", 
        action="store_true",
        help="Run alert processing once and exit"
    )
    parser.add_argument(
        "--log-level", 
        "-l", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Check if config file exists
    if not os.path.exists(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    
    # Run the notification system
    asyncio.run(run_system(args.config, args.once))


if __name__ == "__main__":
    main()