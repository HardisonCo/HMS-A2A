#!/usr/bin/env python3
"""
Agency Implementation Framework Demo Script

This script demonstrates the capabilities of the agency implementation framework,
showcasing core foundation components and how they can be adapted for different agency needs.
It provides examples of:
1. Base services and extension points
2. Agency-specific implementations
3. Integration between services
4. Configuration and customization
"""

import asyncio
import logging
import json
import datetime
from typing import Dict, List, Any, Optional, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agency-demo")

# Import mock extension registry for demo
class MockExtensionRegistry:
    """Mock extension registry for demonstration purposes."""
    
    def __init__(self):
        self.data_sources = {}
        self.notification_channels = {}
        self.predictive_models = {}

    def register_data_source(self, name, source):
        self.data_sources[name] = source
        
    def get_data_source(self, name):
        return self.data_sources.get(name)
    
    def register_notification_channel(self, name, channel):
        self.notification_channels[name] = channel
        
    def get_notification_channel(self, name):
        return self.notification_channels.get(name)
    
    def register_predictive_model(self, name, model):
        self.predictive_models[name] = model
        
    def get_predictive_model(self, name):
        return self.predictive_models.get(name)


# Mock implementation of core services
class MockBaseService:
    """Base service implementation for demo."""
    
    def __init__(self, service_name, config=None):
        self.service_name = service_name
        self.config = config or {}
        self.logger = logging.getLogger(f"service.{service_name}")
        
    def get_status(self):
        return {
            "service": self.service_name,
            "status": "operational",
            "config": {k: v for k, v in self.config.items() if not k.startswith('_')}
        }


class MockDetectionService(MockBaseService):
    """Mock detection service implementation."""
    
    def __init__(self, config=None):
        super().__init__("detection", config)
        
    async def detect_anomalies(self, data, baseline_period, detection_algorithms=None):
        """Detect anomalies in the provided data."""
        self.logger.info(f"Detecting anomalies using algorithms: {detection_algorithms}")
        
        # For demo purposes, generate some mock anomalies
        anomalies = [
            {
                "id": "anomaly-001",
                "location": {"lat": 34.0522, "lng": -118.2437, "name": "Los Angeles County"},
                "confidence": 0.85,
                "data_sources": ["surveillance", "laboratory"],
                "metrics": {
                    "case_count": 127,
                    "positivity_rate": 0.12,
                    "growth_rate": 1.8
                }
            },
            {
                "id": "anomaly-002",
                "location": {"lat": 37.7749, "lng": -122.4194, "name": "San Francisco County"},
                "confidence": 0.76,
                "data_sources": ["surveillance"],
                "metrics": {
                    "case_count": 89,
                    "positivity_rate": 0.09,
                    "growth_rate": 1.4
                }
            }
        ]
        
        return anomalies


class MockNotificationService(MockBaseService):
    """Mock notification service implementation."""
    
    def __init__(self, config=None, extension_registry=None):
        super().__init__("notification", config)
        self.extension_registry = extension_registry or MockExtensionRegistry()
        
    async def send_notification(self, notification_data, channels=None):
        """Send notification through specified channels."""
        channels = channels or ["console"]
        self.logger.info(f"Sending notification: {notification_data['title']} via {channels}")
        
        for channel in channels:
            self.logger.info(f"Notification sent via {channel}: {notification_data['message']}")
            
        return {
            "status": "sent",
            "channels": channels,
            "timestamp": datetime.datetime.now().isoformat()
        }


# Mock implementations of agency-specific models and services
# CDC Disease Implementation
class DiseaseCategoryEnum:
    INFECTIOUS = "infectious"
    ZOONOTIC = "zoonotic"
    VECTOR_BORNE = "vector_borne"
    FOODBORNE = "foodborne"
    RESPIRATORY = "respiratory"

class TransmissionTypeEnum:
    AIRBORNE = "airborne"
    DIRECT_CONTACT = "direct_contact"
    VECTOR_BORNE = "vector_borne"

class SeverityLevelEnum:
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    CRITICAL = "critical"

class DiseaseModel:
    """Simplified disease model for demonstration purposes."""
    
    def __init__(self, disease_id, name, category, transmission_types, severity_level):
        self.disease_id = disease_id
        self.name = name
        self.scientific_name = f"Scientific {name}"
        self.category = category
        self.transmission_types = transmission_types
        self.incubation_period_days = {"min": 1, "max": 14, "mean": 5}
        self.infectious_period_days = {"min": 3, "max": 10, "mean": 7}
        self.r0_estimate = 2.5
        self.case_fatality_rate = 0.01
        self.severity_level = severity_level
        self.reportable = True
        self.description = f"Description of {name}"
        self.symptoms = ["fever", "cough", "fatigue"]
        self.preventive_measures = ["vaccination", "hand washing"]
        self.treatments = ["supportive care", "antivirals"]
        self.variants = []
        self.emergence_date = datetime.datetime.now() - datetime.timedelta(days=120)
        self.last_updated = datetime.datetime.now()
        
    def calculate_transmission_risk(self, population_density, vaccination_rate=0.0, mobility_factor=1.0):
        """Calculate disease transmission risk."""
        base_risk = self.r0_estimate * mobility_factor
        density_factor = min(1.0, population_density / 1000)
        immune_escape = 0.2  # Mock value
        effective_vaccination = vaccination_rate * (1.0 - immune_escape)
        transmission_risk = base_risk * (1 + density_factor) * (1 - (0.8 * effective_vaccination))
        return max(0.0, transmission_risk)


