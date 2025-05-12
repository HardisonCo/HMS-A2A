"""
Human Disease Surveillance service module initialization.
Exports key components for direct import from the module.
"""

from .surveillance_service import HumanDiseaseSurveillanceService
from .repository import HumanDiseaseRepository
from .adapters import HealthcareSystemAdapter, PublicHealthReportingAdapter