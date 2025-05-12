"""
Interagency Data Federation Module

This module implements the federation hub and related components for enabling
data sharing and coordination between CDC, EPA, FEMA, and other agencies.
"""

from .core import FederationHub, AgencyRegistration, get_federation_hub
from .adapters import (
    FederationAdapter, CDCFederationAdapter, EPAFederationAdapter, FEMAFederationAdapter
)
from .services import (
    FederatedQueryService, CrossAgencyAlertService, Alert,
    ResourceCoordinationService, ResourceRequest, ResourceAllocation,
    JointAnalysisService, AnalysisRequest, AnalysisResult
)

__all__ = [
    'FederationHub',
    'AgencyRegistration',
    'get_federation_hub',
    'FederationAdapter',
    'CDCFederationAdapter',
    'EPAFederationAdapter',
    'FEMAFederationAdapter',
    'FederatedQueryService',
    'CrossAgencyAlertService',
    'Alert',
    'ResourceCoordinationService',
    'ResourceRequest',
    'ResourceAllocation',
    'JointAnalysisService',
    'AnalysisRequest',
    'AnalysisResult'
]