class DiseaseSurveillanceService(MockBaseService):
    """Mock disease surveillance service for CDC implementation."""
    
    def __init__(self, config=None, extension_registry=None, detection_service=None, notification_service=None):
        super().__init__("disease_surveillance", config)
        self.extension_registry = extension_registry or MockExtensionRegistry()
        self.detection_service = detection_service
        self.notification_service = notification_service
        self.active_outbreaks = {}
        self.monitoring_diseases = {}
        
    async def start_monitoring(self):
        """Start disease surveillance monitoring."""
        self.logger.info("Starting CDC disease surveillance monitoring")
        
        # Add some mock diseases to monitor
        avian_flu = DiseaseModel(
            disease_id="avian-influenza",
            name="Avian Influenza A(H5N1)",
            category=DiseaseCategoryEnum.ZOONOTIC,
            transmission_types=[TransmissionTypeEnum.AIRBORNE, TransmissionTypeEnum.DIRECT_CONTACT],
            severity_level=SeverityLevelEnum.HIGH
        )
        
        self.monitoring_diseases["avian-influenza"] = {
            "disease": avian_flu,
            "thresholds": {
                "emergency": {"case_count": 100, "growth_rate": 1.5},
                "warning": {"case_count": 50, "growth_rate": 1.2},
                "advisory": {"case_count": 20, "growth_rate": 1.1},
                "info": {"case_count": 5, "growth_rate": 1.0}
            },
            "alert_levels": {
                "emergency": {"notification_channels": ["email", "sms", "api"]},
                "warning": {"notification_channels": ["email", "api"]},
                "advisory": {"notification_channels": ["email"]},
                "info": {"notification_channels": ["dashboard"]}
            },
            "last_checked": datetime.datetime.now() - datetime.timedelta(days=1)
        }
        
        self.logger.info(f"Initialized monitoring for {len(self.monitoring_diseases)} diseases")
        return True
    
    async def collect_and_analyze_data(self):
        """Collect and analyze surveillance data."""
        self.logger.info("Collecting surveillance data from sources")
        
        # Simulate data collection
        collected_data = {
            "surveillance": {
                "avian-influenza": {
                    "case_count": 127,
                    "locations": [
                        {"lat": 34.0522, "lng": -118.2437, "name": "Los Angeles County", "count": 72},
                        {"lat": 37.7749, "lng": -122.4194, "name": "San Francisco County", "count": 55}
                    ],
                    "positivity_rate": 0.12,
                    "demographic_distribution": {"0-18": 0.15, "19-64": 0.7, "65+": 0.15},
                    "source": "Public Health Surveillance System"
                }
            },
            "laboratory": {
                "avian-influenza": {
                    "tests_performed": 1050,
                    "positive_tests": 127,
                    "variant_distribution": {"variant_a": 0.8, "variant_b": 0.15, "other": 0.05},
                    "source": "National Laboratory Network"
                }
            }
        }
        
        self.logger.info("Analyzing collected surveillance data")
        
        # Use detection service to analyze data
        signals = []
        if self.detection_service:
            anomalies = await self.detection_service.detect_anomalies(
                data=collected_data,
                baseline_period=28,
                detection_algorithms=["cusum", "ewma"]
            )
            
            # Process detected anomalies
            for anomaly in anomalies:
                signal = {
                    "disease_id": "avian-influenza",
                    "location": anomaly["location"],
                    "timestamp": datetime.datetime.now(),
                    "confidence": anomaly["confidence"],
                    "data_sources": anomaly["data_sources"],
                    "metrics": anomaly["metrics"],
                    "alert_level": self._determine_alert_level(
                        anomaly["metrics"], 
                        self.monitoring_diseases["avian-influenza"]["thresholds"]
                    )
                }
                signals.append(signal)
        
        return signals
    
    def _determine_alert_level(self, metrics, thresholds):
        """Determine alert level based on metrics and thresholds."""
        alert_level = "info"
        
        for level in ["emergency", "warning", "advisory", "info"]:
            level_thresholds = thresholds.get(level, {})
            conditions_met = all(
                metrics.get(metric_name, 0) >= threshold_value
                for metric_name, threshold_value in level_thresholds.items()
                if metric_name in metrics
            )
            
            if conditions_met:
                alert_level = level
                break
                
        return alert_level
    
    async def register_outbreak(self, signal):
        """Register a new disease outbreak based on surveillance signal."""
        disease_id = signal["disease_id"]
        self.logger.info(f"Registering new outbreak for disease {disease_id}")
        
        # Create outbreak event ID
        outbreak_id = f"OB-{disease_id}-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
        
        # Register outbreak in system
        self.active_outbreaks[outbreak_id] = {
            "outbreak_id": outbreak_id,
            "disease_id": disease_id,
            "disease_name": self.monitoring_diseases[disease_id]["disease"].name,
            "location": signal["location"],
            "start_date": datetime.datetime.now(),
            "status": "active",
            "case_count": signal["metrics"].get("case_count", 0),
            "alert_level": signal["alert_level"],
            "confidence": signal["confidence"]
        }
        
        # Send notification
        if self.notification_service:
            await self._send_outbreak_notification(self.active_outbreaks[outbreak_id])
            
        return outbreak_id
    
    async def _send_outbreak_notification(self, outbreak):
        """Send notification about a detected outbreak."""
        urgency_level = outbreak["alert_level"]
        
        notification_data = {
            "title": f"Disease Outbreak: {outbreak['disease_name']}",
            "message": (
                f"A {urgency_level} level outbreak of {outbreak['disease_name']} "
                f"has been detected in {outbreak['location'].get('name', 'Unknown location')}. "
                f"Current case count: {outbreak['case_count']}."
            ),
            "details": {
                "outbreak_id": outbreak["outbreak_id"],
                "disease": outbreak["disease_name"],
                "location": outbreak["location"],
                "case_count": outbreak["case_count"],
                "confidence": outbreak["confidence"]
            },
            "urgency_level": urgency_level
        }
        
        channels = self.monitoring_diseases[outbreak["disease_id"]]["alert_levels"][urgency_level]["notification_channels"]
        
        await self.notification_service.send_notification(
            notification_data,
            channels=channels
        )


