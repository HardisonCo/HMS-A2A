"""
HMS Integration module for CDC implementation.

This module handles integration with the HMS (Health Management System) API for
data exchange, alert distribution, and reporting.
"""
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import aiohttp
import requests

# Foundation imports
from agency_implementation.foundation.api_framework.auth.jwt import JWTAuthenticator


logger = logging.getLogger(__name__)


class HMSIntegration:
    """
    Integration with Health Management System API.
    
    This class provides methods for communicating with HMS API endpoints
    to exchange public health data, distribute alerts, and generate reports.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the HMS integration.
        
        Args:
            config: Configuration for the HMS integration
        """
        self.enabled = config.get("enabled", False)
        if not self.enabled:
            logger.info("HMS integration is disabled")
            return
            
        self.endpoint = config.get("endpoint", "")
        if not self.endpoint:
            logger.error("HMS endpoint not configured")
            raise ValueError("HMS API endpoint must be configured")
            
        # Get auth token from environment
        token_env_var = config.get("auth_token_env", "HMS_API_TOKEN")
        self.auth_token = os.environ.get(token_env_var)
        if not self.auth_token:
            logger.error(f"HMS auth token not found in environment variable {token_env_var}")
            raise ValueError(f"HMS auth token not found in environment variable {token_env_var}")
            
        self.services = config.get("services", [])
        self.authenticator = JWTAuthenticator(token=self.auth_token)
        
        logger.info(f"Initialized HMS integration with endpoint {self.endpoint}")
        logger.info(f"Enabled services: {', '.join(self.services)}")
        
    async def verify_connection(self) -> bool:
        """
        Verify the connection to the HMS API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        if not self.enabled:
            return False
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = await self._get_auth_headers()
                async with session.get(f"{self.endpoint}/health", headers=headers) as response:
                    if response.status == 200:
                        logger.info("HMS API connection verified successfully")
                        return True
                    else:
                        logger.error(f"HMS API connection failed: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error verifying HMS API connection: {e}")
            return False
            
    async def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authenticated headers for HMS API requests.
        
        Returns:
            Headers dictionary with authorization
        """
        token = await self.authenticator.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "CDC-HMS-Integration/1.0"
        }
        
    async def send_disease_data(self, data: Dict[str, Any]) -> bool:
        """
        Send disease surveillance data to HMS.
        
        Args:
            data: Disease data to send
            
        Returns:
            True if data was sent successfully, False otherwise
        """
        if not self.enabled or "data_exchange" not in self.services:
            logger.warning("Data exchange service not enabled for HMS integration")
            return False
            
        try:
            logger.info(f"Sending disease data to HMS: {len(data)} records")
            
            async with aiohttp.ClientSession() as session:
                headers = await self._get_auth_headers()
                payload = {
                    "source": "CDC",
                    "timestamp": datetime.now().isoformat(),
                    "data_type": "disease_surveillance",
                    "data": data
                }
                
                async with session.post(
                    f"{self.endpoint}/api/v1/data/disease-surveillance",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status in (200, 201):
                        response_data = await response.json()
                        logger.info(f"Successfully sent disease data. Response: {response_data}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send disease data. Status: {response.status}, Error: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending disease data to HMS: {e}")
            return False
            
    async def distribute_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Distribute a public health alert through HMS.
        
        Args:
            alert: Alert data to distribute
            
        Returns:
            Response data from HMS API
        """
        if not self.enabled or "alert_distribution" not in self.services:
            logger.warning("Alert distribution service not enabled for HMS integration")
            return {"status": "failed", "reason": "service_not_enabled"}
            
        try:
            logger.info(f"Distributing alert through HMS: {alert.get('title')}")
            
            async with aiohttp.ClientSession() as session:
                headers = await self._get_auth_headers()
                
                # Ensure alert has required fields
                required_fields = ["title", "message", "urgency_level"]
                for field in required_fields:
                    if field not in alert:
                        error_msg = f"Alert missing required field: {field}"
                        logger.error(error_msg)
                        return {"status": "failed", "reason": "missing_required_fields", "details": error_msg}
                
                # Add metadata
                alert_payload = {
                    **alert,
                    "source": "CDC",
                    "timestamp": datetime.now().isoformat(),
                    "distribution_type": "public_health_alert"
                }
                
                async with session.post(
                    f"{self.endpoint}/api/v1/alerts/distribute",
                    headers=headers,
                    json=alert_payload
                ) as response:
                    response_data = await response.json()
                    
                    if response.status in (200, 201):
                        logger.info(f"Successfully distributed alert. Response: {response_data}")
                    else:
                        logger.error(f"Failed to distribute alert. Status: {response.status}, Response: {response_data}")
                        
                    return {
                        "status": "success" if response.status in (200, 201) else "failed",
                        "response": response_data,
                        "http_status": response.status
                    }
                    
        except Exception as e:
            logger.error(f"Error distributing alert through HMS: {e}")
            return {"status": "failed", "reason": "exception", "details": str(e)}
            
    async def generate_report(self, 
                             report_type: str, 
                             parameters: Dict[str, Any],
                             format: str = "pdf") -> Dict[str, Any]:
        """
        Generate a report using HMS reporting services.
        
        Args:
            report_type: Type of report to generate
            parameters: Parameters for report generation
            format: Output format (pdf, csv, json)
            
        Returns:
            Response with report URL or error information
        """
        if not self.enabled or "reporting" not in self.services:
            logger.warning("Reporting service not enabled for HMS integration")
            return {"status": "failed", "reason": "service_not_enabled"}
            
        try:
            logger.info(f"Generating {report_type} report through HMS")
            
            async with aiohttp.ClientSession() as session:
                headers = await self._get_auth_headers()
                
                report_request = {
                    "report_type": report_type,
                    "parameters": parameters,
                    "format": format,
                    "requester": "CDC",
                    "timestamp": datetime.now().isoformat()
                }
                
                async with session.post(
                    f"{self.endpoint}/api/v1/reports/generate",
                    headers=headers,
                    json=report_request
                ) as response:
                    response_data = await response.json()
                    
                    if response.status in (200, 201, 202):
                        logger.info(f"Successfully requested report generation. Response: {response_data}")
                        return {
                            "status": "success",
                            "report_id": response_data.get("report_id"),
                            "estimated_completion": response_data.get("estimated_completion"),
                            "report_url": response_data.get("report_url")
                        }
                    else:
                        logger.error(f"Failed to generate report. Status: {response.status}, Response: {response_data}")
                        return {
                            "status": "failed",
                            "reason": "api_error",
                            "details": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Error generating report through HMS: {e}")
            return {"status": "failed", "reason": "exception", "details": str(e)}
            
    async def fetch_reference_data(self, data_type: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Fetch reference data from HMS.
        
        Args:
            data_type: Type of reference data to fetch
            parameters: Parameters for the data request
            
        Returns:
            Retrieved reference data or error information
        """
        if not self.enabled or "data_exchange" not in self.services:
            logger.warning("Data exchange service not enabled for HMS integration")
            return {"status": "failed", "reason": "service_not_enabled"}
            
        try:
            logger.info(f"Fetching {data_type} reference data from HMS")
            
            params = parameters or {}
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])
            
            async with aiohttp.ClientSession() as session:
                headers = await self._get_auth_headers()
                
                async with session.get(
                    f"{self.endpoint}/api/v1/reference/{data_type}?{query_params}",
                    headers=headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        logger.info(f"Successfully fetched reference data: {data_type}")
                        return {
                            "status": "success",
                            "data": response_data
                        }
                    else:
                        logger.error(f"Failed to fetch reference data. Status: {response.status}, Response: {response_data}")
                        return {
                            "status": "failed",
                            "reason": "api_error",
                            "details": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Error fetching reference data from HMS: {e}")
            return {"status": "failed", "reason": "exception", "details": str(e)}