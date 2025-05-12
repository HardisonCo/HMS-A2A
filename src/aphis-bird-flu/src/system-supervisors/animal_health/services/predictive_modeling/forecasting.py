"""
Forecasting service for avian influenza outbreak prediction.

This module provides a unified interface for generating forecasts using
various underlying predictive models. It handles model selection,
ensemble techniques, and forecast evaluation.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Type, Union
from datetime import datetime, timedelta
import numpy as np
from scipy import stats
import pandas as pd
import joblib
import os

from ...models.base import GeoLocation, GeoRegion
from ...models.case import Case, VirusSubtype
from ...models.surveillance import SurveillanceSite
from .spatial_models import (
    SpatialSpreadModel, 
    DistanceBasedSpreadModel, 
    NetworkBasedSpreadModel,
    GaussianProcessSpatioTemporalModel
)

logger = logging.getLogger(__name__)


class ForecastManager:
    """
    Manages multiple forecast models and generates ensemble predictions.
    """
    
    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize the forecast manager.
        
        Args:
            models_dir: Directory to save/load serialized models
        """
        self.models: Dict[str, SpatialSpreadModel] = {}
        self.models_dir = models_dir
        self.model_weights: Dict[str, float] = {}
        self.evaluation_metrics: Dict[str, Dict[str, float]] = {}
    
    def add_model(self, 
                 model: SpatialSpreadModel, 
                 model_id: Optional[str] = None,
                 weight: float = 1.0) -> str:
        """
        Add a predictive model to the manager.
        
        Args:
            model: A spatial spread model instance
            model_id: Optional identifier for the model
            weight: Weight for ensemble predictions (default: 1.0)
            
        Returns:
            The model_id (generated if not provided)
        """
        if model_id is None:
            model_id = f"{model.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.models[model_id] = model
        self.model_weights[model_id] = weight
        return model_id
    
    def train_models(self, 
                    historical_cases: List[Case],
                    regions: List[GeoRegion],
                    **kwargs) -> None:
        """
        Train all registered models.
        
        Args:
            historical_cases: List of historical case data
            regions: List of geographical regions
            **kwargs: Additional parameters to pass to model fitting methods
        """
        for model_id, model in self.models.items():
            logger.info(f"Training model: {model_id}")
            try:
                model.fit(historical_cases, regions, **kwargs)
                logger.info(f"Successfully trained model: {model_id}")
            except Exception as e:
                logger.error(f"Error training model {model_id}: {str(e)}")
    
    def generate_forecast(self,
                         current_cases: List[Case],
                         regions: List[GeoRegion],
                         days_ahead: int = 7,
                         use_ensemble: bool = True,
                         selected_models: Optional[List[str]] = None,
                         **kwargs) -> Dict[str, Any]:
        """
        Generate forecasts using either a single model, selected models, or an ensemble.
        
        Args:
            current_cases: Current active cases
            regions: List of geographical regions
            days_ahead: Number of days to predict ahead
            use_ensemble: Whether to use ensemble predictions
            selected_models: List of model IDs to use (if not using all)
            **kwargs: Additional parameters to pass to models
            
        Returns:
            Dictionary containing forecast results:
                - risk_by_region: Dictionary mapping region IDs to risk scores
                - predicted_case_count: Estimated number of new cases by region
                - confidence_intervals: Confidence intervals for predictions
                - model_predictions: Individual model predictions if use_ensemble is True
        """
        if not self.models:
            raise ValueError("No models registered with forecast manager")
        
        # Determine which models to use
        models_to_use = {}
        if selected_models:
            for model_id in selected_models:
                if model_id in self.models:
                    models_to_use[model_id] = self.models[model_id]
                else:
                    logger.warning(f"Model {model_id} not found")
        else:
            models_to_use = self.models
        
        if not models_to_use:
            raise ValueError("No valid models selected for forecast")
        
        # Generate predictions from each model
        model_predictions = {}
        for model_id, model in models_to_use.items():
            if not hasattr(model, 'fitted') or not model.fitted:
                logger.warning(f"Model {model_id} has not been fitted. Skipping.")
                continue
                
            try:
                prediction = model.predict(current_cases, regions, days_ahead, **kwargs)
                model_predictions[model_id] = prediction
            except Exception as e:
                logger.error(f"Error generating prediction with model {model_id}: {str(e)}")
        
        if not model_predictions:
            raise ValueError("No models were able to generate predictions")
        
        # Return single model prediction if not using ensemble
        if not use_ensemble or len(model_predictions) == 1:
            model_id = list(model_predictions.keys())[0]
            result = model_predictions[model_id].copy()
            result["model_id"] = model_id
            return result
        
        # Create ensemble prediction
        return self._create_ensemble_prediction(model_predictions, regions)
    
    def _create_ensemble_prediction(self, 
                                   model_predictions: Dict[str, Dict[str, Any]],
                                   regions: List[GeoRegion]) -> Dict[str, Any]:
        """
        Create an ensemble prediction from multiple model outputs.
        
        Args:
            model_predictions: Dictionary of model predictions
            regions: List of geographical regions
            
        Returns:
            Ensemble prediction dictionary
        """
        # Initialize ensemble outputs
        ensemble_risk = {}
        ensemble_cases = {}
        ensemble_confidence = {}
        
        # Get all region IDs
        region_ids = [region.id for region in regions]
        
        # Combine predictions with weighted average
        total_weight = sum(self.model_weights.get(model_id, 1.0) 
                          for model_id in model_predictions.keys())
        
        # Default to equal weights if total is 0
        if total_weight == 0:
            equal_weight = 1.0 / len(model_predictions)
            weights = {model_id: equal_weight for model_id in model_predictions.keys()}
        else:
            weights = {model_id: self.model_weights.get(model_id, 1.0) / total_weight 
                      for model_id in model_predictions.keys()}
        
        # Combine predictions for each region
        for region_id in region_ids:
            # Weighted risk scores
            risk_values = []
            risk_weights = []
            
            # Weighted case predictions
            case_values = []
            case_weights = []
            
            # Confidence intervals for aggregation
            lower_bounds = []
            upper_bounds = []
            
            for model_id, prediction in model_predictions.items():
                weight = weights[model_id]
                
                # Risk scores
                if 'risk_by_region' in prediction and region_id in prediction['risk_by_region']:
                    risk = prediction['risk_by_region'][region_id]
                    risk_values.append(risk)
                    risk_weights.append(weight)
                
                # Case predictions
                case_key = 'predicted_case_count' if 'predicted_case_count' in prediction else 'predicted_cases'
                if case_key in prediction and region_id in prediction[case_key]:
                    cases = prediction[case_key][region_id]
                    case_values.append(cases)
                    case_weights.append(weight)
                
                # Confidence intervals
                if 'confidence_intervals' in prediction and region_id in prediction['confidence_intervals']:
                    lower, upper = prediction['confidence_intervals'][region_id]
                    lower_bounds.append(lower)
                    upper_bounds.append(upper)
            
            # Calculate ensemble values
            if risk_values and risk_weights:
                ensemble_risk[region_id] = np.average(risk_values, weights=risk_weights)
            
            if case_values and case_weights:
                ensemble_cases[region_id] = np.average(case_values, weights=case_weights)
            
            # Aggregate confidence intervals (taking min lower bound and max upper bound)
            if lower_bounds and upper_bounds:
                ensemble_confidence[region_id] = (min(lower_bounds), max(upper_bounds))
        
        return {
            'risk_by_region': ensemble_risk,
            'predicted_case_count': ensemble_cases,
            'confidence_intervals': ensemble_confidence,
            'model_predictions': model_predictions,
            'model_weights': weights
        }
    
    def evaluate_models(self, 
                       test_cases: List[Case],
                       historical_cases: List[Case],
                       regions: List[GeoRegion],
                       evaluation_window: int = 7,
                       **kwargs) -> Dict[str, Dict[str, float]]:
        """
        Evaluate model performance on test data.
        
        Args:
            test_cases: Cases to use for evaluation
            historical_cases: Historical cases used for making predictions
            regions: List of geographical regions
            evaluation_window: Days to include in evaluation window
            **kwargs: Additional parameters for predictions
            
        Returns:
            Dictionary of evaluation metrics by model
        """
        # Group test cases by date
        cases_by_date = {}
        for case in test_cases:
            case_date = datetime.fromisoformat(case.detection_date).date()
            if case_date not in cases_by_date:
                cases_by_date[case_date] = []
            cases_by_date[case_date].append(case)
        
        # Sort dates
        dates = sorted(cases_by_date.keys())
        if not dates:
            logger.warning("No test cases with valid dates for evaluation")
            return {}
        
        # Create evaluation windows
        evaluation_periods = []
        for i in range(len(dates) - evaluation_window):
            start_date = dates[i]
            end_date = dates[i + evaluation_window - 1]
            evaluation_periods.append((start_date, end_date))
        
        if not evaluation_periods:
            logger.warning(f"Insufficient test data for {evaluation_window}-day evaluation")
            return {}
        
        # Track metrics for each model
        metrics = {model_id: {
            'rmse': [],
            'mae': [],
            'bias': [],
            'sharpness': [],
            'calibration': []
        } for model_id in self.models}
        
        # Evaluate each model on each evaluation period
        for start_date, end_date in evaluation_periods:
            # Get historical cases before start date
            historical_cutoff = start_date - timedelta(days=1)
            train_cases = [case for case in historical_cases 
                         if datetime.fromisoformat(case.detection_date).date() <= historical_cutoff]
            
            # Get test cases in evaluation window
            test_window_cases = []
            for d in (start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)):
                if d in cases_by_date:
                    test_window_cases.extend(cases_by_date[d])
            
            # Count actual cases by region
            actual_cases = {}
            for case in test_window_cases:
                if hasattr(case, 'region_id'):
                    region_id = case.region_id
                    if region_id not in actual_cases:
                        actual_cases[region_id] = 0
                    actual_cases[region_id] += 1
            
            # Make predictions with each model
            for model_id, model in self.models.items():
                try:
                    # Train model on historical data up to start date
                    model.fit(train_cases, regions, **kwargs)
                    
                    # Generate predictions
                    days_ahead = (end_date - start_date).days + 1
                    predictions = model.predict(
                        [c for c in train_cases if datetime.fromisoformat(c.detection_date).date() >= historical_cutoff - timedelta(days=14)],
                        regions,
                        days_ahead,
                        **kwargs
                    )
                    
                    # Extract predicted cases
                    case_key = 'predicted_case_count' if 'predicted_case_count' in predictions else 'predicted_cases'
                    predicted_cases = predictions.get(case_key, {})
                    confidence_intervals = predictions.get('confidence_intervals', {})
                    
                    # Calculate metrics
                    errors = []
                    abs_errors = []
                    coverage = []
                    sharpness = []
                    
                    for region in regions:
                        region_id = region.id
                        actual = actual_cases.get(region_id, 0)
                        predicted = predicted_cases.get(region_id, 0)
                        
                        # Error metrics
                        error = predicted - actual
                        errors.append(error)
                        abs_errors.append(abs(error))
                        
                        # Coverage and sharpness
                        if region_id in confidence_intervals:
                            lower, upper = confidence_intervals[region_id]
                            is_covered = lower <= actual <= upper
                            interval_width = upper - lower
                            coverage.append(float(is_covered))
                            sharpness.append(interval_width)
                    
                    # Compute aggregate metrics
                    if errors:
                        metrics[model_id]['rmse'].append(np.sqrt(np.mean(np.square(errors))))
                        metrics[model_id]['mae'].append(np.mean(abs_errors))
                        metrics[model_id]['bias'].append(np.mean(errors))
                    
                    if coverage:
                        metrics[model_id]['calibration'].append(np.mean(coverage))
                    
                    if sharpness:
                        metrics[model_id]['sharpness'].append(np.mean(sharpness))
                    
                except Exception as e:
                    logger.error(f"Error evaluating model {model_id}: {str(e)}")
        
        # Compute average metrics
        result = {}
        for model_id, model_metrics in metrics.items():
            result[model_id] = {}
            for metric_name, values in model_metrics.items():
                if values:
                    result[model_id][metric_name] = np.mean(values)
        
        # Update manager's evaluation metrics
        self.evaluation_metrics = result
        
        # Update weights based on RMSE if available
        self._update_weights_from_metrics()
        
        return result
    
    def _update_weights_from_metrics(self) -> None:
        """
        Update model weights based on evaluation metrics.
        Models with lower RMSE get higher weights.
        """
        # Check if we have RMSE metrics for models
        rmse_values = {}
        for model_id, metrics in self.evaluation_metrics.items():
            if 'rmse' in metrics:
                rmse_values[model_id] = metrics['rmse']
        
        if not rmse_values:
            return
        
        # Convert RMSE to weights (lower RMSE = higher weight)
        max_rmse = max(rmse_values.values())
        for model_id, rmse in rmse_values.items():
            # Invert and normalize
            if max_rmse > 0:
                # Different weighting strategies can be used here
                # This one gives higher weights to models with lower RMSE
                self.model_weights[model_id] = (max_rmse / rmse) if rmse > 0 else max_rmse
    
    def save_models(self, directory: Optional[str] = None) -> None:
        """
        Save all models to disk.
        
        Args:
            directory: Directory to save models, defaults to self.models_dir
        """
        save_dir = directory or self.models_dir
        if not save_dir:
            raise ValueError("No save directory specified")
        
        os.makedirs(save_dir, exist_ok=True)
        
        for model_id, model in self.models.items():
            try:
                model_path = os.path.join(save_dir, f"{model_id}.joblib")
                joblib.dump(model, model_path)
                logger.info(f"Saved model {model_id} to {model_path}")
            except Exception as e:
                logger.error(f"Error saving model {model_id}: {str(e)}")
    
    def load_models(self, directory: Optional[str] = None) -> None:
        """
        Load all models from disk.
        
        Args:
            directory: Directory to load models from, defaults to self.models_dir
        """
        load_dir = directory or self.models_dir
        if not load_dir:
            raise ValueError("No load directory specified")
        
        if not os.path.exists(load_dir):
            logger.warning(f"Model directory {load_dir} does not exist")
            return
        
        # Find all joblib files
        model_files = [f for f in os.listdir(load_dir) if f.endswith('.joblib')]
        
        for model_file in model_files:
            try:
                model_path = os.path.join(load_dir, model_file)
                model = joblib.load(model_path)
                
                # Get model ID from filename
                model_id = os.path.splitext(model_file)[0]
                
                self.models[model_id] = model
                if model_id not in self.model_weights:
                    self.model_weights[model_id] = 1.0
                
                logger.info(f"Loaded model {model_id} from {model_path}")
            except Exception as e:
                logger.error(f"Error loading model {model_file}: {str(e)}")


