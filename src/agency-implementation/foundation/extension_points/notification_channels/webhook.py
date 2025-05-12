"""
Webhook Notification Channel

Extension point implementation for webhook-based notifications.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import asyncio
import aiohttp
import json
import uuid
from . import NotificationChannelExtensionPoint
from .. import base

logger = logging.getLogger(__name__)

@base.BaseExtensionPoint.extension_point("notification_channel", "webhook")
class WebhookNotificationChannel(NotificationChannelExtensionPoint):
    """Implementation of notification channel extension point for webhook notifications."""
    
    def __init__(self):
        self.endpoints = {}
        self.session = None
        self.default_headers = {}
        self.verify_ssl = True
        self.timeout = 30
        self.retry_count = 3
        self.retry_delay = 1.0
        self.is_initialized = False
        self.message_statuses = {}
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the webhook notification channel.
        
        Args:
            config: Configuration parameters for webhook endpoints
            
        Returns:
            bool: True if initialization successful
        """
        try:
            # Load endpoint configurations
            endpoints_config = config.get("endpoints", {})
            for endpoint_name, endpoint_config in endpoints_config.items():
                url = endpoint_config.get("url")
                if not url:
                    logger.warning(f"No URL provided for endpoint '{endpoint_name}', skipping")
                    continue
                
                # Store endpoint configuration
                self.endpoints[endpoint_name] = {
                    "url": url,
                    "method": endpoint_config.get("method", "POST"),
                    "headers": endpoint_config.get("headers", {}),
                    "auth": endpoint_config.get("auth", {}),
                    "format": endpoint_config.get("format", "json"),
                }
            
            # Global settings
            self.default_headers = config.get("default_headers", {})
            self.verify_ssl = config.get("verify_ssl", True)
            self.timeout = config.get("timeout", 30)
            self.retry_count = config.get("retry_count", 3)
            self.retry_delay = config.get("retry_delay", 1.0)
            
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                headers=self.default_headers,
                timeout=timeout,
            )
            
            # Test endpoints if requested
            if config.get("test_endpoints", False):
                test_payload = config.get("test_payload", {"test": True})
                
                for endpoint_name, endpoint_config in self.endpoints.items():
                    try:
                        # Create a minimal request for testing
                        url = endpoint_config["url"]
                        method = endpoint_config["method"]
                        headers = {**self.default_headers, **endpoint_config.get("headers", {})}
                        
                        # Make test request
                        async with getattr(self.session, method.lower())(
                            url,
                            json=test_payload,
                            headers=headers,
                            ssl=self.verify_ssl,
                        ) as response:
                            if response.status >= 400:
                                logger.warning(f"Test request to endpoint '{endpoint_name}' failed: {response.status}")
                    except Exception as e:
                        logger.warning(f"Test request to endpoint '{endpoint_name}' failed: {e}")
            
            self.is_initialized = True
            return True
        
        except Exception as e:
            logger.error(f"Error initializing webhook notification channel: {e}")
            if self.session:
                await self.session.close()
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the webhook notification channel."""
        if self.session:
            await self.session.close()
        self.is_initialized = False
    
    async def send_notification(self, message: Dict[str, Any], recipients: List[str]) -> bool:
        """
        Send a webhook notification.
        
        Args:
            message: Notification content and metadata
            recipients: List of endpoint names to send to
            
        Returns:
            bool: True if sending successful to all recipients
        """
        if not self.is_initialized:
            raise RuntimeError("Webhook notification channel not initialized")
            
        if not recipients:
            logger.warning("No recipients (endpoints) specified for webhook notification")
            return False
            
        success = True
        message_id = str(uuid.uuid4())
        
        try:
            # Prepare the payload
            payload = message.get("payload", {})
            
            # Track status for each endpoint
            self.message_statuses[message_id] = {
                "status": "sending",
                "endpoints": {},
                "timestamp": asyncio.get_event_loop().time(),
            }
            
            # Send to each endpoint
            for endpoint_name in recipients:
                if endpoint_name not in self.endpoints:
                    logger.warning(f"Endpoint '{endpoint_name}' not found")
                    self.message_statuses[message_id]["endpoints"][endpoint_name] = {
                        "status": "failed",
                        "error": "Endpoint not found",
                    }
                    success = False
                    continue
                
                endpoint = self.endpoints[endpoint_name]
                url = endpoint["url"]
                method = endpoint["method"].lower()
                headers = {**self.default_headers, **endpoint.get("headers", {})}
                
                # Add message-specific headers if provided
                if "headers" in message:
                    headers.update(message["headers"])
                
                # Format the payload according to endpoint configuration
                format_type = endpoint.get("format", "json")
                
                request_kwargs = {
                    "ssl": self.verify_ssl,
                    "headers": headers,
                }
                
                if format_type == "json":
                    request_kwargs["json"] = payload
                elif format_type == "form":
                    request_kwargs["data"] = payload
                elif format_type == "multipart":
                    # This would need more complex handling for files
                    form_data = aiohttp.FormData()
                    for key, value in payload.items():
                        form_data.add_field(key, str(value))
                    request_kwargs["data"] = form_data
                
                # Send with retry logic
                retry_count = 0
                while retry_count <= self.retry_count:
                    try:
                        async with getattr(self.session, method)(url, **request_kwargs) as response:
                            response_status = response.status
                            response_text = await response.text()
                            
                            if response_status < 400:
                                self.message_statuses[message_id]["endpoints"][endpoint_name] = {
                                    "status": "delivered",
                                    "http_status": response_status,
                                    "response": response_text[:1000],  # Truncate long responses
                                }
                                break
                            else:
                                logger.warning(f"Webhook request to {endpoint_name} failed: {response_status}")
                                
                                # Last retry
                                if retry_count == self.retry_count:
                                    self.message_statuses[message_id]["endpoints"][endpoint_name] = {
                                        "status": "failed",
                                        "http_status": response_status,
                                        "error": f"HTTP error {response_status}",
                                        "response": response_text[:1000],
                                    }
                                    success = False
                                    
                    except Exception as e:
                        logger.warning(f"Webhook request to {endpoint_name} failed: {e}")
                        
                        # Last retry
                        if retry_count == self.retry_count:
                            self.message_statuses[message_id]["endpoints"][endpoint_name] = {
                                "status": "failed",
                                "error": str(e),
                            }
                            success = False
                            
                    # Retry with exponential backoff
                    retry_count += 1
                    if retry_count <= self.retry_count:
                        await asyncio.sleep(self.retry_delay * (2 ** (retry_count - 1)))
            
            # Update overall status
            self.message_statuses[message_id]["status"] = "delivered" if success else "partial_failure"
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
            self.message_statuses[message_id]["status"] = "failed"
            self.message_statuses[message_id]["error"] = str(e)
            return False
    
    async def send_batch(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send a batch of webhook notifications.
        
        Args:
            messages: List of message objects with endpoint information
            
        Returns:
            Dict with results information
        """
        if not self.is_initialized:
            raise RuntimeError("Webhook notification channel not initialized")
            
        if not messages:
            logger.warning("No messages to send in batch")
            return {"success_count": 0, "failure_count": 0, "failures": []}
            
        success_count = 0
        failure_count = 0
        failures = []
        message_ids = []
        
        # Process each message
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
                
                # Send the message
                if await self.send_notification(message, recipients):
                    success_count += 1
                    # Get the message ID from the most recent send
                    message_ids.append(list(self.message_statuses.keys())[-1])
                else:
                    failure_count += 1
                    failures.append({
                        "index": idx,
                        "error": "Failed to send to one or more endpoints",
                    })
                
            except Exception as e:
                logger.error(f"Error sending message {idx} in batch: {e}")
                failure_count += 1
                failures.append({
                    "index": idx,
                    "error": str(e),
                })
        
        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "failures": failures,
            "message_ids": message_ids,
        }
    
    def get_channel_info(self) -> Dict[str, Any]:
        """
        Get information about this webhook notification channel.
        
        Returns:
            Dict with channel information and capabilities
        """
        return {
            "channel_type": "webhook",
            "available_endpoints": list(self.endpoints.keys()),
            "supported_formats": ["json", "form", "multipart"],
            "supports_retry": True,
            "max_retry_count": self.retry_count,
            "supports_delivery_status": True,
        }
    
    def format_message(self, template_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a webhook message using a template.
        
        Args:
            template_name: Name of the template to use
            data: Data to populate the template
            
        Returns:
            Dict with formatted message content
        """
        # Templates could be stored in a database or file system
        # For simplicity, we'll use predefined templates
        
        templates = {
            "alert": {
                "payload": {
                    "event_type": "alert",
                    "severity": data.get("severity", "info"),
                    "message": data.get("message", ""),
                    "details": data.get("details", {}),
                    "timestamp": data.get("timestamp", ""),
                },
                "headers": {
                    "X-Event-Type": "alert",
                }
            },
            "status_update": {
                "payload": {
                    "event_type": "status_update",
                    "status": data.get("status", ""),
                    "component": data.get("component", ""),
                    "message": data.get("message", ""),
                    "details": data.get("details", {}),
                    "timestamp": data.get("timestamp", ""),
                },
                "headers": {
                    "X-Event-Type": "status_update",
                }
            },
            "data_refresh": {
                "payload": {
                    "event_type": "data_refresh",
                    "dataset": data.get("dataset", ""),
                    "changes": data.get("changes", {}),
                    "timestamp": data.get("timestamp", ""),
                },
                "headers": {
                    "X-Event-Type": "data_refresh",
                }
            },
        }
        
        if template_name not in templates:
            raise ValueError(f"Template '{template_name}' not found")
            
        return templates[template_name]
    
    def validate_recipient(self, recipient: str) -> bool:
        """
        Validate if an endpoint name is valid.
        
        Args:
            recipient: Endpoint name to validate
            
        Returns:
            bool: True if endpoint exists
        """
        return recipient in self.endpoints
    
    def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the delivery status of a sent webhook notification.
        
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