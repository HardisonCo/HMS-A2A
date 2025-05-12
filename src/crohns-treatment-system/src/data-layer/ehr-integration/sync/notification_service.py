#!/usr/bin/env python3
"""
EHR Notification Service for Crohn's Disease Treatment System
This module provides a service for handling notifications about patient data changes,
including critical updates to patient records and integration with the adaptive trial system.
"""
import os
import json
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Callable, Awaitable
from datetime import datetime, timedelta
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ehr-notification")

class NotificationPriority(Enum):
    """Priority levels for notifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationType(Enum):
    """Types of notifications"""
    PATIENT_UPDATE = "patient_update"
    MEDICATION_CHANGE = "medication_change"
    LAB_RESULT = "lab_result"
    DISEASE_SEVERITY_CHANGE = "disease_severity_change"
    ADVERSE_EVENT = "adverse_event"
    TRIAL_STATUS_CHANGE = "trial_status_change"
    SYNC_ISSUE = "sync_issue"
    SYSTEM_ALERT = "system_alert"

class Notification:
    """Notification about patient data changes"""
    def __init__(
        self,
        notification_type: NotificationType,
        subject: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        metadata: Dict[str, Any] = None,
        timestamp: Optional[datetime] = None,
        id: Optional[str] = None,
        read: bool = False
    ):
        self.id = id or f"{int(time.time())}-{subject}-{notification_type.value}"
        self.notification_type = notification_type
        self.subject = subject  # Usually patient_id
        self.message = message
        self.priority = priority
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now()
        self.read = read
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "notification_type": self.notification_type.value,
            "subject": self.subject,
            "message": self.message,
            "priority": self.priority.value,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "read": self.read
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """Create from dictionary representation"""
        return cls(
            id=data["id"],
            notification_type=NotificationType(data["notification_type"]),
            subject=data["subject"],
            message=data["message"],
            priority=NotificationPriority(data["priority"]),
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            read=data.get("read", False)
        )

class NotificationHandler:
    """Base class for notification handlers"""
    async def handle(self, notification: Notification) -> bool:
        """
        Handle a notification
        
        Args:
            notification: The notification to handle
            
        Returns:
            True if the notification was handled successfully, False otherwise
        """
        raise NotImplementedError("Notification handlers must implement handle()")

class EmailNotificationHandler(NotificationHandler):
    """Notification handler that sends emails"""
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        recipient_mapping: Dict[str, str]
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.recipient_mapping = recipient_mapping
    
    async def handle(self, notification: Notification) -> bool:
        """
        Handle a notification by sending an email
        
        Args:
            notification: The notification to handle
            
        Returns:
            True if the email was sent successfully, False otherwise
        """
        # This is a placeholder implementation
        # In a real implementation, this would connect to SMTP server and send email
        logger.info(
            f"Sending email notification: {notification.message} "
            f"to {self.recipient_mapping.get(notification.subject, 'default@example.com')}"
        )
        
        # Simulate email sending
        await asyncio.sleep(0.5)
        
        logger.info("Email notification sent successfully")
        return True

class WebhookNotificationHandler(NotificationHandler):
    """Notification handler that sends HTTP webhooks"""
    def __init__(
        self,
        webhook_url: str,
        headers: Dict[str, str] = None,
        timeout: int = 10
    ):
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout
    
    async def handle(self, notification: Notification) -> bool:
        """
        Handle a notification by sending a webhook
        
        Args:
            notification: The notification to handle
            
        Returns:
            True if the webhook was sent successfully, False otherwise
        """
        # This is a placeholder implementation
        # In a real implementation, this would make an HTTP POST request
        logger.info(f"Sending webhook notification to {self.webhook_url}")
        
        # Simulate webhook request
        await asyncio.sleep(0.3)
        
        logger.info("Webhook notification sent successfully")
        return True

class TrialSystemNotificationHandler(NotificationHandler):
    """Notification handler that updates the adaptive trial system"""
    def __init__(
        self,
        api_base_url: str,
        api_key: str = None
    ):
        self.api_base_url = api_base_url
        self.api_key = api_key
    
    async def handle(self, notification: Notification) -> bool:
        """
        Handle a notification by updating the adaptive trial system
        
        Args:
            notification: The notification to handle
            
        Returns:
            True if the trial system was updated successfully, False otherwise
        """
        # This is a placeholder implementation
        # In a real implementation, this would make API calls to trial system
        logger.info(f"Sending notification to trial system: {notification.message}")
        
        # Simulate API call
        await asyncio.sleep(0.2)
        
        logger.info("Trial system notification handled successfully")
        return True

class NotificationService:
    """
    Service for managing notifications about patient data changes
    Supports filtering, routing, and persistence of notifications
    """
    def __init__(
        self,
        data_dir: str = None,
        notification_ttl: int = 30  # Days to retain notifications
    ):
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data"
        )
        self.notifications_path = os.path.join(self.data_dir, "notifications.json")
        self.notification_ttl = notification_ttl
        self.handlers: Dict[NotificationType, List[NotificationHandler]] = {}
        self.notifications: List[Notification] = []
        self.running = False
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing notifications
        self._load_notifications()
        
        logger.info("Notification Service initialized")
    
    def _load_notifications(self) -> None:
        """Load notifications from file"""
        if not os.path.exists(self.notifications_path):
            self.notifications = []
            return
        
        try:
            with open(self.notifications_path, 'r') as f:
                notifications_data = json.load(f)
                self.notifications = [
                    Notification.from_dict(notification) for notification in notifications_data
                ]
            logger.info(f"Loaded {len(self.notifications)} notifications from file")
        except Exception as e:
            logger.error(f"Error loading notifications: {str(e)}")
            self.notifications = []
    
    def _save_notifications(self) -> None:
        """Save notifications to file"""
        try:
            # Remove expired notifications
            cutoff_time = datetime.now() - timedelta(days=self.notification_ttl)
            active_notifications = [
                notification for notification in self.notifications
                if notification.timestamp > cutoff_time
            ]
            
            with open(self.notifications_path, 'w') as f:
                json.dump([notification.to_dict() for notification in active_notifications], f, indent=2)
            
            # Update in-memory list with pruned list
            self.notifications = active_notifications
            
            logger.info(f"Saved {len(active_notifications)} notifications to file")
        except Exception as e:
            logger.error(f"Error saving notifications: {str(e)}")
    
    def register_handler(
        self,
        notification_type: NotificationType,
        handler: NotificationHandler
    ) -> None:
        """
        Register a notification handler for a specific notification type
        
        Args:
            notification_type: Type of notifications to handle
            handler: Handler to process notifications
        """
        if notification_type not in self.handlers:
            self.handlers[notification_type] = []
        
        self.handlers[notification_type].append(handler)
        logger.info(f"Registered handler for {notification_type.value} notifications")
    
    def register_generic_handler(
        self,
        handler: NotificationHandler
    ) -> None:
        """
        Register a handler for all notification types
        
        Args:
            handler: Handler to process all notifications
        """
        for notification_type in NotificationType:
            self.register_handler(notification_type, handler)
        
        logger.info("Registered generic handler for all notification types")
    
    async def publish_notification(
        self,
        notification: Notification
    ) -> List[bool]:
        """
        Publish a notification to all registered handlers and store it
        
        Args:
            notification: The notification to publish
            
        Returns:
            List of boolean results from handlers (True for success, False for failure)
        """
        logger.info(
            f"Publishing {notification.priority.value} priority "
            f"{notification.notification_type.value} notification: {notification.message}"
        )
        
        # Store notification
        self.notifications.append(notification)
        self._save_notifications()
        
        # Get handlers for this notification type
        type_handlers = self.handlers.get(notification.notification_type, [])
        
        # Process notification with handlers
        results = []
        for handler in type_handlers:
            try:
                result = await handler.handle(notification)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in notification handler: {str(e)}")
                results.append(False)
        
        logger.info(
            f"Notification published with {sum(results)}/{len(results)} "
            f"successful handler executions"
        )
        
        return results
    
    async def start(self) -> None:
        """Start the notification service"""
        if self.running:
            logger.warning("Notification Service is already running")
            return
        
        self.running = True
        logger.info("Notification Service started")
        
        try:
            while self.running:
                # Periodically clean up old notifications
                cutoff_time = datetime.now() - timedelta(days=self.notification_ttl)
                original_count = len(self.notifications)
                
                self.notifications = [
                    notification for notification in self.notifications
                    if notification.timestamp > cutoff_time
                ]
                
                if len(self.notifications) < original_count:
                    logger.info(
                        f"Cleaned up {original_count - len(self.notifications)} "
                        f"expired notifications"
                    )
                    self._save_notifications()
                
                # Sleep for an hour before next cleanup
                await asyncio.sleep(3600)
        except Exception as e:
            logger.error(f"Error in Notification Service: {str(e)}")
            self.running = False
    
    def stop(self) -> None:
        """Stop the notification service"""
        self.running = False
        logger.info("Notification Service stopped")
    
    def get_notifications(
        self,
        subject: Optional[str] = None,
        notification_type: Optional[NotificationType] = None,
        priority: Optional[NotificationPriority] = None,
        read_status: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get filtered notifications
        
        Args:
            subject: Filter by subject (usually patient_id)
            notification_type: Filter by notification type
            priority: Filter by priority
            read_status: Filter by read status
            limit: Maximum number of notifications to return
            offset: Number of notifications to skip
            
        Returns:
            List of notification dictionaries
        """
        filtered_notifications = self.notifications
        
        if subject:
            filtered_notifications = [
                n for n in filtered_notifications if n.subject == subject
            ]
        
        if notification_type:
            filtered_notifications = [
                n for n in filtered_notifications if n.notification_type == notification_type
            ]
        
        if priority:
            filtered_notifications = [
                n for n in filtered_notifications if n.priority == priority
            ]
        
        if read_status is not None:
            filtered_notifications = [
                n for n in filtered_notifications if n.read == read_status
            ]
        
        # Sort by timestamp (newest first)
        sorted_notifications = sorted(
            filtered_notifications,
            key=lambda n: n.timestamp,
            reverse=True
        )
        
        # Apply pagination
        paginated_notifications = sorted_notifications[offset:offset + limit]
        
        return [n.to_dict() for n in paginated_notifications]
    
    def mark_as_read(
        self,
        notification_id: str
    ) -> bool:
        """
        Mark a notification as read
        
        Args:
            notification_id: ID of the notification to mark as read
            
        Returns:
            True if the notification was found and marked as read, False otherwise
        """
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.read = True
                self._save_notifications()
                return True
        
        return False
    
    def mark_all_as_read(
        self,
        subject: Optional[str] = None
    ) -> int:
        """
        Mark all notifications as read
        
        Args:
            subject: If provided, only mark notifications for this subject as read
            
        Returns:
            Number of notifications marked as read
        """
        count = 0
        for notification in self.notifications:
            if subject is None or notification.subject == subject:
                if not notification.read:
                    notification.read = True
                    count += 1
        
        if count > 0:
            self._save_notifications()
        
        return count
    
    def delete_notification(
        self,
        notification_id: str
    ) -> bool:
        """
        Delete a notification
        
        Args:
            notification_id: ID of the notification to delete
            
        Returns:
            True if the notification was found and deleted, False otherwise
        """
        original_count = len(self.notifications)
        self.notifications = [
            n for n in self.notifications if n.id != notification_id
        ]
        
        if len(self.notifications) < original_count:
            self._save_notifications()
            return True
        
        return False

