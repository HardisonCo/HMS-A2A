"""
Notification service for avian influenza alerts.

This module provides notification capabilities to alert stakeholders
about detected outbreaks, high-risk predictions, and other important events
related to avian influenza surveillance.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

logger = logging.getLogger(__name__)


class NotificationChannel:
    """Base class for notification channels."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize a notification channel.
        
        Args:
            name: Channel name
            config: Channel configuration
        """
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', True)
    
    def send(self, message: Dict[str, Any]) -> bool:
        """
        Send a notification.
        
        Args:
            message: Message content
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement send()")


class EmailChannel(NotificationChannel):
    """Email notification channel."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email notification channel.
        
        Args:
            config: Channel configuration with SMTP settings
        """
        super().__init__("email", config)
        self.smtp_server = config.get('smtp_server', 'localhost')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_user = config.get('smtp_user', '')
        self.smtp_password = config.get('smtp_password', '')
        self.from_address = config.get('from_address', 'aphis-alerts@usda.gov')
        self.use_tls = config.get('use_tls', True)
    
    def send(self, message: Dict[str, Any]) -> bool:
        """
        Send an email notification.
        
        Args:
            message: Dictionary containing:
                - recipients: List of email addresses
                - subject: Email subject
                - body_text: Plain text body
                - body_html: Optional HTML body
                
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.info("Email notifications are disabled")
            return False
        
        recipients = message.get('recipients', [])
        if not recipients:
            logger.error("No recipients specified for email notification")
            return False
        
        subject = message.get('subject', 'APHIS Bird Flu Alert')
        body_text = message.get('body_text', '')
        body_html = message.get('body_html')
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_address
            msg['To'] = ', '.join(recipients)
            
            # Attach text part
            part1 = MIMEText(body_text, 'plain')
            msg.attach(part1)
            
            # Attach HTML part if provided
            if body_html:
                part2 = MIMEText(body_html, 'html')
                msg.attach(part2)
            
            # Connect to SMTP server
            if self.use_tls:
                smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
                smtp.starttls()
            else:
                smtp = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            
            # Login if credentials provided
            if self.smtp_user and self.smtp_password:
                smtp.login(self.smtp_user, self.smtp_password)
            
            # Send email
            smtp.sendmail(self.from_address, recipients, msg.as_string())
            smtp.quit()
            
            logger.info(f"Email notification sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False


class SMSChannel(NotificationChannel):
    """SMS notification channel."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SMS notification channel.
        
        Args:
            config: Channel configuration with SMS gateway settings
        """
        super().__init__("sms", config)
        self.provider = config.get('provider', 'twilio')
        self.api_key = config.get('api_key', '')
        self.api_secret = config.get('api_secret', '')
        self.from_number = config.get('from_number', '')
        self.api_url = config.get('api_url', '')
    
    def send(self, message: Dict[str, Any]) -> bool:
        """
        Send an SMS notification.
        
        Args:
            message: Dictionary containing:
                - recipients: List of phone numbers
                - body: Message text
                
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.info("SMS notifications are disabled")
            return False
        
        recipients = message.get('recipients', [])
        if not recipients:
            logger.error("No recipients specified for SMS notification")
            return False
        
        body = message.get('body', '')
        if not body:
            logger.error("No message body specified for SMS notification")
            return False
        
        if self.provider == 'twilio':
            return self._send_twilio(recipients, body)
        elif self.provider == 'aws_sns':
            return self._send_aws_sns(recipients, body)
        else:
            logger.error(f"Unsupported SMS provider: {self.provider}")
            return False
    
    def _send_twilio(self, recipients: List[str], body: str) -> bool:
        """Send SMS using Twilio."""
        try:
            from twilio.rest import Client
            
            client = Client(self.api_key, self.api_secret)
            
            success_count = 0
            for recipient in recipients:
                try:
                    message = client.messages.create(
                        body=body,
                        from_=self.from_number,
                        to=recipient
                    )
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send SMS to {recipient}: {str(e)}")
            
            logger.info(f"SMS sent to {success_count}/{len(recipients)} recipients")
            return success_count > 0
            
        except ImportError:
            logger.error("Twilio package not installed. Install with 'pip install twilio'")
            return False
        except Exception as e:
            logger.error(f"Failed to send Twilio SMS: {str(e)}")
            return False
    
    def _send_aws_sns(self, recipients: List[str], body: str) -> bool:
        """Send SMS using AWS SNS."""
        try:
            import boto3
            
            sns = boto3.client('sns')
            
            success_count = 0
            for recipient in recipients:
                try:
                    response = sns.publish(
                        PhoneNumber=recipient,
                        Message=body,
                        MessageAttributes={
                            'AWS.SNS.SMS.SenderID': {
                                'DataType': 'String',
                                'StringValue': 'APHIS'
                            }
                        }
                    )
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send SMS to {recipient}: {str(e)}")
            
            logger.info(f"AWS SNS SMS sent to {success_count}/{len(recipients)} recipients")
            return success_count > 0
            
        except ImportError:
            logger.error("Boto3 package not installed. Install with 'pip install boto3'")
            return False
        except Exception as e:
            logger.error(f"Failed to send AWS SNS SMS: {str(e)}")
            return False


