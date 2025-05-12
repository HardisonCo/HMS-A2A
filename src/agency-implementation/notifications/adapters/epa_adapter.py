"""
EPA Alert Adapter

Adapter for EPA (Environmental Protection Agency) alerts.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
import aiohttp
from datetime import datetime

from .alert_adapter import AlertAdapter
from ..models.alert import Alert, AlertSeverity, AlertStatus

logger = logging.getLogger(__name__)


@AlertAdapter.register_adapter("epa")
class EPAAlertAdapter(AlertAdapter):
    """
    Adapter for EPA alerts related to environmental hazards, air quality,
    water quality, and other environmental issues.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the EPA alert adapter.
        
        Args:
            config: Configuration for the adapter
        """
        super().__init__(config)
        self.api_url = config.get("api_url", "https://api.epa.gov/alerts")
        self.api_key = config.get("api_key", "")
        self.timeout = config.get("timeout", 30)
        self.session = None
        
        # Specific EPA settings
        self.include_air_quality = config.get("include_air_quality", True)
        self.include_water_quality = config.get("include_water_quality", True)
        self.include_hazardous_materials = config.get("include_hazardous_materials", True)
        self.severity_threshold = AlertSeverity(config.get("severity_threshold", "low"))
    
    async def initialize(self) -> bool:
        """
        Initialize the EPA alert adapter.
        
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
                            logger.error(f"EPA API health check failed: {response.status}")
                            return False
                except Exception as e:
                    logger.error(f"EPA API connection test failed: {e}")
                    return False
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing EPA alert adapter: {e}")
            if self.session:
                await self.session.close()
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the EPA alert adapter."""
        if self.session:
            await self.session.close()
        self.is_initialized = False
    
    async def get_alerts(self) -> List[Alert]:
        """
        Get alerts from EPA API.
        
        Returns:
            List of alerts
        """
        if not self.is_initialized:
            raise RuntimeError("EPA alert adapter not initialized")
            
        alerts = []
        
        # Build query parameters
        params = {
            "format": "json",
            "limit": 100,
        }
        
        # Add filters based on configuration
        alert_types = []
        if self.include_air_quality:
            alert_types.append("air_quality")
        if self.include_water_quality:
            alert_types.append("water_quality")
        if self.include_hazardous_materials:
            alert_types.append("hazardous_materials")
            
        if alert_types:
            params["type"] = ",".join(alert_types)
        
        try:
            async with self.session.get(self.api_url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Error fetching EPA alerts: {response.status}")
                    return []
                    
                data = await response.json()
                
                # Process alerts
                for alert_data in data.get("alerts", []):
                    try:
                        alert = self._process_alert(alert_data)
                        if alert and self._meets_severity_threshold(alert):
                            alerts.append(alert)
                    except Exception as e:
                        logger.error(f"Error processing EPA alert: {e}")
                
        except Exception as e:
            logger.error(f"Error fetching EPA alerts: {e}")
        
        return alerts
    
    def _process_alert(self, alert_data: Dict[str, Any]) -> Optional[Alert]:
        """
        Process EPA alert data into unified Alert format.
        
        Args:
            alert_data: Raw alert data from EPA API
            
        Returns:
            Processed Alert or None if invalid
        """
        try:
            # Map EPA severity to unified severity
            severity_map = {
                "hazardous": AlertSeverity.CRITICAL,
                "unhealthy": AlertSeverity.HIGH,
                "moderate": AlertSeverity.MEDIUM,
                "acceptable": AlertSeverity.LOW,
                "good": AlertSeverity.INFORMATIONAL,
            }
            
            epa_severity = alert_data.get("severity", "").lower()
            severity = severity_map.get(epa_severity, AlertSeverity.MEDIUM)
            
            # Map EPA alert type
            alert_type_map = {
                "air_quality": "air_quality_alert",
                "water_quality": "water_quality_alert",
                "hazardous_materials": "hazardous_materials_alert",
                "chemical_spill": "chemical_spill",
                "radiation": "radiation_alert",
            }
            
            epa_type = alert_data.get("type", "").lower()
            alert_type = alert_type_map.get(epa_type, "environmental_alert")
            
            # Parse dates
            created_at = None
            expires_at = None
            
            if "issuedDate" in alert_data:
                try:
                    created_at = datetime.fromisoformat(alert_data["issuedDate"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
                    
            if "expirationDate" in alert_data:
                try:
                    expires_at = datetime.fromisoformat(alert_data["expirationDate"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            
            # Create alert
            alert = Alert(
                id=alert_data.get("id", ""),
                title=alert_data.get("title", ""),
                description=alert_data.get("description", ""),
                source="EPA",
                alert_type=alert_type,
                severity=severity,
                status=AlertStatus.NEW,
                url=alert_data.get("moreInfoUrl"),
                created_at=created_at,
                expires_at=expires_at,
            )
            
            # Add EPA-specific fields
            if "affectedAreas" in alert_data:
                alert.regions = alert_data["affectedAreas"]
                
            if "recommendedActions" in alert_data:
                alert.recommended_actions = alert_data["recommendedActions"]
                
            if "populationImpact" in alert_data:
                try:
                    alert.affected_population = int(alert_data["populationImpact"])
                except (ValueError, TypeError):
                    pass
            
            # Add all remaining data to metadata
            alert.metadata = {k: v for k, v in alert_data.items() if k not in [
                "id", "title", "description", "moreInfoUrl", "severity", "type",
                "issuedDate", "expirationDate", "affectedAreas",
                "recommendedActions", "populationImpact"
            ]}
            
            # Add EPA-specific metadata
            if "aqi" in alert_data:  # Air Quality Index
                alert.metadata["aqi"] = alert_data["aqi"]
            if "pollutants" in alert_data:
                alert.metadata["pollutants"] = alert_data["pollutants"]
            if "waterBodyName" in alert_data:
                alert.metadata["water_body"] = alert_data["waterBodyName"]
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating Alert from EPA data: {e}")
            return None
    
    def _meets_severity_threshold(self, alert: Alert) -> bool:
        """
        Check if alert meets the configured severity threshold.
        
        Args:
            alert: The alert to check
            
        Returns:
            bool: True if alert meets threshold
        """
        # Convert severities to numeric values for comparison
        severity_values = {
            AlertSeverity.CRITICAL: 5,
            AlertSeverity.HIGH: 4,
            AlertSeverity.MEDIUM: 3,
            AlertSeverity.LOW: 2,
            AlertSeverity.INFORMATIONAL: 1,
        }
        
        alert_value = severity_values.get(alert.severity, 0)
        threshold_value = severity_values.get(self.severity_threshold, 0)
        
        return alert_value >= threshold_value
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for EPA API requests."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "EPAAlertAdapter/1.0",
        }
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            
        return headers