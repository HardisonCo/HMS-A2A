"""
Contact Tracing Service for the CDC implementation.

This service provides functionality for contact tracing, including
contact identification, monitoring, follow-up, and visualization.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import date, datetime, timedelta
import logging
import uuid
import json
import networkx as nx

from agency_implementation.cdc.models.human_disease import (
    Contact, HumanDiseaseCase, RiskLevel
)
from agency_implementation.cdc.models.base import GeoLocation
from .repository import ContactRepository
from .adapters import NotificationAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContactTracingService:
    """
    Service for contact tracing.
    
    This service provides functionality for:
    1. Contact registration and management
    2. Risk assessment and prioritization
    3. Contact monitoring
    4. Notifications and follow-up
    5. Visualization and analysis
    """
    
    def __init__(
        self,
        repository: ContactRepository,
        notification_adapter: Optional[NotificationAdapter] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the service.
        
        Args:
            repository: Repository for contacts
            notification_adapter: Adapter for sending notifications
            config: Service configuration
        """
        self.repository = repository
        self.notification_adapter = notification_adapter
        self.config = config or {}
        
        # Default monitoring period in days
        self.monitoring_period = self.config.get('monitoring_period', 14)
        
        # Risk assessment configuration
        self.risk_factors = self.config.get('risk_factors', {
            'exposure_duration': {
                'threshold': 15,  # minutes
                'weight': 2.0
            },
            'distance': {
                'threshold': 6,  # feet/meters
                'weight': 1.5
            },
            'location': {
                'indoor': 2.0,
                'outdoor': 1.0
            },
            'mask_usage': {
                'none': 2.0,
                'case_only': 1.5,
                'contact_only': 1.5,
                'both': 1.0
            }
        })
        
        # Auto-notification configuration
        self.auto_notify = self.config.get('auto_notify', False)
        
        logger.info("ContactTracingService initialized")
    
    def get_contact(self, contact_id: str) -> Optional[Contact]:
        """
        Get a contact by ID.
        
        Args:
            contact_id: The ID of the contact to retrieve
            
        Returns:
            The contact if found, None otherwise
        """
        return self.repository.get_by_id(contact_id)
    
    def get_all_contacts(self) -> List[Contact]:
        """
        Get all contacts.
        
        Returns:
            List of all contacts
        """
        return self.repository.get_all()
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Contact:
        """
        Create a new contact.
        
        Args:
            contact_data: Dictionary with contact data
            
        Returns:
            The created contact
            
        Raises:
            ValueError: If contact data is invalid
        """
        # Validate required fields
        required_fields = ['person_id', 'case_id', 'contact_date', 'location', 'contact_type']
        for field in required_fields:
            if field not in contact_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Calculate risk assessment if not provided
        if 'risk_assessment' not in contact_data and 'risk_factors' in contact_data:
            risk_level = self._calculate_risk_level(contact_data['risk_factors'])
            contact_data['risk_assessment'] = risk_level
        
        # Create the contact
        contact = Contact(**contact_data)
        
        # Save the contact
        created_contact = self.repository.create(contact)
        
        logger.info(f"Created new contact with ID: {created_contact.id}")
        
        # Send initial notification if configured
        if self.auto_notify and self.notification_adapter:
            self.notification_adapter.notify_monitoring_instructions(created_contact)
        
        return created_contact
    
    def update_contact(self, contact_id: str, updates: Dict[str, Any]) -> Optional[Contact]:
        """
        Update an existing contact.
        
        Args:
            contact_id: ID of the contact to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated contact or None if contact not found
            
        Raises:
            ValueError: If updates are invalid
        """
        # Get the contact
        contact = self.repository.get_by_id(contact_id)
        if not contact:
            logger.warning(f"Contact not found for update: {contact_id}")
            return None
        
        # Update the contact
        for key, value in updates.items():
            setattr(contact, key, value)
            
        # Update timestamp
        contact.updated_at = datetime.now().isoformat()
        
        # Save the updated contact
        updated_contact = self.repository.update(contact)
        
        logger.info(f"Updated contact with ID: {contact_id}")
        return updated_contact
    
    def find_contacts(self, criteria: Dict[str, Any]) -> List[Contact]:
        """
        Find contacts matching criteria.
        
        Args:
            criteria: Dictionary of field-value pairs to match
            
        Returns:
            List of matching contacts
        """
        return self.repository.find(criteria)
    
    def find_contacts_by_case(self, case_id: str) -> List[Contact]:
        """
        Find contacts associated with a case.
        
        Args:
            case_id: The case ID to filter by
            
        Returns:
            List of contacts associated with the case
        """
        return self.repository.find_by_case_id(case_id)
    
    def find_contacts_by_person(self, person_id: str) -> List[Contact]:
        """
        Find contacts by person ID.
        
        Args:
            person_id: The person ID to filter by
            
        Returns:
            List of contacts for the person
        """
        return self.repository.find_by_person_id(person_id)
    
    def find_contacts_by_risk_level(self, risk_level: Union[RiskLevel, str]) -> List[Contact]:
        """
        Find contacts by risk level.
        
        Args:
            risk_level: The risk level to filter by
            
        Returns:
            List of contacts with the specified risk level
        """
        return self.repository.find_by_risk_level(risk_level)
    
    def find_active_monitoring(self) -> List[Contact]:
        """
        Find contacts under active monitoring.
        
        Returns:
            List of contacts under active monitoring
        """
        return self.repository.find_active_monitoring()
    
    def register_contacts_from_case(self, case: HumanDiseaseCase, contacts_data: List[Dict[str, Any]]) -> List[Contact]:
        """
        Register multiple contacts associated with a case.
        
        Args:
            case: The case these contacts are associated with
            contacts_data: List of dictionaries with contact data
            
        Returns:
            List of created contacts
        """
        created_contacts = []
        
        for contact_data in contacts_data:
            # Add case ID if not provided
            if 'case_id' not in contact_data:
                contact_data['case_id'] = case.id
            
            try:
                # Create contact
                contact = self.create_contact(contact_data)
                created_contacts.append(contact)
            except Exception as e:
                logger.error(f"Error creating contact: {str(e)}")
        
        logger.info(f"Registered {len(created_contacts)} contacts for case {case.id}")
        return created_contacts
    
    def update_monitoring_status(self, contact_id: str, status: str) -> Optional[Contact]:
        """
        Update the monitoring status of a contact.
        
        Args:
            contact_id: ID of the contact to update
            status: New monitoring status
            
        Returns:
            The updated contact or None if contact not found
        """
        # Get the contact
        contact = self.repository.get_by_id(contact_id)
        if not contact:
            logger.warning(f"Contact not found for status update: {contact_id}")
            return None
        
        # Update status
        contact.update_monitoring_status(status)
        
        # Save the updated contact
        updated_contact = self.repository.update(contact)
        
        logger.info(f"Updated monitoring status to {status} for contact {contact_id}")
        return updated_contact
    
    def update_isolation_status(self, contact_id: str, status: str) -> Optional[Contact]:
        """
        Update the isolation status of a contact.
        
        Args:
            contact_id: ID of the contact to update
            status: New isolation status
            
        Returns:
            The updated contact or None if contact not found
        """
        # Get the contact
        contact = self.repository.get_by_id(contact_id)
        if not contact:
            logger.warning(f"Contact not found for isolation update: {contact_id}")
            return None
        
        # Update status
        contact.update_isolation_status(status)
        
        # Save the updated contact
        updated_contact = self.repository.update(contact)
        
        logger.info(f"Updated isolation status to {status} for contact {contact_id}")
        
        # Send isolation instructions if status is 'isolated'
        if status == 'isolated' and self.notification_adapter:
            self.notification_adapter.notify_isolation_instructions(updated_contact)
        
        return updated_contact
    
    def add_test_result(self, contact_id: str, result: Dict[str, Any]) -> Optional[Contact]:
        """
        Add a test result for a contact.
        
        Args:
            contact_id: ID of the contact
            result: Test result data
            
        Returns:
            The updated contact or None if contact not found
        """
        # Get the contact
        contact = self.repository.get_by_id(contact_id)
        if not contact:
            logger.warning(f"Contact not found for adding test result: {contact_id}")
            return None
        
        # Add test result
        contact.add_test_result(result)
        
        # Save the updated contact
        updated_contact = self.repository.update(contact)
        
        logger.info(f"Added test result for contact {contact_id}")
        return updated_contact
    
    def add_symptoms(self, contact_id: str, symptoms: List[str]) -> Optional[Contact]:
        """
        Add symptoms for a contact.
        
        Args:
            contact_id: ID of the contact
            symptoms: List of symptoms
            
        Returns:
            The updated contact or None if contact not found
        """
        # Get the contact
        contact = self.repository.get_by_id(contact_id)
        if not contact:
            logger.warning(f"Contact not found for adding symptoms: {contact_id}")
            return None
        
        # Add symptoms
        contact.add_symptoms(symptoms)
        
        # Save the updated contact
        updated_contact = self.repository.update(contact)
        
        logger.info(f"Added symptoms for contact {contact_id}")
        return updated_contact
    
    def recommend_testing(self, contact_id: str, test_location: str, test_date: str) -> bool:
        """
        Recommend testing for a contact and send notification.
        
        Args:
            contact_id: ID of the contact
            test_location: Location for testing
            test_date: Recommended test date
            
        Returns:
            True if successful, False otherwise
        """
        # Check if notification adapter is available
        if not self.notification_adapter:
            logger.warning("Cannot recommend testing: notification adapter not configured")
            return False
        
        # Get the contact
        contact = self.repository.get_by_id(contact_id)
        if not contact:
            logger.warning(f"Contact not found for test recommendation: {contact_id}")
            return False
        
        # Send notification
        success = self.notification_adapter.notify_test_recommendation(contact, test_location, test_date)
        
        if success:
            # Update contact record
            if not hasattr(contact, 'test_recommendations'):
                contact.test_recommendations = []
            
            contact.test_recommendations.append({
                'date': datetime.now().isoformat(),
                'test_location': test_location,
                'test_date': test_date
            })
            
            self.repository.update(contact)
            logger.info(f"Test recommendation sent to contact {contact_id}")
        
        return success
    
    def bulk_recommend_testing(self, contact_ids: List[str], test_location: str, test_date: str) -> Dict[str, bool]:
        """
        Recommend testing for multiple contacts.
        
        Args:
            contact_ids: List of contact IDs
            test_location: Location for testing
            test_date: Recommended test date
            
        Returns:
            Dictionary mapping contact IDs to success status
        """
        results = {}
        
        for contact_id in contact_ids:
            success = self.recommend_testing(contact_id, test_location, test_date)
            results[contact_id] = success
        
        return results
    
    def prioritize_contacts(self, case_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Prioritize contacts for follow-up based on risk level and other factors.
        
        Args:
            case_ids: Optional list of case IDs to filter by
            
        Returns:
            List of contacts with priority scoring
        """
        # Get contacts to prioritize
        if case_ids:
            contacts = []
            for case_id in case_ids:
                contacts.extend(self.repository.find_by_case_id(case_id))
        else:
            contacts = self.repository.get_all()
        
        # Skip contacts that are not under active monitoring
        contacts = [c for c in contacts if hasattr(c, 'monitoring_status') and c.monitoring_status != 'completed']
        
        prioritized = []
        
        for contact in contacts:
            # Calculate priority score based on risk level and other factors
            priority_score = 0
            
            # Risk level contribution
            if hasattr(contact, 'risk_assessment'):
                risk_level = contact.risk_assessment
                if risk_level == RiskLevel.HIGH:
                    priority_score += 10
                elif risk_level == RiskLevel.MEDIUM:
                    priority_score += 5
                elif risk_level == RiskLevel.LOW:
                    priority_score += 2
            
            # Days since contact contribution
            days_since_contact = contact.calculate_days_since_contact()
            if days_since_contact is not None:
                if days_since_contact <= 2:
                    priority_score += 5  # Very recent contact, high priority
                elif days_since_contact <= 7:
                    priority_score += 3  # Recent contact, medium priority
                elif days_since_contact <= 14:
                    priority_score += 1  # Older contact, low priority
            
            # Presence of symptoms contribution
            has_symptoms = hasattr(contact, 'symptoms') and contact.symptoms
            if has_symptoms:
                priority_score += 8  # Symptomatic contacts are high priority
            
            # Add to prioritized list
            prioritized.append({
                'contact': contact,
                'priority_score': priority_score,
                'days_since_contact': days_since_contact,
                'has_symptoms': has_symptoms
            })
        
        # Sort by priority score, descending
        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return prioritized
    
    def generate_monitoring_report(self, days: int = 14) -> Dict[str, Any]:
        """
        Generate a report of contact monitoring activities.
        
        Args:
            days: Number of days to include in the report
            
        Returns:
            Dictionary with monitoring report data
        """
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get contacts in date range
        contacts = self.repository.find_by_date_range(start_date, end_date)
        
        # Count by risk level
        risk_counts = self.repository.count_by_risk_level()
        
        # Count by monitoring status
        monitoring_counts = self.repository.count_by_monitoring_status()
        
        # Count active monitoring
        active_monitoring = len(self.repository.find_active_monitoring())
        
        # Calculate monitoring compliance rate (if we had actual monitoring data)
        # For demonstration, use a mock value
        monitoring_compliance = 0.85
        
        # Count contacts with symptoms
        symptomatic_contacts = sum(1 for c in contacts if hasattr(c, 'symptoms') and c.symptoms)
        
        # Count contacts with positive test results
        positive_tests = 0
        for c in contacts:
            if hasattr(c, 'test_results') and c.test_results:
                for test in c.test_results:
                    if test.get('result') == 'positive':
                        positive_tests += 1
                        break
        
        return {
            'time_period': f"{start_date.isoformat()} to {end_date.isoformat()}",
            'total_contacts': len(contacts),
            'by_risk_level': risk_counts,
            'by_monitoring_status': monitoring_counts,
            'active_monitoring': active_monitoring,
            'monitoring_compliance': monitoring_compliance,
            'symptomatic_contacts': symptomatic_contacts,
            'positive_tests': positive_tests,
            'generated_at': datetime.now().isoformat()
        }
    
    def construct_transmission_network(self, case_ids: List[str]) -> Dict[str, Any]:
        """
        Construct a transmission network from cases and their contacts.
        
        Args:
            case_ids: List of case IDs to include in the network
            
        Returns:
            Dictionary with network information
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add nodes and edges for each case and its contacts
        for case_id in case_ids:
            # Add case node
            G.add_node(case_id, type='case')
            
            # Get contacts for this case
            contacts = self.repository.find_by_case_id(case_id)
            
            for contact in contacts:
                # Add contact node
                G.add_node(contact.person_id, type='contact')
                
                # Add edge from case to contact
                G.add_edge(case_id, contact.person_id, contact_date=contact.contact_date)
                
                # If contact has become a case, add that relationship too
                if contact.person_id in case_ids:
                    G.add_edge(contact.person_id, case_id, contact_type='exposure')
        
        # Extract network statistics
        node_count = G.number_of_nodes()
        edge_count = G.number_of_edges()
        
        # Find nodes with the most connections
        degree_centrality = nx.degree_centrality(G)
        top_centrality = {node: score for node, score in sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]}
        
        # Find potential superspreaders (nodes with high out-degree)
        out_degrees = dict(G.out_degree())
        potential_superspreaders = {node: degree for node, degree in sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:5]}
        
        # Get network as adjacency list for visualization
        network_data = {
            'nodes': [{'id': node, 'type': data['type']} for node, data in G.nodes(data=True)],
            'edges': [{'source': u, 'target': v, 'date': data.get('contact_date')} for u, v, data in G.edges(data=True)]
        }
        
        return {
            'network_data': network_data,
            'statistics': {
                'node_count': node_count,
                'edge_count': edge_count,
                'average_connections': edge_count / node_count if node_count > 0 else 0,
                'top_centrality': top_centrality,
                'potential_superspreaders': potential_superspreaders
            }
        }
    
    def _calculate_risk_level(self, risk_factors: Dict[str, Any]) -> RiskLevel:
        """
        Calculate risk level based on risk factors.
        
        Args:
            risk_factors: Dictionary of risk factors
            
        Returns:
            Risk level assessment
        """
        risk_score = 0.0
        
        # Exposure duration
        if 'exposure_duration' in risk_factors:
            duration = risk_factors['exposure_duration']
            threshold = self.risk_factors['exposure_duration']['threshold']
            weight = self.risk_factors['exposure_duration']['weight']
            
            if duration >= threshold:
                risk_score += weight
        
        # Distance
        if 'distance' in risk_factors:
            distance = risk_factors['distance']
            threshold = self.risk_factors['distance']['threshold']
            weight = self.risk_factors['distance']['weight']
            
            if distance <= threshold:
                risk_score += weight
        
        # Location type
        if 'location_type' in risk_factors:
            location_type = risk_factors['location_type']
            weight = self.risk_factors['location'].get(location_type, 1.0)
            risk_score += weight
        
        # Mask usage
        if 'mask_usage' in risk_factors:
            mask_usage = risk_factors['mask_usage']
            weight = self.risk_factors['mask_usage'].get(mask_usage, 1.0)
            risk_score += weight
        
        # Determine risk level based on score
        if risk_score >= 5.0:
            return RiskLevel.HIGH
        elif risk_score >= 3.0:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW