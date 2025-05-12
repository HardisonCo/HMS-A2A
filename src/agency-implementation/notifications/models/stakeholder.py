"""
Stakeholder Model

This module defines the Stakeholder model and related enums for the notification system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Set
import uuid


class StakeholderGroup(Enum):
    """Types of stakeholder groups."""
    GENERAL_PUBLIC = "general_public"
    HEALTHCARE = "healthcare"
    EMERGENCY_MANAGEMENT = "emergency_management"
    GOVERNMENT = "government"
    LAW_ENFORCEMENT = "law_enforcement"
    TRANSPORTATION = "transportation"
    EDUCATION = "education"
    UTILITIES = "utilities"
    INDUSTRY = "industry"


class StakeholderRole(Enum):
    """Roles a stakeholder may have."""
    VIEWER = "viewer"
    RESPONDER = "responder"
    COORDINATOR = "coordinator"
    ADMINISTRATOR = "administrator"
    ANALYST = "analyst"
    MANAGER = "manager"


@dataclass
class Stakeholder:
    """
    Represents a stakeholder who receives notifications.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    organization: str = ""
    email: str = ""
    phone: Optional[str] = None
    groups: List[StakeholderGroup] = field(default_factory=list)
    role: StakeholderRole = StakeholderRole.VIEWER
    regions: List[str] = field(default_factory=list)  # Geographical areas of interest
    is_active: bool = True
    created_at: Optional[str] = None
    
    # Notification preferences
    preferred_channels: List[str] = field(default_factory=lambda: ["email"])
    notification_schedule: Dict[str, Any] = field(default_factory=dict)  # Schedule for notifications
    subscribed_alert_types: Set[str] = field(default_factory=set)  # Alert types subscribed to
    
    # Integration information
    webhook_endpoints: List[str] = field(default_factory=list)  # Webhook endpoints for API notifications
    api_keys: List[str] = field(default_factory=list)  # API keys for integrations
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "organization": self.organization,
            "email": self.email,
            "phone": self.phone,
            "groups": [g.value for g in self.groups],
            "role": self.role.value,
            "regions": self.regions,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "preferred_channels": self.preferred_channels,
            "notification_schedule": self.notification_schedule,
            "subscribed_alert_types": list(self.subscribed_alert_types),
            "webhook_endpoints": self.webhook_endpoints,
            "api_keys": self.api_keys,
            "metadata": self.metadata,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stakeholder':
        """Create stakeholder from dictionary representation."""
        # Handle enum lists
        if "groups" in data and isinstance(data["groups"], list):
            data["groups"] = [StakeholderGroup(g) if isinstance(g, str) else g for g in data["groups"]]
            
        # Handle single enum
        if "role" in data and isinstance(data["role"], str):
            data["role"] = StakeholderRole(data["role"])
            
        # Handle set conversion
        if "subscribed_alert_types" in data and isinstance(data["subscribed_alert_types"], list):
            data["subscribed_alert_types"] = set(data["subscribed_alert_types"])
            
        return cls(**data)