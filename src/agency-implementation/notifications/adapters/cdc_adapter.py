"""
CDC Alert Adapter

Adapter for CDC (Centers for Disease Control and Prevention) alerts.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
import aiohttp
from datetime import datetime

from .alert_adapter import AlertAdapter
from ..models.alert import Alert, AlertSeverity, AlertStatus

logger = logging.getLogger(__name__)


@AlertAdapter.register_adapter("cdc")
class CDCAlertAdapter(AlertAdapter):
    """
    Adapter for CDC alerts related to disease outbreaks, health advisories,
    and public health emergencies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the CDC alert adapter.
        
        Args:
            config: Configuration for the adapter
        """
        super().__init__(config)
        self.api_url = config.get("api_url", "https://api.cdc.gov/alerts")
        self.api_key = config.get("api_key", "")
        self.timeout = config.get("timeout", 30)
        self.session = None
        
        # Specific CDC settings
        self.include_advisories = config.get("include_advisories", True)
        self.include_outbreaks = config.get("include_outbreaks", True)
        self.include_recalls = config.get("include_recalls", True)
    
    async def initialize(self) -> bool:
        """
        Initialize the CDC alert adapter.
        
        Returns:
            bool: True if initialization was successful
        """
        try:
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                headers=self._get_headers(),
                timeout=timeout,
            )
            
            # Test connection if needed
            if self.config.get("test_connection", True):
                try:
                    async with self.session.get(f"{self.api_url}/health") as response:
                        if response.status != 200:
                            logger.error(f"CDC API health check failed: {response.status}")
                            return False
                except Exception as e:
                    logger.error(f"CDC API connection test failed: {e}")
                    return False
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing CDC alert adapter: {e}")
            if self.session:
                await self.session.close()
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the CDC alert adapter."""
        if self.session:
            await self.session.close()
        self.is_initialized = False
    
    async def get_alerts(self) -> List[Alert]:
        """
        Get alerts from CDC API.
        
        Returns:
            List of alerts
        """
        if not self.is_initialized:
            raise RuntimeError("CDC alert adapter not initialized")
            
        alerts = []
        
        # Build query parameters
        params = {
            "format": "json",
            "limit": 100,
        }
        
        # Add filters based on configuration
        alert_types = []
        if self.include_advisories:
            alert_types.append("advisory")
        if self.include_outbreaks:
            alert_types.append("outbreak")
        if self.include_recalls:
            alert_types.append("recall")
            
        if alert_types:
            params["type"] = ",".join(alert_types)
        
        try:
            async with self.session.get(self.api_url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Error fetching CDC alerts: {response.status}")
                    return []
                    
                data = await response.json()
                
                # Process alerts
                for alert_data in data.get("alerts", []):
                    try:
                        alert = self._process_alert(alert_data)
                        if alert:
                            alerts.append(alert)
                    except Exception as e:
                        logger.error(f"Error processing CDC alert: {e}")
                
        except Exception as e:
            logger.error(f"Error fetching CDC alerts: {e}")
        
        return alerts
    
    def _process_alert(self, alert_data: Dict[str, Any]) -> Optional[Alert]:
        """
        Process CDC alert data into unified Alert format.
        
        Args:
            alert_data: Raw alert data from CDC API
            
        Returns:
            Processed Alert or None if invalid
        """
        try:
            # Map CDC severity to unified severity
            severity_map = {
                "critical": AlertSeverity.CRITICAL,
                "severe": AlertSeverity.HIGH,
                "important": AlertSeverity.MEDIUM,
                "moderate": AlertSeverity.MEDIUM,
                "standard": AlertSeverity.LOW,
                "info": AlertSeverity.INFORMATIONAL,
            }
            
            cdc_severity = alert_data.get("severity", "").lower()
            severity = severity_map.get(cdc_severity, AlertSeverity.MEDIUM)
            
            # Map CDC alert type
            alert_type_map = {
                "outbreak": "disease_outbreak",
                "recall": "product_recall",
                "advisory": "health_advisory",
            }
            
            cdc_type = alert_data.get("type", "").lower()
            alert_type = alert_type_map.get(cdc_type, "health_alert")
            
            # Parse dates
            created_at = None
            expires_at = None
            
            if "publishedDate" in alert_data:
                try:
                    created_at = datetime.fromisoformat(alert_data["publishedDate"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
                    
            if "expiresDate" in alert_data:
                try:
                    expires_at = datetime.fromisoformat(alert_data["expiresDate"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            
            # Create alert
            alert = Alert(
                id=alert_data.get("id", ""),
                title=alert_data.get("title", ""),
                description=alert_data.get("description", ""),
                source="CDC",
                alert_type=alert_type,
                severity=severity,
                status=AlertStatus.NEW,
                url=alert_data.get("url"),
                created_at=created_at,
                expires_at=expires_at,
            )
            
            # Add CDC-specific fields
            if "affectedLocations" in alert_data:
                alert.regions = alert_data["affectedLocations"]
                
            if "recommendedActions" in alert_data:
                alert.recommended_actions = alert_data["recommendedActions"]
                
            if "affectedPopulation" in alert_data:
                try:
                    alert.affected_population = int(alert_data["affectedPopulation"])
                except (ValueError, TypeError):
                    pass
            
            # Add all remaining data to metadata
            alert.metadata = {k: v for k, v in alert_data.items() if k not in [
                "id", "title", "description", "url", "severity", "type",
                "publishedDate", "expiresDate", "affectedLocations",
                "recommendedActions", "affectedPopulation"
            ]}
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating Alert from CDC data: {e}")
            return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for CDC API requests."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "CDCAlertAdapter/1.0",
        }
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            
        return headers