"""
Data models for the Federation Framework.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Union
from enum import Enum
from datetime import datetime


class TrustLevel(str, Enum):
    """Trust levels for partner agencies."""
    TRUSTED = "TRUSTED"       # Highest trust level, minimal restrictions
    PARTNER = "PARTNER"       # Standard trust level, normal restrictions
    LIMITED = "LIMITED"       # Limited trust, higher restrictions
    EXTERNAL = "EXTERNAL"     # External party, maximum restrictions


class SecurityClassification(str, Enum):
    """Security classifications for data."""
    PUBLIC = "PUBLIC"                 # Publicly available data
    SENSITIVE = "SENSITIVE"           # Sensitive but not restricted
    RESTRICTED = "RESTRICTED"         # Restricted access
    HIGHLY_RESTRICTED = "HIGHLY_RESTRICTED"  # Highly restricted access


class SyncMode(str, Enum):
    """Synchronization modes."""
    FULL = "FULL"               # Full data synchronization
    INCREMENTAL = "INCREMENTAL" # Incremental updates only
    DELTA = "DELTA"             # Delta changes only


@dataclass
class Agency:
    """Represents a partner agency in the federation."""
    id: str
    endpoint: str
    trust_level: Union[TrustLevel, str]
    allowed_datasets: List[str] = field(default_factory=list)
    contact_email: Optional[str] = None
    api_key: Optional[str] = None
    certificates: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Normalize enum values after initialization."""
        if isinstance(self.trust_level, str):
            self.trust_level = TrustLevel(self.trust_level)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "endpoint": self.endpoint,
            "trust_level": self.trust_level.value,
            "allowed_datasets": self.allowed_datasets,
            "contact_email": self.contact_email,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agency':
        """Create instance from dictionary."""
        # Handle datetime conversion
        for date_field in ['created_at', 'updated_at']:
            if date_field in data and isinstance(data[date_field], str):
                data[date_field] = datetime.fromisoformat(data[date_field])
        return cls(**data)


@dataclass
class DatasetSchema:
    """Schema definition for a federated dataset."""
    name: str
    version: str
    fields: Dict[str, Dict[str, Any]]
    security_classification: Union[SecurityClassification, str]
    description: Optional[str] = None
    owner_agency: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Normalize enum values after initialization."""
        if isinstance(self.security_classification, str):
            self.security_classification = SecurityClassification(self.security_classification)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "version": self.version,
            "fields": self.fields,
            "security_classification": self.security_classification.value,
            "description": self.description,
            "owner_agency": self.owner_agency,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class AccessRule:
    """Access control rule for federation policies."""
    agency_patterns: List[str]
    role_patterns: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    effect: str = "ALLOW"  # ALLOW or DENY
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "agency_patterns": self.agency_patterns,
            "role_patterns": self.role_patterns,
            "conditions": self.conditions,
            "effect": self.effect
        }


@dataclass
class FederationPolicy:
    """Policy governing federation access control."""
    dataset: str
    security_classification: Union[SecurityClassification, str]
    rules: List[AccessRule] = field(default_factory=list)
    retention_period: Optional[str] = None
    data_sovereignty: Optional[List[str]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Normalize enum values after initialization."""
        if isinstance(self.security_classification, str):
            self.security_classification = SecurityClassification(self.security_classification)
    
    def add_rule(self, rule: AccessRule) -> None:
        """Add an access rule to the policy."""
        self.rules.append(rule)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "dataset": self.dataset,
            "security_classification": self.security_classification.value,
            "rules": [rule.to_dict() for rule in self.rules],
            "retention_period": self.retention_period,
            "data_sovereignty": self.data_sovereignty,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class FederationRequest:
    """Represents a request for federated data."""
    request_id: str
    source_agency: str
    target_agency: str
    dataset: str
    query: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "request_id": self.request_id,
            "source_agency": self.source_agency,
            "target_agency": self.target_agency,
            "dataset": self.dataset,
            "query": self.query,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class FederationResponse:
    """Represents a response to a federation request."""
    request_id: str
    status: str  # SUCCESS, ERROR, PARTIAL
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "request_id": self.request_id,
            "status": self.status,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class SyncJob:
    """Represents a data synchronization job."""
    job_id: str
    source_agency: str
    target_agency: str
    datasets: List[str]
    sync_mode: Union[SyncMode, str]
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
    progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Normalize enum values after initialization."""
        if isinstance(self.sync_mode, str):
            self.sync_mode = SyncMode(self.sync_mode)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "job_id": self.job_id,
            "source_agency": self.source_agency,
            "target_agency": self.target_agency,
            "datasets": self.datasets,
            "sync_mode": self.sync_mode.value,
            "status": self.status,
            "progress": self.progress,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "error": self.error,
            "metadata": self.metadata
        }


@dataclass
class AuditEvent:
    """Represents an audit log event."""
    event_id: str
    event_type: str
    agency_id: str
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    request_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "agency_id": self.agency_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "ip_address": self.ip_address,
            "request_id": self.request_id
        }