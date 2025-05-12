"""
Emergency Response Service for FEMA implementation.

This service extends the base services to provide emergency response
coordination capabilities for disaster events, including resource management,
response planning, and multi-agency coordination.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

# Import foundation services
from agency_implementation.foundation.core_services.base_service import BaseService
from agency_implementation.foundation.core_services.notification_service import NotificationService
from agency_implementation.foundation.extension_points.registry import ExtensionRegistry

# Import FEMA-specific models
from ..models.disaster_model import Disaster, DisasterPhase, SeverityLevel


logger = logging.getLogger(__name__)


class EmergencyResponseService(BaseService):
    """
    Service for coordinating emergency response activities for disasters,
    including resource allocation, response planning, and multi-agency coordination.
    """
    
    def __init__(self, 
                 config: Dict[str, Any],
                 extension_registry: ExtensionRegistry,
                 notification_service: NotificationService):
        """
        Initialize the emergency response service.
        
        Args:
            config: Configuration parameters for the service
            extension_registry: Registry for accessing extensions
            notification_service: Service for sending notifications
        """
        super().__init__("emergency_response")
        self.config = config
        self.extension_registry = extension_registry
        self.notification_service = notification_service
        self.active_responses = {}  # Disaster ID -> response plan
        self.resource_registry = {}  # Resource type -> available resources
        self.coordination_partners = {}  # Partner ID -> coordination info
        self.coordination_levels = config.get("coordination_levels", [])
        self.resource_types = config.get("resource_types", [])
        
    async def initialize_resource_registry(self) -> None:
        """Initialize the resource registry with available emergency resources."""
        logger.info("Initializing emergency resource registry")
        
        # This would typically load resource data from a database or external service
        # For this example, we'll create a simple mock registry
        
        for resource_type in self.resource_types:
            try:
                # In real implementation, would fetch from database or inventory system
                self.resource_registry[resource_type] = {
                    "available": 0,
                    "allocated": 0,
                    "pending": 0,
                    "units": [],
                    "last_updated": datetime.now()
                }
                logger.info(f"Initialized resource type: {resource_type}")
            except Exception as e:
                logger.error(f"Error initializing resource type {resource_type}: {e}")
    
    async def initialize_coordination_partners(self) -> None:
        """Initialize coordination partnerships with other agencies and organizations."""
        logger.info("Initializing coordination partnerships")
        
        # This would typically load partner data from a database or configuration
        # For this example, we'll create a simple mock setup
        
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
                    "contact_info": {},
                    "capabilities": [],
                    "agreement_status": "active",
                    "last_contact": None
                }
                
        logger.info(f"Initialized {len(self.coordination_partners)} coordination partners")
    
    async def activate_emergency_response(self, disaster: Disaster) -> str:
        """
        Activate an emergency response for a disaster.
        
        Args:
            disaster: The disaster to activate response for
            
        Returns:
            Response plan ID
        """
        logger.info(f"Activating emergency response for disaster {disaster.disaster_id}: {disaster.name}")
        
        # Create response plan ID
        response_id = f"ER-{disaster.disaster_id}-{datetime.now().strftime('%Y%m%d%H%M')}"
        
        # Create initial response plan
        response_plan = {
            "response_id": response_id,
            "disaster_id": disaster.disaster_id,
            "disaster_name": disaster.name,
            "disaster_type": disaster.type.value,
            "activation_time": datetime.now(),
            "status": "activated",
            "coordination_level": _determine_coordination_level(disaster),
            "lead_agency": _determine_lead_agency(disaster),
            "resource_allocations": {},
            "response_actions": [],
            "coordination_partners": _identify_relevant_partners(disaster, self.coordination_partners),
            "situation_reports": [],
            "updates": []
        }
        
        # Store response plan
        self.active_responses[disaster.disaster_id] = response_plan
        
        # Add initial situation report
        await self.add_situation_report(
            disaster_id=disaster.disaster_id,
            report_data={
                "disaster_phase": disaster.phase.value,
                "severity": disaster.severity.value,
                "location": disaster.location,
                "affected_area": disaster.affected_area,
                "population_affected": disaster.population_affected,
                "impact_assessment": _simplify_impact_assessment(disaster.impact_assessment),
                "hazard_data": disaster.hazard_data
            },
            source="system"
        )
        
        # Create initial response actions based on disaster type
        await self._create_initial_response_actions(disaster)
        
        # Notify coordination partners
        await self._notify_coordination_partners(response_plan)
        
        logger.info(f"Emergency response activated: {response_id}")
        return response_id
    
    async def add_situation_report(self, 
                                  disaster_id: str, 
                                  report_data: Dict[str, Any],
                                  source: str) -> None:
        """
        Add a situation report to the response plan.
        
        Args:
            disaster_id: ID of the disaster
            report_data: Situation report data
            source: Source of the report
        """
        if disaster_id not in self.active_responses:
            logger.warning(f"Attempted to add situation report for inactive response: {disaster_id}")
            return
            
        response_plan = self.active_responses[disaster_id]
        
        # Create situation report
        situation_report = {
            "report_id": f"SITREP-{len(response_plan['situation_reports']) + 1}",
            "timestamp": datetime.now(),
            "data": report_data,
            "source": source
        }
        
        # Add to response plan
        response_plan["situation_reports"].append(situation_report)
        
        # Add to updates
        response_plan["updates"].append({
            "timestamp": datetime.now(),
            "type": "situation_report_added",
            "details": {
                "report_id": situation_report["report_id"],
                "source": source
            }
        })
        
        logger.info(f"Added situation report {situation_report['report_id']} to response {disaster_id}")
        
        # Evaluate if response escalation is needed based on report
        await self._evaluate_response_escalation(disaster_id, report_data)
    
    async def _evaluate_response_escalation(self, 
                                          disaster_id: str, 
                                          report_data: Dict[str, Any]) -> None:
        """
        Evaluate if the response needs to be escalated based on situation report.
        
        Args:
            disaster_id: ID of the disaster
            report_data: Situation report data
        """
        response_plan = self.active_responses[disaster_id]
        current_level = response_plan["coordination_level"]
        
        # Factors that may trigger escalation
        escalation_needed = False
        escalation_reason = ""
        
        # Check severity change
        if "severity" in report_data:
            if report_data["severity"] in ["major", "catastrophic"] and current_level in ["local", "state"]:
                escalation_needed = True
                escalation_reason = f"Severity increased to {report_data['severity']}"
        
        # Check impact assessment
        if "impact_assessment" in report_data:
            impact = report_data["impact_assessment"]
            # If casualties exceed thresholds
            if impact.get("casualties", {}).get("fatalities", 0) > 10 or \
               impact.get("casualties", {}).get("injuries", 0) > 100 or \
               impact.get("displaced_persons", 0) > 1000:
                escalation_needed = True
                escalation_reason = "Impact threshold exceeded for human casualties/displacement"
        
        # If escalation needed, update coordination level
        if escalation_needed:
            if current_level == "local":
                new_level = "state"
            elif current_level == "state":
                new_level = "federal"
            else:
                new_level = current_level  # Already at highest level
                
            if new_level != current_level:
                response_plan["coordination_level"] = new_level
                response_plan["updates"].append({
                    "timestamp": datetime.now(),
                    "type": "coordination_escalation",
                    "details": {
                        "old_level": current_level,
                        "new_level": new_level,
                        "reason": escalation_reason
                    }
                })
                
                # Update lead agency based on new level
                response_plan["lead_agency"] = _determine_lead_agency_for_level(
                    disaster_type=response_plan["disaster_type"],
                    coordination_level=new_level
                )
                
                # Identify additional partners for new level
                additional_partners = _identify_partners_for_level(
                    new_level, self.coordination_partners
                )
                response_plan["coordination_partners"].update(additional_partners)
                
                logger.info(
                    f"Response for disaster {disaster_id} escalated from {current_level} to {new_level}: {escalation_reason}"
                )
                
                # Notify about escalation
                await self._notify_escalation(response_plan, current_level, new_level, escalation_reason)
    
    async def allocate_resources(self, 
                                disaster_id: str, 
                                resource_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Allocate resources to a disaster response.
        
        Args:
            disaster_id: ID of the disaster
            resource_requests: List of resource allocation requests
            
        Returns:
            Dictionary with allocation results
        """
        if disaster_id not in self.active_responses:
            logger.warning(f"Attempted to allocate resources for inactive response: {disaster_id}")
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
                    "allocation_time": datetime.now(),
                    "requested_quantity": quantity
                }
                
                # Add to updates
                response_plan["updates"].append({
                    "timestamp": datetime.now(),
                    "type": "resource_allocation",
                    "details": {
                        "allocation_id": allocation_id,
                        "resource_type": resource_type,
                        "quantity": allocated_quantity,
                        "status": allocation_status
                    }
                })
        
        return {
            "status": "completed",
            "results": allocation_results
        }
    
    async def add_response_action(self, 
                                 disaster_id: str,
                                 action_type: str,
                                 description: str,
                                 assigned_to: str,
                                 location: Dict[str, Any] = None,
                                 priority: str = "normal",
                                 dependencies: List[str] = None) -> str:
        """
        Add a response action to the response plan.
        
        Args:
            disaster_id: ID of the disaster
            action_type: Type of response action
            description: Description of the action
            assigned_to: Entity responsible for the action
            location: Geographic location for the action
            priority: Priority level (low, normal, high, urgent)
            dependencies: IDs of actions this action depends on
            
        Returns:
            Action ID
        """
        if disaster_id not in self.active_responses:
            logger.warning(f"Attempted to add action for inactive response: {disaster_id}")
            return None
            
        response_plan = self.active_responses[disaster_id]
        
        # Create action ID
        action_id = f"ACTION-{len(response_plan['response_actions']) + 1}"
        
        # Create action object
        action = {
            "action_id": action_id,
            "type": action_type,
            "description": description,
            "status": "planned",
            "assigned_to": assigned_to,
            "location": location or {},
            "priority": priority,
            "dependencies": dependencies or [],
            "created": datetime.now(),
            "updated": datetime.now(),
            "updates": []
        }
        
        # Add to response plan
        response_plan["response_actions"].append(action)
        
        # Add to updates
        response_plan["updates"].append({
            "timestamp": datetime.now(),
            "type": "response_action_added",
            "details": {
                "action_id": action_id,
                "action_type": action_type,
                "assigned_to": assigned_to,
                "priority": priority
            }
        })
        
        logger.info(f"Added response action {action_id} to response for disaster {disaster_id}")
        
        # Notify assigned entity
        await self._notify_action_assignment(disaster_id, action)
        
        return action_id
    
    async def update_response_action(self, 
                                    disaster_id: str,
                                    action_id: str,
                                    updates: Dict[str, Any]) -> bool:
        """
        Update a response action.
        
        Args:
            disaster_id: ID of the disaster
            action_id: ID of the action to update
            updates: Dictionary of updates to apply
            
        Returns:
            True if update was successful, False otherwise
        """
        if disaster_id not in self.active_responses:
            logger.warning(f"Attempted to update action for inactive response: {disaster_id}")
            return False
            
        response_plan = self.active_responses[disaster_id]
        
        # Find action
        action = None
        for a in response_plan["response_actions"]:
            if a["action_id"] == action_id:
                action = a
                break
                
        if not action:
            logger.warning(f"Action {action_id} not found in response plan for disaster {disaster_id}")
            return False
            
        # Apply updates
        update_details = {}
        
        if "status" in updates:
            old_status = action["status"]
            action["status"] = updates["status"]
            update_details["status"] = {"old": old_status, "new": updates["status"]}
            
        if "description" in updates:
            action["description"] = updates["description"]
            update_details["description"] = True
            
        if "assigned_to" in updates:
            old_assignee = action["assigned_to"]
            action["assigned_to"] = updates["assigned_to"]
            update_details["assigned_to"] = {"old": old_assignee, "new": updates["assigned_to"]}
            
        if "priority" in updates:
            old_priority = action["priority"]
            action["priority"] = updates["priority"]
            update_details["priority"] = {"old": old_priority, "new": updates["priority"]}
            
        if "location" in updates:
            action["location"] = updates["location"]
            update_details["location"] = True
            
        if "notes" in updates:
            update_details["notes"] = updates["notes"]
            
        # Update timestamps
        action["updated"] = datetime.now()
        
        # Add action update
        action["updates"].append({
            "timestamp": datetime.now(),
            "changes": update_details,
            "source": updates.get("source", "system")
        })
        
        # Add to response plan updates
        response_plan["updates"].append({
            "timestamp": datetime.now(),
            "type": "response_action_updated",
            "details": {
                "action_id": action_id,
                "changes": update_details
            }
        })
        
        logger.info(f"Updated response action {action_id} for disaster {disaster_id}")
        
        # If assignee changed, notify new assignee
        if "assigned_to" in update_details:
            await self._notify_action_assignment(disaster_id, action)
            
        return True
    
    async def _create_initial_response_actions(self, disaster: Disaster) -> None:
        """
        Create initial response actions based on disaster type.
        
        Args:
            disaster: The disaster to create actions for
        """
        # This would be more sophisticated in a real implementation,
        # with actions tailored to the specific disaster
        
        # Common initial actions for all disasters
        common_actions = [
            {
                "action_type": "situation_assessment",
                "description": "Conduct initial situation assessment and damage survey",
                "assigned_to": "field_assessment_team",
                "priority": "urgent"
            },
            {
                "action_type": "coordination_activation",
                "description": "Activate emergency coordination center",
                "assigned_to": "emergency_manager",
                "priority": "urgent"
            },
            {
                "action_type": "public_notification",
                "description": "Issue public notification and safety instructions",
                "assigned_to": "public_affairs",
                "priority": "urgent"
            }
        ]
        
        # Add common actions
        for action in common_actions:
            await self.add_response_action(
                disaster_id=disaster.disaster_id,
                action_type=action["action_type"],
                description=action["description"],
                assigned_to=action["assigned_to"],
                priority=action["priority"]
            )
        
        # Add disaster-specific actions based on type
        disaster_specific_actions = _get_disaster_specific_actions(disaster)
        
        for action in disaster_specific_actions:
            await self.add_response_action(
                disaster_id=disaster.disaster_id,
                action_type=action["action_type"],
                description=action["description"],
                assigned_to=action["assigned_to"],
                priority=action["priority"]
            )
    
    async def _notify_coordination_partners(self, response_plan: Dict[str, Any]) -> None:
        """
        Notify coordination partners about emergency response activation.
        
        Args:
            response_plan: The activated response plan
        """
        # In a real implementation, this would send notifications via various channels
        logger.info(f"Notifying coordination partners for response {response_plan['response_id']}")
        
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
        
        # Send to all coordination partners
        partner_ids = list(response_plan["coordination_partners"].keys())
        
        # This would use the notification service to send to partners
        # For this example, we'll just log it
        logger.info(f"Emergency response activation notification sent to {len(partner_ids)} partners")
    
    async def _notify_escalation(self, 
                               response_plan: Dict[str, Any],
                               old_level: str,
                               new_level: str,
                               reason: str) -> None:
        """
        Notify about response escalation.
        
        Args:
            response_plan: The response plan
            old_level: Previous coordination level
            new_level: New coordination level
            reason: Reason for escalation
        """
        # Prepare notification message
        notification = {
            "title": f"Response Escalation: {response_plan['disaster_name']}",
            "message": (
                f"The emergency response for {response_plan['disaster_name']} has been escalated "
                f"from {old_level} to {new_level} level. "
                f"Reason: {reason}"
            ),
            "details": {
                "response_id": response_plan["response_id"],
                "disaster_id": response_plan["disaster_id"],
                "disaster_name": response_plan["disaster_name"],
                "old_level": old_level,
                "new_level": new_level,
                "reason": reason,
                "new_lead_agency": response_plan["lead_agency"]
            },
            "urgency_level": "emergency"
        }
        
        # Send to all coordination partners
        partner_ids = list(response_plan["coordination_partners"].keys())
        
        # This would use the notification service to send to partners
        # For this example, we'll just log it
        logger.info(f"Response escalation notification sent to {len(partner_ids)} partners")
    
    async def _notify_action_assignment(self, 
                                      disaster_id: str,
                                      action: Dict[str, Any]) -> None:
        """
        Notify assigned entity about a response action.
        
        Args:
            disaster_id: ID of the disaster
            action: The action that was assigned
        """
        response_plan = self.active_responses[disaster_id]
        
        # Prepare notification message
        notification = {
            "title": f"Response Action Assignment: {action['action_type']}",
            "message": (
                f"You have been assigned a response action for the {response_plan['disaster_name']} disaster. "
                f"Action: {action['description']}. "
                f"Priority: {action['priority']}."
            ),
            "details": {
                "response_id": response_plan["response_id"],
                "disaster_id": disaster_id,
                "disaster_name": response_plan["disaster_name"],
                "action_id": action["action_id"],
                "action_type": action["action_type"],
                "description": action["description"],
                "priority": action["priority"],
                "status": action["status"]
            },
            "urgency_level": _priority_to_urgency(action["priority"])
        }
        
        # Determine notification target
        target = action["assigned_to"]
        
        # This would use the notification service to send to the assigned entity
        # For this example, we'll just log it
        logger.info(f"Action assignment notification sent to {target} for action {action['action_id']}")
        
    async def deactivate_response(self, 
                                 disaster_id: str,
                                 reason: str) -> bool:
        """
        Deactivate an emergency response.
        
        Args:
            disaster_id: ID of the disaster
            reason: Reason for deactivation
            
        Returns:
            True if deactivation was successful, False otherwise
        """
        if disaster_id not in self.active_responses:
            logger.warning(f"Attempted to deactivate inactive response: {disaster_id}")
            return False
            
        response_plan = self.active_responses[disaster_id]
        
        # Update response status
        response_plan["status"] = "deactivated"
        response_plan["deactivation_time"] = datetime.now()
        response_plan["deactivation_reason"] = reason
        
        # Add to updates
        response_plan["updates"].append({
            "timestamp": datetime.now(),
            "type": "response_deactivation",
            "details": {
                "reason": reason
            }
        })
        
        # Return allocated resources
        for allocation_id, allocation in response_plan["resource_allocations"].items():
            resource_type = allocation["resource_type"]
            quantity = allocation["quantity"]
            
            # Update resource registry
            if resource_type in self.resource_registry:
                self.resource_registry[resource_type]["available"] += quantity
                self.resource_registry[resource_type]["allocated"] -= quantity
                
        logger.info(f"Deactivated emergency response for disaster {disaster_id}: {reason}")
        
        # Notify coordination partners
        await self._notify_deactivation(response_plan, reason)
        
        # Move to inactive responses (in a real implementation, this would archive to database)
        # self.inactive_responses[disaster_id] = response_plan
        # del self.active_responses[disaster_id]
        
        return True
        
    async def _notify_deactivation(self, 
                                 response_plan: Dict[str, Any],
                                 reason: str) -> None:
        """
        Notify about response deactivation.
        
        Args:
            response_plan: The response plan
            reason: Reason for deactivation
        """
        # Prepare notification message
        notification = {
            "title": f"Response Deactivation: {response_plan['disaster_name']}",
            "message": (
                f"The emergency response for {response_plan['disaster_name']} has been deactivated. "
                f"Reason: {reason}"
            ),
            "details": {
                "response_id": response_plan["response_id"],
                "disaster_id": response_plan["disaster_id"],
                "disaster_name": response_plan["disaster_name"],
                "reason": reason,
                "deactivation_time": datetime.now().isoformat()
            },
            "urgency_level": "advisory"
        }
        
        # Send to all coordination partners
        partner_ids = list(response_plan["coordination_partners"].keys())
        
        # This would use the notification service to send to partners
        # For this example, we'll just log it
        logger.info(f"Response deactivation notification sent to {len(partner_ids)} partners")


