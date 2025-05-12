"""
Notification services for avian influenza alerting.

This package provides functionality for sending alerts and notifications
about avian influenza outbreaks, high-risk predictions, and system events
to stakeholders through various channels.
"""

from .notification_service import (
    NotificationService,
    NotificationChannel,
    EmailChannel,
    SMSChannel,
    WebhookChannel
)

__all__ = [
    'NotificationService',
    'NotificationChannel',
    'EmailChannel',
    'SMSChannel',
    'WebhookChannel'
]