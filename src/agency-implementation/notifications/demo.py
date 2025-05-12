#!/usr/bin/env python3
"""
Demonstration script for the Unified Notification System.

This script shows how to use the notification system with sample data.
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
import sys

from models.alert import Alert, AlertSeverity, AlertStatus
from core.unified_notification_system import UnifiedNotificationSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)

logger = logging.getLogger(__name__)


async def run_demo():
    """Run a demonstration of the notification system."""
    logger.info("Starting Unified Notification System Demo")
    
    # Load config from a mock file
    config_path = os.path.join(os.path.dirname(__file__), "config", "notification_config.json")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        return
        
    # For demo purposes, we'll mock the external APIs
    # by setting mock: true in the config
    config["mock_external_apis"] = True
    
    # Create notification system
    notification_system = UnifiedNotificationSystem(config)
    
    # Initialize the system
    logger.info("Initializing notification system...")
    await notification_system.initialize()
    
    try:
        # Demo 1: Create some sample alerts
        logger.info("Creating sample alerts...")
        sample_alerts = create_sample_alerts()
        
        # Demo 2: Prioritize alerts
        logger.info("Prioritizing alerts...")
        prioritized_alerts = await notification_system.prioritize_alerts(sample_alerts)
        
        logger.info(f"Prioritized {len(prioritized_alerts)} alerts:")
        for i, alert in enumerate(prioritized_alerts, 1):
            logger.info(f"{i}. [{alert.severity.name}] {alert.title} (Priority Score: {alert.priority_score:.1f})")
        
        # Demo 3: Process mock alert lifecycle
        logger.info("\nProcessing alert lifecycle...")
        
        # Mock the collect_alerts method to return our sample alerts
        notification_system.collect_alerts = lambda: asyncio.sleep(0, result=sample_alerts)
        
        results = await notification_system.process_alert_lifecycle()
        logger.info(f"Alert lifecycle results: {results}")
        
        # Demo 4: Show active alerts
        active_alerts = await notification_system.get_active_alerts()
        logger.info(f"\nActive alerts: {len(active_alerts)}")
        for alert in active_alerts:
            logger.info(f"- {alert.title} ({alert.source})")
        
        # Demo 5: Acknowledge an alert
        if active_alerts:
            alert_to_ack = active_alerts[0]
            logger.info(f"\nAcknowledging alert: {alert_to_ack.title}")
            updated_alert = await notification_system.acknowledge_alert(
                alert_to_ack.id, "demo-user"
            )
            logger.info(f"Alert acknowledged by {updated_alert.acknowledged_by}")
        
        # Demo 6: Close an alert
        if len(active_alerts) > 1:
            alert_to_close = active_alerts[1]
            logger.info(f"\nClosing alert: {alert_to_close.title}")
            closed_alert = await notification_system.close_alert(
                alert_to_close.id, "demo-user", "Resolved in demo"
            )
            logger.info(f"Alert closed with notes: {closed_alert.resolution_notes}")
            
        # Demo 7: Get alert history
        history = await notification_system.get_alert_history()
        logger.info(f"\nAlert history: {len(history)} entries")
        for entry in history:
            logger.info(f"- {entry['title']} ({entry['source']})")
            
    except Exception as e:
        logger.error(f"Error in demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        logger.info("\nShutting down notification system...")
        await notification_system.shutdown()
        logger.info("Demo complete")


def create_sample_alerts():
    """Create sample alerts for demonstration."""
    now = datetime.utcnow()
    
    return [
        Alert(
            id="cdc-001",
            title="COVID-19 Variant Update",
            description="A new COVID-19 variant has been detected in multiple states.",
            source="CDC",
            alert_type="disease_outbreak",
            severity=AlertSeverity.HIGH,
            status=AlertStatus.NEW,
            url="https://www.cdc.gov/alerts/covid-variant",
            created_at=now - timedelta(hours=2),
            regions=["CA", "NY", "FL", "TX"],
            recommended_actions=[
                "Get vaccinated and boosted",
                "Wear masks in crowded indoor settings",
                "Monitor for symptoms"
            ],
            affected_population=25000000,
        ),
        Alert(
            id="epa-001",
            title="Air Quality Warning",
            description="Air quality has reached unhealthy levels due to wildfire smoke.",
            source="EPA",
            alert_type="air_quality_alert",
            severity=AlertSeverity.MEDIUM,
            status=AlertStatus.NEW,
            url="https://www.airnow.gov/",
            created_at=now - timedelta(hours=5),
            regions=["CA", "OR", "WA"],
            recommended_actions=[
                "Stay indoors when possible",
                "Use air purifiers",
                "Avoid outdoor exercise"
            ],
            affected_population=5000000,
        ),
        Alert(
            id="fema-001",
            title="Flash Flood Emergency",
            description="Catastrophic flooding is occurring in the Houston metropolitan area.",
            source="FEMA",
            alert_type="emergency_warning",
            severity=AlertSeverity.CRITICAL,
            status=AlertStatus.NEW,
            url="https://www.weather.gov/alerts",
            created_at=now - timedelta(minutes=30),
            regions=["TX"],
            recommended_actions=[
                "Move to higher ground immediately",
                "Do not drive through flooded roadways",
                "Follow evacuation orders"
            ],
            affected_population=4000000,
        ),
        Alert(
            id="epa-002",
            title="Drinking Water Advisory",
            description="Contaminants detected in municipal water supply.",
            source="EPA",
            alert_type="water_quality_alert",
            severity=AlertSeverity.HIGH,
            status=AlertStatus.NEW,
            url="https://www.epa.gov/wateralerts",
            created_at=now - timedelta(hours=12),
            regions=["MI"],
            recommended_actions=[
                "Use bottled water for drinking and cooking",
                "Boil tap water before use",
                "Do not use hot water from tap"
            ],
            affected_population=120000,
        ),
        Alert(
            id="cdc-002",
            title="Foodborne Illness Outbreak",
            description="E. coli outbreak linked to romaine lettuce.",
            source="CDC",
            alert_type="food_safety",
            severity=AlertSeverity.MEDIUM,
            status=AlertStatus.NEW,
            url="https://www.cdc.gov/foodsafety/alerts",
            created_at=now - timedelta(days=1),
            regions=["US"],
            recommended_actions=[
                "Do not eat romaine lettuce",
                "Discard any romaine lettuce at home",
                "Wash hands and surfaces thoroughly"
            ],
            affected_population=None,
        ),
    ]


if __name__ == "__main__":
    asyncio.run(run_demo())