"""
Alert Model

This module defines the Alert model and related enums used throughout the notification system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class AlertSeverity(Enum):
    """Severity levels for alerts."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class AlertStatus(Enum):
    """Status values for alerts."""
    NEW = "new"
    PROCESSING = "processing"
    DISTRIBUTED = "distributed"
    ACKNOWLEDGED = "acknowledged"
    CLOSED = "closed"
    EXPIRED = "expired"


@dataclass
class Alert:
    """
    Represents an alert from a federal agency or other source.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    source: str = ""  # Agency or source system
    alert_type: str = ""  # Type of alert (e.g., "disease_outbreak", "environmental_hazard")
    severity: AlertSeverity = AlertSeverity.MEDIUM
    status: AlertStatus = AlertStatus.NEW
    url: Optional[str] = None  # URL with more information
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    priority_score: float = 0.0  # Calculated priority (0-100)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Distribution information
    distribution_timestamp: Optional[datetime] = None
    
    # Acknowledgment information
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    
    # Resolution information
    closed_by: Optional[str] = None
    closed_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    # Optional fields for specific alert types
    regions: List[str] = field(default_factory=list)  # Affected geographical regions
    recommended_actions: List[str] = field(default_factory=list)  # Recommended actions
    affected_population: Optional[int] = None  # Estimated affected population
    
    def __post_init__(self):
        """Initialize after creation."""
        if not self.created_at:
            self.created_at = datetime.utcnow()
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "alert_type": self.alert_type,
            "severity": self.severity.value,
            "status": self.status.value,
            "url": self.url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "priority_score": self.priority_score,
            "metadata": self.metadata,
            "distribution_timestamp": self.distribution_timestamp.isoformat() if self.distribution_timestamp else None,
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "closed_by": self.closed_by,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "resolution_notes": self.resolution_notes,
            "regions": self.regions,
            "recommended_actions": self.recommended_actions,
            "affected_population": self.affected_population,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alert':
        """Create alert from dictionary representation."""
        # Handle enum fields
        if "severity" in data and isinstance(data["severity"], str):
            data["severity"] = AlertSeverity(data["severity"])
        if "status" in data and isinstance(data["status"], str):
            data["status"] = AlertStatus(data["status"])
            
        # Handle datetime fields
        for dt_field in ["created_at", "expires_at", "distribution_timestamp", "acknowledged_at", "closed_at"]:
            if dt_field in data and data[dt_field] and isinstance(data[dt_field], str):
                try:
                    data[dt_field] = datetime.fromisoformat(data[dt_field])
                except (ValueError, TypeError):
                    data[dt_field] = None
                    
        return cls(**data)