# Factory methods for common notification types
def create_medication_change_notification(
    patient_id: str,
    medication_name: str,
    change_type: str,  # "started", "stopped", "dose_changed"
    details: str,
    priority: NotificationPriority = NotificationPriority.HIGH
) -> Notification:
    """Create a notification for medication changes"""
    return Notification(
        notification_type=NotificationType.MEDICATION_CHANGE,
        subject=patient_id,
        message=f"Medication change: {medication_name} {change_type} - {details}",
        priority=priority,
        metadata={
            "medication_name": medication_name,
            "change_type": change_type,
            "details": details
        }
    )

def create_lab_result_notification(
    patient_id: str,
    test_name: str,
    result: str,
    is_abnormal: bool,
    reference_range: str = None,
    priority: NotificationPriority = None
) -> Notification:
    """Create a notification for lab results"""
    # Set priority based on abnormality
    if priority is None:
        priority = NotificationPriority.HIGH if is_abnormal else NotificationPriority.MEDIUM
    
    message_parts = [f"Lab result: {test_name} - {result}"]
    if reference_range:
        message_parts.append(f"(Reference range: {reference_range})")
    if is_abnormal:
        message_parts.append("[ABNORMAL]")
    
    return Notification(
        notification_type=NotificationType.LAB_RESULT,
        subject=patient_id,
        message=" ".join(message_parts),
        priority=priority,
        metadata={
            "test_name": test_name,
            "result": result,
            "is_abnormal": is_abnormal,
            "reference_range": reference_range
        }
    )