class WebhookChannel(NotificationChannel):
    """Webhook notification channel."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize webhook notification channel.
        
        Args:
            config: Channel configuration with webhook settings
        """
        super().__init__("webhook", config)
        self.endpoints = config.get('endpoints', [])
        self.headers = config.get('headers', {})
        self.auth_type = config.get('auth_type', None)
        self.auth_username = config.get('auth_username', '')
        self.auth_token = config.get('auth_token', '')
    
    def send(self, message: Dict[str, Any]) -> bool:
        """
        Send a webhook notification.
        
        Args:
            message: Dictionary containing the payload to send
                
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.info("Webhook notifications are disabled")
            return False
        
        if not self.endpoints:
            logger.error("No webhook endpoints configured")
            return False
        
        # Prepare payload
        payload = message.copy()
        payload['timestamp'] = datetime.now().isoformat()
        
        # Prepare auth
        auth = None
        if self.auth_type == 'basic':
            auth = (self.auth_username, self.auth_token)
        
        # Add headers
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json'
        
        # Add auth token if using bearer auth
        if self.auth_type == 'bearer':
            headers['Authorization'] = f"Bearer {self.auth_token}"
        
        # Send to all endpoints
        success_count = 0
        for endpoint in self.endpoints:
            try:
                response = requests.post(
                    endpoint, 
                    json=payload,
                    headers=headers,
                    auth=auth,
                    timeout=10
                )
                
                if response.status_code < 300:
                    success_count += 1
                else:
                    logger.error(f"Webhook failed with status {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"Failed to send webhook to {endpoint}: {str(e)}")
        
        logger.info(f"Webhook sent to {success_count}/{len(self.endpoints)} endpoints")
        return success_count > 0


class NotificationService:
    """
    Service for sending notifications about avian influenza events.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the notification service.
        
        Args:
            config_path: Path to notification configuration file
        """
        self.channels: Dict[str, NotificationChannel] = {}
        self.config: Dict[str, Any] = {}
        
        # Load configuration
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load notification config: {str(e)}")
                self.config = {}
        
        # Initialize channels
        self._init_channels()
    
    def _init_channels(self) -> None:
        """Initialize notification channels from configuration."""
        channels_config = self.config.get('channels', {})
        
        # Initialize email channel
        if 'email' in channels_config:
            self.channels['email'] = EmailChannel(channels_config['email'])
        
        # Initialize SMS channel
        if 'sms' in channels_config:
            self.channels['sms'] = SMSChannel(channels_config['sms'])
        
        # Initialize webhook channel
        if 'webhook' in channels_config:
            self.channels['webhook'] = WebhookChannel(channels_config['webhook'])
    
    def add_channel(self, channel: NotificationChannel) -> None:
        """
        Add a notification channel.
        
        Args:
            channel: The notification channel to add
        """
        self.channels[channel.name] = channel
    
    def remove_channel(self, channel_name: str) -> None:
        """
        Remove a notification channel.
        
        Args:
            channel_name: Name of the channel to remove
        """
        if channel_name in self.channels:
            del self.channels[channel_name]
    
    def send_notification(self, 
                         message: Dict[str, Any],
                         channels: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Send a notification through specified channels.
        
        Args:
            message: Notification content
            channels: List of channel names to use (if None, use all enabled channels)
            
        Returns:
            Dictionary mapping channel names to success status
        """
        results = {}
        
        # Determine which channels to use
        channels_to_use = channels or list(self.channels.keys())
        
        # Send through each channel
        for channel_name in channels_to_use:
            if channel_name in self.channels:
                channel = self.channels[channel_name]
                results[channel_name] = channel.send(message)
            else:
                logger.warning(f"Unknown notification channel: {channel_name}")
                results[channel_name] = False
        
        return results
    
    def send_outbreak_alert(self,
                           regions: List[Dict[str, Any]],
                           detection_time: str,
                           severity_level: str = "moderate",
                           details: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
        """
        Send an alert about a detected outbreak.
        
        Args:
            regions: List of affected regions with metadata
            detection_time: Time when the outbreak was detected (ISO format)
            severity_level: Severity level (low, moderate, high, severe)
            details: Additional details about the outbreak
            
        Returns:
            Dictionary mapping channel names to success status
        """
        # Format region names for display
        region_names = [region.get('name', region.get('id', 'Unknown')) for region in regions]
        region_display = ", ".join(region_names)
        
        # Create message for different channels
        email_subject = f"APHIS Alert: Avian Influenza Outbreak - {severity_level.upper()}"
        
        # Create email body
        email_body_text = f"""
APHIS Bird Flu Alert - {severity_level.upper()} PRIORITY

Avian influenza outbreak detected in:
{region_display}

Detection Time: {detection_time}
Severity Level: {severity_level.upper()}

"""
        
        if details:
            email_body_text += "Additional Details:\n"
            for key, value in details.items():
                email_body_text += f"{key}: {value}\n"
        
        # Create HTML version if needed
        email_body_html = None
        if 'email' in self.channels and self.channels['email'].enabled:
            email_body_html = f"""
<html>
<head>
  <style>
    body {{ font-family: Arial, sans-serif; }}
    .header {{ background-color: #880000; color: white; padding: 10px; text-align: center; }}
    .content {{ padding: 20px; }}
    .region {{ font-weight: bold; }}
    .details {{ margin-top: 20px; border-top: 1px solid #ccc; padding-top: 10px; }}
  </style>
</head>
<body>
  <div class="header">
    <h2>APHIS Bird Flu Alert - {severity_level.upper()} PRIORITY</h2>
  </div>
  <div class="content">
    <p>Avian influenza outbreak detected in:</p>
    <p class="region">{region_display}</p>
    
    <p><strong>Detection Time:</strong> {detection_time}</p>
    <p><strong>Severity Level:</strong> {severity_level.upper()}</p>
    
"""
            
            if details:
                email_body_html += "<div class='details'><h3>Additional Details:</h3><ul>"
                for key, value in details.items():
                    email_body_html += f"<li><strong>{key}:</strong> {value}</li>"
                email_body_html += "</ul></div>"
            
            email_body_html += """
  </div>
</body>
</html>
"""
        
        # Create SMS message (shorter)
        sms_body = f"APHIS ALERT: Bird flu outbreak - {severity_level.upper()} priority in {region_display}. Check email for details."
        
        # Prepare webhook payload
        webhook_payload = {
            "alert_type": "outbreak_detection",
            "regions": regions,
            "detection_time": detection_time,
            "severity_level": severity_level,
            "details": details
        }
        
        # Send through each channel type
        results = {}
        
        # Email
        if 'email' in self.channels:
            email_message = {
                'recipients': self.config.get('recipients', {}).get('email', []),
                'subject': email_subject,
                'body_text': email_body_text,
                'body_html': email_body_html
            }
            results['email'] = self.channels['email'].send(email_message)
        
        # SMS
        if 'sms' in self.channels:
            sms_message = {
                'recipients': self.config.get('recipients', {}).get('sms', []),
                'body': sms_body
            }
            results['sms'] = self.channels['sms'].send(sms_message)
        
        # Webhook
        if 'webhook' in self.channels:
            results['webhook'] = self.channels['webhook'].send(webhook_payload)
        
        return results
    
    def send_risk_prediction_alert(self,
                                  high_risk_regions: List[Dict[str, Any]],
                                  forecast_date: str,
                                  days_ahead: int,
                                  details: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
        """
        Send an alert about high-risk predictions for future outbreaks.
        
        Args:
            high_risk_regions: List of high-risk regions with metadata
            forecast_date: Date of the forecast (ISO format)
            days_ahead: Number of days ahead in the forecast
            details: Additional details about the prediction
            
        Returns:
            Dictionary mapping channel names to success status
        """
        # Format region information
        region_info = []
        for region in high_risk_regions:
            name = region.get('name', region.get('id', 'Unknown'))
            risk = f"{region.get('risk_score', 0) * 100:.1f}%"
            cases = region.get('predicted_cases', 'N/A')
            region_info.append(f"{name} (Risk: {risk}, Predicted Cases: {cases})")
        
        region_display = "\n".join(region_info)
        short_region_list = ", ".join([r.get('name', r.get('id', 'Unknown')) 
                                     for r in high_risk_regions[:3]])
        if len(high_risk_regions) > 3:
            short_region_list += f" and {len(high_risk_regions) - 3} more"
        
        # Create messages
        email_subject = f"APHIS Alert: High Risk Bird Flu Prediction for Next {days_ahead} Days"
        
        email_body_text = f"""
APHIS Bird Flu Risk Prediction Alert

The following regions are at HIGH RISK for avian influenza outbreaks in the next {days_ahead} days:

{region_display}

Forecast Date: {forecast_date}
Prediction Window: {days_ahead} days

"""
        
        if details:
            email_body_text += "Additional Details:\n"
            for key, value in details.items():
                email_body_text += f"{key}: {value}\n"
        
        # Create HTML version
        email_body_html = None
        if 'email' in self.channels and self.channels['email'].enabled:
            email_body_html = f"""
<html>
<head>
  <style>
    body {{ font-family: Arial, sans-serif; }}
    .header {{ background-color: #884400; color: white; padding: 10px; text-align: center; }}
    .content {{ padding: 20px; }}
    .regions {{ margin-top: 10px; margin-bottom: 10px; }}
    .region {{ margin-bottom: 5px; }}
    .details {{ margin-top: 20px; border-top: 1px solid #ccc; padding-top: 10px; }}
  </style>
</head>
<body>
  <div class="header">
    <h2>APHIS Bird Flu Risk Prediction Alert</h2>
  </div>
  <div class="content">
    <p>The following regions are at <strong>HIGH RISK</strong> for avian influenza outbreaks in the next {days_ahead} days:</p>
    
    <div class="regions">
"""
            
            for region in high_risk_regions:
                name = region.get('name', region.get('id', 'Unknown'))
                risk = f"{region.get('risk_score', 0) * 100:.1f}%"
                cases = region.get('predicted_cases', 'N/A')
                email_body_html += f'<p class="region"><strong>{name}</strong> - Risk: {risk}, Predicted Cases: {cases}</p>\n'
            
            email_body_html += f"""
    </div>
    
    <p><strong>Forecast Date:</strong> {forecast_date}</p>
    <p><strong>Prediction Window:</strong> {days_ahead} days</p>
"""
            
            if details:
                email_body_html += "<div class='details'><h3>Additional Details:</h3><ul>"
                for key, value in details.items():
                    email_body_html += f"<li><strong>{key}:</strong> {value}</li>"
                email_body_html += "</ul></div>"
            
            email_body_html += """
  </div>
</body>
</html>
"""
        
        # Create SMS message (shorter)
        sms_body = f"APHIS PREDICTION: High risk of bird flu in {short_region_list} in next {days_ahead} days. Check email for details."
        
        # Prepare webhook payload
        webhook_payload = {
            "alert_type": "risk_prediction",
            "high_risk_regions": high_risk_regions,
            "forecast_date": forecast_date,
            "days_ahead": days_ahead,
            "details": details
        }
        
        # Send through each channel type
        results = {}
        
        # Email
        if 'email' in self.channels:
            email_message = {
                'recipients': self.config.get('recipients', {}).get('email', []),
                'subject': email_subject,
                'body_text': email_body_text,
                'body_html': email_body_html
            }
            results['email'] = self.channels['email'].send(email_message)
        
        # SMS
        if 'sms' in self.channels:
            sms_message = {
                'recipients': self.config.get('recipients', {}).get('sms', []),
                'body': sms_body
            }
            results['sms'] = self.channels['sms'].send(sms_message)
        
        # Webhook
        if 'webhook' in self.channels:
            results['webhook'] = self.channels['webhook'].send(webhook_payload)
        
        return results
    
    def send_system_notification(self,
                               subject: str,
                               message: str,
                               level: str = "info",
                               details: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
        """
        Send a system notification (e.g., model training completed, data updated).
        
        Args:
            subject: Notification subject
            message: Notification message
            level: Notification level (info, warning, error)
            details: Additional details
            
        Returns:
            Dictionary mapping channel names to success status
        """
        # Prepare webhook payload
        webhook_payload = {
            "notification_type": "system",
            "subject": subject,
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        # Prepare email message
        email_subject = f"APHIS System Notification: {subject}"
        email_body_text = f"""
APHIS System Notification - {level.upper()}

{message}

Time: {datetime.now().isoformat()}
"""
        
        if details:
            email_body_text += "\nDetails:\n"
            for key, value in details.items():
                email_body_text += f"{key}: {value}\n"
        
        # Only send SMS for warning/error levels
        send_sms = level in ("warning", "error")
        sms_body = None
        if send_sms:
            sms_body = f"APHIS SYSTEM {level.upper()}: {subject} - {message}"
        
        # Send through appropriate channels
        results = {}
        
        # Email
        if 'email' in self.channels:
            email_message = {
                'recipients': self.config.get('recipients', {}).get('email', []),
                'subject': email_subject,
                'body_text': email_body_text
            }
            results['email'] = self.channels['email'].send(email_message)
        
        # SMS (only for warning/error)
        if send_sms and 'sms' in self.channels:
            sms_message = {
                'recipients': self.config.get('recipients', {}).get('sms', []),
                'body': sms_body
            }
            results['sms'] = self.channels['sms'].send(sms_message)
        
        # Webhook
        if 'webhook' in self.channels:
            results['webhook'] = self.channels['webhook'].send(webhook_payload)
        
        return results