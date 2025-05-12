"""
Pollution Modeling Service for the EPA implementation.

This service provides functionality for modeling pollution dispersion, 
emission sources, and environmental impacts.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date, timedelta
import logging
import uuid
import os
import json

from agency_implementation.epa.models.pollution import (
    PollutionModel, EmissionSource, ModelRun, 
    ModelResult, ScenarioAnalysis, EnvironmentalImpactAssessment
)
from agency_implementation.epa.models.base import PollutantType
from .repository import (
    PollutionModelRepository, EmissionSourceRepository,
    ModelRunRepository, ModelResultRepository
)
from .adapters import ModelingSystemAdapter, ModelResultAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PollutionModelingService:
    """
    Service for pollution modeling.
    
    This service provides functionality for:
    1. Pollution model management
    2. Emission source management
    3. Model execution and scenario analysis
    4. Results processing and impact assessment
    """
    
    def __init__(
        self,
        model_repository: PollutionModelRepository,
        source_repository: EmissionSourceRepository,
        run_repository: ModelRunRepository,
        result_repository: ModelResultRepository,
        modeling_adapter: Optional[ModelingSystemAdapter] = None,
        result_adapter: Optional[ModelResultAdapter] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the service.
        
        Args:
            model_repository: Repository for pollution models
            source_repository: Repository for emission sources
            run_repository: Repository for model runs
            result_repository: Repository for model results
            modeling_adapter: Adapter for external modeling system integration
            result_adapter: Adapter for model result processing
            config: Service configuration
        """
        self.model_repository = model_repository
        self.source_repository = source_repository
        self.run_repository = run_repository
        self.result_repository = result_repository
        self.modeling_adapter = modeling_adapter
        self.result_adapter = result_adapter
        self.config = config or {}
        
        # Initialize model run parameters
        self.default_run_parameters = self.config.get('default_run_parameters', {
            'grid_resolution': 1.0,  # km
            'time_resolution': 1.0,  # hour
            'use_terrain': True,
            'include_background': True,
            'output_formats': ['concentration', 'deposition']
        })
        
        # Initialize result thresholds for comparison
        self.result_thresholds = self.config.get('result_thresholds', {
            'PM25': 35.0,  # EPA standard for PM2.5 (μg/m³, 24-hour)
            'PM10': 150.0,  # EPA standard for PM10 (μg/m³, 24-hour)
            'OZONE': 0.070,  # EPA standard for ozone (ppm, 8-hour)
            'NO2': 100.0,  # EPA standard for NO2 (ppb, 1-hour)
            'SO2': 75.0,  # EPA standard for SO2 (ppb, 1-hour)
            'CO': 9.0,  # EPA standard for CO (ppm, 8-hour)
            'LEAD': 0.15,  # EPA standard for lead (μg/m³, 3-month)
        })
        
        # Initialize working directory for model runs
        self.working_dir = self.config.get('working_dir', '/tmp/epa_modeling')
        os.makedirs(self.working_dir, exist_ok=True)
        
        logger.info("PollutionModelingService initialized")
    
    # Model Management Methods
    
    def get_model(self, model_id: str) -> Optional[PollutionModel]:
        """
        Get a pollution model by ID.
        
        Args:
            model_id: The ID of the model to retrieve
            
        Returns:
            The model if found, None otherwise
        """
        return self.model_repository.get_by_id(model_id)
    
    def get_all_models(self) -> List[PollutionModel]:
        """
        Get all pollution models.
        
        Returns:
            List of all models
        """
        return self.model_repository.get_all()
    
    def create_model(self, model_data: Dict[str, Any]) -> PollutionModel:
        """
        Create a new pollution model.
        
        Args:
            model_data: Dictionary with model data
            
        Returns:
            The created model
            
        Raises:
            ValueError: If model data is invalid
        """
        # Validate required fields
        required_fields = ['model_name', 'model_type', 'pollutant_types', 
                          'spatial_resolution', 'temporal_resolution', 'version']
        for field in required_fields:
            if field not in model_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create the model
        model = PollutionModel(**model_data)
        
        # Save the model
        created_model = self.model_repository.create(model)
        
        logger.info(f"Created new pollution model with ID: {created_model.id}")
        return created_model
    
    def update_model(self, model_id: str, updates: Dict[str, Any]) -> Optional[PollutionModel]:
        """
        Update an existing pollution model.
        
        Args:
            model_id: ID of the model to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated model or None if model not found
            
        Raises:
            ValueError: If updates are invalid
        """
        # Get the model
        model = self.model_repository.get_by_id(model_id)
        if not model:
            logger.warning(f"Model not found for update: {model_id}")
            return None
        
        # Update the model
        for key, value in updates.items():
            setattr(model, key, value)
            
        # Update timestamp
        model.updated_at = datetime.now().isoformat()
        
        # Save the updated model
        updated_model = self.model_repository.update(model)
        
        logger.info(f"Updated model with ID: {model_id}")
        return updated_model
    
    def find_models_by_type(self, model_type: str) -> List[PollutionModel]:
        """
        Find models by type.
        
        Args:
            model_type: Type of model
            
        Returns:
            List of models of the specified type
        """
        return self.model_repository.find_by_model_type(model_type)
    
    def find_models_by_pollutant(self, pollutant_type: Union[PollutantType, str]) -> List[PollutionModel]:
        """
        Find models supporting a specific pollutant type.
        
        Args:
            pollutant_type: Pollutant type
            
        Returns:
            List of models supporting the specified pollutant
        """
        return self.model_repository.find_by_pollutant_type(pollutant_type)
    
    def find_latest_model_versions(self) -> List[PollutionModel]:
        """
        Find the latest version of each model name.
        
        Returns:
            List of latest model versions
        """
        return self.model_repository.find_latest_versions()
    
    # Emission Source Management Methods
    
    def get_emission_source(self, source_id: str) -> Optional[EmissionSource]:
        """
        Get an emission source by ID.
        
        Args:
            source_id: The ID of the source to retrieve
            
        Returns:
            The emission source if found, None otherwise
        """
        return self.source_repository.get_by_id(source_id)
    
    def get_all_emission_sources(self) -> List[EmissionSource]:
        """
        Get all emission sources.
        
        Returns:
            List of all emission sources
        """
        return self.source_repository.get_all()
    
    def create_emission_source(self, source_data: Dict[str, Any]) -> EmissionSource:
        """
        Create a new emission source.
        
        Args:
            source_data: Dictionary with emission source data
            
        Returns:
            The created emission source
            
        Raises:
            ValueError: If source data is invalid
        """
        # Validate required fields
        required_fields = ['source_name', 'source_type', 'location', 
                          'pollutant_types', 'emission_rates']
        for field in required_fields:
            if field not in source_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create the emission source
        source = EmissionSource(**source_data)
        
        # Save the emission source
        created_source = self.source_repository.create(source)
        
        logger.info(f"Created new emission source with ID: {created_source.id}")
        return created_source
    
    def update_emission_source(self, source_id: str, updates: Dict[str, Any]) -> Optional[EmissionSource]:
        """
        Update an existing emission source.
        
        Args:
            source_id: ID of the emission source to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated emission source or None if source not found
            
        Raises:
            ValueError: If updates are invalid
        """
        # Get the emission source
        source = self.source_repository.get_by_id(source_id)
        if not source:
            logger.warning(f"Emission source not found for update: {source_id}")
            return None
        
        # Update the emission source
        for key, value in updates.items():
            setattr(source, key, value)
            
        # Update timestamp
        source.updated_at = datetime.now().isoformat()
        
        # Save the updated emission source
        updated_source = self.source_repository.update(source)
        
        logger.info(f"Updated emission source with ID: {source_id}")
        return updated_source
    
    def find_sources_by_facility(self, facility_id: str) -> List[EmissionSource]:
        """
        Find emission sources by facility ID.
        
        Args:
            facility_id: ID of the facility
            
        Returns:
            List of emission sources for the facility
        """
        return self.source_repository.find_by_facility_id(facility_id)
    
    def find_sources_by_type(self, source_type: str) -> List[EmissionSource]:
        """
        Find emission sources by type.
        
        Args:
            source_type: Type of emission source
            
        Returns:
            List of emission sources of the specified type
        """
        return self.source_repository.find_by_source_type(source_type)
    
    def find_sources_by_pollutant(self, pollutant_type: Union[PollutantType, str]) -> List[EmissionSource]:
        """
        Find emission sources emitting a specific pollutant type.
        
        Args:
            pollutant_type: Pollutant type
            
        Returns:
            List of emission sources emitting the specified pollutant
        """
        return self.source_repository.find_by_pollutant_type(pollutant_type)
    
    def find_sources_by_emission_rate(
        self, 
        pollutant: str, 
        min_rate: float
    ) -> List[EmissionSource]:
        """
        Find emission sources with emission rate above minimum for a specific pollutant.
        
        Args:
            pollutant: Pollutant name
            min_rate: Minimum emission rate
            
        Returns:
            List of emission sources with emission rate above minimum
        """
        return self.source_repository.find_by_emission_rate(pollutant, min_rate)
    
    def find_sources_in_area(
        self, 
        min_lat: float, 
        min_lon: float, 
        max_lat: float, 
        max_lon: float
    ) -> List[EmissionSource]:
        """
        Find emission sources within a geographic bounding box.
        
        Args:
            min_lat: Minimum latitude
            min_lon: Minimum longitude
            max_lat: Maximum latitude
            max_lon: Maximum longitude
            
        Returns:
            List of emission sources within the bounding box
        """
        return self.source_repository.find_by_geographic_area(min_lat, min_lon, max_lat, max_lon)
    
    # Model Run Management Methods
    
    def get_model_run(self, run_id: str) -> Optional[ModelRun]:
        """
        Get a model run by ID.
        
        Args:
            run_id: The ID of the run to retrieve
            
        Returns:
            The model run if found, None otherwise
        """
        return self.run_repository.get_by_id(run_id)
    
    def get_all_model_runs(self) -> List[ModelRun]:
        """
        Get all model runs.
        
        Returns:
            List of all model runs
        """
        return self.run_repository.get_all()
    
    def create_model_run(
        self, 
        model_id: str, 
        emission_source_ids: List[str],
        start_time: Union[datetime, str],
        end_time: Union[datetime, str],
        spatial_domain: Dict[str, Any],
        run_parameters: Optional[Dict[str, Any]] = None,
        meteorological_data: Optional[str] = None,
        terrain_data: Optional[str] = None,
        background_concentrations: Optional[Dict[str, float]] = None,
        user_id: Optional[str] = None
    ) -> ModelRun:
        """
        Create a new model run.
        
        Args:
            model_id: ID of the model to run
            emission_source_ids: List of emission source IDs to include
            start_time: Start time for the model run
            end_time: End time for the model run
            spatial_domain: Dictionary with spatial domain parameters
            run_parameters: Optional dictionary with run parameters
            meteorological_data: Optional path to meteorological data
            terrain_data: Optional path to terrain data
            background_concentrations: Optional dictionary with background concentrations
            user_id: Optional ID of the user creating the run
            
        Returns:
            The created model run
            
        Raises:
            ValueError: If model or sources don't exist, or if parameters are invalid
        """
        # Check model exists
        model = self.model_repository.get_by_id(model_id)
        if not model:
            raise ValueError(f"Model with ID {model_id} does not exist")
        
        # Check emission sources exist
        for source_id in emission_source_ids:
            source = self.source_repository.get_by_id(source_id)
            if not source:
                raise ValueError(f"Emission source with ID {source_id} does not exist")
        
        # Convert datetime objects to strings if needed
        if isinstance(start_time, datetime):
            start_time = start_time.isoformat()
        if isinstance(end_time, datetime):
            end_time = end_time.isoformat()
        
        # Merge default and provided run parameters
        if run_parameters is None:
            run_parameters = {}
            
        combined_parameters = {**self.default_run_parameters, **run_parameters}
        
        # Create model run
        run_data = {
            'model_id': model_id,
            'emission_sources': emission_source_ids,
            'start_time': start_time,
            'end_time': end_time,
            'spatial_domain': spatial_domain,
            'run_parameters': combined_parameters,
            'run_status': 'PENDING',
            'run_by': user_id
        }
        
        if meteorological_data:
            run_data['meteorological_data'] = meteorological_data
            
        if terrain_data:
            run_data['terrain_data'] = terrain_data
            
        if background_concentrations:
            run_data['background_concentrations'] = background_concentrations
        
        run = ModelRun(**run_data)
        
        # Save the model run
        created_run = self.run_repository.create(run)
        
        logger.info(f"Created new model run with ID: {created_run.id}")
        return created_run
    
    def execute_model_run(self, run_id: str, user_id: Optional[str] = None) -> ModelRun:
        """
        Execute a model run.
        
        Args:
            run_id: ID of the model run to execute
            user_id: Optional ID of the user executing the run
            
        Returns:
            The updated model run with execution results
            
        Raises:
            ValueError: If model run does not exist or is not in PENDING status
            RuntimeError: If modeling adapter is not configured or execution fails
        """
        # Check model run exists
        run = self.run_repository.get_by_id(run_id)
        if not run:
            raise ValueError(f"Model run with ID {run_id} does not exist")
        
        # Check run status
        if hasattr(run, 'run_status') and run.run_status != 'PENDING':
            raise ValueError(f"Model run {run_id} is not in PENDING status (current status: {run.run_status})")
        
        # Get the model
        model = self.model_repository.get_by_id(run.model_id)
        if not model:
            raise ValueError(f"Model with ID {run.model_id} does not exist")
        
        # Get emission sources
        sources = []
        for source_id in run.emission_sources:
            source = self.source_repository.get_by_id(source_id)
            if not source:
                raise ValueError(f"Emission source with ID {source_id} does not exist")
            sources.append(source)
        
        # Set the run to RUNNING status
        if hasattr(run, 'start_run'):
            run.start_run(user_id)
        else:
            run.run_status = 'RUNNING'
            run.run_start = datetime.now().isoformat()
            if user_id:
                run.run_by = user_id
        
        self.run_repository.update(run)
        
        # Execute the model run
        try:
            if self.modeling_adapter:
                # Use external modeling system via adapter
                result = self._execute_with_adapter(run, model, sources)
            else:
                # Use local execution (simplified implementation)
                result = self._execute_locally(run, model, sources)
            
            # Update the run with results
            if hasattr(run, 'complete_run'):
                run.complete_run(True)
            else:
                run.run_status = 'COMPLETED'
                run.run_end = datetime.now().isoformat()
                
            updated_run = self.run_repository.update(run)
            
            # Create model results
            self._create_results_from_execution(updated_run, result)
            
            logger.info(f"Successfully executed model run with ID: {run_id}")
            return updated_run
            
        except Exception as e:
            # Mark the run as failed
            if hasattr(run, 'complete_run'):
                run.complete_run(False)
            else:
                run.run_status = 'FAILED'
                run.run_end = datetime.now().isoformat()
                run.failure_reason = str(e)
                
            self.run_repository.update(run)
            
            logger.error(f"Error executing model run {run_id}: {str(e)}")
            raise RuntimeError(f"Model run execution failed: {str(e)}")
    
    def get_run_results(self, run_id: str) -> List[ModelResult]:
        """
        Get results for a model run.
        
        Args:
            run_id: ID of the model run
            
        Returns:
            List of model results for the run
            
        Raises:
            ValueError: If model run does not exist
        """
        # Check model run exists
        run = self.run_repository.get_by_id(run_id)
        if not run:
            raise ValueError(f"Model run with ID {run_id} does not exist")
        
        return self.result_repository.find_by_model_run_id(run_id)
    
    def find_run_by_status(self, status: str) -> List[ModelRun]:
        """
        Find model runs by status.
        
        Args:
            status: Run status
            
        Returns:
            List of model runs with the specified status
        """
        return self.run_repository.find_by_status(status)
    
    def find_run_by_model(self, model_id: str) -> List[ModelRun]:
        """
        Find model runs by model ID.
        
        Args:
            model_id: ID of the model
            
        Returns:
            List of model runs for the specified model
        """
        return self.run_repository.find_by_model_id(model_id)
    
    def find_run_by_source(self, source_id: str) -> List[ModelRun]:
        """
        Find model runs that include a specific emission source.
        
        Args:
            source_id: ID of the emission source
            
        Returns:
            List of model runs including the specified source
        """
        return self.run_repository.find_by_emission_source(source_id)
    
    def find_run_by_date_range(
        self, 
        start_date: Union[datetime, str], 
        end_date: Union[datetime, str]
    ) -> List[ModelRun]:
        """
        Find model runs within a simulation date range.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            
        Returns:
            List of model runs within the specified date range
        """
        return self.run_repository.find_by_date_range(start_date, end_date)
    
    # Scenario Analysis Methods
    
    def create_scenario_analysis(
        self,
        scenario_name: str,
        base_run_id: str,
        scenario_run_ids: List[str],
        scenario_descriptions: Dict[str, str],
        comparison_metrics: List[str],
        user_id: Optional[str] = None
    ) -> ScenarioAnalysis:
        """
        Create a new scenario analysis.
        
        Args:
            scenario_name: Name of the scenario analysis
            base_run_id: ID of the base model run
            scenario_run_ids: List of scenario model run IDs
            scenario_descriptions: Dictionary mapping run IDs to descriptions
            comparison_metrics: List of metrics to compare
            user_id: Optional ID of the user creating the analysis
            
        Returns:
            The created scenario analysis
            
        Raises:
            ValueError: If runs don't exist or are not completed
        """
        # Check base run exists and is completed
        base_run = self.run_repository.get_by_id(base_run_id)
        if not base_run:
            raise ValueError(f"Base model run with ID {base_run_id} does not exist")
            
        if hasattr(base_run, 'run_status') and base_run.run_status != 'COMPLETED':
            raise ValueError(f"Base model run {base_run_id} is not completed (status: {base_run.run_status})")
        
        # Check scenario runs exist and are completed
        for run_id in scenario_run_ids:
            run = self.run_repository.get_by_id(run_id)
            if not run:
                raise ValueError(f"Scenario model run with ID {run_id} does not exist")
                
            if hasattr(run, 'run_status') and run.run_status != 'COMPLETED':
                raise ValueError(f"Scenario model run {run_id} is not completed (status: {run.run_status})")
            
            # Ensure run_id is in scenario_descriptions
            if run_id not in scenario_descriptions:
                scenario_descriptions[run_id] = f"Scenario run {run_id}"
        
        # Create the scenario analysis
        analysis_data = {
            'scenario_name': scenario_name,
            'base_model_run_id': base_run_id,
            'scenario_model_runs': scenario_run_ids,
            'scenario_descriptions': scenario_descriptions,
            'comparison_metrics': comparison_metrics,
            'created_by': user_id,
            'creation_date': datetime.now().isoformat(),
            'status': 'CREATED'
        }
        
        analysis = ScenarioAnalysis(**analysis_data)
        
        # Save the scenario analysis
        created_analysis = self.run_repository.create(analysis)
        
        logger.info(f"Created new scenario analysis with ID: {created_analysis.id}")
        return created_analysis
    
    def run_scenario_analysis(self, analysis_id: str) -> ScenarioAnalysis:
        """
        Run a scenario analysis to compare scenarios.
        
        Args:
            analysis_id: ID of the scenario analysis to run
            
        Returns:
            The updated scenario analysis with results
            
        Raises:
            ValueError: If scenario analysis does not exist or is not in CREATED status
        """
        # Get the scenario analysis
        analysis = self.run_repository.get_by_id(analysis_id)
        if not analysis:
            raise ValueError(f"Scenario analysis with ID {analysis_id} does not exist")
        
        # Check analysis status
        if hasattr(analysis, 'status') and analysis.status != 'CREATED':
            raise ValueError(f"Scenario analysis {analysis_id} is not in CREATED status (current status: {analysis.status})")
        
        # Update status to RUNNING
        analysis.status = 'RUNNING'
        self.run_repository.update(analysis)
        
        try:
            # Get base run and results
            base_run = self.run_repository.get_by_id(analysis.base_model_run_id)
            base_results = self.result_repository.find_by_model_run_id(analysis.base_model_run_id)
            
            # Process results for each metric
            results = {}
            
            for metric in analysis.comparison_metrics:
                metric_results = {}
                
                # Get base value for this metric
                base_value = self._extract_metric_value(base_results, metric)
                metric_results['base'] = base_value
                
                # Get scenario values for this metric
                for run_id in analysis.scenario_model_runs:
                    scenario_results = self.result_repository.find_by_model_run_id(run_id)
                    scenario_value = self._extract_metric_value(scenario_results, metric)
                    
                    # Calculate change from base
                    if base_value is not None and scenario_value is not None and base_value != 0:
                        percent_change = ((scenario_value - base_value) / base_value) * 100
                    else:
                        percent_change = None
                    
                    metric_results[run_id] = {
                        'value': scenario_value,
                        'change': scenario_value - base_value if base_value is not None and scenario_value is not None else None,
                        'percent_change': percent_change
                    }
                
                # Add to results
                results[metric] = metric_results
                
                # Add the result to the analysis
                if hasattr(analysis, 'add_result'):
                    analysis.add_result(metric, metric_results)
                else:
                    if not hasattr(analysis, 'results') or analysis.results is None:
                        analysis.results = {}
                    analysis.results[metric] = metric_results
            
            # Generate recommendation based on results
            recommendation = self._generate_analysis_recommendation(analysis, results)
            
            # Mark analysis as complete
            if hasattr(analysis, 'complete_analysis'):
                analysis.complete_analysis(recommendation)
            else:
                analysis.status = 'COMPLETED'
                analysis.recommendation = recommendation
            
            # Save the updated analysis
            updated_analysis = self.run_repository.update(analysis)
            
            logger.info(f"Completed scenario analysis with ID: {analysis_id}")
            return updated_analysis
            
        except Exception as e:
            # Mark the analysis as failed
            analysis.status = 'FAILED'
            analysis.failure_reason = str(e)
            self.run_repository.update(analysis)
            
            logger.error(f"Error running scenario analysis {analysis_id}: {str(e)}")
            raise RuntimeError(f"Scenario analysis failed: {str(e)}")
    
    def create_impact_assessment(
        self,
        assessment_name: str,
        model_result_ids: List[str],
        assessment_type: str,
        receptors: List[Dict[str, Any]],
        impact_criteria: Dict[str, Any],
        assessor_id: Optional[str] = None
    ) -> EnvironmentalImpactAssessment:
        """
        Create a new environmental impact assessment.
        
        Args:
            assessment_name: Name of the assessment
            model_result_ids: List of model result IDs to include
            assessment_type: Type of assessment
            receptors: List of receptors to assess
            impact_criteria: Criteria for assessing impacts
            assessor_id: Optional ID of the user creating the assessment
            
        Returns:
            The created environmental impact assessment
            
        Raises:
            ValueError: If results don't exist
        """
        # Check model results exist
        for result_id in model_result_ids:
            result = self.result_repository.get_by_id(result_id)
            if not result:
                raise ValueError(f"Model result with ID {result_id} does not exist")
        
        # Create the impact assessment
        assessment_data = {
            'assessment_name': assessment_name,
            'model_result_ids': model_result_ids,
            'assessment_type': assessment_type,
            'receptors': receptors,
            'impact_criteria': impact_criteria,
            'assessor_id': assessor_id,
            'assessment_date': datetime.now().isoformat(),
            'status': 'INITIATED'
        }
        
        assessment = EnvironmentalImpactAssessment(**assessment_data)
        
        # Save the impact assessment
        created_assessment = self.run_repository.create(assessment)
        
        logger.info(f"Created new environmental impact assessment with ID: {created_assessment.id}")
        return created_assessment
    
    def conduct_impact_assessment(self, assessment_id: str) -> EnvironmentalImpactAssessment:
        """
        Conduct an environmental impact assessment.
        
        Args:
            assessment_id: ID of the assessment to conduct
            
        Returns:
            The updated assessment with findings
            
        Raises:
            ValueError: If assessment does not exist or is not in INITIATED status
        """
        # Get the impact assessment
        assessment = self.run_repository.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Environmental impact assessment with ID {assessment_id} does not exist")
        
        # Check assessment status
        if hasattr(assessment, 'status') and assessment.status != 'INITIATED':
            raise ValueError(f"Assessment {assessment_id} is not in INITIATED status (current status: {assessment.status})")
        
        # Update status to IN_PROGRESS
        assessment.status = 'IN_PROGRESS'
        self.run_repository.update(assessment)
        
        try:
            # Get model results
            results = []
            for result_id in assessment.model_result_ids:
                result = self.result_repository.get_by_id(result_id)
                if result:
                    results.append(result)
            
            # Assess impacts for each receptor
            for receptor in assessment.receptors:
                receptor_type = receptor.get('type')
                location = receptor.get('location')
                sensitivity = receptor.get('sensitivity', 'Medium')
                
                # Evaluate impacts based on receptor type and model results
                impact_findings = self._evaluate_receptor_impact(
                    receptor_type, 
                    location, 
                    sensitivity, 
                    results, 
                    assessment.impact_criteria
                )
                
                # Add findings to the assessment
                for finding in impact_findings:
                    if hasattr(assessment, 'add_finding'):
                        assessment.add_finding(
                            receptor_type=receptor_type,
                            impact_level=finding['impact_level'],
                            description=finding['description'],
                            confidence=finding.get('confidence')
                        )
                    else:
                        if not hasattr(assessment, 'findings') or assessment.findings is None:
                            assessment.findings = []
                        
                        assessment.findings.append({
                            'receptor_type': receptor_type,
                            'impact_level': finding['impact_level'],
                            'description': finding['description'],
                            'confidence': finding.get('confidence'),
                            'timestamp': datetime.now().isoformat()
                        })
            
            # Generate recommendations based on findings
            recommendations = self._generate_assessment_recommendations(assessment)
            
            # Add recommendations to the assessment
            for rec in recommendations:
                if hasattr(assessment, 'add_recommendation'):
                    assessment.add_recommendation(
                        recommendation_type=rec['type'],
                        description=rec['description'],
                        priority=rec.get('priority', 'MEDIUM')
                    )
                else:
                    if not hasattr(assessment, 'recommendations') or assessment.recommendations is None:
                        assessment.recommendations = []
                    
                    assessment.recommendations.append({
                        'recommendation_type': rec['type'],
                        'description': rec['description'],
                        'priority': rec.get('priority', 'MEDIUM'),
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Mark assessment as complete
            if hasattr(assessment, 'complete_assessment'):
                assessment.complete_assessment()
            else:
                assessment.status = 'COMPLETED'
            
            # Save the updated assessment
            updated_assessment = self.run_repository.update(assessment)
            
            logger.info(f"Completed environmental impact assessment with ID: {assessment_id}")
            return updated_assessment
            
        except Exception as e:
            # Mark the assessment as failed
            assessment.status = 'FAILED'
            assessment.failure_reason = str(e)
            self.run_repository.update(assessment)
            
            logger.error(f"Error conducting environmental impact assessment {assessment_id}: {str(e)}")
            raise RuntimeError(f"Environmental impact assessment failed: {str(e)}")
    
    # Helper methods
    
    def _execute_with_adapter(
        self, 
        run: ModelRun, 
        model: PollutionModel, 
        sources: List[EmissionSource]
    ) -> Dict[str, Any]:
        """
        Execute a model run using the external modeling system adapter.
        
        Args:
            run: The model run
            model: The pollution model
            sources: List of emission sources
            
        Returns:
            Dictionary with model results
            
        Raises:
            RuntimeError: If modeling adapter is not configured or execution fails
        """
        if not self.modeling_adapter:
            raise RuntimeError("Modeling system adapter not configured")
        
        # Prepare run data for the adapter
        run_data = {
            'run_id': run.id,
            'model': model.to_dict(),
            'sources': [source.to_dict() for source in sources],
            'parameters': run.run_parameters,
            'start_time': run.start_time,
            'end_time': run.end_time,
            'spatial_domain': run.spatial_domain,
        }
        
        if hasattr(run, 'meteorological_data') and run.meteorological_data:
            run_data['meteorological_data'] = run.meteorological_data
            
        if hasattr(run, 'terrain_data') and run.terrain_data:
            run_data['terrain_data'] = run.terrain_data
            
        if hasattr(run, 'background_concentrations') and run.background_concentrations:
            run_data['background_concentrations'] = run.background_concentrations
        
        # Execute via adapter
        result = self.modeling_adapter.execute_model(run_data)
        
        return result
    
    def _execute_locally(
        self, 
        run: ModelRun, 
        model: PollutionModel, 
        sources: List[EmissionSource]
    ) -> Dict[str, Any]:
        """
        Execute a model run locally (simplified implementation).
        
        Args:
            run: The model run
            model: The pollution model
            sources: List of emission sources
            
        Returns:
            Dictionary with model results
        """
        # This is a simplified implementation that generates mock results
        # In a real implementation, this would run a pollution model
        
        # Get all pollutant types from sources
        pollutant_types = set()
        for source in sources:
            for pollutant in source.pollutant_types:
                pollutant_types.add(pollutant)
        
        # Generate mock results for each pollutant type
        pollutant_results = {}
        
        for pollutant in pollutant_types:
            # Create a simple Gaussian plume model result
            grid_size = run.run_parameters.get('grid_resolution', 1.0)
            
            # Create a grid around the sources
            min_lat = min(source.location.latitude for source in sources) - 0.1
            max_lat = max(source.location.latitude for source in sources) + 0.1
            min_lon = min(source.location.longitude for source in sources) - 0.1
            max_lon = max(source.location.longitude for source in sources) + 0.1
            
            # Create concentration grid
            grid = []
            for lat in [min_lat + i * grid_size / 100 for i in range(int((max_lat - min_lat) * 100 / grid_size) + 1)]:
                for lon in [min_lon + i * grid_size / 100 for i in range(int((max_lon - min_lon) * 100 / grid_size) + 1)]:
                    # Calculate distance from each source
                    concentration = 0
                    for source in sources:
                        if pollutant in source.pollutant_types:
                            # Get emission rate for this pollutant
                            emission_rate = source.emission_rates.get(pollutant, 0)
                            
                            # Calculate distance from source to this grid point
                            distance = ((lat - source.location.latitude) ** 2 + 
                                       (lon - source.location.longitude) ** 2) ** 0.5
                            
                            # Simple inverse-square model
                            if distance > 0:
                                point_concentration = emission_rate / (distance * 111000) ** 2  # Convert to approx meters
                                concentration += point_concentration
                    
                    if concentration > 0:
                        grid.append({
                            'latitude': lat,
                            'longitude': lon,
                            'concentration': concentration
                        })
            
            # Calculate basic statistics
            concentrations = [point['concentration'] for point in grid]
            max_concentration = max(concentrations) if concentrations else 0
            avg_concentration = sum(concentrations) / len(concentrations) if concentrations else 0
            
            # Check for exceedances
            threshold = self.result_thresholds.get(pollutant)
            exceedances = []
            
            if threshold is not None:
                for point in grid:
                    if point['concentration'] > threshold:
                        exceedance = {
                            'latitude': point['latitude'],
                            'longitude': point['longitude'],
                            'concentration': point['concentration'],
                            'threshold': threshold,
                            'exceedance_ratio': point['concentration'] / threshold
                        }
                        exceedances.append(exceedance)
            
            pollutant_results[pollutant] = {
                'grid': grid,
                'statistics': {
                    'max_concentration': max_concentration,
                    'avg_concentration': avg_concentration,
                    'num_grid_points': len(grid),
                    'num_exceedances': len(exceedances)
                },
                'exceedances': exceedances
            }
        
        # Assemble overall results
        result = {
            'run_id': run.id,
            'execution_time': datetime.now().isoformat(),
            'pollutant_results': pollutant_results,
            'model_parameters': run.run_parameters,
            'spatial_domain': run.spatial_domain,
            'temporal_domain': {
                'start_time': run.start_time,
                'end_time': run.end_time
            }
        }
        
        # Write result to file
        result_file = os.path.join(self.working_dir, f"{run.id}_result.json")
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        return result
    
    def _create_results_from_execution(self, run: ModelRun, execution_result: Dict[str, Any]) -> List[ModelResult]:
        """
        Create model results from execution output.
        
        Args:
            run: The model run
            execution_result: Dictionary with execution results
            
        Returns:
            List of created model results
        """
        created_results = []
        
        # Process each pollutant result
        for pollutant, pollutant_data in execution_result.get('pollutant_results', {}).items():
            # Determine result type (concentration, deposition, etc.)
            result_type = 'concentration'
            
            # Get spatial coverage
            spatial_coverage = run.spatial_domain.copy() if hasattr(run, 'spatial_domain') else {}
            
            # Get timestamps (start and end time for now)
            timestamps = [run.start_time, run.end_time]
            
            # Create a result object
            result_data = {
                'model_run_id': run.id,
                'result_type': result_type,
                'pollutant_type': pollutant,
                'timestamps': timestamps,
                'spatial_coverage': spatial_coverage,
                'data_format': 'json',
                'data_url': os.path.join(self.working_dir, f"{run.id}_result.json"),
                'data_summary': pollutant_data.get('statistics', {})
            }
            
            # Add exceedances if present
            if 'exceedances' in pollutant_data and pollutant_data['exceedances']:
                result_data['exceedances'] = pollutant_data['exceedances']
                
            # Generate visualization if adapter available
            if self.result_adapter:
                try:
                    visualization_result = self.result_adapter.generate_visualization({
                        'result_type': result_type,
                        'pollutant_type': pollutant,
                        'grid_data': pollutant_data.get('grid', []),
                        'exceedances': pollutant_data.get('exceedances', []),
                        'spatial_domain': spatial_coverage,
                        'model_run_id': run.id
                    })
                    
                    if 'visualization_url' in visualization_result:
                        result_data['visualization_url'] = visualization_result['visualization_url']
                        
                except Exception as e:
                    logger.warning(f"Error generating visualization for result: {str(e)}")
            
            # Create and save the result
            result = ModelResult(**result_data)
            created_result = self.result_repository.create(result)
            created_results.append(created_result)
        
        return created_results
    
    def _extract_metric_value(self, results: List[ModelResult], metric: str) -> Optional[float]:
        """
        Extract a specific metric value from model results.
        
        Args:
            results: List of model results
            metric: Metric to extract
            
        Returns:
            The metric value or None if not found
        """
        if not results:
            return None
        
        # Parse metric format (e.g., "max_concentration.PM25")
        metric_parts = metric.split('.')
        
        if len(metric_parts) == 2:
            stat_name = metric_parts[0]
            pollutant = metric_parts[1]
            
            # Find result for the pollutant
            result = next((r for r in results if hasattr(r, 'pollutant_type') and r.pollutant_type == pollutant), None)
            
            if result and hasattr(result, 'data_summary'):
                # Extract statistic
                return result.data_summary.get(stat_name)
                
        elif len(metric_parts) == 1:
            # Aggregate metric across all results
            if metric == 'total_exceedances':
                total = 0
                for result in results:
                    if hasattr(result, 'exceedances'):
                        total += len(result.exceedances)
                return total
                
            elif metric == 'max_concentration_any':
                max_value = 0
                for result in results:
                    if hasattr(result, 'data_summary'):
                        value = result.data_summary.get('max_concentration', 0)
                        max_value = max(max_value, value)
                return max_value
        
        return None
    
    def _generate_analysis_recommendation(
        self, 
        analysis: ScenarioAnalysis, 
        results: Dict[str, Any]
    ) -> str:
        """
        Generate a recommendation based on scenario analysis results.
        
        Args:
            analysis: The scenario analysis
            results: Analysis results
            
        Returns:
            Recommendation text
        """
        # Find the best scenario for each metric
        best_scenarios = {}
        
        for metric, metric_results in results.items():
            if 'exceedances' in metric or 'concentration' in metric:
                # For these metrics, lower is better
                best_run_id = None
                best_value = float('inf')
                
                for run_id, run_data in metric_results.items():
                    if run_id == 'base':
                        continue
                        
                    value = run_data.get('value')
                    if value is not None and value < best_value:
                        best_value = value
                        best_run_id = run_id
                        
                if best_run_id and best_value < metric_results.get('base', float('inf')):
                    if best_run_id not in best_scenarios:
                        best_scenarios[best_run_id] = []
                    best_scenarios[best_run_id].append(metric)
        
        # Count how many metrics each scenario is best for
        scenario_counts = {run_id: len(metrics) for run_id, metrics in best_scenarios.items()}
        
        # Find the overall best scenario
        best_scenario_id = max(scenario_counts.items(), key=lambda x: x[1])[0] if scenario_counts else None
        
        # Generate recommendation
        if best_scenario_id:
            scenario_name = analysis.scenario_descriptions.get(best_scenario_id, f"Scenario {best_scenario_id}")
            metrics_improved = best_scenarios[best_scenario_id]
            
            recommendation = f"Based on the analysis, {scenario_name} appears to be the most promising scenario. "
            recommendation += f"It provides the best results for {len(metrics_improved)} of the {len(analysis.comparison_metrics)} metrics analyzed, "
            recommendation += f"including {', '.join(metrics_improved[:3])}"
            
            if len(metrics_improved) > 3:
                recommendation += f", and {len(metrics_improved) - 3} others"
                
            recommendation += ". This scenario should be considered for further assessment and potential implementation."
            
        else:
            recommendation = "None of the analyzed scenarios showed significant improvements over the base case. "
            recommendation += "Further refinement of scenarios or consideration of additional alternatives is recommended."
        
        return recommendation
    
    def _evaluate_receptor_impact(
        self, 
        receptor_type: str, 
        location: Dict[str, Any], 
        sensitivity: str, 
        results: List[ModelResult], 
        impact_criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate impacts on a specific receptor.
        
        Args:
            receptor_type: Type of receptor
            location: Location of the receptor
            sensitivity: Sensitivity of the receptor
            results: List of model results
            impact_criteria: Criteria for impact assessment
            
        Returns:
            List of impact findings
        """
        findings = []
        
        # Get criteria for this receptor type
        type_criteria = impact_criteria.get(receptor_type, impact_criteria.get('default', {}))
        
        if not type_criteria:
            # No criteria for this receptor type
            findings.append({
                'impact_level': 'Unknown',
                'description': f"No impact criteria available for {receptor_type} receptors",
                'confidence': 'Low'
            })
            return findings
        
        # Extract receptor location
        if not location or 'latitude' not in location or 'longitude' not in location:
            findings.append({
                'impact_level': 'Unknown',
                'description': f"Invalid location data for {receptor_type} receptor",
                'confidence': 'Low'
            })
            return findings
            
        receptor_lat = location['latitude']
        receptor_lon = location['longitude']
        
        # Assess impact for each result
        for result in results:
            if not hasattr(result, 'pollutant_type'):
                continue
                
            pollutant = result.pollutant_type
            
            # Get criteria for this pollutant
            pollutant_criteria = type_criteria.get(pollutant, type_criteria.get('default', {}))
            
            if not pollutant_criteria:
                continue
                
            # Find concentration at receptor location
            concentration = self._interpolate_concentration(
                result, receptor_lat, receptor_lon)
                
            if concentration is None:
                continue
                
            # Get thresholds from criteria
            thresholds = pollutant_criteria.get('thresholds', {})
            
            # Determine impact level based on concentration and sensitivity
            impact_level = 'Negligible'
            
            if sensitivity == 'High':
                if concentration > thresholds.get('severe', float('inf')):
                    impact_level = 'Severe'
                elif concentration > thresholds.get('major', float('inf')):
                    impact_level = 'Major'
                elif concentration > thresholds.get('moderate', float('inf')):
                    impact_level = 'Moderate'
                elif concentration > thresholds.get('minor', float('inf')):
                    impact_level = 'Minor'
            elif sensitivity == 'Medium':
                if concentration > thresholds.get('severe', float('inf')) * 1.5:
                    impact_level = 'Severe'
                elif concentration > thresholds.get('major', float('inf')) * 1.5:
                    impact_level = 'Major'
                elif concentration > thresholds.get('moderate', float('inf')) * 1.5:
                    impact_level = 'Moderate'
                elif concentration > thresholds.get('minor', float('inf')) * 1.5:
                    impact_level = 'Minor'
            else:  # Low sensitivity
                if concentration > thresholds.get('severe', float('inf')) * 2:
                    impact_level = 'Severe'
                elif concentration > thresholds.get('major', float('inf')) * 2:
                    impact_level = 'Major'
                elif concentration > thresholds.get('moderate', float('inf')) * 2:
                    impact_level = 'Moderate'
                elif concentration > thresholds.get('minor', float('inf')) * 2:
                    impact_level = 'Minor'
            
            # Add finding for this pollutant
            finding = {
                'impact_level': impact_level,
                'description': f"{impact_level} impact on {receptor_type} receptor due to {pollutant} concentration of {concentration:.2f}",
                'confidence': 'Medium',
                'pollutant': pollutant,
                'concentration': concentration
            }
            
            findings.append(finding)
        
        return findings
    
    def _generate_assessment_recommendations(self, assessment: EnvironmentalImpactAssessment) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on impact assessment findings.
        
        Args:
            assessment: The environmental impact assessment
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not hasattr(assessment, 'findings') or not assessment.findings:
            # No findings to base recommendations on
            recommendations.append({
                'type': 'Further Assessment',
                'description': 'Conduct more detailed assessment with additional data to better evaluate potential impacts',
                'priority': 'MEDIUM'
            })
            return recommendations
        
        # Group findings by impact level
        findings_by_level = {
            'Severe': [],
            'Major': [],
            'Moderate': [],
            'Minor': [],
            'Negligible': []
        }
        
        # Group findings by receptor type
        findings_by_receptor = {}
        
        # Group findings by pollutant
        findings_by_pollutant = {}
        
        for finding in assessment.findings:
            level = finding.get('impact_level', 'Unknown')
            if level in findings_by_level:
                findings_by_level[level].append(finding)
                
            receptor_type = finding.get('receptor_type', 'Unknown')
            if receptor_type not in findings_by_receptor:
                findings_by_receptor[receptor_type] = []
            findings_by_receptor[receptor_type].append(finding)
            
            pollutant = finding.get('pollutant')
            if pollutant:
                if pollutant not in findings_by_pollutant:
                    findings_by_pollutant[pollutant] = []
                findings_by_pollutant[pollutant].append(finding)
        
        # Generate recommendations based on findings
        
        # Address severe impacts first
        if findings_by_level['Severe']:
            pollutants = set(f.get('pollutant') for f in findings_by_level['Severe'] if f.get('pollutant'))
            receptors = set(f.get('receptor_type') for f in findings_by_level['Severe'])
            
            recommendations.append({
                'type': 'Mitigation - Urgent',
                'description': f"Implement immediate measures to reduce {', '.join(pollutants)} emissions to address severe impacts on {', '.join(receptors)}",
                'priority': 'HIGH'
            })
        
        # Address major impacts
        if findings_by_level['Major']:
            pollutants = set(f.get('pollutant') for f in findings_by_level['Major'] if f.get('pollutant'))
            receptors = set(f.get('receptor_type') for f in findings_by_level['Major'])
            
            recommendations.append({
                'type': 'Mitigation - High Priority',
                'description': f"Develop and implement plans to reduce {', '.join(pollutants)} emissions to minimize major impacts on {', '.join(receptors)}",
                'priority': 'HIGH'
            })
        
        # Address moderate impacts
        if findings_by_level['Moderate']:
            pollutants = set(f.get('pollutant') for f in findings_by_level['Moderate'] if f.get('pollutant'))
            
            recommendations.append({
                'type': 'Mitigation - Medium Priority',
                'description': f"Consider measures to reduce {', '.join(pollutants)} emissions where technically and economically feasible",
                'priority': 'MEDIUM'
            })
        
        # Recommend monitoring for key pollutants
        key_pollutants = set()
        for level in ['Severe', 'Major', 'Moderate']:
            key_pollutants.update(f.get('pollutant') for f in findings_by_level[level] if f.get('pollutant'))
        
        if key_pollutants:
            recommendations.append({
                'type': 'Monitoring',
                'description': f"Implement enhanced monitoring program for {', '.join(key_pollutants)} to track concentrations and verify model predictions",
                'priority': 'MEDIUM'
            })
        
        # Recommend sensitive receptor protection
        sensitive_receptors = []
        for receptor_type, findings in findings_by_receptor.items():
            high_impact_count = 0
            for finding in findings:
                level = finding.get('impact_level')
                if level in ['Severe', 'Major']:
                    high_impact_count += 1
            
            if high_impact_count > 0:
                sensitive_receptors.append(receptor_type)
        
        if sensitive_receptors:
            recommendations.append({
                'type': 'Receptor Protection',
                'description': f"Develop specific protection measures for sensitive {', '.join(sensitive_receptors)} receptors experiencing high impacts",
                'priority': 'HIGH' if 'Severe' in [f.get('impact_level') for f in assessment.findings] else 'MEDIUM'
            })
        
        # Recommend long-term planning for persistent issues
        if len(findings_by_level['Major']) + len(findings_by_level['Severe']) > 0:
            recommendations.append({
                'type': 'Planning',
                'description': "Develop long-term emission reduction strategy to ensure sustainable compliance with environmental standards",
                'priority': 'MEDIUM'
            })
        
        # Recommend further assessment if few findings
        if len(assessment.findings) < 5:
            recommendations.append({
                'type': 'Further Assessment',
                'description': 'Conduct more detailed assessment with additional receptors and scenarios to better characterize potential impacts',
                'priority': 'MEDIUM'
            })
        
        return recommendations
    
    def _interpolate_concentration(
        self, 
        result: ModelResult, 
        latitude: float, 
        longitude: float
    ) -> Optional[float]:
        """
        Interpolate concentration at a specific location from grid data.
        
        Args:
            result: Model result with grid data
            latitude: Latitude of the receptor
            longitude: Longitude of the receptor
            
        Returns:
            Interpolated concentration or None if not available
        """
        # In a real implementation, this would access the result data and perform spatial interpolation
        # For this simplified version, we'll generate a value based on proximity to exceedances
        
        # Check if result has exceedances
        if not hasattr(result, 'exceedances') or not result.exceedances:
            return None
        
        # Find nearest exceedance point
        min_distance = float('inf')
        nearest_concentration = None
        
        for exceedance in result.exceedances:
            if 'latitude' not in exceedance or 'longitude' not in exceedance:
                continue
                
            # Calculate distance
            distance = ((latitude - exceedance['latitude']) ** 2 + 
                       (longitude - exceedance['longitude']) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                nearest_concentration = exceedance.get('concentration')
        
        if nearest_concentration is not None:
            # Decrease concentration with distance (inverse linear relationship)
            # Convert degrees to approximate kilometers (very rough approximation)
            distance_km = min_distance * 111  # 1 degree is roughly 111 km at the equator
            
            if distance_km < 0.1:
                return nearest_concentration
            elif distance_km < 10:
                return nearest_concentration * (1 - (distance_km / 10))
            else:
                return nearest_concentration * 0.1  # Minimum 10% of nearest exceedance
        
        # If no exceedances or couldn't calculate, return a default low value
        return 0.1  # Arbitrary low value