def create_disease_severity_change_notification(
    patient_id: str,
    old_severity: str,
    new_severity: str,
    details: str = None
) -> Notification:
    """Create a notification for disease severity changes"""
    message = f"Disease severity changed: {old_severity} → {new_severity}"
    if details:
        message += f" - {details}"
    
    # Determine priority based on change direction
    severity_levels = {
        "remission": 0,
        "mild": 1,
        "moderate": 2,
        "severe": 3
    }
    
    try:
        old_level = severity_levels.get(old_severity.lower(), 1)
        new_level = severity_levels.get(new_severity.lower(), 1)
        
        if new_level > old_level:
            priority = NotificationPriority.HIGH
        else:
            priority = NotificationPriority.MEDIUM
    except:
        priority = NotificationPriority.MEDIUM
    
    return Notification(
        notification_type=NotificationType.DISEASE_SEVERITY_CHANGE,
        subject=patient_id,
        message=message,
        priority=priority,
        metadata={
            "old_severity": old_severity,
            "new_severity": new_severity,
            "details": details
        }
    )

def create_adverse_event_notification(
    patient_id: str,
    event_description: str,
    severity: str,  # "mild", "moderate", "severe", "life_threatening"
    related_to_medication: bool = None,
    medication_name: str = None
) -> Notification:
    """Create a notification for adverse events"""
    message_parts = [f"Adverse event: {event_description} ({severity})"]
    
    if related_to_medication is not None:
        relation = "Related to" if related_to_medication else "Not related to"
        if medication_name:
            message_parts.append(f"{relation} {medication_name}")
        else:
            message_parts.append(f"{relation} medication")
    
    # Set priority based on severity
    priority_mapping = {
        "mild": NotificationPriority.MEDIUM,
        "moderate": NotificationPriority.HIGH,
        "severe": NotificationPriority.CRITICAL,
        "life_threatening": NotificationPriority.CRITICAL
    }
    priority = priority_mapping.get(severity.lower(), NotificationPriority.HIGH)
    
    return Notification(
        notification_type=NotificationType.ADVERSE_EVENT,
        subject=patient_id,
        message=" ".join(message_parts),
        priority=priority,
        metadata={
            "event_description": event_description,
            "severity": severity,
            "related_to_medication": related_to_medication,
            "medication_name": medication_name
        }
    )

