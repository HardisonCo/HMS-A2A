"""
Controller for avian influenza predictive modeling services.

This module provides API endpoints for generating, managing,
and accessing forecasts for avian influenza outbreaks.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field

from ..models.base import GeoRegion
from ..models.case import Case
from ..services.predictive_modeling import ForecastService

# Define API models
class ForecastParameters(BaseModel):
    """Parameters for generating a forecast."""
    days_ahead: int = Field(7, description="Number of days to forecast ahead")
    use_ensemble: bool = Field(True, description="Whether to use ensemble of models")
    selected_models: Optional[List[str]] = Field(None, description="List of model IDs to use")
    include_confidence_intervals: bool = Field(True, description="Include confidence intervals")
    environmental_factors: Optional[Dict[str, float]] = Field(None, 
                                                             description="Environmental factors by region")
    seasonal_factor: Optional[float] = Field(None, description="Seasonal adjustment factor")
    
    class Config:
        schema_extra = {
            "example": {
                "days_ahead": 14,
                "use_ensemble": True,
                "selected_models": ["distance_based", "gaussian_process"],
                "include_confidence_intervals": True,
                "seasonal_factor": 1.2
            }
        }

class RiskLevel(BaseModel):
    """Risk level for a region."""
    region_id: str = Field(..., description="Region identifier")
    risk_score: float = Field(..., description="Risk score (0-1)")
    risk_level: str = Field(..., description="Risk level category")
    predicted_cases: float = Field(..., description="Predicted case count")
    lower_bound: Optional[float] = Field(None, description="Lower confidence bound")
    upper_bound: Optional[float] = Field(None, description="Upper confidence bound")

class ForecastResult(BaseModel):
    """Result of a forecast operation."""
    forecast_id: str = Field(..., description="Unique forecast identifier")
    created_at: str = Field(..., description="Timestamp when forecast was created")
    forecast_date: str = Field(..., description="Date of the forecast")
    days_ahead: int = Field(..., description="Number of days forecasted ahead")
    model_info: Dict[str, Any] = Field(..., description="Information about models used")
    risk_levels: List[RiskLevel] = Field(..., description="Risk levels by region")

class TrainingParameters(BaseModel):
    """Parameters for training forecast models."""
    start_date: str = Field(..., description="Start date for historical data (ISO format)")
    end_date: str = Field(..., description="End date for historical data (ISO format)")
    include_network_model: bool = Field(False, description="Whether to include network model")
    network_type: Optional[str] = Field(None, description="Type of network to use")
    
    class Config:
        schema_extra = {
            "example": {
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "include_network_model": True,
                "network_type": "migration"
            }
        }

class EvaluationResult(BaseModel):
    """Result of model evaluation."""
    evaluation_id: str = Field(..., description="Unique evaluation identifier")
    created_at: str = Field(..., description="Timestamp when evaluation was performed")
    metrics: Dict[str, Dict[str, float]] = Field(..., description="Evaluation metrics by model")
    best_model: str = Field(..., description="ID of the best performing model")


# Create router
router = APIRouter(
    prefix="/api/v1/predictive",
    tags=["predictive"],
    responses={404: {"description": "Not found"}},
)

# Service dependency
def get_forecast_service():
    """Dependency to get forecast service instance."""
    return ForecastService()

# Data access dependencies
def get_case_repository():
    """Dependency to get case repository."""
    # This would be implemented based on your data access layer
    return None

def get_region_repository():
    """Dependency to get region repository."""
    # This would be implemented based on your data access layer
    return None

def get_network_repository():
    """Dependency to get network data repository."""
    # This would be implemented based on your data access layer
    return None


# API endpoints
@router.post("/forecasts", response_model=ForecastResult)
async def generate_forecast(
    params: ForecastParameters,
    forecast_service: ForecastService = Depends(get_forecast_service),
    case_repo = Depends(get_case_repository),
    region_repo = Depends(get_region_repository),
    network_repo = Depends(get_network_repository)
):
    """
    Generate a new forecast for avian influenza spread.
    """
    # Get current cases (active in the last 30 days)
    now = datetime.now()
    start_date = now - timedelta(days=30)
    current_cases = case_repo.get_cases_by_date_range(
        start_date.isoformat(),
        now.isoformat()
    )
    
    # Get all regions
    regions = region_repo.get_all_regions()
    
    # Get forecast
    kwargs = params.dict(exclude_unset=True)
    
    # Add network data if using network model
    if any(model_id.startswith("network_") for model_id in (params.selected_models or [])):
        network_data = network_repo.get_network_data()
        kwargs["network_data"] = network_data
    
    # Generate forecast
    forecast = forecast_service.generate_forecast(
        current_cases=current_cases,
        regions=regions,
        **kwargs
    )
    
    # Format result for API response
    risk_by_region = forecast.get('risk_by_region', {})
    predicted_cases = forecast.get('predicted_case_count', {})
    confidence_intervals = forecast.get('confidence_intervals', {})
    
    risk_levels = []
    for region_id, risk in risk_by_region.items():
        # Determine risk level category
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
            
        # Create risk level entry
        entry = RiskLevel(
            region_id=region_id,
            risk_score=risk,
            risk_level=level,
            predicted_cases=predicted_cases.get(region_id, 0)
        )
        
        # Add confidence intervals if available
        if region_id in confidence_intervals:
            lower, upper = confidence_intervals[region_id]
            entry.lower_bound = lower
            entry.upper_bound = upper
            
        risk_levels.append(entry)
    
    # Create forecast result
    result = ForecastResult(
        forecast_id=f"forecast_{now.strftime('%Y%m%d_%H%M%S')}",
        created_at=now.isoformat(),
        forecast_date=now.date().isoformat(),
        days_ahead=params.days_ahead,
        model_info={
            "models_used": params.selected_models or list(forecast.get('model_weights', {}).keys()),
            "ensemble": params.use_ensemble
        },
        risk_levels=risk_levels
    )
    
    return result


@router.post("/models/train", response_model=Dict[str, Any])
async def train_models(
    params: TrainingParameters,
    forecast_service: ForecastService = Depends(get_forecast_service),
    case_repo = Depends(get_case_repository),
    region_repo = Depends(get_region_repository),
    network_repo = Depends(get_network_repository)
):
    """
    Train predictive models using historical data.
    """
    # Get historical cases
    historical_cases = case_repo.get_cases_by_date_range(
        params.start_date,
        params.end_date
    )
    
    if not historical_cases:
        raise HTTPException(status_code=404, detail="No historical cases found in date range")
    
    # Get all regions
    regions = region_repo.get_all_regions()
    
    # Additional parameters
    kwargs = {}
    
    # Add network model if requested
    if params.include_network_model and params.network_type:
        network_data = network_repo.get_network_data(params.network_type)
        if network_data:
            forecast_service.add_network_model(network_data, params.network_type)
            kwargs["network_data"] = network_data
    
    # Train models
    forecast_service.train_models(historical_cases, regions, **kwargs)
    
    return {
        "status": "success",
        "message": "Models trained successfully",
        "models": list(forecast_service.forecast_manager.models.keys()),
        "training_data": {
            "start_date": params.start_date,
            "end_date": params.end_date,
            "case_count": len(historical_cases)
        }
    }


@router.post("/models/evaluate", response_model=EvaluationResult)
async def evaluate_models(
    params: TrainingParameters,
    test_start_date: str = Query(..., description="Start date for test data"),
    test_end_date: str = Query(..., description="End date for test data"),
    forecast_service: ForecastService = Depends(get_forecast_service),
    case_repo = Depends(get_case_repository),
    region_repo = Depends(get_region_repository)
):
    """
    Evaluate predictive model performance using test data.
    """
    # Get historical cases for training
    historical_cases = case_repo.get_cases_by_date_range(
        params.start_date,
        params.end_date
    )
    
    # Get test cases
    test_cases = case_repo.get_cases_by_date_range(
        test_start_date,
        test_end_date
    )
    
    if not historical_cases:
        raise HTTPException(status_code=404, detail="No historical cases found for training")
    
    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found for evaluation")
    
    # Get all regions
    regions = region_repo.get_all_regions()
    
    # Evaluate models
    metrics = forecast_service.evaluate_models(
        test_cases=test_cases,
        historical_cases=historical_cases,
        regions=regions
    )
    
    # Find best model based on RMSE
    best_model = None
    best_rmse = float('inf')
    for model_id, model_metrics in metrics.items():
        if 'rmse' in model_metrics and model_metrics['rmse'] < best_rmse:
            best_rmse = model_metrics['rmse']
            best_model = model_id
    
    return EvaluationResult(
        evaluation_id=f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        created_at=datetime.now().isoformat(),
        metrics=metrics,
        best_model=best_model or list(metrics.keys())[0] if metrics else "unknown"
    )


@router.get("/forecasts/latest", response_model=ForecastResult)
async def get_latest_forecast(
    days_ahead: int = Query(7, description="Number of days ahead to forecast"),
    case_repo = Depends(get_case_repository),
    region_repo = Depends(get_region_repository),
    forecast_service: ForecastService = Depends(get_forecast_service)
):
    """
    Get the latest forecast for avian influenza spread.
    """
    # Implementation would depend on how forecasts are stored
    # Here's a simplified version that generates a new forecast
    
    # Get current cases (active in the last 30 days)
    now = datetime.now()
    start_date = now - timedelta(days=30)
    current_cases = case_repo.get_cases_by_date_range(
        start_date.isoformat(),
        now.isoformat()
    )
    
    # Get all regions
    regions = region_repo.get_all_regions()
    
    # Generate forecast
    forecast = forecast_service.generate_forecast(
        current_cases=current_cases,
        regions=regions,
        days_ahead=days_ahead,
        use_ensemble=True
    )
    
    # Format result (similar to generate_forecast endpoint)
    # ... (formatting code would be the same)
    
    # This is a placeholder - actual implementation would reuse logic from generate_forecast
    # or retrieve the latest saved forecast
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/risk-map", response_model=Dict[str, Any])
async def get_risk_map_data(
    forecast_id: Optional[str] = Query(None, description="Specific forecast ID to use"),
    days_ahead: int = Query(7, description="Number of days ahead for forecast"),
    forecast_service: ForecastService = Depends(get_forecast_service),
    case_repo = Depends(get_case_repository),
    region_repo = Depends(get_region_repository)
):
    """
    Get risk map data for visualization.
    """
    # Get current cases (active in the last 30 days)
    now = datetime.now()
    start_date = now - timedelta(days=30)
    current_cases = case_repo.get_cases_by_date_range(
        start_date.isoformat(),
        now.isoformat()
    )
    
    # Get all regions
    regions = region_repo.get_all_regions()
    
    # Generate forecast
    forecast = forecast_service.generate_forecast(
        current_cases=current_cases,
        regions=regions,
        days_ahead=days_ahead,
        use_ensemble=True
    )
    
    # Process for risk map
    risk_map_data = forecast_service.get_risk_map_data(forecast)
    
    # Add timestamp and metadata
    result = {
        "timestamp": now.isoformat(),
        "days_ahead": days_ahead,
        "data": risk_map_data
    }
    
    return result