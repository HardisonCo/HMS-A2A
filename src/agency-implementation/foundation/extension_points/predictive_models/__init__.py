"""
Predictive Models Extension Points

This module defines interfaces for extending the system with custom predictive models.
"""

from typing import Dict, List, Any, Optional, Union, TypeVar, Generic
import abc
from ..base import BaseExtensionPoint

# Generic type for model outputs
T = TypeVar('T')


class PredictiveModelExtensionPoint(BaseExtensionPoint, Generic[T]):
    """
    Extension point for custom predictive models.
    
    Allows agencies to integrate custom predictive models for forecasting,
    risk assessment, and other predictive analytics needs.
    """
    
    _extension_type: str = "predictive_model"
    
    @abc.abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the predictive model.
        
        Args:
            config: Configuration parameters for the model
            
        Returns:
            bool: True if initialization is successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def shutdown(self) -> None:
        """
        Clean up resources used by the predictive model.
        """
        pass
    
    @abc.abstractmethod
    async def train(self, training_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train the predictive model.
        
        Args:
            training_data: The data to train the model on
            options: Training options
            
        Returns:
            Dict with training results and metrics
        """
        pass
    
    @abc.abstractmethod
    async def predict(self, input_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate predictions using the model.
        
        Args:
            input_data: The input data for predictions
            options: Prediction options
            
        Returns:
            Dict with prediction results
        """
        pass
    
    @abc.abstractmethod
    async def evaluate(self, test_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the model on test data.
        
        Args:
            test_data: The data to evaluate the model on
            options: Evaluation options
            
        Returns:
            Dict with evaluation metrics
        """
        pass
    
    @abc.abstractmethod
    async def save_model(self, path: str) -> bool:
        """
        Save the trained model to a file.
        
        Args:
            path: The file path to save the model to
            
        Returns:
            bool: True if saving is successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def load_model(self, path: str) -> bool:
        """
        Load a trained model from a file.
        
        Args:
            path: The file path to load the model from
            
        Returns:
            bool: True if loading is successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about this predictive model.
        
        Returns:
            Dict with model information
        """
        pass
    
    @abc.abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Get the schema of input data expected by this model.
        
        Returns:
            Dict describing the required input structure
        """
        pass
    
    @abc.abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Get the schema of output data produced by this model.
        
        Returns:
            Dict describing the output structure
        """
        pass
    
    @abc.abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input data against the expected schema.
        
        Args:
            input_data: The data to validate
            
        Returns:
            Dict with validation results
        """
        pass
    
    @abc.abstractmethod
    def get_hyperparameters(self) -> Dict[str, Any]:
        """
        Get the current hyperparameters of the model.
        
        Returns:
            Dict of hyperparameter values
        """
        pass
    
    @abc.abstractmethod
    async def tune_hyperparameters(self, training_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tune the model's hyperparameters.
        
        Args:
            training_data: The data to use for tuning
            options: Tuning options
            
        Returns:
            Dict with tuning results and optimal hyperparameters
        """
        pass


# Import specific predictive model implementations for easy access
from .time_series_forecasting import TimeSeriesForecaster
from .disease_spread_model import DiseaseSpreadModel
from .risk_assessment_model import RiskAssessmentModel
from .classification_model import ClassificationModel

__all__ = [
    'PredictiveModelExtensionPoint',
    'TimeSeriesForecaster',
    'DiseaseSpreadModel',
    'RiskAssessmentModel',
    'ClassificationModel',
]