# FEMA Disaster Implementation
class DisasterTypeEnum:
    HURRICANE = "hurricane"
    FLOOD = "flood"
    WILDFIRE = "wildfire"
    EARTHQUAKE = "earthquake"
    TORNADO = "tornado"
    PANDEMIC = "pandemic"

class DisasterPhaseEnum:
    PREPAREDNESS = "preparedness"
    RESPONSE = "response"
    RECOVERY = "recovery"
    MITIGATION = "mitigation"

class DisasterModel:
    """Simplified disaster model for demonstration purposes."""
    
    def __init__(self, disaster_id, name, disaster_type, severity, phase, location, population_affected):
        self.disaster_id = disaster_id
        self.name = name
        self.type = DisasterTypeEnum()
        setattr(self.type, "value", disaster_type)
        self.severity = SeverityLevelEnum()
        setattr(self.severity, "value", severity)
        self.phase = DisasterPhaseEnum()
        setattr(self.phase, "value", phase)
        self.location = location
        self.affected_area = {"radius_km": 75, "area_sq_km": 8000}
        self.population_affected = population_affected
        self.start_date = datetime.datetime.now() - datetime.timedelta(days=2)
        self.hazard_data = {"wind_speed": 110, "rainfall_cm": 45}
        self.impact_assessment = {
            "casualties": {"fatalities": 5, "injuries": 82, "missing": 12},
            "displaced_persons": 2500,
            "structures_affected": {"destroyed": 75, "major_damage": 320, "minor_damage": 840},
            "confidence_level": 0.75
        }