# Helper functions

def _determine_coordination_level(disaster: Disaster) -> str:
    """
    Determine the appropriate coordination level based on disaster characteristics.
    
    Args:
        disaster: Disaster object
        
    Returns:
        Coordination level (local, state, federal)
    """
    # Determine based on severity and type
    if disaster.severity == SeverityLevel.CATASTROPHIC:
        return "federal"
    elif disaster.severity == SeverityLevel.MAJOR:
        # Some major disasters require federal coordination immediately
        federal_immediate_types = [
            "hurricane", "earthquake", "tsunami", "volcanic_eruption",
            "radiological_incident", "terrorism", "pandemic"
        ]
        if disaster.type.value in federal_immediate_types:
            return "federal"
        else:
            return "state"
    elif disaster.severity == SeverityLevel.MODERATE:
        return "state"
    else:  # MINOR
        return "local"


def _determine_lead_agency(disaster: Disaster) -> str:
    """
    Determine the appropriate lead agency based on disaster characteristics.
    
    Args:
        disaster: Disaster object
        
    Returns:
        Lead agency name
    """
    # First determine coordination level
    level = _determine_coordination_level(disaster)
    
    # Then determine agency within that level
    return _determine_lead_agency_for_level(disaster.type.value, level)


def _determine_lead_agency_for_level(disaster_type: str, level: str) -> str:
    """
    Determine the appropriate lead agency for a given coordination level.
    
    Args:
        disaster_type: Type of disaster
        level: Coordination level
        
    Returns:
        Lead agency name
    """
    if level == "federal":
        # Federal level agencies based on disaster type
        lead_agencies = {
            "hurricane": "FEMA",
            "tornado": "FEMA",
            "flood": "FEMA",
            "wildfire": "USFS",
            "earthquake": "FEMA",
            "tsunami": "NOAA",
            "volcanic_eruption": "USGS",
            "winter_storm": "FEMA",
            "drought": "USDA",
            "extreme_heat": "HHS",
            "landslide": "USGS",
            "pandemic": "HHS",
            "chemical_spill": "EPA",
            "radiological_incident": "DOE",
            "terrorism": "DHS",
            "cyber_incident": "CISA",
            "dam_failure": "USACE",
            "power_outage": "DOE"
        }
        return lead_agencies.get(disaster_type, "FEMA")
    
    elif level == "state":
        return "STATE_EOC"
    
    else:  # local
        return "LOCAL_EOC"


