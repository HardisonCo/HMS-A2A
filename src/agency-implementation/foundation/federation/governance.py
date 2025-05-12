"""
Governance System for federation framework.

This module provides mechanisms for defining and enforcing policies
that govern how data is shared and accessed across agencies.
"""

import logging
import uuid
import json
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
import os
import threading

from federation.models import FederationPolicy, AccessRule, SecurityClassification
from federation.exceptions import GovernanceError

logger = logging.getLogger(__name__)


class PolicyValidator:
    """Base class for policy validators."""
    
    def validate(self, policy: FederationPolicy) -> List[str]:
        """
        Validate a federation policy.
        
        Args:
            policy: Policy to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        raise NotImplementedError("Subclasses must implement validate()")


class DefaultPolicyValidator(PolicyValidator):
    """Default implementation of policy validator."""
    
    def validate(self, policy: FederationPolicy) -> List[str]:
        """
        Validate a federation policy.
        
        Args:
            policy: Policy to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check basic fields
        if not policy.dataset:
            errors.append("Policy must have a dataset name")
        
        # Validate security classification
        try:
            if isinstance(policy.security_classification, str):
                SecurityClassification(policy.security_classification)
        except ValueError:
            errors.append(f"Invalid security classification: {policy.security_classification}")
        
        # Validate access rules
        for i, rule in enumerate(policy.rules):
            # Check agency patterns
            if not rule.agency_patterns:
                errors.append(f"Rule {i+1} must have at least one agency pattern")
            
            # Check effect
            if rule.effect not in ["ALLOW", "DENY"]:
                errors.append(f"Rule {i+1} has invalid effect: {rule.effect}")
        
        return errors


