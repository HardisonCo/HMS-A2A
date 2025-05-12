"""
Unified Notification System

This module provides a centralized system for aggregating and distributing
alerts from federal agencies (CDC, EPA, FEMA) using federated components.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional, Union, Set
from datetime import datetime

from ..models.alert import Alert, AlertSeverity, AlertStatus
from ..models.stakeholder import Stakeholder, StakeholderGroup
from ..federation.federation_client import FederationClient
from ..channels.channel_manager import NotificationChannelManager
from ..adapters.alert_adapter import AlertAdapter

logger = logging.getLogger(__name__)

class UnifiedNotificationSystem:
    """
    A system that aggregates alerts from multiple federal agencies,
    prioritizes them, and distributes them to appropriate stakeholders.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the unified notification system.
        
        Args:
            config: Configuration for the notification system
        """
        self.config = config
        self.federation_client = FederationClient(config.get("federation", {}))
        self.channel_manager = NotificationChannelManager(config.get("channels", {}))
        self.alert_adapters: Dict[str, AlertAdapter] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.stakeholder_subscriptions: Dict[str, Set[str]] = {}  # stakeholder_id -> alert_types
        self.alert_history: List[Dict[str, Any]] = []
        self.maintenance_mode = False
        
        # Initialize alert adapters
        for agency, adapter_config in config.get("adapters", {}).items():
            adapter_type = adapter_config.get("type")
            adapter_class = AlertAdapter.get_adapter(adapter_type)
            if adapter_class:
                self.alert_adapters[agency] = adapter_class(adapter_config)
            else:
                logger.warning(f"Unknown adapter type '{adapter_type}' for agency '{agency}'")
    
    async def initialize(self) -> bool:
        """
        Initialize all components of the notification system.
        
        Returns:
            bool: True if initialization was successful
        """
        try:
            # Initialize federation client
            federation_ok = await self.federation_client.initialize()
            if not federation_ok:
                logger.error("Failed to initialize federation client")
                return False
                
            # Initialize channel manager
            channels_ok = await self.channel_manager.initialize()
            if not channels_ok:
                logger.error("Failed to initialize notification channels")
                return False
                
            # Initialize agency adapters
            for agency, adapter in self.alert_adapters.items():
                adapter_ok = await adapter.initialize()
                if not adapter_ok:
                    logger.error(f"Failed to initialize adapter for {agency}")
                    return False
            
            # Load stakeholder subscriptions
            await self._load_stakeholder_subscriptions()
            
            logger.info("Unified notification system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing notification system: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the notification system and release resources."""
        try:
            await self.federation_client.shutdown()
            await self.channel_manager.shutdown()
            
            for adapter in self.alert_adapters.values():
                await adapter.shutdown()
                
            logger.info("Unified notification system shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during notification system shutdown: {e}")
    
    async def collect_alerts(self) -> List[Alert]:
        """
        Collect alerts from all agency sources.
        
        Returns:
            List of collected alerts
        """
        all_alerts = []
        
        # Collect from each agency adapter
        for agency_name, adapter in self.alert_adapters.items():
            try:
                agency_alerts = await adapter.get_alerts()
                for alert in agency_alerts:
                    # Set source agency if not already set
                    if not alert.source:
                        alert.source = agency_name
                    all_alerts.append(alert)
            except Exception as e:
                logger.error(f"Error collecting alerts from {agency_name}: {e}")
        
        # Collect from federated sources
        try:
            federated_alerts = await self.federation_client.get_alerts()
            all_alerts.extend(federated_alerts)
        except Exception as e:
            logger.error(f"Error collecting federated alerts: {e}")
        
        logger.info(f"Collected {len(all_alerts)} alerts from all sources")
        return all_alerts
    
    async def prioritize_alerts(self, alerts: List[Alert]) -> List[Alert]:
        """
        Prioritize alerts based on severity, relevance, and other factors.
        
        Args:
            alerts: List of alerts to prioritize
            
        Returns:
            Prioritized list of alerts
        """
        if not alerts:
            return []
        
        # Apply prioritization rules
        for alert in alerts:
            # Calculate base priority score from severity
            if alert.severity == AlertSeverity.CRITICAL:
                alert.priority_score = 100
            elif alert.severity == AlertSeverity.HIGH:
                alert.priority_score = 75
            elif alert.severity == AlertSeverity.MEDIUM:
                alert.priority_score = 50
            elif alert.severity == AlertSeverity.LOW:
                alert.priority_score = 25
            else:
                alert.priority_score = 10
            
            # Adjust based on age (newer alerts get higher priority)
            if alert.created_at:
                age_hours = (datetime.utcnow() - alert.created_at).total_seconds() / 3600
                if age_hours < 1:  # Less than one hour old
                    alert.priority_score += 20
                elif age_hours < 6:  # Less than six hours old
                    alert.priority_score += 10
                elif age_hours > 48:  # More than two days old
                    alert.priority_score -= 20
            
            # Adjust based on affected population size
            if hasattr(alert, 'affected_population') and alert.affected_population:
                if alert.affected_population > 1000000:  # Over 1 million affected
                    alert.priority_score += 25
                elif alert.affected_population > 100000:  # Over 100k affected
                    alert.priority_score += 15
                elif alert.affected_population > 10000:  # Over 10k affected
                    alert.priority_score += 5
            
            # Ensure the score stays within 0-100 range
            alert.priority_score = max(0, min(100, alert.priority_score))
        
        # Sort by priority score (descending)
        prioritized_alerts = sorted(alerts, key=lambda x: x.priority_score, reverse=True)
        return prioritized_alerts
    
    async def distribute_alerts(self, alerts: List[Alert]) -> Dict[str, Any]:
        """
        Distribute alerts to appropriate stakeholders via configured channels.
        
        Args:
            alerts: Prioritized list of alerts to distribute
            
        Returns:
            Dict with distribution results
        """
        if not alerts:
            return {"distributed_count": 0, "stakeholders_notified": 0}
        
        total_distributed = 0
        stakeholders_notified = set()
        results_by_channel = {}
        
        # Group alerts by stakeholder for efficient distribution
        stakeholder_alerts: Dict[str, List[Alert]] = {}
        
        for alert in alerts:
            # Find stakeholders for this alert
            recipients = await self._get_stakeholders_for_alert(alert)
            
            for stakeholder_id in recipients:
                if stakeholder_id not in stakeholder_alerts:
                    stakeholder_alerts[stakeholder_id] = []
                stakeholder_alerts[stakeholder_id].append(alert)
        
        # Distribute to each stakeholder
        for stakeholder_id, stakeholder_alerts in stakeholder_alerts.items():
            try:
                stakeholder = await self._get_stakeholder(stakeholder_id)
                if not stakeholder:
                    logger.warning(f"Stakeholder {stakeholder_id} not found, skipping distribution")
                    continue
                
                # Determine preferred channels for this stakeholder
                channels = stakeholder.get("preferred_channels", ["email"])
                
                # Distribute via each channel
                for channel_name in channels:
                    try:
                        channel = self.channel_manager.get_channel(channel_name)
                        if not channel:
                            logger.warning(f"Channel {channel_name} not available")
                            continue
                        
                        # Format alerts for this channel
                        formatted_alerts = []
                        for alert in stakeholder_alerts:
                            formatted_alert = await self._format_alert_for_channel(
                                alert, channel_name, stakeholder
                            )
                            if formatted_alert:
                                formatted_alerts.append(formatted_alert)
                        
                        # Send via channel
                        if formatted_alerts:
                            result = await channel.send_batch(formatted_alerts)
                            
                            # Track results
                            if channel_name not in results_by_channel:
                                results_by_channel[channel_name] = {
                                    "success_count": 0,
                                    "failure_count": 0
                                }
                            
                            results_by_channel[channel_name]["success_count"] += result.get("success_count", 0)
                            results_by_channel[channel_name]["failure_count"] += result.get("failure_count", 0)
                            
                            if result.get("success_count", 0) > 0:
                                stakeholders_notified.add(stakeholder_id)
                                total_distributed += result.get("success_count", 0)
                        
                    except Exception as e:
                        logger.error(f"Error distributing alerts via {channel_name}: {e}")
            
            except Exception as e:
                logger.error(f"Error distributing alerts to stakeholder {stakeholder_id}: {e}")
        
        # Update alert statuses
        for alert in alerts:
            alert.status = AlertStatus.DISTRIBUTED
            alert.distribution_timestamp = datetime.utcnow()
            self.active_alerts[alert.id] = alert
            
            # Add to history
            self.alert_history.append({
                "alert_id": alert.id,
                "title": alert.title,
                "source": alert.source,
                "severity": alert.severity.value,
                "distributed_at": alert.distribution_timestamp.isoformat(),
                "stakeholders_count": len(await self._get_stakeholders_for_alert(alert)),
            })
        
        return {
            "distributed_count": total_distributed,
            "stakeholders_notified": len(stakeholders_notified),
            "results_by_channel": results_by_channel
        }
    
    async def process_alert_lifecycle(self) -> Dict[str, Any]:
        """
        Full lifecycle processing of alerts: collect, prioritize, and distribute.
        
        Returns:
            Dict with processing results
        """
        if self.maintenance_mode:
            logger.info("System is in maintenance mode, skipping alert processing")
            return {"status": "maintenance", "processed": 0, "distributed": 0}
        
        try:
            # Step 1: Collect alerts from all sources
            collected_alerts = await self.collect_alerts()
            
            # Step 2: Deduplicate alerts
            unique_alerts = await self._deduplicate_alerts(collected_alerts)
            
            # Step 3: Prioritize alerts
            prioritized_alerts = await self.prioritize_alerts(unique_alerts)
            
            # Step 4: Distribute alerts to stakeholders
            distribution_results = await self.distribute_alerts(prioritized_alerts)
            
            results = {
                "status": "success",
                "collected": len(collected_alerts),
                "unique": len(unique_alerts),
                "prioritized": len(prioritized_alerts),
                "distributed": distribution_results.get("distributed_count", 0),
                "stakeholders_notified": distribution_results.get("stakeholders_notified", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Alert lifecycle processing complete: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in alert lifecycle processing: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def add_stakeholder_subscription(self, stakeholder_id: str, 
                                         alert_types: List[str]) -> bool:
        """
        Add or update a stakeholder's alert subscriptions.
        
        Args:
            stakeholder_id: Unique ID of the stakeholder
            alert_types: List of alert types to subscribe to
            
        Returns:
            bool: True if successful
        """
        try:
            if stakeholder_id not in self.stakeholder_subscriptions:
                self.stakeholder_subscriptions[stakeholder_id] = set()
                
            # Add new alert types
            self.stakeholder_subscriptions[stakeholder_id].update(alert_types)
            
            # Persist subscriptions
            await self._save_stakeholder_subscriptions()
            return True
            
        except Exception as e:
            logger.error(f"Error adding stakeholder subscription: {e}")
            return False
    
    async def remove_stakeholder_subscription(self, stakeholder_id: str, 
                                            alert_types: Optional[List[str]] = None) -> bool:
        """
        Remove a stakeholder's alert subscriptions.
        
        Args:
            stakeholder_id: Unique ID of the stakeholder
            alert_types: Optional list of alert types to unsubscribe from.
                         If None, removes all subscriptions.
            
        Returns:
            bool: True if successful
        """
        try:
            if stakeholder_id not in self.stakeholder_subscriptions:
                return True  # Nothing to do
            
            if alert_types is None:
                # Remove all subscriptions
                del self.stakeholder_subscriptions[stakeholder_id]
            else:
                # Remove specific alert types
                self.stakeholder_subscriptions[stakeholder_id].difference_update(alert_types)
                
                # If no subscriptions left, remove the stakeholder
                if not self.stakeholder_subscriptions[stakeholder_id]:
                    del self.stakeholder_subscriptions[stakeholder_id]
            
            # Persist subscriptions
            await self._save_stakeholder_subscriptions()
            return True
            
        except Exception as e:
            logger.error(f"Error removing stakeholder subscription: {e}")
            return False
    
    async def get_active_alerts(self, filters: Optional[Dict[str, Any]] = None) -> List[Alert]:
        """
        Get active alerts with optional filtering.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of active alerts matching filters
        """
        alerts = list(self.active_alerts.values())
        
        if not filters:
            return alerts
        
        filtered_alerts = []
        for alert in alerts:
            match = True
            
            # Apply each filter
            for key, value in filters.items():
                if key == "severity":
                    if alert.severity != AlertSeverity(value):
                        match = False
                        break
                elif key == "source":
                    if alert.source != value:
                        match = False
                        break
                elif key == "min_priority":
                    if alert.priority_score < value:
                        match = False
                        break
                elif key == "alert_type":
                    if alert.alert_type != value:
                        match = False
                        break
                elif key == "region":
                    if not hasattr(alert, 'regions') or value not in alert.regions:
                        match = False
                        break
            
            if match:
                filtered_alerts.append(alert)
        
        return filtered_alerts
    
    async def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get history of processed alerts.
        
        Args:
            limit: Maximum number of history entries to return
            
        Returns:
            List of alert history entries
        """
        return self.alert_history[-limit:]
    
    async def acknowledge_alert(self, alert_id: str, 
                              acknowledged_by: str) -> Optional[Alert]:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: ID of the alert to acknowledge
            acknowledged_by: ID or name of the user acknowledging the alert
            
        Returns:
            Updated alert or None if not found
        """
        if alert_id not in self.active_alerts:
            return None
        
        alert = self.active_alerts[alert_id]
        alert.acknowledged = True
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.utcnow()
        
        return alert
    
    async def close_alert(self, alert_id: str, 
                        closed_by: str,
                        resolution_notes: Optional[str] = None) -> Optional[Alert]:
        """
        Close an alert.
        
        Args:
            alert_id: ID of the alert to close
            closed_by: ID or name of the user closing the alert
            resolution_notes: Optional notes on resolution
            
        Returns:
            Updated alert or None if not found
        """
        if alert_id not in self.active_alerts:
            return None
        
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.CLOSED
        alert.closed_by = closed_by
        alert.closed_at = datetime.utcnow()
        
        if resolution_notes:
            alert.resolution_notes = resolution_notes
        
        # Remove from active alerts
        del self.active_alerts[alert_id]
        
        # Add to history if not already there
        history_entry = next((h for h in self.alert_history if h["alert_id"] == alert_id), None)
        if not history_entry:
            self.alert_history.append({
                "alert_id": alert.id,
                "title": alert.title,
                "source": alert.source,
                "severity": alert.severity.value,
                "closed_at": alert.closed_at.isoformat(),
                "closed_by": closed_by,
            })
        else:
            history_entry["closed_at"] = alert.closed_at.isoformat()
            history_entry["closed_by"] = closed_by
        
        return alert
    
    async def set_maintenance_mode(self, enabled: bool) -> bool:
        """
        Set the system maintenance mode.
        
        Args:
            enabled: True to enable maintenance mode, False to disable
            
        Returns:
            bool: Current maintenance mode state
        """
        self.maintenance_mode = enabled
        logger.info(f"Maintenance mode {'enabled' if enabled else 'disabled'}")
        return self.maintenance_mode
    
    async def _deduplicate_alerts(self, alerts: List[Alert]) -> List[Alert]:
        """
        Remove duplicate alerts based on content similarity.
        
        Args:
            alerts: List of alerts to deduplicate
            
        Returns:
            List of unique alerts
        """
        if not alerts:
            return []
        
        unique_alerts = []
        unique_fingerprints = set()
        
        for alert in alerts:
            # Generate fingerprint
            fingerprint = f"{alert.source}:{alert.alert_type}:{alert.title}"
            
            # Check if this is a duplicate
            if fingerprint in unique_fingerprints:
                continue
            
            # Check against active alerts
            is_active = False
            for active_alert in self.active_alerts.values():
                active_fingerprint = f"{active_alert.source}:{active_alert.alert_type}:{active_alert.title}"
                if fingerprint == active_fingerprint:
                    is_active = True
                    break
            
            if not is_active:
                unique_fingerprints.add(fingerprint)
                unique_alerts.append(alert)
        
        logger.info(f"Deduplicated {len(alerts)} alerts to {len(unique_alerts)} unique alerts")
        return unique_alerts
    
    async def _get_stakeholders_for_alert(self, alert: Alert) -> Set[str]:
        """
        Get stakeholders who should receive this alert.
        
        Args:
            alert: The alert to check
            
        Returns:
            Set of stakeholder IDs
        """
        recipients = set()
        
        # Check subscriptions
        for stakeholder_id, alert_types in self.stakeholder_subscriptions.items():
            if alert.alert_type in alert_types or "*" in alert_types:
                recipients.add(stakeholder_id)
        
        # For critical alerts, notify emergency management stakeholders
        if alert.severity == AlertSeverity.CRITICAL:
            emergency_stakeholders = await self._get_emergency_stakeholders()
            recipients.update([s.id for s in emergency_stakeholders])
        
        # Add region-specific stakeholders if applicable
        if hasattr(alert, 'regions') and alert.regions:
            regional_stakeholders = await self._get_regional_stakeholders(alert.regions)
            recipients.update([s.id for s in regional_stakeholders])
        
        return recipients
    
    async def _get_stakeholder(self, stakeholder_id: str) -> Optional[Dict[str, Any]]:
        """
        Get stakeholder information by ID.
        
        Args:
            stakeholder_id: Stakeholder ID to look up
            
        Returns:
            Stakeholder information or None if not found
        """
        try:
            # This would typically fetch from a database
            # For now, use the federation client
            return await self.federation_client.get_stakeholder(stakeholder_id)
        except Exception as e:
            logger.error(f"Error fetching stakeholder {stakeholder_id}: {e}")
            return None
    
    async def _get_emergency_stakeholders(self) -> List[Stakeholder]:
        """
        Get stakeholders with emergency management responsibilities.
        
        Returns:
            List of emergency management stakeholders
        """
        try:
            return await self.federation_client.get_stakeholders_by_group(
                StakeholderGroup.EMERGENCY_MANAGEMENT
            )
        except Exception as e:
            logger.error(f"Error fetching emergency stakeholders: {e}")
            return []
    
    async def _get_regional_stakeholders(self, regions: List[str]) -> List[Stakeholder]:
        """
        Get stakeholders for specific regions.
        
        Args:
            regions: List of region codes
            
        Returns:
            List of regional stakeholders
        """
        try:
            stakeholders = []
            for region in regions:
                regional = await self.federation_client.get_stakeholders_by_region(region)
                stakeholders.extend(regional)
            return stakeholders
        except Exception as e:
            logger.error(f"Error fetching regional stakeholders: {e}")
            return []
    
    async def _format_alert_for_channel(self, alert: Alert, 
                                      channel_name: str,
                                      stakeholder: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Format an alert for a specific notification channel.
        
        Args:
            alert: The alert to format
            channel_name: The channel to format for
            stakeholder: The stakeholder receiving the alert
            
        Returns:
            Formatted message or None if formatting failed
        """
        try:
            channel = self.channel_manager.get_channel(channel_name)
            if not channel:
                return None
            
            # Format based on channel type
            if channel_name == "email":
                return {
                    "subject": f"{alert.severity.name} Alert: {alert.title}",
                    "html_body": self._generate_email_body(alert),
                    "text_body": self._generate_text_body(alert),
                    "recipients": [stakeholder.get("email")]
                }
            elif channel_name == "sms":
                return {
                    "body": self._generate_sms_body(alert),
                    "recipients": [stakeholder.get("phone")]
                }
            elif channel_name == "webhook":
                return {
                    "payload": {
                        "alert_id": alert.id,
                        "title": alert.title,
                        "description": alert.description,
                        "severity": alert.severity.value,
                        "source": alert.source,
                        "alert_type": alert.alert_type,
                        "url": alert.url,
                        "created_at": alert.created_at.isoformat() if alert.created_at else None,
                    },
                    "recipients": stakeholder.get("webhook_endpoints", [])
                }
            else:
                logger.warning(f"Unsupported channel type: {channel_name}")
                return None
        
        except Exception as e:
            logger.error(f"Error formatting alert for channel {channel_name}: {e}")
            return None
    
    def _generate_email_body(self, alert: Alert) -> str:
        """Generate HTML email body for an alert."""
        severity_color = {
            AlertSeverity.CRITICAL: "#FF0000",
            AlertSeverity.HIGH: "#FF9900",
            AlertSeverity.MEDIUM: "#FFCC00",
            AlertSeverity.LOW: "#CCFF00",
            AlertSeverity.INFORMATIONAL: "#00CCFF"
        }.get(alert.severity, "#CCCCCC")
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: {severity_color}; padding: 10px; text-align: center;">
                <h2 style="margin: 0; color: white;">{alert.severity.name} ALERT</h2>
            </div>
            <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
                <h3>{alert.title}</h3>
                <p><strong>Source:</strong> {alert.source}</p>
                <p><strong>Time:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC') if alert.created_at else 'N/A'}</p>
                <p><strong>Description:</strong></p>
                <p>{alert.description}</p>
                
                {'<p><strong>Recommended Actions:</strong></p><ul>' + ''.join([f'<li>{action}</li>' for action in alert.recommended_actions]) + '</ul>' if hasattr(alert, 'recommended_actions') and alert.recommended_actions else ''}
                
                {'<p><strong>Affected Regions:</strong> ' + ', '.join(alert.regions) + '</p>' if hasattr(alert, 'regions') and alert.regions else ''}
                
                {'<p><a href="' + alert.url + '" style="display: inline-block; background-color: #007BFF; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px;">More Information</a></p>' if alert.url else ''}
            </div>
            <div style="padding: 10px; background-color: #f5f5f5; font-size: 12px; text-align: center;">
                <p>This is an automated alert from the Federal Agency Unified Notification System.</p>
                <p>To manage your notification preferences, log in to your agency portal.</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _generate_text_body(self, alert: Alert) -> str:
        """Generate plain text email body for an alert."""
        text = f"""
{alert.severity.name} ALERT: {alert.title}

Source: {alert.source}
Time: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC') if alert.created_at else 'N/A'}

{alert.description}

"""
        
        if hasattr(alert, 'recommended_actions') and alert.recommended_actions:
            text += "RECOMMENDED ACTIONS:\n"
            for action in alert.recommended_actions:
                text += f"- {action}\n"
            text += "\n"
            
        if hasattr(alert, 'regions') and alert.regions:
            text += f"AFFECTED REGIONS: {', '.join(alert.regions)}\n\n"
            
        if alert.url:
            text += f"More Information: {alert.url}\n\n"
            
        text += "This is an automated alert from the Federal Agency Unified Notification System."
        return text
    
    def _generate_sms_body(self, alert: Alert) -> str:
        """Generate SMS text for an alert."""
        # Keep SMS short due to character limitations
        return f"{alert.severity.name} ALERT: {alert.title} - {alert.description[:100]}{'...' if len(alert.description) > 100 else ''}"
    
    async def _load_stakeholder_subscriptions(self) -> None:
        """Load stakeholder subscriptions from persistent storage."""
        try:
            # This would typically load from a database
            # For demo purposes, we'll use the federation client
            subscriptions = await self.federation_client.get_subscriptions()
            
            for subscription in subscriptions:
                stakeholder_id = subscription.get("stakeholder_id")
                alert_types = subscription.get("alert_types", [])
                
                if stakeholder_id and alert_types:
                    if stakeholder_id not in self.stakeholder_subscriptions:
                        self.stakeholder_subscriptions[stakeholder_id] = set()
                    self.stakeholder_subscriptions[stakeholder_id].update(alert_types)
                    
            logger.info(f"Loaded subscriptions for {len(self.stakeholder_subscriptions)} stakeholders")
            
        except Exception as e:
            logger.error(f"Error loading stakeholder subscriptions: {e}")
    
    async def _save_stakeholder_subscriptions(self) -> None:
        """Save stakeholder subscriptions to persistent storage."""
        try:
            # This would typically save to a database
            # For demo purposes, we'll use the federation client
            subscriptions = []
            
            for stakeholder_id, alert_types in self.stakeholder_subscriptions.items():
                subscriptions.append({
                    "stakeholder_id": stakeholder_id,
                    "alert_types": list(alert_types)
                })
                
            await self.federation_client.update_subscriptions(subscriptions)
            logger.info("Saved stakeholder subscriptions")
            
        except Exception as e:
            logger.error(f"Error saving stakeholder subscriptions: {e}")