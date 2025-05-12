"""Notification service interface for alerts and communication."""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime

from .base_service import BaseService

class NotificationService(BaseService):
    """Abstract base class for notification services.
    
    This service is responsible for generating and sending notifications,
    alerts, and other communications to users, stakeholders, and systems
    based on detected events or scheduled updates.
    """
    
    def default_config(self) -> Dict[str, Any]:
        """Get the default configuration for notifications.
        
        Returns:
            Dictionary with default configuration values
        """
        return {
            "default_channels": ["email", "sms", "dashboard"],
            "priority_levels": ["low", "medium", "high", "critical"],
            "default_priority": "medium",
            "throttling": {"enabled": True, "max_per_hour": 10},
            "templates": {},
            "suppress_duplicates": True,
            "duplicate_window_minutes": 60,
        }
    
    @abstractmethod
    def send_notification(self, message: Dict[str, Any],
                        recipients: List[Dict[str, Any]],
                        channels: Optional[List[str]] = None,
                        parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a notification to specified recipients.
        
        Args:
            message: Notification message content and metadata
            recipients: List of recipient specifications
            channels: Optional list of channels to use
            parameters: Optional notification parameters
            
        Returns:
            Dictionary with notification results and metadata
        """
        pass
    
    @abstractmethod
    def create_alert(self, alert_type: str,
                   data: Dict[str, Any],
                   severity: str,
                   parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create an alert based on a detected event or condition.
        
        Args:
            alert_type: Type of alert to create
            data: Alert data and context
            severity: Alert severity level
            parameters: Optional alert parameters
            
        Returns:
            Dictionary with created alert details
        """
        pass
    
    @abstractmethod
    def register_template(self, template_id: str,
                        template_content: Dict[str, Any]) -> None:
        """Register a notification template.
        
        Args:
            template_id: Identifier for the template
            template_content: Template content and metadata
        """
        pass
    
    @abstractmethod
    def get_notification_history(self, filters: Optional[Dict[str, Any]] = None,
                              limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical notification records.
        
        Args:
            filters: Optional filters for notification history
            limit: Maximum number of records to return
            
        Returns:
            List of notification history records
        """
        pass
    
    @abstractmethod
    def schedule_notification(self, message: Dict[str, Any],
                           recipients: List[Dict[str, Any]],
                           schedule_time: datetime,
                           parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Schedule a notification for future delivery.
        
        Args:
            message: Notification message content and metadata
            recipients: List of recipient specifications
            schedule_time: When to send the notification
            parameters: Optional notification parameters
            
        Returns:
            Dictionary with scheduled notification details
        """
        pass
    
    @abstractmethod
    def create_digest(self, events: List[Dict[str, Any]],
                    recipients: List[Dict[str, Any]],
                    parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a digest of multiple events for notification.
        
        Args:
            events: List of events to include in digest
            recipients: List of recipient specifications
            parameters: Optional digest parameters
            
        Returns:
            Dictionary with digest notification details
        """
        pass