class ForecastService:
    """
    Service for generating and managing avian influenza outbreak forecasts.
    """
    
    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize the forecast service.
        
        Args:
            models_dir: Directory to save/load serialized models
        """
        self.forecast_manager = ForecastManager(models_dir)
        self._initialize_default_models()
    
    def _initialize_default_models(self) -> None:
        """Initialize a set of default models for forecasting."""
        # Distance-based model
        distance_model = DistanceBasedSpreadModel(
            distance_decay=2.0,
            transmission_threshold=100.0,
            time_window=14
        )
        self.forecast_manager.add_model(distance_model, "distance_based")
        
        # Gaussian Process model
        gp_model = GaussianProcessSpatioTemporalModel(
            spatial_length_scale=50.0,
            temporal_length_scale=7.0,
            nugget=0.05
        )
        self.forecast_manager.add_model(gp_model, "gaussian_process")
    
    def add_network_model(self, network_data: Dict[str, float], network_type: str = "migration") -> str:
        """
        Add a network-based model using provided network data.
        
        Args:
            network_data: Dictionary of network connection weights
            network_type: Type of network (migration, trade, transport)
            
        Returns:
            The model ID
        """
        network_model = NetworkBasedSpreadModel(network_type=network_type)
        return self.forecast_manager.add_model(
            network_model, 
            f"network_{network_type}"
        )
    
    def train_models(self, historical_cases: List[Case], regions: List[GeoRegion], **kwargs) -> None:
        """
        Train all available models.
        
        Args:
            historical_cases: Historical case data
            regions: List of geographical regions
            **kwargs: Additional training parameters
        """
        self.forecast_manager.train_models(historical_cases, regions, **kwargs)
    
    def generate_forecast(self, 
                         current_cases: List[Case],
                         regions: List[GeoRegion],
                         days_ahead: int = 7,
                         use_ensemble: bool = True,
                         **kwargs) -> Dict[str, Any]:
        """
        Generate a forecast for the specified period.
        
        Args:
            current_cases: Current active cases
            regions: List of geographical regions
            days_ahead: Number of days to predict ahead
            use_ensemble: Whether to use ensemble predictions
            **kwargs: Additional forecast parameters
            
        Returns:
            Forecast results
        """
        return self.forecast_manager.generate_forecast(
            current_cases=current_cases,
            regions=regions,
            days_ahead=days_ahead,
            use_ensemble=use_ensemble,
            **kwargs
        )
    
    def evaluate_models(self, 
                      test_cases: List[Case],
                      historical_cases: List[Case],
                      regions: List[GeoRegion],
                      **kwargs) -> Dict[str, Dict[str, float]]:
        """
        Evaluate model performance.
        
        Args:
            test_cases: Cases to use for evaluation
            historical_cases: Historical cases for training/prediction
            regions: List of geographical regions
            **kwargs: Additional evaluation parameters
            
        Returns:
            Evaluation metrics by model
        """
        return self.forecast_manager.evaluate_models(
            test_cases=test_cases,
            historical_cases=historical_cases,
            regions=regions,
            **kwargs
        )
    
    def get_risk_map_data(self, 
                        forecast_results: Dict[str, Any], 
                        include_predictions: bool = True) -> Dict[str, Any]:
        """
        Process forecast results into a format suitable for risk map visualization.
        
        Args:
            forecast_results: Results from generate_forecast
            include_predictions: Whether to include detailed predictions
            
        Returns:
            Formatted data for risk map visualization
        """
        risk_by_region = forecast_results.get('risk_by_region', {})
        predicted_cases = forecast_results.get(
            'predicted_case_count', 
            forecast_results.get('predicted_cases', {})
        )
        confidence_intervals = forecast_results.get('confidence_intervals', {})
        
        # Convert to risk levels for visualization
        risk_levels = {}
        for region_id, risk in risk_by_region.items():
            # Categorize risk into levels
            if risk < 0.2:
                level = "low"
            elif risk < 0.4:
                level = "moderate_low"
            elif risk < 0.6:
                level = "moderate"
            elif risk < 0.8:
                level = "moderate_high"
            else:
                level = "high"
            
            risk_levels[region_id] = level
        
        result = {
            'risk_levels': risk_levels,
            'raw_risk_scores': risk_by_region,
        }
        
        if include_predictions:
            result['predicted_cases'] = predicted_cases
            result['confidence_intervals'] = confidence_intervals
        
        return result
    
    def save_models(self, directory: Optional[str] = None) -> None:
        """
        Save all models to disk.
        
        Args:
            directory: Directory to save models
        """
        self.forecast_manager.save_models(directory)
    
    def load_models(self, directory: Optional[str] = None) -> None:
        """
        Load all models from disk.
        
        Args:
            directory: Directory to load models from
        """
        self.forecast_manager.load_models(directory)