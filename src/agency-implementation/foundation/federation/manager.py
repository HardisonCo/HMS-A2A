"""
Federation Manager - Core orchestration component for federation activities.
"""

import logging
from typing import Dict, List, Optional, Any, Union

from federation.models import Agency, FederationPolicy, DatasetSchema
from federation.query import QueryManager
from federation.sync import SyncManager
from federation.identity import IdentityManager
from federation.security import SecurityManager
from federation.audit import AuditManager
from federation.schema import SchemaRegistry
from federation.governance import GovernanceManager
from federation.exceptions import FederationError, ConfigurationError

logger = logging.getLogger(__name__)

class FederationManager:
    """
    Main entry point for the federation framework.
    
    This class orchestrates all federation activities including:
    - Partner agency registration and management
    - Federated queries across agencies
    - Data synchronization between agencies
    - Access control and security enforcement
    - Audit logging of all federation activities
    - Schema and governance management
    """
    
    def __init__(
        self, 
        local_agency_id: str,
        config_path: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Federation Manager.
        
        Args:
            local_agency_id: Identifier for the local agency
            config_path: Optional path to configuration file
            **kwargs: Additional configuration parameters
        """
        self.local_agency_id = local_agency_id
        self.config = self._load_configuration(config_path, **kwargs)
        
        # Initialize partner registry
        self.partners: Dict[str, Agency] = {}
        
        # Initialize federation components
        self.security = SecurityManager(self)
        self.identity = IdentityManager(self)
        self.audit = AuditManager(self)
        self.schema_registry = SchemaRegistry(self)
        self.governance = GovernanceManager(self)
        
        # Initialize query and sync managers
        self.query = QueryManager(self)
        self.sync = SyncManager(self)
        
        logger.info(f"Federation Manager initialized for agency: {local_agency_id}")
    
    def _load_configuration(self, config_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Load configuration from file and/or keyword arguments.
        
        Args:
            config_path: Path to configuration file
            **kwargs: Additional configuration parameters
            
        Returns:
            Dict containing configuration parameters
        """
        config = {}
        
        # Load from file if specified
        if config_path:
            try:
                import yaml
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    config.update(file_config.get('federation', {}))
            except Exception as e:
                raise ConfigurationError(f"Failed to load configuration from {config_path}: {str(e)}")
        
        # Override with provided kwargs
        config.update(kwargs)
        
        # Apply default values
        config.setdefault('gateway', {}).setdefault('port', 8585)
        config.setdefault('gateway', {}).setdefault('host', '0.0.0.0')
        
        return config
    
    def register_partner(
        self,
        agency_id: str,
        endpoint: str,
        trust_level: str,
        allowed_datasets: Optional[List[str]] = None,
        **kwargs
    ) -> Agency:
        """
        Register a partner agency for federation.
        
        Args:
            agency_id: Unique identifier for the partner agency
            endpoint: Federation endpoint URL for the partner
            trust_level: Trust level (TRUSTED, PARTNER, LIMITED)
            allowed_datasets: List of datasets allowed to be shared
            **kwargs: Additional agency configuration
            
        Returns:
            Agency object representing the registered partner
        """
        if agency_id in self.partners:
            logger.warning(f"Updating existing partner agency: {agency_id}")
        
        agency = Agency(
            id=agency_id,
            endpoint=endpoint,
            trust_level=trust_level,
            allowed_datasets=allowed_datasets or [],
            **kwargs
        )
        
        self.partners[agency_id] = agency
        self.audit.log_event(
            event_type="PARTNER_REGISTERED",
            details={"agency_id": agency_id, "trust_level": trust_level}
        )
        
        logger.info(f"Registered partner agency: {agency_id} with trust level: {trust_level}")
        return agency
    
    def get_partner(self, agency_id: str) -> Optional[Agency]:
        """
        Get a registered partner agency by ID.
        
        Args:
            agency_id: Agency identifier
            
        Returns:
            Agency object if found, None otherwise
        """
        return self.partners.get(agency_id)
    
    def list_partners(self) -> List[Agency]:
        """
        List all registered partner agencies.
        
        Returns:
            List of Agency objects
        """
        return list(self.partners.values())
    
    def start_gateway(self, port: Optional[int] = None, host: Optional[str] = None) -> None:
        """
        Start the federation gateway service.
        
        Args:
            port: Override port from configuration
            host: Override host from configuration
        """
        gateway_config = self.config.get('gateway', {})
        port = port or gateway_config.get('port', 8585)
        host = host or gateway_config.get('host', '0.0.0.0')
        
        # Gateway server implementation would go here
        # This would initialize the server for handling incoming federation requests
        
        logger.info(f"Federation gateway started on {host}:{port}")
    
    def stop_gateway(self) -> None:
        """Stop the federation gateway service."""
        # Gateway server shutdown would go here
        logger.info("Federation gateway stopped")
    
    def get_policy(self, dataset: str) -> FederationPolicy:
        """
        Get the federation policy for a specific dataset.
        
        Args:
            dataset: Dataset name
            
        Returns:
            FederationPolicy containing access rules
        """
        return self.governance.get_policy(dataset)
    
    def apply_policy(self, dataset: str, policy: FederationPolicy) -> None:
        """
        Apply federation policy to a dataset.
        
        Args:
            dataset: Dataset name
            policy: Policy to apply
        """
        self.governance.apply_policy(dataset, policy)
        self.audit.log_event(
            event_type="POLICY_APPLIED",
            details={"dataset": dataset, "policy": policy.to_dict()}
        )