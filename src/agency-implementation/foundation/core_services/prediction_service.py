"""Prediction service interface for forecasting future patterns and trends."""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .base_service import BaseService

class PredictionService(BaseService):
    """Abstract base class for prediction and forecasting services.
    
    This service is responsible for developing and running predictive models
    that forecast future events, trends, or patterns based on historical data
    and current conditions.
    """
    
    def default_config(self) -> Dict[str, Any]:
        """Get the default configuration for prediction.
        
        Returns:
            Dictionary with default configuration values
        """
        return {
            "forecast_horizon_days": 14,
            "prediction_intervals": [0.5, 0.8, 0.95],
            "ensemble_weights": {"statistical": 0.4, "mechanistic": 0.4, "ml": 0.2},
            "training_window_days": 365,
            "include_uncertainty": True,
            "validation_method": "cross_validation"
        }
    
    @abstractmethod
    def forecast_time_series(self, historical_data: List[Dict[str, Any]], 
                          horizon_days: int,
                          parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate time series forecasts for a specified horizon.
        
        Args:
            historical_data: Historical time series data
            horizon_days: Number of days to forecast
            parameters: Optional parameters for the forecast
            
        Returns:
            Dictionary with forecast results and metadata
        """
        pass
    
    @abstractmethod
    def forecast_spatial_spread(self, cases: List[Dict[str, Any]],
                             regions: List[Dict[str, Any]],
                             horizon_days: int,
                             parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Forecast the spatial spread of cases across regions.
        
        Args:
            cases: Historical case data with geo coordinates
            regions: Regions for prediction
            horizon_days: Number of days to forecast
            parameters: Optional parameters for the forecast
            
        Returns:
            Dictionary with spatial forecast results and metadata
        """
        pass
    
    @abstractmethod
    def predict_risk_levels(self, regions: List[Dict[str, Any]],
                         context_data: Dict[str, Any],
                         horizon_days: int,
                         parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
        """Predict risk levels for specific regions.
        
        Args:
            regions: Regions for risk prediction
            context_data: Contextual data for risk assessment
            horizon_days: Number of days to forecast
            parameters: Optional parameters for the prediction
            
        Returns:
            Dictionary mapping region IDs to risk predictions
        """
        pass
    
    @abstractmethod
    def forecast_impact(self, scenario: Dict[str, Any],
                     parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Forecast the potential impact of a scenario.
        
        Args:
            scenario: Scenario description and parameters
            parameters: Optional additional parameters
            
        Returns:
            Dictionary with impact forecasts and metadata
        """
        pass
    
    @abstractmethod
    def evaluate_forecast_accuracy(self, forecast: Dict[str, Any],
                                actual_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate the accuracy of a previous forecast.
        
        Args:
            forecast: Previous forecast to evaluate
            actual_data: Actual data that occurred after the forecast
            
        Returns:
            Dictionary with accuracy metrics
        """
        pass
    
    @abstractmethod
    def get_ensemble_forecast(self, models: List[str],
                           historical_data: List[Dict[str, Any]],
                           horizon_days: int,
                           parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate an ensemble forecast combining multiple models.
        
        Args:
            models: List of model identifiers to include
            historical_data: Historical data for forecasting
            horizon_days: Number of days to forecast
            parameters: Optional parameters including weights
            
        Returns:
            Dictionary with ensemble forecast results
        """
        pass