def _identify_relevant_partners(disaster: Disaster, 
                              all_partners: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Identify relevant coordination partners based on disaster characteristics.
    
    Args:
        disaster: Disaster object
        all_partners: Dictionary of all potential partners
        
    Returns:
        Dictionary of relevant partners
    """
    level = _determine_coordination_level(disaster)
    
    # Get all partners for this level and below
    relevant_levels = []
    if level == "federal":
        relevant_levels = ["federal", "state", "local"]
    elif level == "state":
        relevant_levels = ["state", "local"]
    else:
        relevant_levels = ["local"]
        
    # Filter partners by level
    relevant_partners = {}
    for partner_id, partner in all_partners.items():
        if partner["level"] in relevant_levels:
            relevant_partners[partner_id] = partner
            
    return relevant_partners


def _identify_partners_for_level(level: str, 
                                all_partners: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Identify coordination partners for a specific level.
    
    Args:
        level: Coordination level
        all_partners: Dictionary of all potential partners
        
    Returns:
        Dictionary of partners for the specified level
    """
    # Filter partners by level
    level_partners = {}
    for partner_id, partner in all_partners.items():
        if partner["level"] == level:
            level_partners[partner_id] = partner
            
    return level_partners


def _simplify_impact_assessment(impact_assessment: Any) -> Dict[str, Any]:
    """
    Simplify impact assessment object for situation reports.
    
    Args:
        impact_assessment: Impact assessment object
        
    Returns:
        Simplified dictionary representation
    """
    # In a real implementation, this would convert the object to a serializable dict
    # For this example, we'll return a simple representation
    return {
        "casualties": getattr(impact_assessment, "casualties", {}),
        "displaced_persons": getattr(impact_assessment, "displaced_persons", 0),
        "structures_affected": getattr(impact_assessment, "structures_affected", {}),
        "confidence_level": getattr(impact_assessment, "confidence_level", 0.5)
    }


def _get_disaster_specific_actions(disaster: Disaster) -> List[Dict[str, Any]]:
    """
    Get disaster-specific response actions based on disaster type.
    
    Args:
        disaster: Disaster object
        
    Returns:
        List of disaster-specific actions
    """
    # Actions based on disaster type
    type_actions = {
        "hurricane": [
            {
                "action_type": "evacuation",
                "description": "Coordinate evacuation of vulnerable coastal areas",
                "assigned_to": "evacuation_coordinator",
                "priority": "urgent"
            },
            {
                "action_type": "shelter_activation",
                "description": "Activate emergency shelters in safe locations",
                "assigned_to": "shelter_coordinator",
                "priority": "urgent"
            }
        ],
        "flood": [
            {
                "action_type": "evacuation",
                "description": "Coordinate evacuation of flood-prone areas",
                "assigned_to": "evacuation_coordinator",
                "priority": "urgent"
            },
            {
                "action_type": "water_rescue",
                "description": "Deploy water rescue teams to affected areas",
                "assigned_to": "search_rescue_coordinator",
                "priority": "urgent"
            }
        ],
        "wildfire": [
            {
                "action_type": "evacuation",
                "description": "Coordinate evacuation of threatened areas",
                "assigned_to": "evacuation_coordinator",
                "priority": "urgent"
            },
            {
                "action_type": "firefighting",
                "description": "Coordinate firefighting resources and strategies",
                "assigned_to": "firefighting_coordinator",
                "priority": "urgent"
            }
        ],
        "earthquake": [
            {
                "action_type": "search_rescue",
                "description": "Deploy urban search and rescue teams",
                "assigned_to": "search_rescue_coordinator",
                "priority": "urgent"
            },
            {
                "action_type": "structural_assessment",
                "description": "Conduct rapid structural assessments of critical infrastructure",
                "assigned_to": "structural_assessment_team",
                "priority": "urgent"
            }
        ],
        "pandemic": [
            {
                "action_type": "medical_surge",
                "description": "Activate medical surge capacity in healthcare facilities",
                "assigned_to": "health_coordinator",
                "priority": "urgent"
            },
            {
                "action_type": "public_health_guidance",
                "description": "Issue public health guidance and preventive measures",
                "assigned_to": "public_health_officer",
                "priority": "urgent"
            }
        ]
    }
    
    # Get actions for this disaster type, or return generic actions if type not found
    return type_actions.get(disaster.type.value, [
        {
            "action_type": "impact_assessment",
            "description": "Assess impact and identify immediate needs",
            "assigned_to": "assessment_coordinator",
            "priority": "high"
        },
        {
            "action_type": "resource_mobilization",
            "description": "Mobilize appropriate resources based on disaster type",
            "assigned_to": "resource_manager",
            "priority": "high"
        }
    ])


def _priority_to_urgency(priority: str) -> str:
    """
    Convert priority level to urgency level for notifications.
    
    Args:
        priority: Priority level
        
    Returns:
        Urgency level
    """
    # Map priority to urgency
    priority_map = {
        "low": "advisory",
        "normal": "watch",
        "high": "warning",
        "urgent": "emergency"
    }
    return priority_map.get(priority, "advisory")