class GovernanceManager:
    """
    Manager for federation governance.
    
    This class manages federation policies that define how data
    is shared and accessed across agencies.
    """
    
    def __init__(self, federation_manager):
        """Initialize with federation manager reference."""
        self._federation = federation_manager
        self._policies = {}  # dataset -> FederationPolicy
        self._validators = [DefaultPolicyValidator()]
        self._policy_dir = self._federation.config.get("governance", {}).get("policy_directory")
        self._policy_lock = threading.Lock()
        
        # Load policies
        if self._policy_dir:
            self._load_policies()
    
    def _load_policies(self) -> None:
        """Load policies from policy directory."""
        if not self._policy_dir:
            return
        
        try:
            os.makedirs(self._policy_dir, exist_ok=True)
            for filename in os.listdir(self._policy_dir):
                if not filename.endswith('.json'):
                    continue
                
                file_path = os.path.join(self._policy_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        policy_data = json.load(f)
                    
                    # Convert rules data to objects
                    rules = []
                    for rule_data in policy_data.get("rules", []):
                        rules.append(AccessRule(**rule_data))
                    
                    # Create policy object
                    policy = FederationPolicy(
                        dataset=policy_data.get("dataset"),
                        security_classification=policy_data.get("security_classification"),
                        rules=rules,
                        retention_period=policy_data.get("retention_period"),
                        data_sovereignty=policy_data.get("data_sovereignty")
                    )
                    
                    # Apply policy
                    self.apply_policy(policy.dataset, policy)
                    
                except Exception as e:
                    logger.error(f"Failed to load policy from {file_path}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Failed to load policies: {str(e)}")
    
    def register_validator(self, validator: PolicyValidator) -> None:
        """
        Register a policy validator.
        
        Args:
            validator: Validator to register
        """
        self._validators.append(validator)
    
    def validate_policy(self, policy: FederationPolicy) -> List[str]:
        """
        Validate a federation policy.
        
        Args:
            policy: Policy to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        all_errors = []
        
        for validator in self._validators:
            try:
                errors = validator.validate(policy)
                all_errors.extend(errors)
            except Exception as e:
                all_errors.append(f"Validator failed: {str(e)}")
        
        return all_errors
    
    def get_policy(self, dataset: str) -> Optional[FederationPolicy]:
        """
        Get the federation policy for a dataset.
        
        Args:
            dataset: Dataset name
            
        Returns:
            FederationPolicy if found, None otherwise
        """
        return self._policies.get(dataset)
    
    def list_policies(self) -> List[FederationPolicy]:
        """
        List all federation policies.
        
        Returns:
            List of all policies
        """
        return list(self._policies.values())
    
    def apply_policy(self, dataset: str, policy: FederationPolicy) -> None:
        """
        Apply a federation policy to a dataset.
        
        Args:
            dataset: Dataset name
            policy: Policy to apply
            
        Raises:
            GovernanceError: If policy is invalid
        """
        # Validate policy
        errors = self.validate_policy(policy)
        if errors:
            error_message = "\n".join(errors)
            raise GovernanceError(f"Invalid policy: {error_message}")
        
        # Update policy
        with self._policy_lock:
            self._policies[dataset] = policy
            
            # Save to file if directory is configured
            if self._policy_dir:
                self._save_policy(policy)
        
        # Log policy application
        logger.info(f"Applied policy for dataset {dataset}")
        self._federation.audit.log_event(
            event_type="POLICY_APPLIED",
            details={"dataset": dataset}
        )
    
    def _save_policy(self, policy: FederationPolicy) -> None:
        """
        Save policy to file.
        
        Args:
            policy: Policy to save
        """
        if not self._policy_dir:
            return
        
        os.makedirs(self._policy_dir, exist_ok=True)
        file_path = os.path.join(self._policy_dir, f"{policy.dataset}_policy.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(policy.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save policy to {file_path}: {str(e)}")
    
    def delete_policy(self, dataset: str) -> bool:
        """
        Delete a federation policy.
        
        Args:
            dataset: Dataset name
            
        Returns:
            True if policy was deleted, False if not found
        """
        with self._policy_lock:
            if dataset not in self._policies:
                return False
            
            # Remove policy
            del self._policies[dataset]
            
            # Delete file if directory is configured
            if self._policy_dir:
                file_path = os.path.join(self._policy_dir, f"{dataset}_policy.json")
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logger.error(f"Failed to delete policy file {file_path}: {str(e)}")
        
        # Log policy deletion
        logger.info(f"Deleted policy for dataset {dataset}")
        self._federation.audit.log_event(
            event_type="POLICY_DELETED",
            details={"dataset": dataset}
        )
        
        return True
    
    def create_default_policy(self, dataset: str, classification: SecurityClassification) -> FederationPolicy:
        """
        Create a default policy for a dataset.
        
        Args:
            dataset: Dataset name
            classification: Security classification
            
        Returns:
            Generated policy
        """
        # Create basic rules based on classification
        rules = []
        
        if classification == SecurityClassification.PUBLIC:
            # Public data - allow all
            rules.append(AccessRule(
                agency_patterns=["*"],
                effect="ALLOW"
            ))
        
        elif classification == SecurityClassification.SENSITIVE:
            # Sensitive data - allow trusted and partner agencies
            rules.append(AccessRule(
                agency_patterns=["*"],
                role_patterns=["admin", "data_officer"],
                effect="ALLOW"
            ))
        
        elif classification == SecurityClassification.RESTRICTED:
            # Restricted data - allow only trusted agencies
            rules.append(AccessRule(
                agency_patterns=["TRUSTED-*"],
                role_patterns=["admin", "data_officer"],
                effect="ALLOW"
            ))
        
        elif classification == SecurityClassification.HIGHLY_RESTRICTED:
            # Highly restricted data - explicit allow only
            rules.append(AccessRule(
                agency_patterns=["TRUSTED-AGENCY-1", "TRUSTED-AGENCY-2"],
                role_patterns=["admin"],
                effect="ALLOW"
            ))
        
        # Create policy
        policy = FederationPolicy(
            dataset=dataset,
            security_classification=classification,
            rules=rules
        )
        
        return policy