class EmergencyResponseService(MockBaseService):
    """Mock emergency response service for FEMA implementation."""
    
    def __init__(self, config=None, extension_registry=None, notification_service=None):
        super().__init__("emergency_response", config)
        self.extension_registry = extension_registry or MockExtensionRegistry()
        self.notification_service = notification_service
        self.active_responses = {}
        self.resource_registry = {
            "emergency_shelter": {"available": 25, "allocated": 0},
            "water_rescue_team": {"available": 8, "allocated": 0},
            "medical_team": {"available": 12, "allocated": 0},
            "emergency_food_supply": {"available": 5000, "allocated": 0},
            "generator": {"available": 30, "allocated": 0},
            "helicopter": {"available": 5, "allocated": 0}
        }
        self.coordination_partners = {}
        
    async def initialize_coordination_partners(self):
        """Initialize coordination partnerships with other agencies."""
        self.logger.info("Initializing coordination partnerships")
        
        # Mock partner agencies
        partners_by_level = {
            "federal": ["FEMA_HQ", "DHS", "DOD", "HHS", "DOE", "DOT"],
            "state": ["STATE_EOC", "STATE_NG", "STATE_DOT", "STATE_DPH"],
            "local": ["COUNTY_EOC", "CITY_EOC", "LOCAL_PD", "LOCAL_FD", "LOCAL_EMS"],
            "tribal": ["TRIBAL_GOV", "TRIBAL_EM"],
            "territorial": ["TERR_GOV", "TERR_EM"]
        }
        
        for level, partners in partners_by_level.items():
            for partner in partners:
                self.coordination_partners[partner] = {
                    "id": partner,
                    "level": level,
                    "agreement_status": "active",
                }
        
        self.logger.info(f"Initialized {len(self.coordination_partners)} coordination partners")
        return True
    
    def _determine_coordination_level(self, disaster):
        """Determine the appropriate coordination level based on disaster characteristics."""
        if disaster.severity.value == SeverityLevelEnum.CRITICAL:
            return "federal"
        elif disaster.severity.value == SeverityLevelEnum.SEVERE:
            # Some major disasters require federal coordination immediately
            federal_immediate_types = [
                "hurricane", "earthquake", "tsunami", "volcanic_eruption",
                "radiological_incident", "terrorism", "pandemic"
            ]
            if disaster.type.value in federal_immediate_types:
                return "federal"
            else:
                return "state"
        elif disaster.severity.value == SeverityLevelEnum.MODERATE:
            return "state"
        else:  # MINOR
            return "local"
    
    def _determine_lead_agency(self, disaster):
        """Determine the appropriate lead agency based on disaster characteristics."""
        level = self._determine_coordination_level(disaster)
        
        if level == "federal":
            # Federal level agencies based on disaster type
            lead_agencies = {
                "hurricane": "FEMA",
                "flood": "FEMA",
                "wildfire": "USFS",
                "earthquake": "FEMA",
                "tornado": "FEMA",
                "pandemic": "HHS"
            }
            return lead_agencies.get(disaster.type.value, "FEMA")
        
        elif level == "state":
            return "STATE_EOC"
        
        else:  # local
            return "LOCAL_EOC"
    
    async def activate_emergency_response(self, disaster):
        """Activate an emergency response for a disaster."""
        self.logger.info(f"Activating emergency response for disaster {disaster.disaster_id}: {disaster.name}")
        
        # Create response plan ID
        response_id = f"ER-{disaster.disaster_id}-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
        
        # Create initial response plan
        coordination_level = self._determine_coordination_level(disaster)
        lead_agency = self._determine_lead_agency(disaster)
        
        response_plan = {
            "response_id": response_id,
            "disaster_id": disaster.disaster_id,
            "disaster_name": disaster.name,
            "disaster_type": disaster.type.value,
            "activation_time": datetime.datetime.now(),
            "status": "activated",
            "coordination_level": coordination_level,
            "lead_agency": lead_agency,
            "resource_allocations": {},
            "response_actions": [],
            "situation_reports": [],
            "updates": []
        }
        
        # Store response plan
        self.active_responses[disaster.disaster_id] = response_plan
        
        # Create initial response actions based on disaster type
        await self._create_initial_response_actions(disaster)
        
        # Send notification if notification service is available
        if self.notification_service:
            await self._notify_coordination_partners(response_plan)
        
        self.logger.info(f"Emergency response activated: {response_id}")
        return response_id
    
    async def _create_initial_response_actions(self, disaster):
        """Create initial response actions based on disaster type."""
        response_plan = self.active_responses[disaster.disaster_id]
        
        # Common initial actions for all disasters
        common_actions = [
            {
                "action_type": "situation_assessment",
                "description": "Conduct initial situation assessment and damage survey",
                "assigned_to": "field_assessment_team",
                "priority": "urgent",
                "status": "planned"
            },
            {
                "action_type": "coordination_activation",
                "description": "Activate emergency coordination center",
                "assigned_to": "emergency_manager",
                "priority": "urgent",
                "status": "planned"
            },
            {
                "action_type": "public_notification",
                "description": "Issue public notification and safety instructions",
                "assigned_to": "public_affairs",
                "priority": "urgent",
                "status": "planned"
            }
        ]
        
        # Add common actions to response plan
        for i, action in enumerate(common_actions):
            action_id = f"ACTION-{i+1}"
            action["action_id"] = action_id
            action["created"] = datetime.datetime.now()
            action["updated"] = datetime.datetime.now()
            response_plan["response_actions"].append(action)
        
        # Add disaster-specific actions based on type
        disaster_specific_actions = self._get_disaster_specific_actions(disaster)
        
        for i, action in enumerate(disaster_specific_actions):
            action_id = f"ACTION-{len(response_plan['response_actions'])+1}"
            action["action_id"] = action_id
            action["created"] = datetime.datetime.now()
            action["updated"] = datetime.datetime.now()
            response_plan["response_actions"].append(action)
            
        self.logger.info(f"Created {len(response_plan['response_actions'])} initial response actions")
    
    def _get_disaster_specific_actions(self, disaster):
        """Get disaster-specific response actions based on disaster type."""
        # Actions based on disaster type
        type_actions = {
            "hurricane": [
                {
                    "action_type": "evacuation",
                    "description": "Coordinate evacuation of vulnerable coastal areas",
                    "assigned_to": "evacuation_coordinator",
                    "priority": "urgent",
                    "status": "planned"
                },
                {
                    "action_type": "shelter_activation",
                    "description": "Activate emergency shelters in safe locations",
                    "assigned_to": "shelter_coordinator",
                    "priority": "urgent",
                    "status": "planned"
                }
            ],
            "flood": [
                {
                    "action_type": "evacuation",
                    "description": "Coordinate evacuation of flood-prone areas",
                    "assigned_to": "evacuation_coordinator",
                    "priority": "urgent",
                    "status": "planned"
                },
                {
                    "action_type": "water_rescue",
                    "description": "Deploy water rescue teams to affected areas",
                    "assigned_to": "search_rescue_coordinator",
                    "priority": "urgent",
                    "status": "planned"
                }
            ],
            "wildfire": [
                {
                    "action_type": "evacuation",
                    "description": "Coordinate evacuation of threatened areas",
                    "assigned_to": "evacuation_coordinator",
                    "priority": "urgent",
                    "status": "planned"
                },
                {
                    "action_type": "firefighting",
                    "description": "Coordinate firefighting resources and strategies",
                    "assigned_to": "firefighting_coordinator",
                    "priority": "urgent",
                    "status": "planned"
                }
            ]
        }
        
        # Get actions for this disaster type, or return generic actions if type not found
        return type_actions.get(disaster.type.value, [
            {
                "action_type": "impact_assessment",
                "description": "Assess impact and identify immediate needs",
                "assigned_to": "assessment_coordinator",
                "priority": "high",
                "status": "planned"
            },
            {
                "action_type": "resource_mobilization",
                "description": "Mobilize appropriate resources based on disaster type",
                "assigned_to": "resource_manager",
                "priority": "high",
                "status": "planned"
            }
        ])
    
    async def allocate_resources(self, disaster_id, resource_requests):
        """Allocate resources to a disaster response."""
        if disaster_id not in self.active_responses:
            self.logger.warning(f"Attempted to allocate resources for inactive response: {disaster_id}")
            return {"status": "failed", "reason": "inactive_response"}
            
        response_plan = self.active_responses[disaster_id]
        allocation_results = {
            "successful": [],
            "partial": [],
            "failed": []
        }
        
        for request in resource_requests:
            resource_type = request.get("resource_type")
            quantity = request.get("quantity", 1)
            priority = request.get("priority", "normal")
            location = request.get("location", {})
            assignment = request.get("assignment", "general")
            
            if not resource_type or resource_type not in self.resource_registry:
                allocation_results["failed"].append({
                    "resource_type": resource_type,
                    "reason": "invalid_resource_type"
                })
                continue
                
            # Check available resources
            resource_info = self.resource_registry[resource_type]
            available = resource_info["available"]
            
            if available >= quantity:
                # Full allocation possible
                allocated_quantity = quantity
                allocation_status = "complete"
                allocation_results["successful"].append({
                    "resource_type": resource_type,
                    "requested": quantity,
                    "allocated": allocated_quantity
                })
            elif available > 0:
                # Partial allocation
                allocated_quantity = available
                allocation_status = "partial"
                allocation_results["partial"].append({
                    "resource_type": resource_type,
                    "requested": quantity,
                    "allocated": allocated_quantity,
                    "shortfall": quantity - allocated_quantity
                })
            else:
                # No allocation possible
                allocated_quantity = 0
                allocation_status = "failed"
                allocation_results["failed"].append({
                    "resource_type": resource_type,
                    "requested": quantity,
                    "reason": "insufficient_resources"
                })
            
            # Update resource registry if any allocation occurred
            if allocated_quantity > 0:
                resource_info["available"] -= allocated_quantity
                resource_info["allocated"] += allocated_quantity
                
                # Add allocation to response plan
                allocation_id = f"ALLOC-{resource_type}-{len(response_plan['resource_allocations']) + 1}"
                response_plan["resource_allocations"][allocation_id] = {
                    "allocation_id": allocation_id,
                    "resource_type": resource_type,
                    "quantity": allocated_quantity,
                    "status": allocation_status,
                    "priority": priority,
                    "location": location,
                    "assignment": assignment,
                    "allocation_time": datetime.datetime.now(),
                    "requested_quantity": quantity
                }
        
        return {
            "status": "completed",
            "results": allocation_results
        }
    
    async def _notify_coordination_partners(self, response_plan):
        """Notify coordination partners about emergency response activation."""
        self.logger.info(f"Notifying coordination partners for response {response_plan['response_id']}")
        
        # Prepare notification message
        notification = {
            "title": f"Emergency Response Activation: {response_plan['disaster_name']}",
            "message": (
                f"An emergency response has been activated for {response_plan['disaster_name']} "
                f"(Type: {response_plan['disaster_type']}). Coordination level: {response_plan['coordination_level']}. "
                f"Lead agency: {response_plan['lead_agency']}."
            ),
            "details": {
                "response_id": response_plan["response_id"],
                "disaster_id": response_plan["disaster_id"],
                "disaster_name": response_plan["disaster_name"],
                "coordination_level": response_plan["coordination_level"],
                "lead_agency": response_plan["lead_agency"],
                "activation_time": response_plan["activation_time"].isoformat()
            },
            "urgency_level": "emergency"
        }
        
        # This would use the notification service to send to partners
        if self.notification_service:
            await self.notification_service.send_notification(notification)


