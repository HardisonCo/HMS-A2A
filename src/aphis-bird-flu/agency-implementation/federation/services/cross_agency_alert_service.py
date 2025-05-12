"""
Cross Agency Alert Service

This module implements a service for broadcasting alerts across multiple
agencies through the federation hub.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from ..core.federation_hub import get_federation_hub

logger = logging.getLogger(__name__)

class Alert(BaseModel):
    """Model for cross-agency alerts"""
    alert_id: str
    type: str  # disease_outbreak, environmental_hazard, emergency_response, etc.
    severity: str = "medium"  # low, medium, high, critical
    title: str
    details: Dict[str, Any] = Field(default_factory=dict)
    source_agency: str
    timestamp: datetime = Field(default_factory=datetime.now)
    location: Optional[Dict[str, Any]] = None
    expiration: Optional[datetime] = None

class CrossAgencyAlertService:
    """
    Service for broadcasting alerts across multiple agencies.
    
    This service provides capabilities for sending alerts, managing
    alert subscriptions, and tracking alert status across agencies.
    """
    
    def __init__(self):
        self.federation_hub = get_federation_hub()
        self._alert_history = []  # List of previously sent alerts
        logger.info("Cross Agency Alert Service initialized")
    
    def broadcast_alert(self, alert: Alert, agencies: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Broadcast an alert to multiple agencies
        
        Args:
            alert: Alert details
            agencies: Optional list of agency IDs to alert (None = all agencies)
            
        Returns:
            Dictionary mapping agency IDs to delivery status
        """
        logger.info(f"Broadcasting {alert.severity} alert '{alert.title}' from {alert.source_agency}")
        
        # Convert alert to dictionary representation
        alert_dict = alert.dict()
        
        # Add alert to history
        self._alert_history.append(alert_dict)
        
        # Broadcast through federation hub
        results = self.federation_hub.broadcast_alert(alert_dict, agencies)
        
        # Log results
        success_count = sum(1 for status in results.values() if status)
        failure_count = sum(1 for status in results.values() if not status)
        logger.info(f"Alert broadcast results: {success_count} successful, {failure_count} failed")
        
        return results
    
    def get_alert_history(self, 
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None,
                          source_agency: Optional[str] = None,
                          alert_types: Optional[List[str]] = None,
                          severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get history of alerts with optional filtering
        
        Args:
            start_time: Optional filter for alerts after this time
            end_time: Optional filter for alerts before this time
            source_agency: Optional filter for alerts from a specific agency
            alert_types: Optional filter for specific alert types
            severity: Optional filter for minimum severity level
            
        Returns:
            List of alerts matching the filter criteria
        """
        # Start with full history
        filtered_history = self._alert_history
        
        # Apply time filters
        if start_time:
            filtered_history = [
                alert for alert in filtered_history
                if alert["timestamp"] >= start_time
            ]
        
        if end_time:
            filtered_history = [
                alert for alert in filtered_history
                if alert["timestamp"] <= end_time
            ]
        
        # Apply source agency filter
        if source_agency:
            filtered_history = [
                alert for alert in filtered_history
                if alert["source_agency"] == source_agency
            ]
        
        # Apply alert type filter
        if alert_types:
            filtered_history = [
                alert for alert in filtered_history
                if alert["type"] in alert_types
            ]
        
        # Apply severity filter
        if severity:
            severity_levels = {
                "low": 0,
                "medium": 1,
                "high": 2,
                "critical": 3
            }
            min_severity_level = severity_levels.get(severity.lower(), 0)
            
            filtered_history = [
                alert for alert in filtered_history
                if severity_levels.get(alert["severity"].lower(), 0) >= min_severity_level
            ]
        
        return filtered_history
    
    def create_alert(self, 
                     alert_type: str,
                     title: str,
                     source_agency: str,
                     severity: str = "medium",
                     details: Optional[Dict[str, Any]] = None,
                     location: Optional[Dict[str, Any]] = None,
                     expiration: Optional[datetime] = None) -> Alert:
        """
        Create a new alert with automatic ID generation
        
        Args:
            alert_type: Type of alert
            title: Alert title
            source_agency: Source agency identifier
            severity: Alert severity level
            details: Optional alert details
            location: Optional location information
            expiration: Optional expiration time
            
        Returns:
            Created Alert object
        """
        # Generate a unique alert ID
        alert_id = f"{source_agency}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create the alert
        alert = Alert(
            alert_id=alert_id,
            type=alert_type,
            severity=severity,
            title=title,
            details=details or {},
            source_agency=source_agency,
            timestamp=datetime.now(),
            location=location,
            expiration=expiration
        )
        
        return alert