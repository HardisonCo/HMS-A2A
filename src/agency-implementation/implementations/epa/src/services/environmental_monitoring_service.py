"""
Environmental Monitoring Service for EPA implementation.

This service extends the base services to provide comprehensive environmental
monitoring capabilities, integrating data from multiple sources and providing
real-time analysis of environmental conditions.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

# Import foundation services
from agency_implementation.foundation.core_services.base_service import BaseService
from agency_implementation.foundation.core_services.detection_service import DetectionService
from agency_implementation.foundation.core_services.notification_service import NotificationService
from agency_implementation.foundation.extension_points.registry import ExtensionRegistry

# Import EPA-specific models
from ..models.pollutant_model import Pollutant, PollutionEvent, HealthRiskLevel


logger = logging.getLogger(__name__)


class EnvironmentalMonitoringService(BaseService):
    """
    Service for monitoring environmental conditions using multiple data sources
    and detection algorithms to identify pollution events and regulatory exceedances.
    """
    
    def __init__(self, 
                 config: Dict[str, Any],
                 extension_registry: ExtensionRegistry,
                 detection_service: DetectionService,
                 notification_service: NotificationService):
        """
        Initialize the environmental monitoring service.
        
        Args:
            config: Configuration parameters for the service
            extension_registry: Registry for accessing extensions
            detection_service: Service for anomaly detection
            notification_service: Service for sending notifications
        """
        super().__init__("environmental_monitoring")
        self.config = config
        self.extension_registry = extension_registry
        self.detection_service = detection_service
        self.notification_service = notification_service
        self.data_sources = {}
        self.active_events = {}
        self.monitoring_categories = config.get("monitoring_categories", [])
        self.refresh_interval = config.get("data_refresh_interval", 1800)  # Default 30 min
        self.alert_threshold = config.get("alert_threshold", 0.80)
        
        # Initialize data sources
        self._initialize_data_sources()
        
    def _initialize_data_sources(self) -> None:
        """Initialize connections to configured data sources."""
        data_source_configs = self.config.get("data_sources", [])
        for source_name in data_source_configs:
            try:
                # Get data source extension from registry
                data_source = self.extension_registry.get_data_source(source_name)
                if data_source:
                    self.data_sources[source_name] = data_source
                    logger.info(f"Initialized data source: {source_name}")
                else:
                    logger.warning(f"Data source {source_name} not found in registry")
            except Exception as e:
                logger.error(f"Error initializing data source {source_name}: {e}")
    
    async def start_monitoring(self) -> None:
        """Start the environmental monitoring process."""
        logger.info("Starting environmental monitoring")
        
        # Initialize monitoring for categories from configuration
        for category in self.monitoring_categories:
            logger.info(f"Setting up monitoring for category: {category}")
            # Load pollutants for this category
            pollutants = await self._load_pollutants_for_category(category)
            logger.info(f"Loaded {len(pollutants)} pollutants for {category}")
        
        # Start periodic data collection
        await self._schedule_data_collection()
    
    async def _load_pollutants_for_category(self, category: str) -> List[Pollutant]:
        """
        Load pollutant definitions for a specific category.
        
        Args:
            category: Category of pollutants to load
            
        Returns:
            List of pollutants in the specified category
        """
        # Implementation would depend on how pollutants are stored
        # This is a placeholder - would typically query a database or service
        logger.info(f"Loading pollutants for category: {category}")
        # In a real implementation, this would fetch from a database
        return []  # Placeholder
        
    async def _schedule_data_collection(self) -> None:
        """Schedule periodic data collection based on configured interval."""
        # In a real implementation, this would set up a periodic task
        logger.info(f"Scheduling data collection every {self.refresh_interval} seconds")
        
        # This would typically use something like asyncio.create_task with a loop
        # or a scheduled task framework
        
    async def collect_monitoring_data(self) -> Dict[str, Any]:
        """
        Collect environmental monitoring data from all configured data sources.
        
        Returns:
            Dictionary of collected data by source and category
        """
        logger.info("Collecting environmental data from all sources")
        collection_results = {}
        
        for source_name, data_source in self.data_sources.items():
            try:
                logger.debug(f"Collecting data from {source_name}")
                source_data = await data_source.fetch_data()
                collection_results[source_name] = source_data
            except Exception as e:
                logger.error(f"Error collecting data from {source_name}: {e}")
                
        return collection_results
    
    async def analyze_monitoring_data(self, collected_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze collected monitoring data to detect potential pollution events.
        
        Args:
            collected_data: Data collected from all sources
            
        Returns:
            List of detected events with confidence scores
        """
        logger.info("Analyzing environmental monitoring data for events")
        detected_events = []
        
        # Process data for each monitoring category
        for category in self.monitoring_categories:
            logger.debug(f"Analyzing data for category: {category}")
            
            # Extract category-specific data from all sources
            category_data = self._extract_category_data(collected_data, category)
            
            # Use the detection service to identify anomalies
            anomalies = await self.detection_service.detect_anomalies(
                data=category_data,
                baseline_period=self.config.get("baseline_period_days", 7),
                detection_algorithms=self.config.get("detection_algorithms", ["threshold", "statistical"])
            )
            
            # Process detected anomalies
            for anomaly in anomalies:
                if anomaly["confidence"] >= self.alert_threshold:
                    event = {
                        "category": category,
                        "pollutant_id": anomaly.get("pollutant_id"),
                        "location": anomaly["location"],
                        "timestamp": datetime.now(),
                        "confidence": anomaly["confidence"],
                        "data_sources": anomaly["data_sources"],
                        "measurements": anomaly["measurements"],
                        "exceedance_ratio": anomaly.get("exceedance_ratio", 1.0)
                    }
                    detected_events.append(event)
        
        return detected_events
    
    def _extract_category_data(self, collected_data: Dict[str, Any], category: str) -> Dict[str, Any]:
        """
        Extract data relevant to a specific environmental category from the collected dataset.
        
        Args:
            collected_data: All data collected from sources
            category: Environmental category to extract data for
            
        Returns:
            Extracted category-specific data
        """
        # This would extract and normalize category-specific data
        # Implementation depends on data structure from sources
        category_data = {
            "source_data": {},
            "locations": [],
            "pollutants": [],
            "timestamps": []
        }
        
        for source, data in collected_data.items():
            if category in data:
                category_data["source_data"][source] = data[category]
                
                # Extract unique locations, pollutants, and timestamps
                if "locations" in data[category]:
                    category_data["locations"].extend(data[category]["locations"])
                if "pollutants" in data[category]:
                    category_data["pollutants"].extend(data[category]["pollutants"])
                if "timestamps" in data[category]:
                    category_data["timestamps"].extend(data[category]["timestamps"])
        
        # Remove duplicates
        category_data["locations"] = list(set(category_data["locations"]))
        category_data["pollutants"] = list(set(category_data["pollutants"]))
        category_data["timestamps"] = list(set(category_data["timestamps"]))
        
        return category_data
    
    async def evaluate_health_risk(self, event_data: Dict[str, Any]) -> HealthRiskLevel:
        """
        Evaluate the health risk associated with a detected environmental event.
        
        Args:
            event_data: Data about the detected event
            
        Returns:
            Health risk level assessment
        """
        pollutant_id = event_data.get("pollutant_id")
        if not pollutant_id:
            logger.warning("Cannot evaluate health risk: No pollutant ID provided")
            return HealthRiskLevel.MODERATE  # Default if pollutant unknown
        
        try:
            # Load pollutant information
            pollutant = await self._load_pollutant(pollutant_id)
            if not pollutant:
                logger.warning(f"Unable to load pollutant {pollutant_id} for risk assessment")
                return HealthRiskLevel.MODERATE
            
            # Get concentration value
            concentration = event_data.get("measurements", {}).get("concentration")
            if concentration is None:
                logger.warning(f"No concentration data for pollutant {pollutant_id}")
                return HealthRiskLevel.MODERATE
            
            # Calculate health risk
            risk_level = pollutant.calculate_health_risk(
                concentration=concentration,
                exposure_duration="acute"  # Default to acute for initial assessment
            )
            
            logger.info(f"Health risk for event with pollutant {pollutant_id}: {risk_level.value}")
            return risk_level
            
        except Exception as e:
            logger.error(f"Error evaluating health risk: {e}")
            return HealthRiskLevel.MODERATE
    
    async def _load_pollutant(self, pollutant_id: str) -> Optional[Pollutant]:
        """
        Load pollutant definition by ID.
        
        Args:
            pollutant_id: ID of the pollutant to load
            
        Returns:
            Pollutant object if found, None otherwise
        """
        # Implementation would depend on how pollutants are stored
        # This is a placeholder - would typically query a database or service
        logger.info(f"Loading pollutant information for {pollutant_id}")
        # In a real implementation, this would fetch from a database
        return None  # Placeholder
        
    async def register_pollution_event(self, 
                                       category: str,
                                       pollutant_id: str,
                                       location: Dict[str, Any],
                                       measurements: Dict[str, Any],
                                       confidence: float) -> str:
        """
        Register a new pollution event based on monitoring signals.
        
        Args:
            category: Environmental category
            pollutant_id: ID of the detected pollutant
            location: Geographic information about the event
            measurements: Measurement data including concentrations
            confidence: Confidence level in the event detection
            
        Returns:
            ID of the registered event
        """
        logger.info(f"Registering new pollution event for {category}, pollutant {pollutant_id}")
        
        # Load pollutant details
        pollutant = await self._load_pollutant(pollutant_id)
        if not pollutant:
            logger.error(f"Cannot register event - pollutant {pollutant_id} not found")
            raise ValueError(f"Pollutant {pollutant_id} not found")
        
        # Evaluate health risk
        health_risk = await self.evaluate_health_risk({
            "pollutant_id": pollutant_id,
            "measurements": measurements
        })
        
        # Create a new pollution event
        event = PollutionEvent(
            event_id=f"PE-{pollutant_id}-{datetime.now().strftime('%Y%m%d%H%M')}",
            pollutant=pollutant,
            location=location,
            start_time=datetime.now(),
            end_time=None,
            peak_concentration=measurements.get("concentration", 0),
            peak_time=datetime.now(),
            average_concentration=measurements.get("concentration", 0),  # Initial average is current value
            measurement_unit=measurements.get("unit", "µg/m³"),
            source=None,  # To be determined through analysis
            status="active",
            health_risk_level=health_risk,
            weather_conditions=measurements.get("weather_conditions", {}),
            notes="Automatically detected through monitoring system"
        )
        
        # In a real implementation, this would persist the event to a database
        self.active_events[event.event_id] = event
        
        # Notify about the new event
        await self._send_event_notification(event)
        
        return event.event_id
    
    async def _send_event_notification(self, event: PollutionEvent) -> None:
        """
        Send notifications about a detected pollution event.
        
        Args:
            event: The pollution event to notify about
        """
        severity = event.calculate_severity_index()
        
        # Determine hazard level based on risk and severity
        hazard_level = "moderate"  # Default
        
        if event.health_risk_level in [HealthRiskLevel.VERY_HIGH, HealthRiskLevel.SEVERE]:
            hazard_level = "hazardous"
        elif event.health_risk_level == HealthRiskLevel.HIGH:
            hazard_level = "unhealthy"
        elif event.health_risk_level == HealthRiskLevel.MODERATE:
            hazard_level = "unhealthy_sensitive"
        elif event.health_risk_level == HealthRiskLevel.LOW:
            hazard_level = "moderate"
        elif event.health_risk_level == HealthRiskLevel.NEGLIGIBLE:
            hazard_level = "good"
            
        # Prepare notification data
        notification_data = {
            "title": f"Environmental Alert: {event.pollutant.name}",
            "message": (
                f"A {hazard_level} level of {event.pollutant.name} "
                f"has been detected in {event.location.get('name', 'Unknown location')}. "
                f"Current concentration: {event.peak_concentration} {event.measurement_unit}."
            ),
            "details": {
                "event_id": event.event_id,
                "pollutant": event.pollutant.name,
                "category": event.pollutant.category.value,
                "location": event.location,
                "concentration": event.peak_concentration,
                "unit": event.measurement_unit,
                "severity_index": severity,
                "health_recommendations": self._get_health_recommendations(event.health_risk_level)
            },
            "hazard_level": hazard_level
        }
        
        # Send through all configured channels
        await self.notification_service.send_notification(
            notification_data,
            channels=self.config.get("notification_channels", ["email", "api_webhook"])
        )
        
    def _get_health_recommendations(self, risk_level: HealthRiskLevel) -> List[str]:
        """
        Get health recommendations based on the risk level.
        
        Args:
            risk_level: Health risk level
            
        Returns:
            List of health recommendations
        """
        recommendations = {
            HealthRiskLevel.NEGLIGIBLE: [
                "No special precautions needed.",
                "Continue normal outdoor activities."
            ],
            HealthRiskLevel.LOW: [
                "Unusually sensitive individuals should consider limiting prolonged outdoor exertion."
            ],
            HealthRiskLevel.MODERATE: [
                "Active children and adults, and people with respiratory disease, such as asthma, should limit prolonged outdoor exertion.",
                "Keep windows closed if sensitive to air quality."
            ],
            HealthRiskLevel.HIGH: [
                "Active children and adults, and people with respiratory disease, such as asthma, should avoid prolonged outdoor exertion.",
                "Everyone else should limit prolonged outdoor exertion.",
                "Stay indoors with windows closed if possible.",
                "Use air purifiers if available."
            ],
            HealthRiskLevel.VERY_HIGH: [
                "Active children and adults, and people with respiratory disease, such as asthma, should avoid all outdoor exertion.",
                "Everyone else should limit outdoor exertion.",
                "Stay indoors with windows closed.",
                "Use air purifiers if available.",
                "Consider wearing masks if outdoor activity is unavoidable."
            ],
            HealthRiskLevel.SEVERE: [
                "Everyone should avoid all outdoor exertion.",
                "Stay indoors with windows closed.",
                "Use air purifiers if available.",
                "Wear appropriate protective equipment if outdoor activity is absolutely necessary.",
                "Follow evacuation orders if issued."
            ]
        }
        
        return recommendations.get(risk_level, ["Monitor local health advisories."])
        
    async def update_event_status(self, 
                                 event_id: str, 
                                 new_data: Dict[str, Any]) -> bool:
        """
        Update the status and data for an existing pollution event.
        
        Args:
            event_id: ID of the event to update
            new_data: New data to update the event with
            
        Returns:
            True if update was successful, False otherwise
        """
        if event_id not in self.active_events:
            logger.warning(f"Attempted to update non-existent event: {event_id}")
            return False
            
        event = self.active_events[event_id]
        
        # Update concentration information if provided
        if "concentration" in new_data:
            current_concentration = new_data["concentration"]
            
            # Update peak if this is higher
            if current_concentration > event.peak_concentration:
                event.peak_concentration = current_concentration
                event.peak_time = datetime.now()
                
            # Update average (simple running average)
            samples = new_data.get("samples", 1)  # How many samples this represents
            current_samples = new_data.get("current_samples", 1)  # How many samples are in current average
            
            # Calculate new average
            total_samples = current_samples + samples
            event.average_concentration = (
                (event.average_concentration * current_samples) + 
                (current_concentration * samples)
            ) / total_samples
            
        # Update status if provided
        if "status" in new_data:
            event.status = new_data["status"]
            
            # If status is resolved, set end time
            if new_data["status"] == "resolved" and not event.end_time:
                event.end_time = datetime.now()
                
        # Update health risk if provided or if concentration changed
        if "health_risk_level" in new_data:
            event.health_risk_level = new_data["health_risk_level"]
        elif "concentration" in new_data:
            # Re-evaluate health risk with new concentration
            health_risk = await self.evaluate_health_risk({
                "pollutant_id": event.pollutant.pollutant_id,
                "measurements": {"concentration": new_data["concentration"]}
            })
            event.health_risk_level = health_risk
            
        # Update source information if provided
        if "source" in new_data:
            event.source = new_data["source"]
        if "source_details" in new_data:
            event.source_details = new_data["source_details"]
            
        # Update response actions if provided
        if "response_actions" in new_data:
            event.response_actions = new_data["response_actions"]
            
        # Add notes if provided
        if "notes" in new_data and new_data["notes"]:
            if event.notes:
                event.notes += f"\n{datetime.now().isoformat()}: {new_data['notes']}"
            else:
                event.notes = f"{datetime.now().isoformat()}: {new_data['notes']}"
                
        logger.info(f"Updated pollution event {event_id} with new data")
        
        # If significant updates occurred, send updated notification
        if any(k in new_data for k in ["concentration", "status", "health_risk_level", "source"]):
            await self._send_event_notification(event)
            
        return True
        
    async def get_active_events(self) -> List[PollutionEvent]:
        """
        Get all currently active pollution events.
        
        Returns:
            List of active pollution events
        """
        return [
            event for event in self.active_events.values()
            if event.is_active()
        ]
        
    async def get_events_by_location(self, 
                                    location_id: str, 
                                    status: Optional[str] = None,
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> List[PollutionEvent]:
        """
        Get pollution events for a specific location with optional filters.
        
        Args:
            location_id: ID of the location
            status: Optional filter by status
            start_date: Optional filter for events after this date
            end_date: Optional filter for events before this date
            
        Returns:
            List of matching pollution events
        """
        # In a real implementation, this would query a database
        # For this example, we'll filter the in-memory events
        
        matching_events = []
        
        for event in self.active_events.values():
            # Check location
            if event.location.get("id") != location_id:
                continue
                
            # Check status if specified
            if status and event.status != status:
                continue
                
            # Check date range if specified
            if start_date and event.start_time < start_date:
                continue
                
            if end_date:
                if not event.end_time and end_date < datetime.now():
                    # Active event and end_date is in the past
                    continue
                elif event.end_time and event.end_time > end_date:
                    continue
                    
            matching_events.append(event)
            
        return matching_events