def create_trial_status_change_notification(
    patient_id: str,
    old_status: str,
    new_status: str,
    details: str = None
) -> Notification:
    """Create a notification for trial status changes"""
    message = f"Trial status changed: {old_status} → {new_status}"
    if details:
        message += f" - {details}"
    
    return Notification(
        notification_type=NotificationType.TRIAL_STATUS_CHANGE,
        subject=patient_id,
        message=message,
        priority=NotificationPriority.MEDIUM,
        metadata={
            "old_status": old_status,
            "new_status": new_status,
            "details": details
        }
    )

def create_sync_issue_notification(
    subject: str,
    issue_description: str,
    priority: NotificationPriority = NotificationPriority.HIGH
) -> Notification:
    """Create a notification for synchronization issues"""
    return Notification(
        notification_type=NotificationType.SYNC_ISSUE,
        subject=subject,
        message=f"Sync issue: {issue_description}",
        priority=priority,
        metadata={
            "issue_description": issue_description
        }
    )

# CLI for testing
if __name__ == "__main__":
    # Create notification service
    service = NotificationService()
    
    # Register handlers
    email_handler = EmailNotificationHandler(
        smtp_server="smtp.example.com",
        smtp_port=587,
        sender_email="crohns-system@example.com",
        recipient_mapping={"default": "admin@example.com"}
    )
    
    webhook_handler = WebhookNotificationHandler(
        webhook_url="https://example.com/webhook"
    )
    
    trial_handler = TrialSystemNotificationHandler(
        api_base_url="https://api.example.com/trial"
    )
    
    # Register handlers for specific notification types
    service.register_handler(NotificationType.MEDICATION_CHANGE, email_handler)
    service.register_handler(NotificationType.LAB_RESULT, email_handler)
    service.register_handler(NotificationType.ADVERSE_EVENT, email_handler)
    
    service.register_handler(NotificationType.MEDICATION_CHANGE, webhook_handler)
    service.register_handler(NotificationType.ADVERSE_EVENT, webhook_handler)
    
    service.register_handler(NotificationType.MEDICATION_CHANGE, trial_handler)
    service.register_handler(NotificationType.LAB_RESULT, trial_handler)
    service.register_handler(NotificationType.DISEASE_SEVERITY_CHANGE, trial_handler)
    service.register_handler(NotificationType.ADVERSE_EVENT, trial_handler)
    
    # Create test notifications
    notifications = [
        create_medication_change_notification(
            patient_id="P12345",
            medication_name="Humira",
            change_type="started",
            details="40mg every other week"
        ),
        create_lab_result_notification(
            patient_id="P12345",
            test_name="C-reactive protein",
            result="12 mg/L",
            is_abnormal=True,
            reference_range="0-5 mg/L"
        ),
        create_disease_severity_change_notification(
            patient_id="P12345",
            old_severity="Moderate",
            new_severity="Mild",
            details="Reduced inflammation in ileum"
        ),
        create_adverse_event_notification(
            patient_id="P12345",
            event_description="Injection site reaction",
            severity="Mild",
            related_to_medication=True,
            medication_name="Humira"
        )
    ]
    
    # Test notification publishing
    async def test_notifications():
        for notification in notifications:
            await service.publish_notification(notification)
        
        # Start notification service
        await service.start()
    
    try:
        asyncio.run(test_notifications())
    except KeyboardInterrupt:
        print("Stopping notification service...")
        service.stop()