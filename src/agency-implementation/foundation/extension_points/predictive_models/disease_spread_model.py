"""
Disease Spread Model

Extension point implementation for disease spread predictions.
"""

from typing import Dict, List, Any, Optional, Union, TypeVar, Generic
import logging
import json
import os
import pickle
import asyncio
import numpy as np
from datetime import datetime, timedelta
from . import PredictiveModelExtensionPoint
from .. import base

logger = logging.getLogger(__name__)

@base.BaseExtensionPoint.extension_point("predictive_model", "disease_spread")
class DiseaseSpreadModel(PredictiveModelExtensionPoint):
    """Implementation of predictive model extension point for disease spread forecasting."""
    
    def __init__(self):
        self.model = None
        self.model_type = None
        self.trained = False
        self.feature_columns = []
        self.target_column = ""
        self.spatial_columns = []
        self.temporal_column = ""
        self.hyperparameters = {}
        self.metrics = {}
        self.is_initialized = False
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the disease spread model.
        
        Args:
            config: Configuration parameters for the model
            
        Returns:
            bool: True if initialization successful
        """
        try:
            # Model type
            self.model_type = config.get("model_type", "seir")
            
            # Feature configuration
            self.feature_columns = config.get("feature_columns", [])
            self.target_column = config.get("target_column", "cases")
            self.spatial_columns = config.get("spatial_columns", ["region_id"])
            self.temporal_column = config.get("temporal_column", "date")
            
            # Initial hyperparameters
            self.hyperparameters = config.get("hyperparameters", {})
            
            # Set default hyperparameters based on model type
            if self.model_type == "seir":
                default_params = {
                    "beta": 0.3,  # Infection rate
                    "sigma": 0.2,  # Incubation rate
                    "gamma": 0.1,  # Recovery rate
                    "mu": 0.001,   # Birth/death rate
                    "N": 1000000,  # Population size
                }
                self.hyperparameters = {**default_params, **self.hyperparameters}
            elif self.model_type == "sir":
                default_params = {
                    "beta": 0.3,    # Infection rate
                    "gamma": 0.1,   # Recovery rate
                    "N": 1000000,   # Population size
                }
                self.hyperparameters = {**default_params, **self.hyperparameters}
            elif self.model_type == "ml":
                default_params = {
                    "learning_rate": 0.01,
                    "max_depth": 5,
                    "n_estimators": 100,
                }
                self.hyperparameters = {**default_params, **self.hyperparameters}
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing disease spread model: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Clean up resources used by the model."""
        self.model = None
        self.trained = False
        self.is_initialized = False
    
    async def train(self, training_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train the disease spread model.
        
        Args:
            training_data: The data to train the model on
            options: Training options
            
        Returns:
            Dict with training results and metrics
        """
        if not self.is_initialized:
            raise RuntimeError("Disease spread model not initialized")
            
        try:
            # Extract data
            data = training_data.get("data", [])
            if not data:
                return {
                    "success": False,
                    "error": "No training data provided",
                }
                
            # Extract options
            validation_split = options.get("validation_split", 0.2)
            random_seed = options.get("random_seed", 42)
            
            # Update hyperparameters if provided
            if "hyperparameters" in options:
                self.hyperparameters.update(options["hyperparameters"])
            
            # Different training logic based on model type
            if self.model_type in ["seir", "sir"]:
                # For compartmental models, we fit the parameters
                await self._train_compartmental_model(data, options)
            elif self.model_type == "ml":
                # For ML models, we train a regression model
                await self._train_ml_model(data, options)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported model type: {self.model_type}",
                }
                
            self.trained = True
            
            return {
                "success": True,
                "metrics": self.metrics,
                "hyperparameters": self.hyperparameters,
            }
            
        except Exception as e:
            logger.error(f"Error training disease spread model: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def _train_compartmental_model(self, data: List[Dict[str, Any]], options: Dict[str, Any]) -> None:
        """Train a compartmental model (SIR or SEIR)."""
        # Group data by region
        regions = {}
        for row in data:
            region_id = self._get_region_id(row)
            if region_id not in regions:
                regions[region_id] = []
            regions[region_id].append(row)
        
        # For each region, fit the model parameters
        all_metrics = {}
        for region_id, region_data in regions.items():
            # Sort by date
            region_data.sort(key=lambda x: x.get(self.temporal_column, ""))
            
            # Extract time series of cases
            cases = [row.get(self.target_column, 0) for row in region_data]
            population = self.hyperparameters.get("N", 1000000)
            
            # Use a simple optimization to fit parameters
            if self.model_type == "sir":
                # Simplified SIR model fitting
                best_params, metrics = self._fit_sir_params(cases, population)
                all_metrics[region_id] = metrics
                
                # Store the best parameters for each region
                if "region_params" not in self.hyperparameters:
                    self.hyperparameters["region_params"] = {}
                self.hyperparameters["region_params"][region_id] = best_params
                
            elif self.model_type == "seir":
                # Simplified SEIR model fitting
                best_params, metrics = self._fit_seir_params(cases, population)
                all_metrics[region_id] = metrics
                
                # Store the best parameters for each region
                if "region_params" not in self.hyperparameters:
                    self.hyperparameters["region_params"] = {}
                self.hyperparameters["region_params"][region_id] = best_params
        
        # Compute average metrics across regions
        avg_metrics = {}
        for metric in ["mse", "mae", "r2"]:
            if all(metric in metrics for metrics in all_metrics.values()):
                avg_metrics[metric] = sum(metrics[metric] for metrics in all_metrics.values()) / len(all_metrics)
        
        self.metrics = {
            "overall": avg_metrics,
            "by_region": all_metrics,
        }
        
        # Store the model (in this case, just the hyperparameters)
        self.model = {
            "type": self.model_type,
            "hyperparameters": self.hyperparameters,
        }
    
    def _fit_sir_params(self, cases: List[float], population: int) -> tuple:
        """
        Fit SIR model parameters to observed cases.
        
        This is a simplified implementation for demonstration purposes.
        A real implementation would use more sophisticated optimization.
        """
        # Convert cases to S, I, R fractions
        n = len(cases)
        I = [c / population for c in cases]
        
        # Simple parameter estimation
        # In a real implementation, you would use proper optimization techniques
        
        # Estimate beta and gamma that minimize prediction error
        best_mse = float('inf')
        best_params = {"beta": 0.3, "gamma": 0.1}
        
        # Grid search over parameter space
        for beta in np.linspace(0.1, 0.5, 5):
            for gamma in np.linspace(0.01, 0.2, 5):
                # Initial conditions
                s, i, r = 1 - I[0], I[0], 0
                
                # Run SIR model
                predictions = [i]
                for t in range(1, n):
                    ds = -beta * s * i
                    di = beta * s * i - gamma * i
                    dr = gamma * i
                    
                    s += ds
                    i += di
                    r += dr
                    
                    predictions.append(i)
                
                # Calculate error
                mse = sum((I[t] - predictions[t])**2 for t in range(n)) / n
                
                if mse < best_mse:
                    best_mse = mse
                    best_params = {"beta": beta, "gamma": gamma}
        
        # Calculate additional metrics
        predictions = []
        s, i, r = 1 - I[0], I[0], 0
        for t in range(n):
            predictions.append(i * population)
            
            if t < n - 1:
                ds = -best_params["beta"] * s * i
                di = best_params["beta"] * s * i - best_params["gamma"] * i
                dr = best_params["gamma"] * i
                
                s += ds
                i += di
                r += dr
        
        # Calculate metrics
        mse = sum((cases[t] - predictions[t])**2 for t in range(n)) / n
        mae = sum(abs(cases[t] - predictions[t]) for t in range(n)) / n
        
        # Calculate R^2
        mean_cases = sum(cases) / n
        ss_tot = sum((cases[t] - mean_cases)**2 for t in range(n))
        ss_res = sum((cases[t] - predictions[t])**2 for t in range(n))
        r2 = 1 - (ss_res / ss_tot if ss_tot > 0 else 0)
        
        metrics = {
            "mse": mse,
            "mae": mae,
            "r2": r2,
        }
        
        return best_params, metrics
    
    def _fit_seir_params(self, cases: List[float], population: int) -> tuple:
        """
        Fit SEIR model parameters to observed cases.
        
        This is a simplified implementation for demonstration purposes.
        A real implementation would use more sophisticated optimization.
        """
        # This would be similar to _fit_sir_params but with additional parameters
        # For simplicity, we'll reuse the SIR logic with some default values for the SEIR-specific parameters
        sir_params, metrics = self._fit_sir_params(cases, population)
        seir_params = {
            **sir_params,
            "sigma": 0.2,  # Default incubation rate
        }
        
        return seir_params, metrics
    
    async def _train_ml_model(self, data: List[Dict[str, Any]], options: Dict[str, Any]) -> None:
        """Train a machine learning model for disease spread prediction."""
        try:
            # For demonstration, we'll use a simple regression model
            # In a real implementation, you would use more sophisticated models
            
            # First, prepare the features and target
            features = []
            targets = []
            
            for row in data:
                feature_vector = [row.get(col, 0) for col in self.feature_columns]
                target_value = row.get(self.target_column, 0)
                
                features.append(feature_vector)
                targets.append(target_value)
            
            # Split into training and validation sets
            validation_split = options.get("validation_split", 0.2)
            split_idx = int(len(features) * (1 - validation_split))
            
            train_features = features[:split_idx]
            train_targets = targets[:split_idx]
            val_features = features[split_idx:]
            val_targets = targets[split_idx:]
            
            # Train a model
            # For demonstration, we'll create a mock ML model
            model = self._create_mock_ml_model(self.hyperparameters)
            
            # Train the model
            model.fit(train_features, train_targets)
            
            # Evaluate on validation data
            val_predictions = model.predict(val_features)
            
            # Calculate metrics
            mse = sum((val_targets[i] - val_predictions[i])**2 for i in range(len(val_targets))) / len(val_targets)
            mae = sum(abs(val_targets[i] - val_predictions[i]) for i in range(len(val_targets))) / len(val_targets)
            
            # Calculate R^2
            mean_val_target = sum(val_targets) / len(val_targets)
            ss_tot = sum((val_targets[i] - mean_val_target)**2 for i in range(len(val_targets)))
            ss_res = sum((val_targets[i] - val_predictions[i])**2 for i in range(len(val_targets)))
            r2 = 1 - (ss_res / ss_tot if ss_tot > 0 else 0)
            
            self.metrics = {
                "validation": {
                    "mse": mse,
                    "mae": mae,
                    "r2": r2,
                }
            }
            
            # Store the trained model
            self.model = model
            
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
            raise
    
    def _create_mock_ml_model(self, hyperparameters: Dict[str, Any]) -> Any:
        """
        Create a mock ML model for demonstration purposes.
        
        In a real implementation, you would use a proper ML library like scikit-learn.
        """
        # Mock model class
        class MockModel:
            def __init__(self, params):
                self.params = params
                self.weights = None
            
            def fit(self, X, y):
                # Simplified linear regression
                n_features = len(X[0])
                self.weights = [0] * (n_features + 1)  # Including bias
                
                # Simple gradient descent
                learning_rate = self.params.get("learning_rate", 0.01)
                n_iterations = 100
                
                for _ in range(n_iterations):
                    predictions = [self._predict_single(x) for x in X]
                    errors = [predictions[i] - y[i] for i in range(len(y))]
                    
                    # Update bias
                    self.weights[0] -= learning_rate * sum(errors) / len(errors)
                    
                    # Update feature weights
                    for j in range(n_features):
                        gradient = sum(errors[i] * X[i][j] for i in range(len(X))) / len(X)
                        self.weights[j + 1] -= learning_rate * gradient
            
            def _predict_single(self, x):
                # Linear prediction
                prediction = self.weights[0]  # Bias
                for j, xj in enumerate(x):
                    prediction += self.weights[j + 1] * xj
                return prediction
            
            def predict(self, X):
                return [self._predict_single(x) for x in X]
        
        return MockModel(hyperparameters)
    
    def _get_region_id(self, row: Dict[str, Any]) -> str:
        """Extract region ID from a data row."""
        if len(self.spatial_columns) == 1:
            return str(row.get(self.spatial_columns[0], ""))
        else:
            return "_".join(str(row.get(col, "")) for col in self.spatial_columns)
    
    async def predict(self, input_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate disease spread predictions.
        
        Args:
            input_data: The input data for predictions
            options: Prediction options
            
        Returns:
            Dict with prediction results
        """
        if not self.is_initialized:
            raise RuntimeError("Disease spread model not initialized")
            
        if not self.trained:
            raise RuntimeError("Disease spread model not trained")
            
        try:
            # Extract options
            forecast_days = options.get("forecast_days", 14)
            include_history = options.get("include_history", False)
            
            # Validate input data
            validation_result = self.validate_input(input_data)
            if not validation_result.get("valid", False):
                return {
                    "success": False,
                    "error": f"Invalid input data: {validation_result.get('errors')}",
                }
            
            # Generate predictions based on model type
            if self.model_type in ["seir", "sir"]:
                # For compartmental models
                prediction_results = self._predict_compartmental(input_data, forecast_days, include_history)
            elif self.model_type == "ml":
                # For ML models
                prediction_results = self._predict_ml(input_data, forecast_days, include_history)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported model type: {self.model_type}",
                }
                
            return {
                "success": True,
                "predictions": prediction_results,
            }
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def _predict_compartmental(self, input_data: Dict[str, Any], forecast_days: int, include_history: bool) -> Dict[str, Any]:
        """Generate predictions using compartmental models (SIR or SEIR)."""
        # Get the current state for each region
        regions_data = input_data.get("regions", {})
        predictions = {}
        
        for region_id, region_data in regions_data.items():
            # Get region-specific parameters, or use global parameters
            region_params = {}
            if "region_params" in self.hyperparameters and region_id in self.hyperparameters["region_params"]:
                region_params = self.hyperparameters["region_params"][region_id]
            else:
                # Use global parameters
                region_params = {k: v for k, v in self.hyperparameters.items() if k != "region_params"}
            
            # Get population size
            population = region_params.get("N", region_data.get("population", 1000000))
            
            # Get initial conditions
            initial_cases = region_data.get("current_cases", 0)
            initial_susceptible = population - initial_cases
            
            if self.model_type == "sir":
                # Simplified SIR model prediction
                beta = region_params.get("beta", 0.3)
                gamma = region_params.get("gamma", 0.1)
                
                # Initialize compartments
                S = [initial_susceptible / population]
                I = [initial_cases / population]
                R = [1 - S[0] - I[0]]
                
                # Run the model forward
                for _ in range(forecast_days):
                    s, i, r = S[-1], I[-1], R[-1]
                    
                    ds = -beta * s * i
                    di = beta * s * i - gamma * i
                    dr = gamma * i
                    
                    S.append(s + ds)
                    I.append(i + di)
                    R.append(r + dr)
                
                # Convert to actual numbers
                cases_forecast = [i * population for i in I]
                
                # Format predictions
                dates = self._generate_dates(region_data.get("current_date", datetime.now().strftime("%Y-%m-%d")), 
                                           forecast_days + 1)
                
                predictions[region_id] = {
                    "dates": dates,
                    "cases": cases_forecast,
                    "susceptible": [s * population for s in S],
                    "recovered": [r * population for r in R],
                }
                
            elif self.model_type == "seir":
                # SEIR model with an additional exposed compartment
                beta = region_params.get("beta", 0.3)
                sigma = region_params.get("sigma", 0.2)
                gamma = region_params.get("gamma", 0.1)
                
                # Initial conditions
                # Assume initial exposed is a fraction of cases
                initial_exposed = region_data.get("current_exposed", initial_cases * 0.5)
                initial_recovered = region_data.get("current_recovered", 0)
                
                S = [(population - initial_cases - initial_exposed - initial_recovered) / population]
                E = [initial_exposed / population]
                I = [initial_cases / population]
                R = [initial_recovered / population]
                
                # Run the model forward
                for _ in range(forecast_days):
                    s, e, i, r = S[-1], E[-1], I[-1], R[-1]
                    
                    ds = -beta * s * i
                    de = beta * s * i - sigma * e
                    di = sigma * e - gamma * i
                    dr = gamma * i
                    
                    S.append(s + ds)
                    E.append(e + de)
                    I.append(i + di)
                    R.append(r + dr)
                
                # Convert to actual numbers
                cases_forecast = [i * population for i in I]
                
                # Format predictions
                dates = self._generate_dates(region_data.get("current_date", datetime.now().strftime("%Y-%m-%d")), 
                                           forecast_days + 1)
                
                predictions[region_id] = {
                    "dates": dates,
                    "cases": cases_forecast,
                    "exposed": [e * population for e in E],
                    "susceptible": [s * population for s in S],
                    "recovered": [r * population for r in R],
                }
            
            # If not including history, remove the first element (current state)
            if not include_history:
                for key in predictions[region_id]:
                    predictions[region_id][key] = predictions[region_id][key][1:]
        
        return predictions
    
    def _predict_ml(self, input_data: Dict[str, Any], forecast_days: int, include_history: bool) -> Dict[str, Any]:
        """Generate predictions using ML models."""
        # Get the input features for each region
        regions_data = input_data.get("regions", {})
        predictions = {}
        
        for region_id, region_data in regions_data.items():
            # Get historical data for the region
            historical_data = region_data.get("historical_data", [])
            
            if not historical_data:
                logger.warning(f"No historical data for region {region_id}, skipping predictions")
                continue
            
            # Sort by date
            historical_data.sort(key=lambda x: x.get(self.temporal_column, ""))
            
            # Get the most recent date
            last_date = historical_data[-1].get(self.temporal_column, datetime.now().strftime("%Y-%m-%d"))
            
            # Generate dates for the forecast period
            forecast_dates = self._generate_dates(last_date, forecast_days + 1)[1:]  # Skip current date
            
            # For recursive forecasting, we'll need to update features with predictions
            forecast_data = []
            current_features = [historical_data[-1].get(col, 0) for col in self.feature_columns]
            
            # Generate predictions one day at a time
            for _ in range(forecast_days):
                # Predict next day's cases
                prediction = self.model.predict([current_features])[0]
                
                # Create a prediction record
                prediction_record = {
                    self.target_column: prediction,
                }
                
                forecast_data.append(prediction_record)
                
                # Update features for next iteration
                # This is a simplified approach; in reality, you would need to update 
                # all relevant features based on the model and domain knowledge
                
                # For demonstration, we'll just use a rolling window approach
                # assuming the last feature is the most recent cases
                if self.feature_columns:
                    # Shift features and add new prediction
                    current_features = current_features[1:] + [prediction]
            
            # Format predictions
            predictions[region_id] = {
                "dates": forecast_dates,
                "cases": [record.get(self.target_column, 0) for record in forecast_data],
            }
            
            # Include historical data if requested
            if include_history:
                historical_dates = [record.get(self.temporal_column, "") for record in historical_data]
                historical_cases = [record.get(self.target_column, 0) for record in historical_data]
                
                predictions[region_id]["dates"] = historical_dates + predictions[region_id]["dates"]
                predictions[region_id]["cases"] = historical_cases + predictions[region_id]["cases"]
        
        return predictions
    
    def _generate_dates(self, start_date: str, num_days: int) -> List[str]:
        """Generate a list of dates starting from start_date."""
        date_format = "%Y-%m-%d"
        start = datetime.strptime(start_date, date_format)
        return [(start + timedelta(days=i)).strftime(date_format) for i in range(num_days)]
    
    async def evaluate(self, test_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the model on test data.
        
        Args:
            test_data: The data to evaluate the model on
            options: Evaluation options
            
        Returns:
            Dict with evaluation metrics
        """
        if not self.is_initialized:
            raise RuntimeError("Disease spread model not initialized")
            
        if not self.trained:
            raise RuntimeError("Disease spread model not trained")
            
        try:
            # Extract test data
            data = test_data.get("data", [])
            if not data:
                return {
                    "success": False,
                    "error": "No test data provided",
                }
                
            # Group by region
            regions = {}
            for row in data:
                region_id = self._get_region_id(row)
                if region_id not in regions:
                    regions[region_id] = []
                regions[region_id].append(row)
            
            # Evaluate for each region
            results = {}
            for region_id, region_data in regions.items():
                # Sort by date
                region_data.sort(key=lambda x: x.get(self.temporal_column, ""))
                
                # Extract actual values
                actual_cases = [row.get(self.target_column, 0) for row in region_data]
                
                # Generate predictions
                # For compartmental models, we need to set up initial conditions
                if self.model_type in ["seir", "sir"]:
                    # Get first data point for initial conditions
                    first_point = region_data[0]
                    population = self.hyperparameters.get("N", 1000000)
                    
                    # Initial input for prediction
                    pred_input = {
                        "regions": {
                            region_id: {
                                "population": population,
                                "current_cases": first_point.get(self.target_column, 0),
                                "current_date": first_point.get(self.temporal_column, ""),
                            }
                        }
                    }
                    
                    # Predict for the length of the test data
                    pred_options = {
                        "forecast_days": len(region_data) - 1,
                        "include_history": True,
                    }
                    
                    pred_result = await self.predict(pred_input, pred_options)
                    
                    if pred_result.get("success", False):
                        predicted_cases = pred_result["predictions"][region_id]["cases"]
                        
                        # Calculate metrics
                        metrics = self._calculate_metrics(actual_cases, predicted_cases)
                        results[region_id] = metrics
                    
                elif self.model_type == "ml":
                    # For ML models, we need to extract features
                    features = []
                    for row in region_data:
                        feature_vector = [row.get(col, 0) for col in self.feature_columns]
                        features.append(feature_vector)
                    
                    # Generate predictions
                    predicted_cases = self.model.predict(features)
                    
                    # Calculate metrics
                    metrics = self._calculate_metrics(actual_cases, predicted_cases)
                    results[region_id] = metrics
            
            # Calculate overall metrics across regions
            overall_metrics = {}
            for metric in ["mse", "mae", "r2"]:
                if all(metric in metrics for metrics in results.values()):
                    overall_metrics[metric] = sum(metrics[metric] for metrics in results.values()) / len(results)
            
            return {
                "success": True,
                "metrics": {
                    "overall": overall_metrics,
                    "by_region": results,
                }
            }
            
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def _calculate_metrics(self, actual: List[float], predicted: List[float]) -> Dict[str, float]:
        """Calculate evaluation metrics."""
        n = min(len(actual), len(predicted))
        
        if n == 0:
            return {"error": "No data points to evaluate"}
            
        # Trim to same length
        actual = actual[:n]
        predicted = predicted[:n]
        
        # Calculate metrics
        mse = sum((actual[i] - predicted[i])**2 for i in range(n)) / n
        mae = sum(abs(actual[i] - predicted[i]) for i in range(n)) / n
        
        # Calculate R^2
        mean_actual = sum(actual) / n
        ss_tot = sum((actual[i] - mean_actual)**2 for i in range(n))
        ss_res = sum((actual[i] - predicted[i])**2 for i in range(n))
        r2 = 1 - (ss_res / ss_tot if ss_tot > 0 else 0)
        
        return {
            "mse": mse,
            "mae": mae,
            "r2": r2,
        }
    
    async def save_model(self, path: str) -> bool:
        """
        Save the trained model to a file.
        
        Args:
            path: The file path to save the model to
            
        Returns:
            bool: True if saving is successful
        """
        if not self.trained:
            raise RuntimeError("Cannot save untrained model")
            
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            
            # Create a model state dict to save
            model_state = {
                "model_type": self.model_type,
                "hyperparameters": self.hyperparameters,
                "feature_columns": self.feature_columns,
                "target_column": self.target_column,
                "spatial_columns": self.spatial_columns,
                "temporal_column": self.temporal_column,
                "metrics": self.metrics,
                "trained": self.trained,
            }
            
            # Save model-specific data
            if self.model_type in ["seir", "sir"]:
                # For compartmental models, we just save the parameters
                model_state["model"] = self.model
            elif self.model_type == "ml":
                # For ML models, we need to save the actual model object
                # In a real implementation, this would depend on the ML framework used
                model_state["model"] = pickle.dumps(self.model)
            
            # Save to file
            with open(path, 'wb') as f:
                pickle.dump(model_state, f)
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    async def load_model(self, path: str) -> bool:
        """
        Load a trained model from a file.
        
        Args:
            path: The file path to load the model from
            
        Returns:
            bool: True if loading is successful
        """
        try:
            if not os.path.exists(path):
                logger.error(f"Model file not found: {path}")
                return False
                
            # Load from file
            with open(path, 'rb') as f:
                model_state = pickle.load(f)
                
            # Restore model state
            self.model_type = model_state["model_type"]
            self.hyperparameters = model_state["hyperparameters"]
            self.feature_columns = model_state["feature_columns"]
            self.target_column = model_state["target_column"]
            self.spatial_columns = model_state["spatial_columns"]
            self.temporal_column = model_state["temporal_column"]
            self.metrics = model_state["metrics"]
            self.trained = model_state["trained"]
            
            # Restore model-specific data
            if self.model_type in ["seir", "sir"]:
                # For compartmental models, we just restore the parameters
                self.model = model_state["model"]
            elif self.model_type == "ml":
                # For ML models, we need to restore the actual model object
                # In a real implementation, this would depend on the ML framework used
                self.model = pickle.loads(model_state["model"])
                
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about this predictive model.
        
        Returns:
            Dict with model information
        """
        return {
            "name": "Disease Spread Model",
            "type": self.model_type,
            "version": "1.0.0",
            "description": "Predicts the spread of infectious diseases using compartmental models or machine learning",
            "trained": self.trained,
            "feature_columns": self.feature_columns,
            "target_column": self.target_column,
            "spatial_columns": self.spatial_columns,
            "temporal_column": self.temporal_column,
            "metrics": self.metrics,
            "hyperparameters": self.hyperparameters,
        }
    
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Get the schema of input data expected by this model.
        
        Returns:
            Dict describing the required input structure
        """
        if self.model_type in ["seir", "sir"]:
            # Compartmental models expect current state by region
            return {
                "type": "object",
                "required": ["regions"],
                "properties": {
                    "regions": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "required": ["population", "current_cases", "current_date"],
                            "properties": {
                                "population": {
                                    "type": "number",
                                    "description": "Total population of the region",
                                },
                                "current_cases": {
                                    "type": "number",
                                    "description": "Current number of active cases",
                                },
                                "current_date": {
                                    "type": "string",
                                    "format": "date",
                                    "description": "Current date (YYYY-MM-DD)",
                                },
                                "current_exposed": {
                                    "type": "number",
                                    "description": "Current number of exposed individuals (SEIR model only)",
                                },
                                "current_recovered": {
                                    "type": "number",
                                    "description": "Current number of recovered individuals",
                                },
                            }
                        }
                    }
                }
            }
        elif self.model_type == "ml":
            # ML models expect historical data for each region
            feature_properties = {}
            for col in self.feature_columns:
                feature_properties[col] = {
                    "type": "number",
                    "description": f"Feature: {col}",
                }
                
            feature_properties[self.temporal_column] = {
                "type": "string",
                "format": "date",
                "description": "Date (YYYY-MM-DD)",
            }
            
            return {
                "type": "object",
                "required": ["regions"],
                "properties": {
                    "regions": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "required": ["historical_data"],
                            "properties": {
                                "historical_data": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": self.feature_columns + [self.temporal_column],
                                        "properties": feature_properties,
                                    }
                                }
                            }
                        }
                    }
                }
            }
        
        return {}
    
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Get the schema of output data produced by this model.
        
        Returns:
            Dict describing the output structure
        """
        if self.model_type == "sir":
            return {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Whether the prediction was successful",
                    },
                    "predictions": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "dates": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "format": "date",
                                    },
                                    "description": "Dates for the forecast period",
                                },
                                "cases": {
                                    "type": "array",
                                    "items": {
                                        "type": "number",
                                    },
                                    "description": "Predicted number of cases for each date",
                                },
                                "susceptible": {
                                    "type": "array",
                                    "items": {
                                        "type": "number",
                                    },
                                    "description": "Predicted number of susceptible individuals",
                                },
                                "recovered": {
                                    "type": "array",
                                    "items": {
                                        "type": "number",
                                    },
                                    "description": "Predicted number of recovered individuals",
                                },
                            }
                        }
                    }
                }
            }
        elif self.model_type == "seir":
            return {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Whether the prediction was successful",
                    },
                    "predictions": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "dates": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "format": "date",
                                    },
                                    "description": "Dates for the forecast period",
                                },
                                "cases": {
                                    "type": "array",
                                    "items": {
                                        "type": "number",
                                    },
                                    "description": "Predicted number of cases for each date",
                                },
                                "exposed": {
                                    "type": "array",
                                    "items": {
                                        "type": "number",
                                    },
                                    "description": "Predicted number of exposed individuals",
                                },
                                "susceptible": {
                                    "type": "array",
                                    "items": {
                                        "type": "number",
                                    },
                                    "description": "Predicted number of susceptible individuals",
                                },
                                "recovered": {
                                    "type": "array",
                                    "items": {
                                        "type": "number",
                                    },
                                    "description": "Predicted number of recovered individuals",
                                },
                            }
                        }
                    }
                }
            }
        elif self.model_type == "ml":
            return {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Whether the prediction was successful",
                    },
                    "predictions": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "dates": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "format": "date",
                                    },
                                    "description": "Dates for the forecast period",
                                },
                                "cases": {
                                    "type": "array",
                                    "items": {
                                        "type": "number",
                                    },
                                    "description": "Predicted number of cases for each date",
                                },
                            }
                        }
                    }
                }
            }
        
        return {}
    
    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input data against the expected schema.
        
        Args:
            input_data: The data to validate
            
        Returns:
            Dict with validation results
        """
        errors = []
        
        # Check basic structure
        if "regions" not in input_data:
            errors.append("Missing required field: regions")
            return {"valid": False, "errors": errors}
            
        if not isinstance(input_data["regions"], dict):
            errors.append("Field 'regions' must be an object")
            return {"valid": False, "errors": errors}
            
        # Validate each region's data based on model type
        for region_id, region_data in input_data["regions"].items():
            if self.model_type in ["seir", "sir"]:
                # Check required fields for compartmental models
                required_fields = ["population", "current_cases", "current_date"]
                for field in required_fields:
                    if field not in region_data:
                        errors.append(f"Missing required field '{field}' for region '{region_id}'")
                
                # Check data types
                if "population" in region_data and not isinstance(region_data["population"], (int, float)):
                    errors.append(f"Field 'population' for region '{region_id}' must be a number")
                    
                if "current_cases" in region_data and not isinstance(region_data["current_cases"], (int, float)):
                    errors.append(f"Field 'current_cases' for region '{region_id}' must be a number")
                    
                if "current_date" in region_data:
                    try:
                        datetime.strptime(region_data["current_date"], "%Y-%m-%d")
                    except ValueError:
                        errors.append(f"Field 'current_date' for region '{region_id}' must be in YYYY-MM-DD format")
                        
            elif self.model_type == "ml":
                # Check required fields for ML models
                if "historical_data" not in region_data:
                    errors.append(f"Missing required field 'historical_data' for region '{region_id}'")
                    continue
                    
                if not isinstance(region_data["historical_data"], list):
                    errors.append(f"Field 'historical_data' for region '{region_id}' must be an array")
                    continue
                    
                # Check each data point
                for i, point in enumerate(region_data["historical_data"]):
                    for col in self.feature_columns:
                        if col not in point:
                            errors.append(f"Missing required feature '{col}' in historical_data[{i}] for region '{region_id}'")
                        elif not isinstance(point[col], (int, float)):
                            errors.append(f"Feature '{col}' in historical_data[{i}] for region '{region_id}' must be a number")
                            
                    if self.temporal_column not in point:
                        errors.append(f"Missing required field '{self.temporal_column}' in historical_data[{i}] for region '{region_id}'")
                    else:
                        try:
                            datetime.strptime(point[self.temporal_column], "%Y-%m-%d")
                        except ValueError:
                            errors.append(f"Field '{self.temporal_column}' in historical_data[{i}] for region '{region_id}' must be in YYYY-MM-DD format")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }
    
    def get_hyperparameters(self) -> Dict[str, Any]:
        """
        Get the current hyperparameters of the model.
        
        Returns:
            Dict of hyperparameter values
        """
        return self.hyperparameters
    
    async def tune_hyperparameters(self, training_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tune the model's hyperparameters.
        
        Args:
            training_data: The data to use for tuning
            options: Tuning options
            
        Returns:
            Dict with tuning results and optimal hyperparameters
        """
        if not self.is_initialized:
            raise RuntimeError("Disease spread model not initialized")
            
        try:
            # Extract data
            data = training_data.get("data", [])
            if not data:
                return {
                    "success": False,
                    "error": "No training data provided",
                }
                
            # Extract options
            num_trials = options.get("num_trials", 10)
            param_grid = options.get("param_grid", {})
            
            if not param_grid:
                if self.model_type == "sir":
                    param_grid = {
                        "beta": [0.1, 0.2, 0.3, 0.4, 0.5],
                        "gamma": [0.05, 0.1, 0.15, 0.2],
                    }
                elif self.model_type == "seir":
                    param_grid = {
                        "beta": [0.1, 0.2, 0.3, 0.4, 0.5],
                        "sigma": [0.1, 0.2, 0.3],
                        "gamma": [0.05, 0.1, 0.15, 0.2],
                    }
                elif self.model_type == "ml":
                    param_grid = {
                        "learning_rate": [0.001, 0.01, 0.1],
                        "max_depth": [3, 5, 7],
                        "n_estimators": [50, 100, 200],
                    }
            
            # Set up validation split
            validation_split = options.get("validation_split", 0.2)
            
            # Simple implementation of grid search
            best_params = {}
            best_score = float('inf')  # Lower is better for MSE
            
            # Group data by region
            regions = {}
            for row in data:
                region_id = self._get_region_id(row)
                if region_id not in regions:
                    regions[region_id] = []
                regions[region_id].append(row)
            
            # Generate parameter combinations
            from itertools import product
            param_names = list(param_grid.keys())
            param_values = list(param_grid.values())
            
            param_combinations = []
            for values in product(*param_values):
                param_dict = {param_names[i]: values[i] for i in range(len(param_names))}
                param_combinations.append(param_dict)
            
            # Limit number of trials if too many combinations
            if len(param_combinations) > num_trials:
                import random
                random.shuffle(param_combinations)
                param_combinations = param_combinations[:num_trials]
            
            # Try each parameter combination
            all_results = []
            for params in param_combinations:
                # Update hyperparameters
                current_params = self.hyperparameters.copy()
                for k, v in params.items():
                    current_params[k] = v
                
                # Setup model with these parameters
                self.hyperparameters = current_params
                
                # Split data for each region
                train_data = {"data": []}
                val_data = {"data": []}
                
                for region_id, region_rows in regions.items():
                    # Sort by date
                    region_rows.sort(key=lambda x: x.get(self.temporal_column, ""))
                    
                    # Split into training and validation
                    split_idx = int(len(region_rows) * (1 - validation_split))
                    train_data["data"].extend(region_rows[:split_idx])
                    val_data["data"].extend(region_rows[split_idx:])
                
                # Train model with these parameters
                train_result = await self.train(train_data, {})
                
                if train_result.get("success", False):
                    # Evaluate on validation data
                    eval_result = await self.evaluate(val_data, {})
                    
                    if eval_result.get("success", False):
                        # Get overall MSE
                        mse = eval_result["metrics"]["overall"].get("mse", float('inf'))
                        
                        all_results.append({
                            "params": params,
                            "score": mse,
                            "metrics": eval_result["metrics"]["overall"],
                        })
                        
                        # Update best if better
                        if mse < best_score:
                            best_score = mse
                            best_params = params
            
            # Set the model to the best hyperparameters
            if best_params:
                for k, v in best_params.items():
                    self.hyperparameters[k] = v
                    
                # Retrain on all data
                await self.train(training_data, {})
            
            return {
                "success": True,
                "best_params": best_params,
                "best_score": best_score,
                "all_results": all_results,
            }
            
        except Exception as e:
            logger.error(f"Error tuning hyperparameters: {e}")
            return {
                "success": False,
                "error": str(e),
            }