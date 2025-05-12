"""
Predictive modeling services for avian influenza outbreaks.

This package provides models and services for predicting the spread
of avian influenza outbreaks, enabling proactive resource allocation
and rapid response to emerging threats.
"""

from .spatial_models import (
    SpatialSpreadModel,
    DistanceBasedSpreadModel,
    NetworkBasedSpreadModel,
    GaussianProcessSpatioTemporalModel
)

from .forecasting import (
    ForecastManager,
    ForecastService
)

__all__ = [
    'SpatialSpreadModel',
    'DistanceBasedSpreadModel',
    'NetworkBasedSpreadModel',
    'GaussianProcessSpatioTemporalModel',
    'ForecastManager',
    'ForecastService'
]