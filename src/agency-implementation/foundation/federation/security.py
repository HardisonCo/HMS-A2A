"""
Security System for federation framework.

This module provides security mechanisms including access control,
encryption, data classification, and policy enforcement for the federation.
"""

import logging
import uuid
import json
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
import re

from federation.models import Agency, FederationPolicy, AccessRule, SecurityClassification
from federation.exceptions import SecurityError, AuthorizationError

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Manager for federation security.
    
    This class provides security services including:
    - Access control and authorization
    - Data classification and handling
    - Security policy enforcement
    - Certificate management
    """
    
    def __init__(self, federation_manager):
        """Initialize with federation manager reference."""
        self._federation = federation_manager
        self._token_validator = None  # Will be initialized when needed
    
    def authorize_request(
        self,
        source_agency: str,
        target_dataset: str,
        operation: str,
        user_id: Optional[str] = None,
        user_roles: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Authorize a federation request.
        
        Args:
            source_agency: ID of requesting agency
            target_dataset: Dataset being accessed
            operation: Requested operation (QUERY, SYNC, etc.)
            user_id: Optional ID of user making the request
            user_roles: Optional roles of user making the request
            context: Optional additional context for authorization
            
        Returns:
            True if authorized, False otherwise
            
        Raises:
            AuthorizationError: If the request cannot be authorized
        """
        # Get policy for target dataset
        policy = self._federation.get_policy(target_dataset)
        if not policy:
            logger.warning(f"No policy found for dataset {target_dataset}")
            return False
        
        # Check security classification
        if not self._check_classification_access(source_agency, policy.security_classification):
            logger.warning(
                f"Agency {source_agency} does not have sufficient clearance for dataset {target_dataset}"
            )
            return False
        
        # Check data sovereignty constraints
        if policy.data_sovereignty and not self._check_data_sovereignty(source_agency, policy.data_sovereignty):
            logger.warning(
                f"Agency {source_agency} does not meet data sovereignty requirements for {target_dataset}"
            )
            return False
        
        # Evaluate access rules
        return self._evaluate_access_rules(
            policy.rules,
            source_agency,
            user_id,
            user_roles or [],
            operation,
            context or {}
        )
    
    def _check_classification_access(
        self, 
        agency_id: str, 
        classification: SecurityClassification
    ) -> bool:
        """
        Check if an agency has access to a given security classification.
        
        Args:
            agency_id: Agency ID
            classification: Security classification
            
        Returns:
            True if agency has access, False otherwise
        """
        agency = self._federation.get_partner(agency_id)
        if not agency:
            return False
        
        # Simple classification hierarchy check
        # In a real implementation, this would be more sophisticated
        agency_level = self._get_classification_level(agency.trust_level)
        required_level = self._get_classification_level(classification)
        
        return agency_level >= required_level
    
    def _get_classification_level(self, classification: Union[str, SecurityClassification]) -> int:
        """
        Get numeric level for a classification.
        
        Args:
            classification: Classification enum or string
            
        Returns:
            Numeric level (higher is more access)
        """
        if isinstance(classification, SecurityClassification):
            classification = classification.value
            
        levels = {
            "PUBLIC": 1,
            "SENSITIVE": 2,
            "RESTRICTED": 3,
            "HIGHLY_RESTRICTED": 4,
            "TRUSTED": 4,
            "PARTNER": 3,
            "LIMITED": 2,
            "EXTERNAL": 1
        }
        
        return levels.get(classification, 0)
    
    def _check_data_sovereignty(self, agency_id: str, sovereignty_regions: List[str]) -> bool:
        """
        Check if an agency complies with data sovereignty requirements.
        
        Args:
            agency_id: Agency ID
            sovereignty_regions: Allowed regions for data storage
            
        Returns:
            True if compliant, False otherwise
        """
        agency = self._federation.get_partner(agency_id)
        if not agency:
            return False
        
        # Check if agency's region is in the allowed regions
        # This is a simplified implementation
        agency_region = agency.metadata.get("region", "UNKNOWN")
        return agency_region in sovereignty_regions
    
    def _evaluate_access_rules(
        self,
        rules: List[AccessRule],
        agency_id: str,
        user_id: Optional[str],
        user_roles: List[str],
        operation: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Evaluate access rules to determine authorization.
        
        Args:
            rules: List of access rules to evaluate
            agency_id: Agency ID
            user_id: User ID
            user_roles: User roles
            operation: Requested operation
            context: Additional context
            
        Returns:
            True if authorized, False otherwise
        """
        # Default to deny if no rules match
        default_effect = "DENY"
        
        for rule in rules:
            # Check if rule applies to this agency
            if not self._matches_pattern_list(agency_id, rule.agency_patterns):
                continue
            
            # Check if rule applies to user roles
            if rule.role_patterns and not any(
                self._matches_pattern_list(role, rule.role_patterns) for role in user_roles
            ):
                continue
            
            # Check additional conditions
            if not self._evaluate_conditions(rule.conditions, operation, context):
                continue
            
            # Rule matched, return its effect
            return rule.effect == "ALLOW"
        
        # No rules matched, return default
        return default_effect == "ALLOW"
    
    def _matches_pattern_list(self, value: str, patterns: List[str]) -> bool:
        """
        Check if a value matches any pattern in a list.
        
        Args:
            value: Value to check
            patterns: List of patterns (supports * wildcard)
            
        Returns:
            True if the value matches any pattern
        """
        for pattern in patterns:
            # Convert glob pattern to regex
            regex_pattern = pattern.replace("*", ".*")
            if re.match(f"^{regex_pattern}$", value):
                return True
        return False
    
    def _evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        operation: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Evaluate additional conditions for access rules.
        
        Args:
            conditions: Conditions to evaluate
            operation: Requested operation
            context: Additional context
            
        Returns:
            True if all conditions are met
        """
        # Check operation condition
        if "operations" in conditions:
            allowed_operations = conditions["operations"]
            if isinstance(allowed_operations, list) and operation not in allowed_operations:
                return False
        
        # Check time-based conditions
        if "time_window" in conditions:
            time_window = conditions["time_window"]
            now = datetime.now().time()
            
            start_time = datetime.strptime(time_window.get("start", "00:00"), "%H:%M").time()
            end_time = datetime.strptime(time_window.get("end", "23:59"), "%H:%M").time()
            
            if not (start_time <= now <= end_time):
                return False
        
        # Check IP range condition
        if "ip_ranges" in conditions and "client_ip" in context:
            client_ip = context["client_ip"]
            allowed_ranges = conditions["ip_ranges"]
            
            # Simplified IP range check
            if not any(client_ip.startswith(ip_range) for ip_range in allowed_ranges):
                return False
        
        # All conditions met
        return True
    
    def encrypt_payload(self, data: Any, target_agency: str) -> Dict[str, Any]:
        """
        Encrypt a data payload for a specific agency.
        
        Args:
            data: Data to encrypt
            target_agency: Target agency ID
            
        Returns:
            Encrypted data envelope
        """
        # In a real implementation, this would use proper encryption
        # For now, this is just a placeholder
        return {
            "encrypted": True,
            "target": target_agency,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    def decrypt_payload(self, encrypted_data: Dict[str, Any]) -> Any:
        """
        Decrypt a data payload.
        
        Args:
            encrypted_data: Encrypted data envelope
            
        Returns:
            Decrypted data
            
        Raises:
            SecurityError: If the payload cannot be decrypted
        """
        # In a real implementation, this would use proper decryption
        # For now, this is just a placeholder
        if not encrypted_data.get("encrypted", False):
            raise SecurityError("Data is not in the expected encrypted format")
        
        return encrypted_data.get("data")
    
    def apply_data_classification(self, data: Dict[str, Any], classification: SecurityClassification) -> Dict[str, Any]:
        """
        Apply security classification to a data payload.
        
        Args:
            data: Data to classify
            classification: Security classification to apply
            
        Returns:
            Data with classification metadata
        """
        # Add classification metadata
        if isinstance(data, dict):
            data["__security_metadata"] = {
                "classification": classification.value if isinstance(classification, SecurityClassification) else classification,
                "classified_at": datetime.now().isoformat(),
                "classified_by": self._federation.local_agency_id
            }
        return data
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a security token.
        
        Args:
            token: Token to validate
            
        Returns:
            Token claims if valid
            
        Raises:
            SecurityError: If the token is invalid
        """
        # In a real implementation, this would validate JWT tokens
        # For now, this is just a placeholder
        try:
            # Simulate token validation
            if not token or not token.startswith("FEDERATION."):
                raise SecurityError("Invalid token format")
            
            # Return simulated claims
            return {
                "agency_id": "SAMPLE-AGENCY",
                "user_id": "sample-user",
                "roles": ["user"],
                "exp": (datetime.now().timestamp() + 3600)
            }
        except Exception as e:
            raise SecurityError(f"Token validation failed: {str(e)}")
    
    def generate_token(self, claims: Dict[str, Any]) -> str:
        """
        Generate a security token.
        
        Args:
            claims: Token claims
            
        Returns:
            Generated token
        """
        # In a real implementation, this would generate JWT tokens
        # For now, this is just a placeholder
        return f"FEDERATION.{uuid.uuid4()}"