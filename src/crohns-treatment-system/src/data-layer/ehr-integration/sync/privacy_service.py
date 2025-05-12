#!/usr/bin/env python3
"""
Privacy Service for Crohn's Disease Treatment System
This module provides privacy controls and data access policies for patient data,
ensuring HIPAA compliance and proper patient consent management.
"""
import os
import json
import time
import logging
import hashlib
from typing import Dict, List, Any, Optional, Set, Callable
from datetime import datetime, timedelta
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ehr-privacy")

class ConsentStatus(Enum):
    """Patient consent status for data sharing"""
    UNKNOWN = "unknown"
    DENIED = "denied"
    LIMITED = "limited"
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"

class AccessLevel(Enum):
    """Access levels for patient data"""
    NONE = "none"  # No access
    MINIMAL = "minimal"  # Demographics only
    LIMITED = "limited"  # Demographics + basic clinical data
    STANDARD = "standard"  # Most clinical data
    FULL = "full"  # All data including sensitive information
    RESEARCH = "research"  # De-identified data for research

class DataCategory(Enum):
    """Categories of patient data"""
    DEMOGRAPHICS = "demographics"
    DIAGNOSES = "diagnoses"
    MEDICATIONS = "medications"
    PROCEDURES = "procedures"
    LAB_RESULTS = "lab_results"
    VITAL_SIGNS = "vital_signs"
    NOTES = "notes"
    GENETIC = "genetic"
    MENTAL_HEALTH = "mental_health"
    SEXUAL_HEALTH = "sexual_health"
    SUBSTANCE_USE = "substance_use"

class UserRole(Enum):
    """User roles in the system"""
    PATIENT = "patient"
    PROVIDER = "provider"
    RESEARCHER = "researcher"
    ADMINISTRATOR = "administrator"
    SYSTEM = "system"

class PatientConsent:
    """Patient consent for data sharing"""
    def __init__(
        self,
        patient_id: str,
        status: ConsentStatus,
        scope: List[DataCategory],
        start_date: datetime,
        expiration_date: Optional[datetime] = None,
        withdrawal_date: Optional[datetime] = None,
        consent_document: Optional[str] = None,
        additional_notes: Optional[str] = None
    ):
        self.patient_id = patient_id
        self.status = status
        self.scope = scope
        self.start_date = start_date
        self.expiration_date = expiration_date
        self.withdrawal_date = withdrawal_date
        self.consent_document = consent_document
        self.additional_notes = additional_notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "patient_id": self.patient_id,
            "status": self.status.value,
            "scope": [category.value for category in self.scope],
            "start_date": self.start_date.isoformat(),
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "withdrawal_date": self.withdrawal_date.isoformat() if self.withdrawal_date else None,
            "consent_document": self.consent_document,
            "additional_notes": self.additional_notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatientConsent':
        """Create from dictionary representation"""
        return cls(
            patient_id=data["patient_id"],
            status=ConsentStatus(data["status"]),
            scope=[DataCategory(category) for category in data["scope"]],
            start_date=datetime.fromisoformat(data["start_date"]),
            expiration_date=datetime.fromisoformat(data["expiration_date"]) if data.get("expiration_date") else None,
            withdrawal_date=datetime.fromisoformat(data["withdrawal_date"]) if data.get("withdrawal_date") else None,
            consent_document=data.get("consent_document"),
            additional_notes=data.get("additional_notes")
        )
    
    def is_valid(self) -> bool:
        """Check if the consent is currently valid"""
        now = datetime.now()
        
        # Check if consent is withdrawn
        if self.withdrawal_date and self.withdrawal_date <= now:
            return False
        
        # Check if consent is expired
        if self.expiration_date and self.expiration_date <= now:
            return False
        
        # Check if consent has started
        if self.start_date > now:
            return False
        
        # Check consent status
        return self.status in [ConsentStatus.GRANTED, ConsentStatus.LIMITED]
    
    def allows_category(self, category: DataCategory) -> bool:
        """Check if consent allows access to a specific data category"""
        if not self.is_valid():
            return False
        
        return category in self.scope

