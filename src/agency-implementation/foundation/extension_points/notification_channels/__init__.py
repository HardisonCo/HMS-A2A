"""
Notification Channel Extension Points

This module defines interfaces for extending the system with custom notification channels.
"""

from typing import Dict, List, Any, Optional, Union
import abc
from ..base import BaseExtensionPoint


class NotificationChannelExtensionPoint(BaseExtensionPoint):
    """
    Extension point for custom notification channels.
    
    Allows agencies to integrate custom notification channels for alerts, updates,
    and other communication needs.
    """
    
    _extension_type: str = "notification_channel"
    
    @abc.abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the notification channel.
        
        Args:
            config: Configuration parameters for the notification channel
            
        Returns:
            bool: True if initialization is successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def shutdown(self) -> None:
        """Shutdown and cleanup resources used by the notification channel."""
        pass
    
    @abc.abstractmethod
    async def send_notification(self, message: Dict[str, Any], recipients: List[str]) -> bool:
        """
        Send a notification to the specified recipients.
        
        Args:
            message: The notification message content and metadata
            recipients: List of recipient identifiers
            
        Returns:
            bool: True if sending is successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def send_batch(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send a batch of notifications.
        
        Args:
            messages: List of message objects with recipient information
            
        Returns:
            Dict with results information, e.g., success count, failures
        """
        pass
    
    @abc.abstractmethod
    def get_channel_info(self) -> Dict[str, Any]:
        """
        Get information about this notification channel.
        
        Returns:
            Dict with channel information and capabilities
        """
        pass
    
    @abc.abstractmethod
    def format_message(self, template_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a message using a template.
        
        Args:
            template_name: Name of the template to use
            data: Data to populate the template
            
        Returns:
            Dict with formatted message content
        """
        pass
    
    @abc.abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        """
        Validate if a recipient is properly formatted for this channel.
        
        Args:
            recipient: Recipient identifier to validate
            
        Returns:
            bool: True if recipient format is valid, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the delivery status of a sent message.
        
        Args:
            message_id: The ID of the message to check
            
        Returns:
            Dict with delivery status information
        """
        pass


# Import specific notification channel implementations for easy access
from .email import EmailNotificationChannel
from .sms import SMSNotificationChannel
from .webhook import WebhookNotificationChannel

__all__ = [
    'NotificationChannelExtensionPoint',
    'EmailNotificationChannel',
    'SMSNotificationChannel',
    'WebhookNotificationChannel',
]