# EPA Environmental Monitoring Implementation
class PollutantTypeEnum:
    AIR = "air"
    WATER = "water"
    SOIL = "soil"
    RADIATION = "radiation"

class PollutantModel:
    """Simplified pollutant model for demonstration purposes."""
    
    def __init__(self, pollutant_id, name, type_category, measurement_unit, threshold_values):
        self.pollutant_id = pollutant_id
        self.name = name
        self.type_category = type_category
        self.measurement_unit = measurement_unit
        self.threshold_values = threshold_values
        self.description = f"Description of {name}"
        self.health_effects = {
            "short_term": ["Description of short term effects"],
            "long_term": ["Description of long term effects"]
        }
        self.sources = ["Example source 1", "Example source 2"]
        self.regulation_info = {
            "regulated_by": ["EPA"],
            "regulation_code": "Example code"
        }
        
    def is_above_threshold(self, value, threshold_type="warning"):
        """Check if value is above the specified threshold type."""
        if threshold_type in self.threshold_values:
            return value > self.threshold_values[threshold_type]
        return False
        
    def calculate_severity(self, value):
        """Calculate severity level based on measured value."""
        if value <= self.threshold_values.get("safe", 0):
            return "normal"
        elif value <= self.threshold_values.get("warning", 0):
            return "elevated"
        elif value <= self.threshold_values.get("hazardous", 0):
            return "warning"
        else:
            return "hazardous"


