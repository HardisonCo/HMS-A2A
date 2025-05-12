"""
Federation Framework for secure cross-agency data sharing and collaboration.

This package provides the necessary components to enable federated queries,
data synchronization, access control, and audit logging across agencies.
"""

from federation.manager import FederationManager
from federation.models import Agency, FederationPolicy, DatasetSchema
from federation.exceptions import FederationError, AuthorizationError, SynchronizationError

__version__ = "0.1.0"
__all__ = [
    "FederationManager",
    "Agency",
    "FederationPolicy",
    "DatasetSchema",
    "FederationError",
    "AuthorizationError",
    "SynchronizationError"
]