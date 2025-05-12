"""
Adapters for the Contact Tracing service.
Provides integration with notification systems.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
import json
import requests
from abc import ABC, abstractmethod

from agency_implementation.cdc.models.human_disease import Contact

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationAdapter:
    """
    Adapter for sending notifications to contacts.
    
    Provides methods for sending various types of notifications to contacts
    through different channels (SMS, email, etc.).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the adapter.
        
        Args:
            config: Configuration dictionary with connection details
        """
        self.config = config
        self.api_url = config.get('api_url')
        self.api_key = config.get('api_key')
        self.sms_enabled = config.get('sms_enabled', False)
        self.email_enabled = config.get('email_enabled', False)
        self.notification_templates = config.get('templates', {})
        self.default_sender = config.get('default_sender', 'CDC Contact Tracing')
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"NotificationAdapter initialized with SMS enabled: {self.sms_enabled}, Email enabled: {self.email_enabled}")
    
    def send_notification(self, contact: Contact, notification_type: str, data: Dict[str, Any] = None) -> bool:
        """
        Send a notification to a contact.
        
        Args:
            contact: The contact to notify
            notification_type: Type of notification to send
            data: Additional data for the notification
            
        Returns:
            True if successful, False otherwise
        """
        if data is None:
            data = {}
            
        # Get contact information
        if not hasattr(contact, 'contact_info') or not contact.contact_info:
            logger.warning(f"Contact {contact.id} has no contact information")
            return False
        
        notification_sent = False
        
        # Try SMS if enabled and phone available
        if self.sms_enabled and 'phone' in contact.contact_info and contact.contact_info['phone']:
            sms_sent = self._send_sms(contact, notification_type, data)
            if sms_sent:
                notification_sent = True
        
        # Try email if enabled and email available
        if self.email_enabled and 'email' in contact.contact_info and contact.contact_info['email']:
            email_sent = self._send_email(contact, notification_type, data)
            if email_sent:
                notification_sent = True
        
        return notification_sent
    
    def _send_sms(self, contact: Contact, notification_type: str, data: Dict[str, Any]) -> bool:
        """
        Send an SMS notification.
        
        Args:
            contact: The contact to notify
            notification_type: Type of notification to send
            data: Additional data for the notification
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the phone number
            phone = contact.contact_info.get('phone')
            if not phone:
                return False
            
            # Get the template for this notification type
            template = self.notification_templates.get('sms', {}).get(notification_type)
            if not template:
                logger.warning(f"No SMS template found for notification type: {notification_type}")
                return False
            
            # Format the message with contact and data values
            message = self._format_template(template, contact, data)
            
            # In a real implementation, this would use a service like Twilio
            # For demonstration, we just log the message
            if not self.api_url:
                logger.info(f"Would send SMS to {phone}: {message}")
                return True
            
            # This is where the actual API call would happen
            # endpoint = 'sms/send'
            # url = f"{self.api_url}/{endpoint}"
            # payload = {
            #    'to': phone,
            #    'message': message,
            #    'sender': self.default_sender
            # }
            # response = requests.post(url, headers=self.headers, json=payload)
            # response.raise_for_status()
            # return True
            
            # For demonstration, return success
            logger.info(f"Would send SMS to {phone}: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {str(e)}")
            return False
    
    def _send_email(self, contact: Contact, notification_type: str, data: Dict[str, Any]) -> bool:
        """
        Send an email notification.
        
        Args:
            contact: The contact to notify
            notification_type: Type of notification to send
            data: Additional data for the notification
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the email address
            email = contact.contact_info.get('email')
            if not email:
                return False
            
            # Get the template for this notification type
            subject_template = self.notification_templates.get('email', {}).get(f"{notification_type}_subject")
            body_template = self.notification_templates.get('email', {}).get(f"{notification_type}_body")
            
            if not subject_template or not body_template:
                logger.warning(f"No email template found for notification type: {notification_type}")
                return False
            
            # Format the subject and body with contact and data values
            subject = self._format_template(subject_template, contact, data)
            body = self._format_template(body_template, contact, data)
            
            # In a real implementation, this would use an email service
            # For demonstration, we just log the message
            if not self.api_url:
                logger.info(f"Would send email to {email}: Subject: {subject}, Body: {body}")
                return True
            
            # This is where the actual API call would happen
            # endpoint = 'email/send'
            # url = f"{self.api_url}/{endpoint}"
            # payload = {
            #    'to': email,
            #    'subject': subject,
            #    'body': body,
            #    'sender': self.default_sender
            # }
            # response = requests.post(url, headers=self.headers, json=payload)
            # response.raise_for_status()
            # return True
            
            # For demonstration, return success
            logger.info(f"Would send email to {email}: Subject: {subject}, Body: {body}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False
    
    def _format_template(self, template: str, contact: Contact, data: Dict[str, Any]) -> str:
        """
        Format a template with contact and data values.
        
        Args:
            template: Template string with placeholders
            contact: Contact object for contact-specific values
            data: Additional data for other placeholders
            
        Returns:
            Formatted message
        """
        # Create a context with contact attributes
        context = {
            'id': contact.id,
            'person_id': contact.person_id if hasattr(contact, 'person_id') else '',
            'case_id': contact.case_id if hasattr(contact, 'case_id') else '',
            'contact_date': contact.contact_date.isoformat() if hasattr(contact, 'contact_date') and not isinstance(contact.contact_date, str) else contact.contact_date if hasattr(contact, 'contact_date') else '',
            'name': contact.contact_info.get('name', '') if hasattr(contact, 'contact_info') else '',
            'monitoring_status': contact.monitoring_status if hasattr(contact, 'monitoring_status') else '',
            'risk_level': contact.risk_assessment.value if hasattr(contact, 'risk_assessment') and hasattr(contact.risk_assessment, 'value') else ''
        }
        
        # Add data values to context
        context.update(data)
        
        # Add current date to context
        context['current_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Format the template with context values
        formatted = template
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            formatted = formatted.replace(placeholder, str(value))
        
        return formatted
    
    def bulk_send_notifications(self, contacts: List[Contact], notification_type: str, data: Dict[str, Any] = None) -> Dict[str, bool]:
        """
        Send notifications to multiple contacts.
        
        Args:
            contacts: List of contacts to notify
            notification_type: Type of notification to send
            data: Additional data for the notifications
            
        Returns:
            Dictionary mapping contact IDs to success status
        """
        if data is None:
            data = {}
            
        results = {}
        
        for contact in contacts:
            success = self.send_notification(contact, notification_type, data)
            results[contact.id] = success
        
        return results
    
    def notify_monitoring_instructions(self, contact: Contact) -> bool:
        """
        Send monitoring instructions to a contact.
        
        Args:
            contact: The contact to notify
            
        Returns:
            True if successful, False otherwise
        """
        # Additional data for monitoring instructions
        data = {
            'monitoring_duration': '14 days',
            'monitoring_start_date': datetime.now().strftime('%Y-%m-%d'),
            'monitoring_end_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'symptom_list': 'fever, cough, shortness of breath, loss of taste or smell',
            'report_phone': self.config.get('report_phone', '1-800-CDC-INFO'),
            'report_website': self.config.get('report_website', 'https://www.cdc.gov/report')
        }
        
        return self.send_notification(contact, 'monitoring_instructions', data)
    
    def notify_test_recommendation(self, contact: Contact, test_location: str, test_date: str) -> bool:
        """
        Send test recommendation notification to a contact.
        
        Args:
            contact: The contact to notify
            test_location: Location for testing
            test_date: Recommended test date
            
        Returns:
            True if successful, False otherwise
        """
        data = {
            'test_location': test_location,
            'test_date': test_date,
            'test_type': 'PCR test',
            'preparation_instructions': 'No food or drink 30 minutes before test'
        }
        
        return self.send_notification(contact, 'test_recommendation', data)
    
    def notify_isolation_instructions(self, contact: Contact) -> bool:
        """
        Send isolation instructions to a contact.
        
        Args:
            contact: The contact to notify
            
        Returns:
            True if successful, False otherwise
        """
        data = {
            'isolation_duration': '10 days',
            'isolation_start_date': datetime.now().strftime('%Y-%m-%d'),
            'isolation_end_date': (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'support_resources': 'Visit www.cdc.gov/isolation for support resources',
            'emergency_symptoms': 'difficulty breathing, persistent pain or pressure in the chest, confusion'
        }
        
        return self.send_notification(contact, 'isolation_instructions', data)