class EnvironmentalMonitoringService(MockBaseService):
    """Mock environmental monitoring service for EPA implementation."""
    
    def __init__(self, config=None, extension_registry=None, notification_service=None):
        super().__init__("environmental_monitoring", config)
        self.extension_registry = extension_registry or MockExtensionRegistry()
        self.notification_service = notification_service
        self.monitored_pollutants = {}
        self.monitoring_stations = {}
        self.active_alerts = {}
        
    async def initialize_monitoring(self):
        """Initialize environmental monitoring."""
        self.logger.info("Initializing EPA environmental monitoring")
        
        # Add some mock pollutants to monitor
        pm25 = PollutantModel(
            pollutant_id="pm25",
            name="Particulate Matter 2.5",
            type_category=PollutantTypeEnum.AIR,
            measurement_unit="μg/m³",
            threshold_values={
                "safe": 12.0,
                "warning": 35.5,
                "hazardous": 55.5
            }
        )
        
        ozone = PollutantModel(
            pollutant_id="ozone",
            name="Ground-level Ozone",
            type_category=PollutantTypeEnum.AIR,
            measurement_unit="ppb",
            threshold_values={
                "safe": 70.0,
                "warning": 125.0,
                "hazardous": 200.0
            }
        )
        
        self.monitored_pollutants["pm25"] = pm25
        self.monitored_pollutants["ozone"] = ozone
        
        # Setup mock monitoring stations
        self.monitoring_stations = {
            "station-001": {
                "id": "station-001",
                "name": "Downtown Air Quality Monitor",
                "location": {"lat": 34.0522, "lng": -118.2437, "name": "Los Angeles"},
                "pollutants_monitored": ["pm25", "ozone"],
                "status": "active",
                "last_reading_time": datetime.datetime.now() - datetime.timedelta(hours=1)
            },
            "station-002": {
                "id": "station-002",
                "name": "Coastal Water Quality Monitor",
                "location": {"lat": 33.9550, "lng": -118.4050, "name": "Santa Monica"},
                "pollutants_monitored": ["ozone"],
                "status": "active",
                "last_reading_time": datetime.datetime.now() - datetime.timedelta(hours=2)
            }
        }
        
        self.logger.info(f"Initialized monitoring for {len(self.monitored_pollutants)} pollutants at {len(self.monitoring_stations)} stations")
        return True
    
    async def collect_and_analyze_readings(self):
        """Collect and analyze environmental readings."""
        self.logger.info("Collecting environmental readings from monitoring stations")
        
        # Simulate data collection
        readings = {}
        alerts = []
        
        for station_id, station in self.monitoring_stations.items():
            station_readings = []
            
            for pollutant_id in station["pollutants_monitored"]:
                if pollutant_id not in self.monitored_pollutants:
                    continue
                    
                pollutant = self.monitored_pollutants[pollutant_id]
                
                # Generate mock reading with simulated spike for PM2.5
                if pollutant_id == "pm25" and station_id == "station-001":
                    value = 42.8  # Above warning threshold
                else:
                    # Generate normal reading
                    base_value = pollutant.threshold_values.get("safe", 0) * 0.7
                    variance = base_value * 0.2
                    value = base_value + (variance * (0.5 - 0.5))  # Random variance
                
                reading = {
                    "station_id": station_id,
                    "pollutant_id": pollutant_id,
                    "value": value,
                    "unit": pollutant.measurement_unit,
                    "timestamp": datetime.datetime.now(),
                    "quality_flag": "valid"
                }
                
                station_readings.append(reading)
                
                # Check if reading exceeds thresholds
                severity = pollutant.calculate_severity(value)
                if severity in ["warning", "hazardous"]:
                    alert = {
                        "alert_id": f"ENV-ALERT-{station_id}-{pollutant_id}-{datetime.datetime.now().strftime('%Y%m%d%H%M')}",
                        "station_id": station_id,
                        "station_name": station["name"],
                        "location": station["location"],
                        "pollutant_id": pollutant_id,
                        "pollutant_name": pollutant.name,
                        "value": value,
                        "unit": pollutant.measurement_unit,
                        "severity": severity,
                        "timestamp": datetime.datetime.now(),
                        "health_recommendations": [
                            "Sensitive groups should reduce outdoor activities",
                            "Keep windows closed in affected areas"
                        ]
                    }
                    alerts.append(alert)
                    self.active_alerts[alert["alert_id"]] = alert
            
            readings[station_id] = station_readings
            
            # Update station's last reading time
            station["last_reading_time"] = datetime.datetime.now()
        
        self.logger.info(f"Collected {sum(len(x) for x in readings.values())} readings, detected {len(alerts)} alerts")
        
        # Send alerts if notification service is available
        if alerts and self.notification_service:
            for alert in alerts:
                await self._send_alert_notification(alert)
        
        return {
            "readings": readings,
            "alerts": alerts
        }
    
    async def _send_alert_notification(self, alert):
        """Send notification about environmental alert."""
        urgency_map = {
            "elevated": "advisory",
            "warning": "warning",
            "hazardous": "emergency"
        }
        
        urgency_level = urgency_map.get(alert["severity"], "advisory")
        
        notification_data = {
            "title": f"Environmental Alert: {alert['pollutant_name']}",
            "message": (
                f"A {alert['severity']} level of {alert['pollutant_name']} "
                f"has been detected at {alert['station_name']}. "
                f"Current reading: {alert['value']} {alert['unit']}."
            ),
            "details": {
                "alert_id": alert["alert_id"],
                "pollutant": alert["pollutant_name"],
                "location": alert["location"],
                "value": alert["value"],
                "unit": alert["unit"],
                "severity": alert["severity"],
                "health_recommendations": alert["health_recommendations"]
            },
            "urgency_level": urgency_level
        }
        
        channels = ["email", "dashboard"]
        if urgency_level == "emergency":
            channels.append("sms")
        
        await self.notification_service.send_notification(
            notification_data,
            channels=channels
        )