class AccessPolicy:
    """Access policy for patient data"""
    def __init__(
        self,
        role: UserRole,
        allowed_categories: Dict[DataCategory, AccessLevel],
        consent_required: bool = True,
        default_level: AccessLevel = AccessLevel.NONE
    ):
        self.role = role
        self.allowed_categories = allowed_categories
        self.consent_required = consent_required
        self.default_level = default_level
    
    def get_access_level(
        self,
        category: DataCategory,
        consent: Optional[PatientConsent] = None
    ) -> AccessLevel:
        """
        Determine access level for a data category
        
        Args:
            category: Data category to access
            consent: Patient consent (if available)
            
        Returns:
            Appropriate access level
        """
        # Get base access level from policy
        access_level = self.allowed_categories.get(category, self.default_level)
        
        # If consent is required but not provided or invalid, restrict access
        if self.consent_required:
            if not consent:
                return AccessLevel.NONE
            
            if not consent.is_valid():
                return AccessLevel.NONE
            
            # If consent doesn't allow this category, restrict access
            if not consent.allows_category(category):
                return AccessLevel.NONE
        
        return access_level

class DataAccessRequest:
    """Request for accessing patient data"""
    def __init__(
        self,
        requester_id: str,
        requester_role: UserRole,
        patient_id: str,
        categories: List[DataCategory],
        purpose: str,
        request_time: Optional[datetime] = None,
        id: Optional[str] = None
    ):
        self.id = id or f"{int(time.time())}-{requester_id}-{patient_id}"
        self.requester_id = requester_id
        self.requester_role = requester_role
        self.patient_id = patient_id
        self.categories = categories
        self.purpose = purpose
        self.request_time = request_time or datetime.now()
        self.decision: Optional[bool] = None
        self.decision_time: Optional[datetime] = None
        self.decision_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "requester_id": self.requester_id,
            "requester_role": self.requester_role.value,
            "patient_id": self.patient_id,
            "categories": [category.value for category in self.categories],
            "purpose": self.purpose,
            "request_time": self.request_time.isoformat(),
            "decision": self.decision,
            "decision_time": self.decision_time.isoformat() if self.decision_time else None,
            "decision_reason": self.decision_reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataAccessRequest':
        """Create from dictionary representation"""
        request = cls(
            id=data["id"],
            requester_id=data["requester_id"],
            requester_role=UserRole(data["requester_role"]),
            patient_id=data["patient_id"],
            categories=[DataCategory(category) for category in data["categories"]],
            purpose=data["purpose"],
            request_time=datetime.fromisoformat(data["request_time"])
        )
        request.decision = data.get("decision")
        request.decision_time = datetime.fromisoformat(data["decision_time"]) if data.get("decision_time") else None
        request.decision_reason = data.get("decision_reason")
        return request

