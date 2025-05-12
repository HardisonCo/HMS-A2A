"""
Documentation Integration Package

This package provides integration with HMS-DOC and HMS-MFE components for
publishing clinical trial data, abstractions, and documentation.
"""

from .doc_integration_service import DocIntegrationService, create_doc_integration_service
from .integration_coordinator import IntegrationCoordinator, coordinator

__all__ = [
    'DocIntegrationService',
    'create_doc_integration_service',
    'IntegrationCoordinator',
    'coordinator'
]