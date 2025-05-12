"""
Contact Tracing service module initialization.
Exports key components for direct import from the module.
"""

from .tracing_service import ContactTracingService
from .repository import ContactRepository
from .adapters import NotificationAdapter