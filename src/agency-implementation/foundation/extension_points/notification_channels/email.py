"""
Email Notification Channel

Extension point implementation for email-based notifications.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import re
import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, BaseLoader, select_autoescape
from . import NotificationChannelExtensionPoint
from .. import base

logger = logging.getLogger(__name__)

@base.BaseExtensionPoint.extension_point("notification_channel", "email")
class EmailNotificationChannel(NotificationChannelExtensionPoint):
    """Implementation of notification channel extension point for email notifications."""
    
    def __init__(self):
        self.smtp_host = None
        self.smtp_port = None
        self.smtp_user = None
        self.smtp_password = None
        self.use_tls = True
        self.default_sender = None
        self.templates = {}
        self.jinja_env = None
        self.is_initialized = False
        self.message_statuses = {}
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the email notification channel.
        
        Args:
            config: Configuration parameters for SMTP connection
            
        Returns:
            bool: True if initialization successful
        """
        try:
            self.smtp_host = config["smtp_host"]
            self.smtp_port = config.get("smtp_port", 587)
            self.smtp_user = config.get("smtp_user", "")
            self.smtp_password = config.get("smtp_password", "")
            self.use_tls = config.get("use_tls", True)
            self.default_sender = config.get("default_sender", "")
            
            # Load templates if provided
            templates_config = config.get("templates", {})
            for name, template_config in templates_config.items():
                subject = template_config.get("subject", "")
                html_body = template_config.get("html_body", "")
                text_body = template_config.get("text_body", "")
                
                self.templates[name] = {
                    "subject": subject,
                    "html_body": html_body,
                    "text_body": text_body,
                }
            
            # Initialize Jinja2 environment for template rendering
            self.jinja_env = Environment(
                loader=BaseLoader(),
                autoescape=select_autoescape(['html', 'xml']),
                enable_async=True,
            )
            
            # Test SMTP connection
            if config.get("test_connection", True):
                try:
                    smtp = aiosmtplib.SMTP(
                        hostname=self.smtp_host,
                        port=self.smtp_port,
                        use_tls=self.use_tls,
                    )
                    await smtp.connect()
                    
                    if self.smtp_user and self.smtp_password:
                        await smtp.login(self.smtp_user, self.smtp_password)
                        
                    await smtp.quit()
                except Exception as e:
                    logger.error(f"SMTP connection test failed: {e}")
                    return False
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing email notification channel: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the email notification channel."""
        self.templates = {}
        self.jinja_env = None
        self.is_initialized = False
    
    async def _render_template(self, template_str: str, data: Dict[str, Any]) -> str:
        """Render a template string with data."""
        if not template_str:
            return ""
            
        template = self.jinja_env.from_string(template_str)
        return await template.render_async(**data)
    
    async def send_notification(self, message: Dict[str, Any], recipients: List[str]) -> bool:
        """
        Send an email notification to recipients.
        
        Args:
            message: Email content and metadata
            recipients: List of email addresses
            
        Returns:
            bool: True if sending successful
        """
        if not self.is_initialized:
            raise RuntimeError("Email notification channel not initialized")
            
        if not recipients:
            logger.warning("No recipients specified for email notification")
            return False
            
        try:
            # Get email content
            subject = message.get("subject", "")
            html_body = message.get("html_body", "")
            text_body = message.get("text_body", "")
            sender = message.get("sender", self.default_sender)
            
            if not sender:
                logger.error("No sender specified for email notification")
                return False
                
            if not subject:
                logger.warning("No subject specified for email notification")
                
            if not html_body and not text_body:
                logger.error("No content specified for email notification")
                return False
                
            # Create MIME message
            mime_message = MIMEMultipart("alternative")
            mime_message["Subject"] = subject
            mime_message["From"] = sender
            mime_message["To"] = ", ".join(recipients)
            
            # Add text part if available
            if text_body:
                mime_message.attach(MIMEText(text_body, "plain"))
                
            # Add HTML part if available
            if html_body:
                mime_message.attach(MIMEText(html_body, "html"))
                
            # Connect to SMTP server and send
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.use_tls,
            )
            
            await smtp.connect()
            
            if self.smtp_user and self.smtp_password:
                await smtp.login(self.smtp_user, self.smtp_password)
                
            send_results = await smtp.send_message(mime_message)
            
            # Store message status
            import uuid
            message_id = str(uuid.uuid4())
            self.message_statuses[message_id] = {
                "status": "sent",
                "recipients": recipients,
                "timestamp": asyncio.get_event_loop().time(),
                "smtp_response": str(send_results),
            }
            
            await smtp.quit()
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    async def send_batch(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send a batch of email notifications.
        
        Args:
            messages: List of message objects with recipient information
            
        Returns:
            Dict with results information
        """
        if not self.is_initialized:
            raise RuntimeError("Email notification channel not initialized")
            
        if not messages:
            logger.warning("No messages to send in batch")
            return {"success_count": 0, "failure_count": 0, "failures": []}
            
        success_count = 0
        failure_count = 0
        failures = []
        message_ids = []
        
        try:
            # Connect to SMTP server once for the batch
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.use_tls,
            )
            
            await smtp.connect()
            
            if self.smtp_user and self.smtp_password:
                await smtp.login(self.smtp_user, self.smtp_password)
                
            # Send each message
            for idx, message in enumerate(messages):
                try:
                    recipients = message.get("recipients", [])
                    if not recipients:
                        logger.warning(f"No recipients for message {idx} in batch")
                        failure_count += 1
                        failures.append({
                            "index": idx,
                            "error": "No recipients specified",
                        })
                        continue
                        
                    subject = message.get("subject", "")
                    html_body = message.get("html_body", "")
                    text_body = message.get("text_body", "")
                    sender = message.get("sender", self.default_sender)
                    
                    if not sender:
                        logger.error(f"No sender for message {idx} in batch")
                        failure_count += 1
                        failures.append({
                            "index": idx,
                            "error": "No sender specified",
                        })
                        continue
                        
                    if not html_body and not text_body:
                        logger.error(f"No content for message {idx} in batch")
                        failure_count += 1
                        failures.append({
                            "index": idx,
                            "error": "No content specified",
                        })
                        continue
                    
                    # Create MIME message
                    mime_message = MIMEMultipart("alternative")
                    mime_message["Subject"] = subject
                    mime_message["From"] = sender
                    mime_message["To"] = ", ".join(recipients)
                    
                    # Add text part if available
                    if text_body:
                        mime_message.attach(MIMEText(text_body, "plain"))
                        
                    # Add HTML part if available
                    if html_body:
                        mime_message.attach(MIMEText(html_body, "html"))
                    
                    # Send the message
                    await smtp.send_message(mime_message)
                    
                    # Store message status
                    import uuid
                    message_id = str(uuid.uuid4())
                    self.message_statuses[message_id] = {
                        "status": "sent",
                        "recipients": recipients,
                        "timestamp": asyncio.get_event_loop().time(),
                    }
                    message_ids.append(message_id)
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error sending message {idx} in batch: {e}")
                    failure_count += 1
                    failures.append({
                        "index": idx,
                        "error": str(e),
                    })
            
            # Disconnect from SMTP server
            await smtp.quit()
            
        except Exception as e:
            logger.error(f"Error in email batch operation: {e}")
            # For any messages not yet processed, count as failures
            remaining = len(messages) - (success_count + failure_count)
            if remaining > 0:
                failure_count += remaining
                failures.append({
                    "index": "batch",
                    "error": str(e),
                    "count": remaining,
                })
        
        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "failures": failures,
            "message_ids": message_ids,
        }
    
    def get_channel_info(self) -> Dict[str, Any]:
        """
        Get information about this email notification channel.
        
        Returns:
            Dict with channel information and capabilities
        """
        return {
            "channel_type": "email",
            "available_templates": list(self.templates.keys()),
            "supports_html": True,
            "supports_text": True,
            "supports_attachments": False,  # Could be extended to support attachments
            "supports_scheduling": False,
            "supports_delivery_status": True,
            "max_recipients_per_message": 100,  # This could be configurable
        }
    
    def format_message(self, template_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format an email message using a template.
        
        Args:
            template_name: Name of the template to use
            data: Data to populate the template
            
        Returns:
            Dict with formatted message content
        """
        if not self.is_initialized:
            raise RuntimeError("Email notification channel not initialized")
            
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
            
        template = self.templates[template_name]
        
        # Render templates synchronously for this method
        rendered_subject = ""
        rendered_html = ""
        rendered_text = ""
        
        if template.get("subject"):
            subject_template = self.jinja_env.from_string(template["subject"])
            rendered_subject = subject_template.render(**data)
            
        if template.get("html_body"):
            html_template = self.jinja_env.from_string(template["html_body"])
            rendered_html = html_template.render(**data)
            
        if template.get("text_body"):
            text_template = self.jinja_env.from_string(template["text_body"])
            rendered_text = text_template.render(**data)
            
        return {
            "subject": rendered_subject,
            "html_body": rendered_html,
            "text_body": rendered_text,
        }
    
    def validate_recipient(self, recipient: str) -> bool:
        """
        Validate if an email address is properly formatted.
        
        Args:
            recipient: Email address to validate
            
        Returns:
            bool: True if email format is valid
        """
        if not recipient:
            return False
            
        # Simple regex for email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_pattern, recipient))
    
    def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the delivery status of a sent email.
        
        Args:
            message_id: The ID of the message to check
            
        Returns:
            Dict with delivery status information
        """
        if message_id not in self.message_statuses:
            return {
                "status": "unknown",
                "message": f"Message ID {message_id} not found",
            }
            
        return self.message_statuses[message_id]