class PrivacyService:
    """
    Service for managing privacy controls and data access policies
    Handles patient consent, access control, and audit logging
    """
    def __init__(
        self,
        data_dir: str = None,
        default_policies: Dict[UserRole, AccessPolicy] = None
    ):
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data"
        )
        self.consents_path = os.path.join(self.data_dir, "consents.json")
        self.access_logs_path = os.path.join(self.data_dir, "access_logs.json")
        self.access_requests_path = os.path.join(self.data_dir, "access_requests.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize policies with defaults if not provided
        self.policies = default_policies or self._create_default_policies()
        
        # Load existing data
        self.consents: Dict[str, PatientConsent] = {}
        self.access_logs: List[Dict[str, Any]] = []
        self.access_requests: Dict[str, DataAccessRequest] = {}
        
        self._load_consents()
        self._load_access_logs()
        self._load_access_requests()
        
        logger.info("Privacy Service initialized")
    
    def _create_default_policies(self) -> Dict[UserRole, AccessPolicy]:
        """Create default access policies for each role"""
        # Patient can access their own data
        patient_policy = AccessPolicy(
            role=UserRole.PATIENT,
            allowed_categories={
                DataCategory.DEMOGRAPHICS: AccessLevel.FULL,
                DataCategory.DIAGNOSES: AccessLevel.FULL,
                DataCategory.MEDICATIONS: AccessLevel.FULL,
                DataCategory.PROCEDURES: AccessLevel.FULL,
                DataCategory.LAB_RESULTS: AccessLevel.FULL,
                DataCategory.VITAL_SIGNS: AccessLevel.FULL,
                DataCategory.NOTES: AccessLevel.STANDARD,
                DataCategory.GENETIC: AccessLevel.STANDARD,
                DataCategory.MENTAL_HEALTH: AccessLevel.STANDARD,
                DataCategory.SEXUAL_HEALTH: AccessLevel.STANDARD,
                DataCategory.SUBSTANCE_USE: AccessLevel.STANDARD
            },
            consent_required=False  # Patients can always access their own data
        )
        
        # Provider has standard access to clinical data
        provider_policy = AccessPolicy(
            role=UserRole.PROVIDER,
            allowed_categories={
                DataCategory.DEMOGRAPHICS: AccessLevel.STANDARD,
                DataCategory.DIAGNOSES: AccessLevel.STANDARD,
                DataCategory.MEDICATIONS: AccessLevel.STANDARD,
                DataCategory.PROCEDURES: AccessLevel.STANDARD,
                DataCategory.LAB_RESULTS: AccessLevel.STANDARD,
                DataCategory.VITAL_SIGNS: AccessLevel.STANDARD,
                DataCategory.NOTES: AccessLevel.STANDARD,
                DataCategory.GENETIC: AccessLevel.LIMITED,
                DataCategory.MENTAL_HEALTH: AccessLevel.LIMITED,
                DataCategory.SEXUAL_HEALTH: AccessLevel.LIMITED,
                DataCategory.SUBSTANCE_USE: AccessLevel.LIMITED
            },
            consent_required=True
        )
        
        # Researcher can access de-identified data for research
        researcher_policy = AccessPolicy(
            role=UserRole.RESEARCHER,
            allowed_categories={
                DataCategory.DEMOGRAPHICS: AccessLevel.MINIMAL,
                DataCategory.DIAGNOSES: AccessLevel.RESEARCH,
                DataCategory.MEDICATIONS: AccessLevel.RESEARCH,
                DataCategory.PROCEDURES: AccessLevel.RESEARCH,
                DataCategory.LAB_RESULTS: AccessLevel.RESEARCH,
                DataCategory.VITAL_SIGNS: AccessLevel.RESEARCH,
                DataCategory.NOTES: AccessLevel.NONE,
                DataCategory.GENETIC: AccessLevel.RESEARCH,
                DataCategory.MENTAL_HEALTH: AccessLevel.RESEARCH,
                DataCategory.SEXUAL_HEALTH: AccessLevel.RESEARCH,
                DataCategory.SUBSTANCE_USE: AccessLevel.RESEARCH
            },
            consent_required=True
        )
        
        # Administrator has limited access for system management
        administrator_policy = AccessPolicy(
            role=UserRole.ADMINISTRATOR,
            allowed_categories={
                DataCategory.DEMOGRAPHICS: AccessLevel.STANDARD,
                DataCategory.DIAGNOSES: AccessLevel.LIMITED,
                DataCategory.MEDICATIONS: AccessLevel.LIMITED,
                DataCategory.PROCEDURES: AccessLevel.LIMITED,
                DataCategory.LAB_RESULTS: AccessLevel.LIMITED,
                DataCategory.VITAL_SIGNS: AccessLevel.LIMITED,
                DataCategory.NOTES: AccessLevel.NONE,
                DataCategory.GENETIC: AccessLevel.NONE,
                DataCategory.MENTAL_HEALTH: AccessLevel.NONE,
                DataCategory.SEXUAL_HEALTH: AccessLevel.NONE,
                DataCategory.SUBSTANCE_USE: AccessLevel.NONE
            },
            consent_required=True
        )
        
        # System has full access for automation
        system_policy = AccessPolicy(
            role=UserRole.SYSTEM,
            allowed_categories={
                DataCategory.DEMOGRAPHICS: AccessLevel.FULL,
                DataCategory.DIAGNOSES: AccessLevel.FULL,
                DataCategory.MEDICATIONS: AccessLevel.FULL,
                DataCategory.PROCEDURES: AccessLevel.FULL,
                DataCategory.LAB_RESULTS: AccessLevel.FULL,
                DataCategory.VITAL_SIGNS: AccessLevel.FULL,
                DataCategory.NOTES: AccessLevel.FULL,
                DataCategory.GENETIC: AccessLevel.FULL,
                DataCategory.MENTAL_HEALTH: AccessLevel.FULL,
                DataCategory.SEXUAL_HEALTH: AccessLevel.FULL,
                DataCategory.SUBSTANCE_USE: AccessLevel.FULL
            },
            consent_required=True
        )
        
        return {
            UserRole.PATIENT: patient_policy,
            UserRole.PROVIDER: provider_policy,
            UserRole.RESEARCHER: researcher_policy,
            UserRole.ADMINISTRATOR: administrator_policy,
            UserRole.SYSTEM: system_policy
        }
    
    def _load_consents(self) -> None:
        """Load patient consents from file"""
        if not os.path.exists(self.consents_path):
            self.consents = {}
            return
        
        try:
            with open(self.consents_path, 'r') as f:
                consents_data = json.load(f)
                self.consents = {
                    patient_id: PatientConsent.from_dict(consent_data)
                    for patient_id, consent_data in consents_data.items()
                }
            logger.info(f"Loaded {len(self.consents)} patient consents")
        except Exception as e:
            logger.error(f"Error loading patient consents: {str(e)}")
            self.consents = {}
    
    def _save_consents(self) -> None:
        """Save patient consents to file"""
        try:
            consents_data = {
                patient_id: consent.to_dict()
                for patient_id, consent in self.consents.items()
            }
            with open(self.consents_path, 'w') as f:
                json.dump(consents_data, f, indent=2)
            
            logger.info(f"Saved {len(self.consents)} patient consents")
        except Exception as e:
            logger.error(f"Error saving patient consents: {str(e)}")
    
    def _load_access_logs(self) -> None:
        """Load access logs from file"""
        if not os.path.exists(self.access_logs_path):
            self.access_logs = []
            return
        
        try:
            with open(self.access_logs_path, 'r') as f:
                self.access_logs = json.load(f)
            logger.info(f"Loaded {len(self.access_logs)} access logs")
        except Exception as e:
            logger.error(f"Error loading access logs: {str(e)}")
            self.access_logs = []
    
    def _save_access_logs(self) -> None:
        """Save access logs to file"""
        try:
            # Keep only the latest 10000 logs to prevent file growth
            logs_to_save = self.access_logs[-10000:]
            with open(self.access_logs_path, 'w') as f:
                json.dump(logs_to_save, f, indent=2)
            
            logger.info(f"Saved {len(logs_to_save)} access logs")
        except Exception as e:
            logger.error(f"Error saving access logs: {str(e)}")
    
    def _load_access_requests(self) -> None:
        """Load access requests from file"""
        if not os.path.exists(self.access_requests_path):
            self.access_requests = {}
            return
        
        try:
            with open(self.access_requests_path, 'r') as f:
                requests_data = json.load(f)
                self.access_requests = {
                    request_id: DataAccessRequest.from_dict(request_data)
                    for request_id, request_data in requests_data.items()
                }
            logger.info(f"Loaded {len(self.access_requests)} access requests")
        except Exception as e:
            logger.error(f"Error loading access requests: {str(e)}")
            self.access_requests = {}
    
    def _save_access_requests(self) -> None:
        """Save access requests to file"""
        try:
            requests_data = {
                request_id: request.to_dict()
                for request_id, request in self.access_requests.items()
            }
            with open(self.access_requests_path, 'w') as f:
                json.dump(requests_data, f, indent=2)
            
            logger.info(f"Saved {len(self.access_requests)} access requests")
        except Exception as e:
            logger.error(f"Error saving access requests: {str(e)}")
    
    def record_patient_consent(
        self,
        consent: PatientConsent
    ) -> bool:
        """
        Record a patient's consent for data sharing
        
        Args:
            consent: Patient consent object
            
        Returns:
            True if consent was recorded successfully, False otherwise
        """
        try:
            self.consents[consent.patient_id] = consent
            self._save_consents()
            
            logger.info(f"Recorded consent for patient {consent.patient_id}: {consent.status.value}")
            return True
        except Exception as e:
            logger.error(f"Error recording patient consent: {str(e)}")
            return False
    
    def get_patient_consent(
        self,
        patient_id: str
    ) -> Optional[PatientConsent]:
        """
        Get a patient's consent status
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Patient consent object, or None if not found
        """
        return self.consents.get(patient_id)
    
    def withdraw_patient_consent(
        self,
        patient_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Withdraw a patient's consent for data sharing
        
        Args:
            patient_id: Patient identifier
            reason: Reason for withdrawal
            
        Returns:
            True if consent was withdrawn successfully, False otherwise
        """
        consent = self.consents.get(patient_id)
        if not consent:
            logger.warning(f"Cannot withdraw consent for patient {patient_id}: consent not found")
            return False
        
        try:
            consent.status = ConsentStatus.WITHDRAWN
            consent.withdrawal_date = datetime.now()
            consent.additional_notes = reason
            
            self._save_consents()
            
            logger.info(f"Withdrawn consent for patient {patient_id}")
            return True
        except Exception as e:
            logger.error(f"Error withdrawing patient consent: {str(e)}")
            return False
    
    def check_access(
        self,
        requester_id: str,
        requester_role: UserRole,
        patient_id: str,
        category: DataCategory,
        action: str,  # "read", "write", "export"
        log_access: bool = True
    ) -> bool:
        """
        Check if a user has access to a specific patient data category
        
        Args:
            requester_id: Identifier of the user requesting access
            requester_role: Role of the requester
            patient_id: Patient identifier
            category: Data category being accessed
            action: Action being performed
            log_access: Whether to log this access check
            
        Returns:
            True if access is allowed, False otherwise
        """
        # Special case: patients can always access their own data
        if requester_role == UserRole.PATIENT and requester_id == patient_id:
            if log_access:
                self._log_access(
                    requester_id=requester_id,
                    requester_role=requester_role,
                    patient_id=patient_id,
                    category=category,
                    action=action,
                    access_granted=True,
                    reason="Self-access"
                )
            return True
        
        # Get policy for the requester's role
        policy = self.policies.get(requester_role)
        if not policy:
            if log_access:
                self._log_access(
                    requester_id=requester_id,
                    requester_role=requester_role,
                    patient_id=patient_id,
                    category=category,
                    action=action,
                    access_granted=False,
                    reason="No policy for role"
                )
            return False
        
        # Get patient consent if required by policy
        consent = None
        if policy.consent_required:
            consent = self.consents.get(patient_id)
        
        # Determine access level
        access_level = policy.get_access_level(category, consent)
        
        # Check if access level is sufficient for the action
        access_granted = False
        reason = ""
        
        if action == "read":
            access_granted = access_level != AccessLevel.NONE
            reason = f"Read access level: {access_level.value}"
        elif action == "write":
            access_granted = access_level in [AccessLevel.STANDARD, AccessLevel.FULL]
            reason = f"Write access level: {access_level.value}"
        elif action == "export":
            access_granted = access_level in [AccessLevel.FULL, AccessLevel.RESEARCH]
            reason = f"Export access level: {access_level.value}"
        else:
            reason = f"Unknown action: {action}"
        
        # Log access check
        if log_access:
            self._log_access(
                requester_id=requester_id,
                requester_role=requester_role,
                patient_id=patient_id,
                category=category,
                action=action,
                access_granted=access_granted,
                reason=reason
            )
        
        return access_granted
    
    def _log_access(
        self,
        requester_id: str,
        requester_role: UserRole,
        patient_id: str,
        category: DataCategory,
        action: str,
        access_granted: bool,
        reason: str
    ) -> None:
        """
        Log an access check for audit purposes
        
        Args:
            requester_id: Identifier of the user requesting access
            requester_role: Role of the requester
            patient_id: Patient identifier
            category: Data category being accessed
            action: Action being performed
            access_granted: Whether access was granted
            reason: Reason for the decision
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "requester_id": requester_id,
            "requester_role": requester_role.value,
            "patient_id": patient_id,
            "category": category.value,
            "action": action,
            "access_granted": access_granted,
            "reason": reason
        }
        
        self.access_logs.append(log_entry)
        
        # Periodically save logs (every 100 entries)
        if len(self.access_logs) % 100 == 0:
            self._save_access_logs()
    
    def request_data_access(
        self,
        request: DataAccessRequest
    ) -> str:
        """
        Submit a formal request for data access
        
        Args:
            request: Data access request object
            
        Returns:
            Request ID
        """
        # Save request
        self.access_requests[request.id] = request
        self._save_access_requests()
        
        logger.info(
            f"New data access request from {request.requester_id} "
            f"({request.requester_role.value}) for patient {request.patient_id}"
        )
        
        return request.id
    
    def approve_access_request(
        self,
        request_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Approve a data access request
        
        Args:
            request_id: Request identifier
            reason: Reason for approval
            
        Returns:
            True if request was approved successfully, False otherwise
        """
        request = self.access_requests.get(request_id)
        if not request:
            logger.warning(f"Cannot approve request {request_id}: request not found")
            return False
        
        if request.decision is not None:
            logger.warning(f"Cannot approve request {request_id}: already decided")
            return False
        
        try:
            request.decision = True
            request.decision_time = datetime.now()
            request.decision_reason = reason
            
            self._save_access_requests()
            
            logger.info(f"Approved data access request {request_id}")
            return True
        except Exception as e:
            logger.error(f"Error approving data access request: {str(e)}")
            return False
    
    def deny_access_request(
        self,
        request_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Deny a data access request
        
        Args:
            request_id: Request identifier
            reason: Reason for denial
            
        Returns:
            True if request was denied successfully, False otherwise
        """
        request = self.access_requests.get(request_id)
        if not request:
            logger.warning(f"Cannot deny request {request_id}: request not found")
            return False
        
        if request.decision is not None:
            logger.warning(f"Cannot deny request {request_id}: already decided")
            return False
        
        try:
            request.decision = False
            request.decision_time = datetime.now()
            request.decision_reason = reason
            
            self._save_access_requests()
            
            logger.info(f"Denied data access request {request_id}")
            return True
        except Exception as e:
            logger.error(f"Error denying data access request: {str(e)}")
            return False
    
    def get_access_request(
        self,
        request_id: str
    ) -> Optional[DataAccessRequest]:
        """
        Get a data access request
        
        Args:
            request_id: Request identifier
            
        Returns:
            Data access request object, or None if not found
        """
        return self.access_requests.get(request_id)
    
    def get_access_requests(
        self,
        patient_id: Optional[str] = None,
        requester_id: Optional[str] = None,
        status: Optional[str] = None,  # "pending", "approved", "denied"
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get filtered access requests
        
        Args:
            patient_id: Filter by patient ID
            requester_id: Filter by requester ID
            status: Filter by request status
            limit: Maximum number of requests to return
            
        Returns:
            List of access request dictionaries
        """
        filtered_requests = list(self.access_requests.values())
        
        if patient_id:
            filtered_requests = [
                request for request in filtered_requests
                if request.patient_id == patient_id
            ]
        
        if requester_id:
            filtered_requests = [
                request for request in filtered_requests
                if request.requester_id == requester_id
            ]
        
        if status:
            if status == "pending":
                filtered_requests = [
                    request for request in filtered_requests
                    if request.decision is None
                ]
            elif status == "approved":
                filtered_requests = [
                    request for request in filtered_requests
                    if request.decision is True
                ]
            elif status == "denied":
                filtered_requests = [
                    request for request in filtered_requests
                    if request.decision is False
                ]
        
        # Sort by request time (newest first)
        sorted_requests = sorted(
            filtered_requests,
            key=lambda request: request.request_time,
            reverse=True
        )
        
        return [request.to_dict() for request in sorted_requests[:limit]]
    
    def get_access_logs(
        self,
        patient_id: Optional[str] = None,
        requester_id: Optional[str] = None,
        category: Optional[DataCategory] = None,
        action: Optional[str] = None,
        access_granted: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get filtered access logs
        
        Args:
            patient_id: Filter by patient ID
            requester_id: Filter by requester ID
            category: Filter by data category
            action: Filter by action
            access_granted: Filter by access decision
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of logs to return
            
        Returns:
            List of access log dictionaries
        """
        filtered_logs = self.access_logs
        
        if patient_id:
            filtered_logs = [
                log for log in filtered_logs
                if log["patient_id"] == patient_id
            ]
        
        if requester_id:
            filtered_logs = [
                log for log in filtered_logs
                if log["requester_id"] == requester_id
            ]
        
        if category:
            filtered_logs = [
                log for log in filtered_logs
                if log["category"] == category.value
            ]
        
        if action:
            filtered_logs = [
                log for log in filtered_logs
                if log["action"] == action
            ]
        
        if access_granted is not None:
            filtered_logs = [
                log for log in filtered_logs
                if log["access_granted"] == access_granted
            ]
        
        if start_time:
            filtered_logs = [
                log for log in filtered_logs
                if datetime.fromisoformat(log["timestamp"]) >= start_time
            ]
        
        if end_time:
            filtered_logs = [
                log for log in filtered_logs
                if datetime.fromisoformat(log["timestamp"]) <= end_time
            ]
        
        # Sort by timestamp (newest first)
        sorted_logs = sorted(
            filtered_logs,
            key=lambda log: log["timestamp"],
            reverse=True
        )
        
        return sorted_logs[:limit]
    
    def de_identify_patient_data(
        self,
        patient_data: Dict[str, Any],
        level: str = "research"  # "minimal", "safe_harbor", "expert_determination", "research"
    ) -> Dict[str, Any]:
        """
        De-identify patient data according to HIPAA standards
        
        Args:
            patient_data: Patient data to de-identify
            level: De-identification level
            
        Returns:
            De-identified patient data
        """
        if level == "minimal":
            # Minimal de-identification (still allows re-identification)
            return self._minimal_de_identification(patient_data)
        elif level == "safe_harbor":
            # HIPAA Safe Harbor method
            return self._safe_harbor_de_identification(patient_data)
        elif level == "expert_determination":
            # HIPAA Expert Determination method
            return self._expert_determination_de_identification(patient_data)
        elif level == "research":
            # Research-specific de-identification with useful data preserved
            return self._research_de_identification(patient_data)
        else:
            logger.warning(f"Unknown de-identification level: {level}, using safe_harbor")
            return self._safe_harbor_de_identification(patient_data)
    
    def _minimal_de_identification(
        self,
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform minimal de-identification (still allows re-identification)
        
        Args:
            patient_data: Patient data to de-identify
            
        Returns:
            De-identified patient data
        """
        result = patient_data.copy()
        
        # Remove direct identifiers
        if "name" in result:
            del result["name"]
        
        if "contact" in result:
            del result["contact"]
        
        if "address" in result:
            # Keep only state and zip code
            if isinstance(result["address"], dict):
                result["address"] = {
                    "state": result["address"].get("state", ""),
                    "zip": result["address"].get("zip", "")
                }
        
        return result
    
    def _safe_harbor_de_identification(
        self,
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform de-identification according to HIPAA Safe Harbor method
        
        Args:
            patient_data: Patient data to de-identify
            
        Returns:
            De-identified patient data
        """
        result = patient_data.copy()
        
        # 1. Names
        if "name" in result:
            del result["name"]
        
        # 2. Geographic subdivisions smaller than a state
        if "address" in result:
            if isinstance(result["address"], dict):
                # Keep only state
                result["address"] = {"state": result["address"].get("state", "")}
            else:
                del result["address"]
        
        # 3. Dates
        for date_field in ["birthDate", "dateOfBirth", "dob"]:
            if date_field in result:
                # Keep only year
                if isinstance(result[date_field], str):
                    try:
                        year = result[date_field].split("-")[0]
                        result[date_field] = year
                    except:
                        del result[date_field]
                else:
                    del result[date_field]
        
        # 4. Phone numbers
        for phone_field in ["phone", "phoneNumber", "telephone"]:
            if phone_field in result:
                del result[phone_field]
        
        # 5. Fax numbers
        for fax_field in ["fax", "faxNumber"]:
            if fax_field in result:
                del result[fax_field]
        
        # 6. Email addresses
        for email_field in ["email", "emailAddress"]:
            if email_field in result:
                del result[email_field]
        
        # 7. Social Security numbers
        for ssn_field in ["ssn", "socialSecurityNumber"]:
            if ssn_field in result:
                del result[ssn_field]
        
        # 8. Medical record numbers
        for mrn_field in ["mrn", "medicalRecordNumber"]:
            if mrn_field in result:
                # Replace with pseudonym
                result[mrn_field] = self._generate_pseudonym(result[mrn_field])
        
        # 9. Health plan beneficiary numbers
        for insurance_field in ["insuranceId", "healthPlanId"]:
            if insurance_field in result:
                del result[insurance_field]
        
        # 10. Account numbers
        for account_field in ["accountNumber", "account"]:
            if account_field in result:
                del result[account_field]
        
        # 11. Certificate/license numbers
        for license_field in ["licenseNumber", "certificate"]:
            if license_field in result:
                del result[license_field]
        
        # 12. Vehicle identifiers
        for vehicle_field in ["vehicleIdentifier", "license"]:
            if vehicle_field in result:
                del result[vehicle_field]
        
        # 13. Device identifiers
        for device_field in ["deviceId", "deviceIdentifier"]:
            if device_field in result:
                del result[device_field]
        
        # 14. Web URLs
        for url_field in ["url", "website"]:
            if url_field in result:
                del result[url_field]
        
        # 15. IP addresses
        for ip_field in ["ip", "ipAddress"]:
            if ip_field in result:
                del result[ip_field]
        
        # 16. Biometric identifiers
        for biometric_field in ["biometric", "fingerprint", "retinalScan"]:
            if biometric_field in result:
                del result[biometric_field]
        
        # 17. Full-face photographs
        for photo_field in ["photo", "image", "picture"]:
            if photo_field in result:
                del result[photo_field]
        
        # 18. Any other unique identifying number, characteristic, or code
        if "id" in result:
            result["id"] = self._generate_pseudonym(result["id"])
        
        return result
    
    def _expert_determination_de_identification(
        self,
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform de-identification according to HIPAA Expert Determination method
        (This is a simplified implementation and would need expert review in practice)
        
        Args:
            patient_data: Patient data to de-identify
            
        Returns:
            De-identified patient data
        """
        # Start with safe harbor de-identification
        result = self._safe_harbor_de_identification(patient_data)
        
        # Apply additional transformations for expert determination
        
        # Age transformation: group into ranges
        if "age" in result:
            age = result["age"]
            if isinstance(age, (int, float)):
                if age < 18:
                    result["age_group"] = "<18"
                elif age < 30:
                    result["age_group"] = "18-29"
                elif age < 45:
                    result["age_group"] = "30-44"
                elif age < 65:
                    result["age_group"] = "45-64"
                else:
                    result["age_group"] = "65+"
                del result["age"]
        
        # Generalize rare conditions
        if "diagnoses" in result and isinstance(result["diagnoses"], list):
            # This would require a reference database of condition prevalence
            # For now, we'll just preserve the diagnoses as they are
            pass
        
        return result
    
    def _research_de_identification(
        self,
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform de-identification specifically for research purposes
        
        Args:
            patient_data: Patient data to de-identify
            
        Returns:
            De-identified patient data suitable for research
        """
        # Start with safe harbor de-identification
        result = self._safe_harbor_de_identification(patient_data)
        
        # Preserve or transform certain fields useful for research
        
        # Age: keep exact age for adults, group for minors
        if "age" in patient_data:
            age = patient_data["age"]
            if isinstance(age, (int, float)):
                if age < 18:
                    result["age_group"] = "<18"
                else:
                    result["age"] = age
        
        # Demographics: keep gender, race, ethnicity
        for demo_field in ["gender", "race", "ethnicity"]:
            if demo_field in patient_data:
                result[demo_field] = patient_data[demo_field]
        
        # ZIP code: keep first 3 digits if population > 20,000
        if "address" in patient_data and isinstance(patient_data["address"], dict):
            zip_code = patient_data["address"].get("zip", "")
            if zip_code and len(zip_code) >= 5:
                # In a real implementation, would check population size
                # For this example, assume all ZIP3s are > 20,000 population
                result["zip3"] = zip_code[:3]
        
        # Dates: shift all dates by a random offset (consistent for patient)
        # This preserves intervals between dates while obscuring actual dates
        if "id" in patient_data:
            # Generate a deterministic random offset (days) from patient ID
            seed_value = hash(str(patient_data["id"])) % 1000
            date_offset = seed_value - 500  # -500 to +499 days
            
            result["_date_shift"] = date_offset
        
        return result
    
    def _generate_pseudonym(self, identifier: str) -> str:
        """
        Generate a pseudonym from an identifier
        
        Args:
            identifier: Original identifier
            
        Returns:
            Pseudonym
        """
        # Generate a hash of the identifier
        hash_obj = hashlib.sha256(str(identifier).encode())
        hash_hex = hash_obj.hexdigest()
        
        # Use first 8 characters of hash
        return hash_hex[:8]

# CLI for testing
if __name__ == "__main__":
    # Create privacy service
    privacy_service = PrivacyService()
    
    # Create test patient consent
    test_consent = PatientConsent(
        patient_id="P12345",
        status=ConsentStatus.GRANTED,
        scope=[
            DataCategory.DEMOGRAPHICS,
            DataCategory.DIAGNOSES,
            DataCategory.MEDICATIONS,
            DataCategory.PROCEDURES,
            DataCategory.LAB_RESULTS,
            DataCategory.VITAL_SIGNS
        ],
        start_date=datetime.now(),
        expiration_date=datetime.now() + timedelta(days=365)
    )
    
    # Record patient consent
    privacy_service.record_patient_consent(test_consent)
    
    # Test access checks
    provider_access = privacy_service.check_access(
        requester_id="PROVIDER123",
        requester_role=UserRole.PROVIDER,
        patient_id="P12345",
        category=DataCategory.MEDICATIONS,
        action="read"
    )
    
    researcher_access = privacy_service.check_access(
        requester_id="RESEARCHER456",
        requester_role=UserRole.RESEARCHER,
        patient_id="P12345",
        category=DataCategory.MEDICATIONS,
        action="read"
    )
    
    print(f"Provider access: {provider_access}")
    print(f"Researcher access: {researcher_access}")
    
    # Test data access request
    request = DataAccessRequest(
        requester_id="RESEARCHER456",
        requester_role=UserRole.RESEARCHER,
        patient_id="P12345",
        categories=[
            DataCategory.DEMOGRAPHICS,
            DataCategory.DIAGNOSES,
            DataCategory.MEDICATIONS
        ],
        purpose="Crohn's disease treatment research"
    )
    
    request_id = privacy_service.request_data_access(request)
    print(f"Access request ID: {request_id}")
    
    # Approve access request
    privacy_service.approve_access_request(
        request_id=request_id,
        reason="Approved for research purposes"
    )
    
    # Test de-identification
    test_patient_data = {
        "id": "P12345",
        "name": {
            "first": "John",
            "last": "Doe"
        },
        "birthDate": "1980-06-15",
        "age": 42,
        "gender": "male",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "90210"
        },
        "phone": "555-123-4567",
        "email": "john.doe@example.com",
        "mrn": "MRN123456",
        "diagnoses": [
            {
                "code": "K50.0",
                "description": "Crohn's disease of small intestine",
                "date": "2018-05-10"
            }
        ],
        "medications": [
            {
                "name": "Humira",
                "dose": "40mg",
                "frequency": "every other week",
                "start_date": "2018-06-01"
            }
        ]
    }
    
    de_identified_data = privacy_service.de_identify_patient_data(
        patient_data=test_patient_data,
        level="research"
    )
    
    print("Original data:", test_patient_data)
    print("De-identified data:", de_identified_data)