# Main demo function
async def run_demo():
    """Run the agency implementation framework demonstration."""
    print("\n===== AGENCY IMPLEMENTATION FRAMEWORK DEMO =====\n")
    print("This demo showcases the core foundation components and how they can be")
    print("adapted for different agency-specific implementations.\n")
    
    # Create extension registry
    extension_registry = MockExtensionRegistry()
    
    # Initialize services
    detection_service = MockDetectionService()
    notification_service = MockNotificationService(extension_registry=extension_registry)
    
    print("\n1. INITIALIZING AGENCY IMPLEMENTATIONS\n")
    print("Initializing CDC Disease Surveillance...")
    cdc_service = DiseaseSurveillanceService(
        config={"data_refresh_interval": 3600},
        extension_registry=extension_registry,
        detection_service=detection_service,
        notification_service=notification_service
    )
    await cdc_service.start_monitoring()
    
    print("\nInitializing FEMA Emergency Response...")
    fema_service = EmergencyResponseService(
        config={},
        extension_registry=extension_registry,
        notification_service=notification_service
    )
    await fema_service.initialize_coordination_partners()
    
    print("\nInitializing EPA Environmental Monitoring...")
    epa_service = EnvironmentalMonitoringService(
        config={},
        extension_registry=extension_registry,
        notification_service=notification_service
    )
    await epa_service.initialize_monitoring()
    
    print("\n2. SIMULATING CDC DISEASE OUTBREAK DETECTION\n")
    print("Collecting and analyzing surveillance data...")
    signals = await cdc_service.collect_and_analyze_data()
    
    if signals:
        print(f"Detected {len(signals)} potential disease outbreak signals:")
        for signal in signals:
            print(f"  • {signal['disease_id']} in {signal['location']['name']}")
            print(f"    Alert Level: {signal['alert_level']}")
            print(f"    Confidence: {signal['confidence']:.2f}")
            print(f"    Case Count: {signal['metrics']['case_count']}")
            
        print("\nRegistering outbreak based on detected signal...")
        outbreak_id = await cdc_service.register_outbreak(signals[0])
        print(f"Registered outbreak: {outbreak_id}")
        
        # Display the active outbreak details
        outbreak = cdc_service.active_outbreaks[outbreak_id]
        print("\nActive Outbreak Details:")
        print(f"  Disease: {outbreak['disease_name']}")
        print(f"  Location: {outbreak['location']['name']}")
        print(f"  Alert Level: {outbreak['alert_level']}")
        print(f"  Case Count: {outbreak['case_count']}")
    else:
        print("No disease outbreak signals detected.")
    
    print("\n3. SIMULATING FEMA EMERGENCY RESPONSE\n")
    # Create a disaster for FEMA response
    hurricane = DisasterModel(
        disaster_id="hurricane-ian-2022",
        name="Hurricane Ian",
        disaster_type="hurricane",
        severity="severe",
        phase="response",
        location={"lat": 26.1224, "lng": -81.8037, "name": "Fort Myers, FL"},
        population_affected=2500000
    )
    
    print(f"Activating emergency response for {hurricane.name}...")
    response_id = await fema_service.activate_emergency_response(hurricane)
    
    # Display the active response details
    response = fema_service.active_responses[hurricane.disaster_id]
    print("\nActive Emergency Response Details:")
    print(f"  Response ID: {response['response_id']}")
    print(f"  Disaster: {response['disaster_name']} ({response['disaster_type']})")
    print(f"  Coordination Level: {response['coordination_level']}")
    print(f"  Lead Agency: {response['lead_agency']}")
    print(f"  Response Actions: {len(response['response_actions'])}")
    
    print("\nAllocating resources for emergency response...")
    resource_requests = [
        {"resource_type": "emergency_shelter", "quantity": 12, "priority": "urgent"},
        {"resource_type": "water_rescue_team", "quantity": 5, "priority": "urgent"},
        {"resource_type": "medical_team", "quantity": 8, "priority": "high"},
        {"resource_type": "emergency_food_supply", "quantity": 2000, "priority": "high"},
        {"resource_type": "generator", "quantity": 15, "priority": "high"},
        {"resource_type": "helicopter", "quantity": 3, "priority": "urgent"}
    ]
    
    allocation_results = await fema_service.allocate_resources(hurricane.disaster_id, resource_requests)
    
    print("\nResource Allocation Results:")
    print(f"  Successful Allocations: {len(allocation_results['results']['successful'])}")
    print(f"  Partial Allocations: {len(allocation_results['results']['partial'])}")
    print(f"  Failed Allocations: {len(allocation_results['results']['failed'])}")
    
    for allocation in allocation_results['results']['successful']:
        print(f"  • Allocated {allocation['allocated']} {allocation['resource_type']}")
    
    print("\n4. SIMULATING EPA ENVIRONMENTAL MONITORING\n")
    print("Collecting and analyzing environmental readings...")
    readings_results = await epa_service.collect_and_analyze_readings()
    
    if readings_results['alerts']:
        print(f"Detected {len(readings_results['alerts'])} environmental alerts:")
        for alert in readings_results['alerts']:
            print(f"  • {alert['pollutant_name']} at {alert['station_name']}")
            print(f"    Severity: {alert['severity']}")
            print(f"    Reading: {alert['value']} {alert['unit']}")
            print(f"    Health Recommendations:")
            for rec in alert['health_recommendations']:
                print(f"      - {rec}")
    else:
        print("No environmental alerts detected.")
    
    print("\n5. DEMONSTRATING CROSS-AGENCY INTEGRATION\n")
    print("In a real implementation, these agencies would coordinate responses")
    print("for scenarios like hurricane-related health hazards or environmental")
    print("impacts of disasters. The foundation layer enables this integration.")
    
    print("\n===== DEMO COMPLETE =====\n")


# Run the demo
if __name__ == "__main__":
    asyncio.run(run_demo())