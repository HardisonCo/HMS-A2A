"""
FEMA Alert Adapter

Adapter for FEMA (Federal Emergency Management Agency) alerts.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
import aiohttp
from datetime import datetime

from .alert_adapter import AlertAdapter
from ..models.alert import Alert, AlertSeverity, AlertStatus

logger = logging.getLogger(__name__)


@AlertAdapter.register_adapter("fema")
class FEMAAlertAdapter(AlertAdapter):
    """
    Adapter for FEMA alerts related to natural disasters, emergency declarations,
    and other emergency management information.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the FEMA alert adapter.
        
        Args:
            config: Configuration for the adapter
        """
        super().__init__(config)
        self.api_url = config.get("api_url", "https://api.fema.gov/alerts")
        self.api_key = config.get("api_key", "")
        self.timeout = config.get("timeout", 30)
        self.session = None
        
        # Specific FEMA settings
        self.include_disasters = config.get("include_disasters", True)
        self.include_emergencies = config.get("include_emergencies", True)
        self.include_warnings = config.get("include_warnings", True)
        self.include_preparedness = config.get("include_preparedness", True)
    
    async def initialize(self) -> bool:
        """
        Initialize the FEMA alert adapter.
        
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
                            logger.error(f"FEMA API health check failed: {response.status}")
                            return False
                except Exception as e:
                    logger.error(f"FEMA API connection test failed: {e}")
                    return False
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing FEMA alert adapter: {e}")
            if self.session:
                await self.session.close()
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the FEMA alert adapter."""
        if self.session:
            await self.session.close()
        self.is_initialized = False
    
    async def get_alerts(self) -> List[Alert]:
        """
        Get alerts from FEMA API.
        
        Returns:
            List of alerts
        """
        if not self.is_initialized:
            raise RuntimeError("FEMA alert adapter not initialized")
            
        alerts = []
        
        # Build query parameters
        params = {
            "format": "json",
            "limit": 100,
        }
        
        # Add filters based on configuration
        alert_types = []
        if self.include_disasters:
            alert_types.append("disaster")
        if self.include_emergencies:
            alert_types.append("emergency")
        if self.include_warnings:
            alert_types.append("warning")
        if self.include_preparedness:
            alert_types.append("preparedness")
            
        if alert_types:
            params["type"] = ",".join(alert_types)
        
        try:
            async with self.session.get(self.api_url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Error fetching FEMA alerts: {response.status}")
                    return []
                    
                data = await response.json()
                
                # Process alerts
                for alert_data in data.get("alerts", []):
                    try:
                        alert = self._process_alert(alert_data)
                        if alert:
                            alerts.append(alert)
                    except Exception as e:
                        logger.error(f"Error processing FEMA alert: {e}")
                
                # If FEMA API provides disaster declarations separately
                disasters_url = f"{self.api_url}/disasters"
                async with self.session.get(disasters_url, params={"format": "json", "limit": 50}) as disaster_response:
                    if disaster_response.status == 200:
                        disaster_data = await disaster_response.json()
                        
                        for disaster in disaster_data.get("disasters", []):
                            try:
                                disaster_alert = self._process_disaster(disaster)
                                if disaster_alert:
                                    alerts.append(disaster_alert)
                            except Exception as e:
                                logger.error(f"Error processing FEMA disaster: {e}")
                
        except Exception as e:
            logger.error(f"Error fetching FEMA alerts: {e}")
        
        return alerts
    
    def _process_alert(self, alert_data: Dict[str, Any]) -> Optional[Alert]:
        """
        Process FEMA alert data into unified Alert format.
        
        Args:
            alert_data: Raw alert data from FEMA API
            
        Returns:
            Processed Alert or None if invalid
        """
        try:
            # Map FEMA severity to unified severity
            severity_map = {
                "extreme": AlertSeverity.CRITICAL,
                "severe": AlertSeverity.HIGH,
                "moderate": AlertSeverity.MEDIUM,
                "minor": AlertSeverity.LOW,
                "unknown": AlertSeverity.INFORMATIONAL,
            }
            
            fema_severity = alert_data.get("severity", "").lower()
            severity = severity_map.get(fema_severity, AlertSeverity.MEDIUM)
            
            # Map FEMA alert type
            alert_type_map = {
                "disaster": "disaster_declaration",
                "emergency": "emergency_declaration",
                "warning": "emergency_warning",
                "preparedness": "preparedness_advisory",
                "evacuation": "evacuation_order",
                "shelter": "shelter_information",
            }
            
            fema_type = alert_data.get("type", "").lower()
            alert_type = alert_type_map.get(fema_type, "emergency_alert")
            
            # Parse dates
            created_at = None
            expires_at = None
            
            if "issueDate" in alert_data:
                try:
                    created_at = datetime.fromisoformat(alert_data["issueDate"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
                    
            if "expiryDate" in alert_data:
                try:
                    expires_at = datetime.fromisoformat(alert_data["expiryDate"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            
            # Create alert
            alert = Alert(
                id=alert_data.get("id", ""),
                title=alert_data.get("title", ""),
                description=alert_data.get("description", ""),
                source="FEMA",
                alert_type=alert_type,
                severity=severity,
                status=AlertStatus.NEW,
                url=alert_data.get("url"),
                created_at=created_at,
                expires_at=expires_at,
            )
            
            # Add FEMA-specific fields
            if "affectedAreas" in alert_data:
                alert.regions = alert_data["affectedAreas"]
            elif "states" in alert_data:
                alert.regions = alert_data["states"]
                
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
                "issueDate", "expiryDate", "affectedAreas", "states",
                "recommendedActions", "affectedPopulation"
            ]}
            
            # Add FEMA-specific metadata
            if "disasterNumber" in alert_data:
                alert.metadata["disaster_number"] = alert_data["disasterNumber"]
            if "incidentType" in alert_data:
                alert.metadata["incident_type"] = alert_data["incidentType"]
            if "declarationType" in alert_data:
                alert.metadata["declaration_type"] = alert_data["declarationType"]
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating Alert from FEMA data: {e}")
            return None
    
    def _process_disaster(self, disaster_data: Dict[str, Any]) -> Optional[Alert]:
        """
        Process FEMA disaster declaration into unified Alert format.
        
        Args:
            disaster_data: Raw disaster data from FEMA API
            
        Returns:
            Processed Alert or None if invalid
        """
        try:
            # Map disaster type to severity
            disaster_severity_map = {
                "Major Disaster": AlertSeverity.HIGH,
                "Emergency": AlertSeverity.HIGH,
                "Fire Management": AlertSeverity.MEDIUM,
                "Biological": AlertSeverity.HIGH,
            }
            
            declaration_type = disaster_data.get("declarationType", "")
            severity = disaster_severity_map.get(declaration_type, AlertSeverity.MEDIUM)
            
            # Parse dates
            created_at = None
            
            if "declarationDate" in disaster_data:
                try:
                    created_at = datetime.fromisoformat(disaster_data["declarationDate"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            
            # Create title and description
            title = f"{declaration_type}: {disaster_data.get('disasterName', 'Unnamed Disaster')}"
            description = f"FEMA has declared a {declaration_type.lower()} for {disaster_data.get('disasterName', 'an incident')}."
            
            if "incidentType" in disaster_data:
                description += f" Incident type: {disaster_data['incidentType']}."
                
            if "designatedAreas" in disaster_data and disaster_data["designatedAreas"]:
                areas = ", ".join(disaster_data["designatedAreas"][:5])
                if len(disaster_data["designatedAreas"]) > 5:
                    areas += f" and {len(disaster_data['designatedAreas']) - 5} more areas"
                description += f" Designated areas include: {areas}."
            
            # Create alert
            alert = Alert(
                id=disaster_data.get("disasterNumber", ""),
                title=title,
                description=description,
                source="FEMA",
                alert_type="disaster_declaration",
                severity=severity,
                status=AlertStatus.NEW,
                url=disaster_data.get("disasterInfoUrl"),
                created_at=created_at,
            )
            
            # Add region information
            if "states" in disaster_data:
                alert.regions = disaster_data["states"]
            elif "designatedAreas" in disaster_data:
                alert.regions = disaster_data["designatedAreas"]
            
            # Add recommended actions
            if severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                alert.recommended_actions = [
                    "Follow local emergency management instructions",
                    "Monitor local news for updates",
                    "Contact your local emergency management office for assistance",
                    "Visit disasterassistance.gov for relief information",
                ]
            
            # Add all data to metadata
            alert.metadata = {k: v for k, v in disaster_data.items()}
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating Alert from FEMA disaster data: {e}")
            return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for FEMA API requests."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "FEMAAlertAdapter/1.0",
        }
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            
        return headers