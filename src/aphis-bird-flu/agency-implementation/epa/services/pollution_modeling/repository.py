"""
Repository implementation for Pollution Modeling service.
Provides data access operations for pollution models and simulation results.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
import json
import os
import logging

from agency_implementation.epa.models.base import EPARepository, PollutantType
from agency_implementation.epa.models.pollution import (
    PollutionModel, EmissionSource, ModelRun, 
    ModelResult, ScenarioAnalysis, EnvironmentalImpactAssessment
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PollutionModelRepository(EPARepository):
    """Repository for pollution models"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize repository"""
        self.storage_path = storage_path
        self.models: Dict[str, PollutionModel] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"PollutionModelRepository initialized with {len(self.models)} models")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for model_data in data.get('models', []):
                model = PollutionModel.from_dict(model_data)
                self.models[model.id] = model
                
            logger.info(f"Loaded {len(self.models)} models from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'models': [model.to_dict() for model in self.models.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.models)} models to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[PollutionModel]:
        """Get a model by ID"""
        return self.models.get(entity_id)
    
    def get_all(self) -> List[PollutionModel]:
        """Get all models"""
        return list(self.models.values())
    
    def create(self, entity: PollutionModel) -> PollutionModel:
        """Create a new model"""
        self.models[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: PollutionModel) -> PollutionModel:
        """Update an existing model"""
        if entity.id not in self.models:
            raise ValueError(f"Model with ID {entity.id} does not exist")
            
        self.models[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a model by ID"""
        if entity_id in self.models:
            del self.models[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[PollutionModel]:
        """Find models matching criteria"""
        results = []
        
        for model in self.models.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(model, key) or getattr(model, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(model)
                
        return results
    
    def find_by_model_type(self, model_type: str) -> List[PollutionModel]:
        """Find models by type"""
        return [m for m in self.models.values() 
                if hasattr(m, 'model_type') and m.model_type == model_type]
    
    def find_by_pollutant_type(self, pollutant_type: PollutantType) -> List[PollutionModel]:
        """Find models supporting a specific pollutant type"""
        if isinstance(pollutant_type, PollutantType):
            pollutant_type = pollutant_type.value
            
        return [m for m in self.models.values() 
                if hasattr(m, 'pollutant_types') and 
                pollutant_type in m.pollutant_types]
    
    def find_by_creator(self, creator: str) -> List[PollutionModel]:
        """Find models by creator"""
        return [m for m in self.models.values() 
                if hasattr(m, 'creator') and m.creator == creator]
    
    def find_by_spatial_resolution(self, max_resolution: float) -> List[PollutionModel]:
        """Find models with spatial resolution less than or equal to maximum"""
        return [m for m in self.models.values() 
                if hasattr(m, 'spatial_resolution') and 
                m.spatial_resolution <= max_resolution]
    
    def find_by_version(self, version: str) -> List[PollutionModel]:
        """Find models by version"""
        return [m for m in self.models.values() 
                if hasattr(m, 'version') and m.version == version]
    
    def find_latest_versions(self) -> List[PollutionModel]:
        """Find latest version of each model name"""
        # Group models by name
        by_name: Dict[str, List[PollutionModel]] = {}
        for model in self.models.values():
            if not hasattr(model, 'model_name'):
                continue
                
            name = model.model_name
            if name not in by_name:
                by_name[name] = []
                
            by_name[name].append(model)
        
        # Find latest version of each model
        latest_models = []
        for name, models in by_name.items():
            # Sort by version (assuming semantic versioning or similar)
            latest = max(models, key=lambda m: m.version)
            latest_models.append(latest)
            
        return latest_models


class EmissionSourceRepository(EPARepository):
    """Repository for emission sources"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize repository"""
        self.storage_path = storage_path
        self.sources: Dict[str, EmissionSource] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"EmissionSourceRepository initialized with {len(self.sources)} sources")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for source_data in data.get('sources', []):
                source = EmissionSource.from_dict(source_data)
                self.sources[source.id] = source
                
            logger.info(f"Loaded {len(self.sources)} sources from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'sources': [source.to_dict() for source in self.sources.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.sources)} sources to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[EmissionSource]:
        """Get a source by ID"""
        return self.sources.get(entity_id)
    
    def get_all(self) -> List[EmissionSource]:
        """Get all sources"""
        return list(self.sources.values())
    
    def create(self, entity: EmissionSource) -> EmissionSource:
        """Create a new source"""
        self.sources[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: EmissionSource) -> EmissionSource:
        """Update an existing source"""
        if entity.id not in self.sources:
            raise ValueError(f"Source with ID {entity.id} does not exist")
            
        self.sources[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a source by ID"""
        if entity_id in self.sources:
            del self.sources[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[EmissionSource]:
        """Find sources matching criteria"""
        results = []
        
        for source in self.sources.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(source, key) or getattr(source, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(source)
                
        return results
    
    def find_by_facility_id(self, facility_id: str) -> List[EmissionSource]:
        """Find sources by facility ID"""
        return [s for s in self.sources.values() 
                if hasattr(s, 'facility_id') and s.facility_id == facility_id]
    
    def find_by_source_type(self, source_type: str) -> List[EmissionSource]:
        """Find sources by type"""
        return [s for s in self.sources.values() 
                if hasattr(s, 'source_type') and s.source_type == source_type]
    
    def find_by_pollutant_type(self, pollutant_type: PollutantType) -> List[EmissionSource]:
        """Find sources emitting a specific pollutant type"""
        if isinstance(pollutant_type, PollutantType):
            pollutant_type = pollutant_type.value
            
        return [s for s in self.sources.values() 
                if hasattr(s, 'pollutant_types') and 
                pollutant_type in s.pollutant_types]
    
    def find_by_emission_rate(
        self, 
        pollutant: str, 
        min_rate: float
    ) -> List[EmissionSource]:
        """Find sources with emission rate above minimum for a specific pollutant"""
        results = []
        
        for source in self.sources.values():
            if not hasattr(source, 'emission_rates'):
                continue
                
            if pollutant in source.emission_rates and source.emission_rates[pollutant] >= min_rate:
                results.append(source)
                
        return results
    
    def find_by_geographic_area(
        self, 
        min_lat: float, 
        min_lon: float, 
        max_lat: float, 
        max_lon: float
    ) -> List[EmissionSource]:
        """Find sources within a geographic bounding box"""
        results = []
        
        for source in self.sources.values():
            if not hasattr(source, 'location'):
                continue
                
            lat = source.location.latitude
            lon = source.location.longitude
            
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                results.append(source)
                
        return results


class ModelRunRepository(EPARepository):
    """Repository for model runs"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize repository"""
        self.storage_path = storage_path
        self.runs: Dict[str, ModelRun] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"ModelRunRepository initialized with {len(self.runs)} runs")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for run_data in data.get('runs', []):
                run = ModelRun.from_dict(run_data)
                self.runs[run.id] = run
                
            logger.info(f"Loaded {len(self.runs)} runs from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'runs': [run.to_dict() for run in self.runs.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.runs)} runs to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[ModelRun]:
        """Get a run by ID"""
        return self.runs.get(entity_id)
    
    def get_all(self) -> List[ModelRun]:
        """Get all runs"""
        return list(self.runs.values())
    
    def create(self, entity: ModelRun) -> ModelRun:
        """Create a new run"""
        self.runs[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: ModelRun) -> ModelRun:
        """Update an existing run"""
        if entity.id not in self.runs:
            raise ValueError(f"Run with ID {entity.id} does not exist")
            
        self.runs[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a run by ID"""
        if entity_id in self.runs:
            del self.runs[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[ModelRun]:
        """Find runs matching criteria"""
        results = []
        
        for run in self.runs.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(run, key) or getattr(run, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(run)
                
        return results
    
    def find_by_model_id(self, model_id: str) -> List[ModelRun]:
        """Find runs by model ID"""
        return [r for r in self.runs.values() 
                if hasattr(r, 'model_id') and r.model_id == model_id]
    
    def find_by_status(self, status: str) -> List[ModelRun]:
        """Find runs by status"""
        return [r for r in self.runs.values() 
                if hasattr(r, 'run_status') and r.run_status == status]
    
    def find_by_emission_source(self, source_id: str) -> List[ModelRun]:
        """Find runs using a specific emission source"""
        return [r for r in self.runs.values() 
                if hasattr(r, 'emission_sources') and 
                source_id in r.emission_sources]
    
    def find_by_date_range(
        self, 
        start_date: Union[datetime, str], 
        end_date: Union[datetime, str]
    ) -> List[ModelRun]:
        """Find runs within a simulation date range"""
        # Convert string dates to datetime objects if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
            
        results = []
        
        for run in self.runs.values():
            if not (hasattr(run, 'start_time') and hasattr(run, 'end_time')):
                continue
                
            run_start = run.start_time
            run_end = run.end_time
            
            # Convert string dates to datetime objects if needed
            if isinstance(run_start, str):
                run_start = datetime.fromisoformat(run_start)
            if isinstance(run_end, str):
                run_end = datetime.fromisoformat(run_end)
                
            # Check for overlap
            if not (run_end < start_date or run_start > end_date):
                results.append(run)
                
        return results
    
    def find_by_run_date_range(
        self, 
        start_date: Union[datetime, str], 
        end_date: Union[datetime, str]
    ) -> List[ModelRun]:
        """Find runs executed within a date range"""
        # Convert string dates to datetime objects if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
            
        results = []
        
        for run in self.runs.values():
            if not hasattr(run, 'run_start'):
                continue
                
            run_start = run.run_start
            
            # Convert string date to datetime object if needed
            if isinstance(run_start, str):
                run_start = datetime.fromisoformat(run_start)
                
            if start_date <= run_start <= end_date:
                results.append(run)
                
        return results
    
    def find_by_run_by(self, run_by: str) -> List[ModelRun]:
        """Find runs executed by a specific user"""
        return [r for r in self.runs.values() 
                if hasattr(r, 'run_by') and r.run_by == run_by]


class ModelResultRepository(EPARepository):
    """Repository for model results"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize repository"""
        self.storage_path = storage_path
        self.results: Dict[str, ModelResult] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"ModelResultRepository initialized with {len(self.results)} results")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for result_data in data.get('results', []):
                result = ModelResult.from_dict(result_data)
                self.results[result.id] = result
                
            logger.info(f"Loaded {len(self.results)} results from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'results': [result.to_dict() for result in self.results.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.results)} results to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[ModelResult]:
        """Get a result by ID"""
        return self.results.get(entity_id)
    
    def get_all(self) -> List[ModelResult]:
        """Get all results"""
        return list(self.results.values())
    
    def create(self, entity: ModelResult) -> ModelResult:
        """Create a new result"""
        self.results[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: ModelResult) -> ModelResult:
        """Update an existing result"""
        if entity.id not in self.results:
            raise ValueError(f"Result with ID {entity.id} does not exist")
            
        self.results[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a result by ID"""
        if entity_id in self.results:
            del self.results[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[ModelResult]:
        """Find results matching criteria"""
        results = []
        
        for result in self.results.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(result, key) or getattr(result, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(result)
                
        return results
    
    def find_by_model_run_id(self, model_run_id: str) -> List[ModelResult]:
        """Find results by model run ID"""
        return [r for r in self.results.values() 
                if hasattr(r, 'model_run_id') and r.model_run_id == model_run_id]
    
    def find_by_result_type(self, result_type: str) -> List[ModelResult]:
        """Find results by type"""
        return [r for r in self.results.values() 
                if hasattr(r, 'result_type') and r.result_type == result_type]
    
    def find_by_pollutant_type(self, pollutant_type: PollutantType) -> List[ModelResult]:
        """Find results for a specific pollutant type"""
        if isinstance(pollutant_type, PollutantType):
            pollutant_type = pollutant_type.value
            
        return [r for r in self.results.values() 
                if hasattr(r, 'pollutant_type') and r.pollutant_type == pollutant_type]
    
    def find_with_exceedances(self) -> List[ModelResult]:
        """Find results that have exceedances"""
        return [r for r in self.results.values() 
                if hasattr(r, 'exceedances') and r.exceedances]
    
    def find_by_data_format(self, data_format: str) -> List[ModelResult]:
        """Find results by data format"""
        return [r for r in self.results.values() 
                if hasattr(r, 'data_format') and r.data_format == data_format]