"""
Pollution modeling models for EPA implementation.
Defines domain models for pollution modeling and prediction.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from agency_implementation.foundation.base_models.base import BaseModel, GeoLocation
from agency_implementation.epa.models.base import PollutantType


class PollutionModel(BaseModel):
    """
    Pollution dispersion or concentration model.
    Represents a computational model for predicting pollution effects.
    """
    
    def __init__(
        self,
        model_name: str,
        model_type: str,
        pollutant_types: List[str],
        spatial_resolution: float,
        temporal_resolution: str,
        version: str,
        parameters: Dict[str, Any] = None,
        validation_metrics: Dict[str, Any] = None,
        creator: str = None,
        creation_date: str = None,
        last_updated: str = None,
        description: str = None,
        **kwargs
    ):
        """Initialize pollution model"""
        super().__init__(**kwargs)
        self.model_name = model_name
        self.model_type = model_type
        self.pollutant_types = pollutant_types
        self.spatial_resolution = spatial_resolution
        self.temporal_resolution = temporal_resolution
        self.version = version
        self.parameters = parameters or {}
        self.validation_metrics = validation_metrics or {}
        self.creator = creator
        self.creation_date = creation_date or datetime.now().isoformat()
        self.last_updated = last_updated or self.creation_date
        self.description = description


class EmissionSource(BaseModel):
    """
    Pollution emission source.
    Represents a source of pollution emissions for modeling.
    """
    
    def __init__(
        self,
        source_name: str,
        source_type: str,
        location: Dict[str, Any],
        pollutant_types: List[str],
        emission_rates: Dict[str, float],
        facility_id: str = None,
        stack_height: float = None,
        stack_diameter: float = None,
        exit_velocity: float = None,
        exit_temperature: float = None,
        operating_schedule: Dict[str, Any] = None,
        seasonal_variation: Dict[str, Any] = None,
        **kwargs
    ):
        """Initialize emission source"""
        super().__init__(**kwargs)
        self.source_name = source_name
        self.source_type = source_type
        self.location = GeoLocation.from_dict(location) if isinstance(location, dict) else location
        self.pollutant_types = pollutant_types
        self.emission_rates = emission_rates
        self.facility_id = facility_id
        self.stack_height = stack_height
        self.stack_diameter = stack_diameter
        self.exit_velocity = exit_velocity
        self.exit_temperature = exit_temperature
        self.operating_schedule = operating_schedule or {}
        self.seasonal_variation = seasonal_variation or {}


class ModelRun(BaseModel):
    """
    Execution of a pollution model.
    Represents a specific simulation run with model and inputs.
    """
    
    def __init__(
        self,
        model_id: str,
        run_parameters: Dict[str, Any],
        emission_sources: List[str],
        start_time: str,
        end_time: str,
        spatial_domain: Dict[str, Any],
        run_status: str = "PENDING",
        meteorological_data: str = None,
        terrain_data: str = None,
        background_concentrations: Dict[str, float] = None,
        run_start: str = None,
        run_end: str = None,
        run_by: str = None,
        **kwargs
    ):
        """Initialize model run"""
        super().__init__(**kwargs)
        self.model_id = model_id
        self.run_parameters = run_parameters
        self.emission_sources = emission_sources
        self.start_time = start_time
        self.end_time = end_time
        self.spatial_domain = spatial_domain
        self.run_status = run_status
        self.meteorological_data = meteorological_data
        self.terrain_data = terrain_data
        self.background_concentrations = background_concentrations or {}
        self.run_start = run_start
        self.run_end = run_end
        self.run_by = run_by
    
    def start_run(self, run_by: str = None) -> None:
        """Mark the model run as started"""
        self.run_status = "RUNNING"
        self.run_start = datetime.now().isoformat()
        if run_by:
            self.run_by = run_by
    
    def complete_run(self, success: bool = True) -> None:
        """Mark the model run as completed"""
        self.run_status = "COMPLETED" if success else "FAILED"
        self.run_end = datetime.now().isoformat()
    
    @property
    def run_duration_seconds(self) -> Optional[float]:
        """Calculate the duration of the model run in seconds"""
        if not self.run_start or not self.run_end:
            return None
        
        start = datetime.fromisoformat(self.run_start) if isinstance(self.run_start, str) else self.run_start
        end = datetime.fromisoformat(self.run_end) if isinstance(self.run_end, str) else self.run_end
        
        return (end - start).total_seconds()


class ModelResult(BaseModel):
    """
    Results of a pollution model simulation.
    Represents output data from a model run.
    """
    
    def __init__(
        self,
        model_run_id: str,
        result_type: str,
        pollutant_type: str,
        timestamps: List[str],
        spatial_coverage: Dict[str, Any],
        data_format: str,
        data_url: str = None,
        data_summary: Dict[str, Any] = None,
        visualization_url: str = None,
        exceedances: List[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize model result"""
        super().__init__(**kwargs)
        self.model_run_id = model_run_id
        self.result_type = result_type
        self.pollutant_type = pollutant_type
        self.timestamps = timestamps
        self.spatial_coverage = spatial_coverage
        self.data_format = data_format
        self.data_url = data_url
        self.data_summary = data_summary or {}
        self.visualization_url = visualization_url
        self.exceedances = exceedances or []


class ScenarioAnalysis(BaseModel):
    """
    Analysis of different pollution scenarios.
    Represents comparison of model runs with different parameters.
    """
    
    def __init__(
        self,
        scenario_name: str,
        base_model_run_id: str,
        scenario_model_runs: List[str],
        scenario_descriptions: Dict[str, str],
        comparison_metrics: List[str],
        created_by: str = None,
        creation_date: str = None,
        status: str = "CREATED",
        results: Dict[str, Any] = None,
        recommendation: str = None,
        **kwargs
    ):
        """Initialize scenario analysis"""
        super().__init__(**kwargs)
        self.scenario_name = scenario_name
        self.base_model_run_id = base_model_run_id
        self.scenario_model_runs = scenario_model_runs
        self.scenario_descriptions = scenario_descriptions
        self.comparison_metrics = comparison_metrics
        self.created_by = created_by
        self.creation_date = creation_date or datetime.now().isoformat()
        self.status = status
        self.results = results or {}
        self.recommendation = recommendation
    
    def add_result(self, metric: str, values: Dict[str, Any]) -> None:
        """Add a comparison result for a specific metric"""
        if not self.results:
            self.results = {}
        self.results[metric] = values
    
    def complete_analysis(self, recommendation: str = None) -> None:
        """Mark analysis as complete and add recommendation"""
        self.status = "COMPLETED"
        if recommendation:
            self.recommendation = recommendation


class EnvironmentalImpactAssessment(BaseModel):
    """
    Assessment of environmental impacts from pollution.
    Represents evaluation of modeled pollution on environment and health.
    """
    
    def __init__(
        self,
        assessment_name: str,
        model_result_ids: List[str],
        assessment_type: str,
        receptors: List[Dict[str, Any]],
        impact_criteria: Dict[str, Any],
        status: str = "INITIATED",
        assessor_id: str = None,
        assessment_date: str = None,
        methodology: str = None,
        findings: List[Dict[str, Any]] = None,
        recommendations: List[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize environmental impact assessment"""
        super().__init__(**kwargs)
        self.assessment_name = assessment_name
        self.model_result_ids = model_result_ids
        self.assessment_type = assessment_type
        self.receptors = receptors
        self.impact_criteria = impact_criteria
        self.status = status
        self.assessor_id = assessor_id
        self.assessment_date = assessment_date or datetime.now().isoformat()
        self.methodology = methodology
        self.findings = findings or []
        self.recommendations = recommendations or []
    
    def add_finding(self, receptor_type: str, impact_level: str, description: str, confidence: str = None) -> None:
        """Add an assessment finding"""
        self.findings.append({
            "receptor_type": receptor_type,
            "impact_level": impact_level,
            "description": description,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_recommendation(self, recommendation_type: str, description: str, priority: str = "MEDIUM") -> None:
        """Add a recommendation based on the assessment"""
        self.recommendations.append({
            "recommendation_type": recommendation_type,
            "description": description,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        })
    
    def complete_assessment(self) -> None:
        """Mark the assessment as completed"""
        self.status = "COMPLETED"