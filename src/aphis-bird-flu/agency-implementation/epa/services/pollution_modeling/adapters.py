"""
Adapters for integrating with external modeling systems and result processing services.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
import os
import requests
from abc import ABC, abstractmethod

from agency_implementation.epa.models.pollution import (
    PollutionModel, EmissionSource, ModelRun, ModelResult
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExternalSystemAdapter(ABC):
    """Base class for external system adapters"""
    
    @abstractmethod
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch data from external system"""
        pass
    
    @abstractmethod
    def send_data(self, data: Any) -> bool:
        """Send data to external system"""
        pass


class ModelingSystemAdapter(ExternalSystemAdapter):
    """
    Adapter for external modeling system integration.
    
    Provides methods to execute pollution models using external modeling systems,
    such as AERMOD, CALPUFF, or cloud-based modeling platforms.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the adapter.
        
        Args:
            config: Configuration dictionary with connection details
        """
        self.config = config
        self.api_url = config.get('api_url')
        self.api_key = config.get('api_key')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.timeout = config.get('timeout', 300)  # Longer timeout for model runs
        self.model_defaults = config.get('model_defaults', {})
        self.working_dir = config.get('working_dir', '/tmp/epa_modeling')
        os.makedirs(self.working_dir, exist_ok=True)
        
        logger.info(f"ModelingSystemAdapter initialized for {self.api_url}")
    
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from modeling system.
        
        Args:
            **kwargs: Query parameters for the request
            
        Returns:
            List of data records from the modeling system
            
        Raises:
            ConnectionError: If connection to the modeling system fails
        """
        try:
            # In a real implementation, this would make an API call to the modeling system
            # For demonstration, we return mock data
            if not self.api_url:
                logger.warning("API URL not configured, returning mock data")
                return self._generate_mock_data(kwargs.get('count', 5))
            
            endpoint = kwargs.get('endpoint', 'results')
            url = f"{self.api_url}/{endpoint}"
            
            logger.info(f"Fetching data from {url} with params: {kwargs}")
            
            # This is where an actual API call would happen
            # response = requests.get(url, headers=self.headers, params=kwargs, timeout=self.timeout)
            # response.raise_for_status()
            # return response.json()
            
            # For demonstration, return mock data
            return self._generate_mock_data(kwargs.get('count', 5))
            
        except Exception as e:
            logger.error(f"Error fetching data from modeling system: {str(e)}")
            raise ConnectionError(f"Failed to connect to modeling system: {str(e)}")
    
    def send_data(self, data: Any) -> bool:
        """
        Send data to modeling system.
        
        Args:
            data: Data to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a real implementation, this would make an API call to the modeling system
            # For demonstration, we just log the data
            if not self.api_url:
                logger.warning("API URL not configured, simulating successful send")
                logger.debug(f"Would send data: {json.dumps(data, default=str)}")
                return True
            
            endpoint = data.get('endpoint', 'upload')
            url = f"{self.api_url}/{endpoint}"
            
            if 'endpoint' in data:
                data_to_send = {k: v for k, v in data.items() if k != 'endpoint'}
            else:
                data_to_send = data
                
            logger.info(f"Sending data to {url}")
            
            # This is where an actual API call would happen
            # response = requests.post(url, headers=self.headers, json=data_to_send, timeout=self.timeout)
            # response.raise_for_status()
            # return True
            
            # For demonstration, return success
            logger.debug(f"Would send data: {json.dumps(data_to_send, default=str)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending data to modeling system: {str(e)}")
            return False
    
    def execute_model(self, run_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a pollution model.
        
        Args:
            run_data: Data for the model run
            
        Returns:
            Dictionary with model results
            
        Raises:
            RuntimeError: If model execution fails
        """
        try:
            # In a real implementation, this would execute the model via API
            # For demonstration, we'll generate mock results
            if not self.api_url:
                logger.warning("API URL not configured, simulating model execution")
                return self._simulate_model_execution(run_data)
            
            # Prepare run data for the API
            execution_data = {
                'run_id': run_data.get('run_id'),
                'model_type': run_data.get('model', {}).get('model_type'),
                'model_configuration': {
                    **run_data.get('model', {}).get('parameters', {}),
                    **run_data.get('parameters', {})
                },
                'sources': run_data.get('sources', []),
                'start_time': run_data.get('start_time'),
                'end_time': run_data.get('end_time'),
                'spatial_domain': run_data.get('spatial_domain'),
                'meteorological_data': run_data.get('meteorological_data'),
                'terrain_data': run_data.get('terrain_data'),
                'background_concentrations': run_data.get('background_concentrations')
            }
            
            endpoint = 'execute'
            url = f"{self.api_url}/{endpoint}"
            
            logger.info(f"Executing model via {url}")
            
            # This is where an actual API call would happen
            # response = requests.post(url, headers=self.headers, json=execution_data, timeout=self.timeout)
            # response.raise_for_status()
            # return response.json()
            
            # For demonstration, simulate execution
            return self._simulate_model_execution(run_data)
            
        except Exception as e:
            logger.error(f"Error executing model: {str(e)}")
            raise RuntimeError(f"Model execution failed: {str(e)}")
    
    def _simulate_model_execution(self, run_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate model execution for demonstration.
        
        Args:
            run_data: Data for the model run
            
        Returns:
            Dictionary with simulated model results
        """
        from random import random, uniform, gauss
        
        # Get run ID and model type
        run_id = run_data.get('run_id', f"run-{int(datetime.now().timestamp())}")
        model_type = run_data.get('model', {}).get('model_type', 'gaussian_plume')
        
        # Get sources
        sources = run_data.get('sources', [])
        
        # Get all pollutant types from sources
        pollutant_types = set()
        for source in sources:
            for pollutant in source.get('pollutant_types', []):
                pollutant_types.add(pollutant)
        
        # Generate mock results for each pollutant type
        pollutant_results = {}
        
        for pollutant in pollutant_types:
            # Get spatial domain
            spatial_domain = run_data.get('spatial_domain', {})
            min_lat = spatial_domain.get('min_latitude', 0)
            max_lat = spatial_domain.get('max_latitude', 1)
            min_lon = spatial_domain.get('min_longitude', 0)
            max_lon = spatial_domain.get('max_longitude', 1)
            
            # Get grid resolution
            grid_resolution = run_data.get('parameters', {}).get('grid_resolution', 0.01)
            
            # Generate grid points
            grid = []
            lat_steps = int((max_lat - min_lat) / grid_resolution) + 1
            lon_steps = int((max_lon - min_lon) / grid_resolution) + 1
            
            for i in range(lat_steps):
                lat = min_lat + i * grid_resolution
                for j in range(lon_steps):
                    lon = min_lon + j * grid_resolution
                    
                    # Calculate concentration based on model type
                    if model_type == 'gaussian_plume':
                        # Simple Gaussian plume model
                        concentration = 0
                        for source in sources:
                            if pollutant in source.get('pollutant_types', []):
                                source_lat = source.get('location', {}).get('latitude', 0)
                                source_lon = source.get('location', {}).get('longitude', 0)
                                
                                # Calculate distance
                                distance = ((lat - source_lat) ** 2 + (lon - source_lon) ** 2) ** 0.5
                                
                                # Get emission rate
                                emission_rate = source.get('emission_rates', {}).get(pollutant, 0)
                                
                                # Simple model - concentration decreases with square of distance
                                if distance > 0:
                                    point_concentration = emission_rate / (distance * 111000) ** 2  # Convert to approx meters
                                    concentration += point_concentration
                    else:
                        # Random concentration for other model types
                        concentration = random() * 10
                    
                    # Add some random variation
                    concentration *= uniform(0.8, 1.2)
                    
                    # Add grid point if concentration is significant
                    if concentration > 0.001:
                        grid.append({
                            'latitude': lat,
                            'longitude': lon,
                            'concentration': concentration
                        })
            
            # Calculate statistics
            concentrations = [point['concentration'] for point in grid]
            max_concentration = max(concentrations) if concentrations else 0
            avg_concentration = sum(concentrations) / len(concentrations) if concentrations else 0
            
            # Define threshold based on pollutant
            threshold_map = {
                'PM25': 35.0,
                'PM10': 150.0,
                'OZONE': 0.070,
                'NO2': 100.0,
                'SO2': 75.0,
                'CO': 9.0,
                'LEAD': 0.15
            }
            
            threshold = threshold_map.get(pollutant, max_concentration * 0.8)
            
            # Find exceedances
            exceedances = []
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
            
            # Save results for this pollutant
            pollutant_results[pollutant] = {
                'grid': grid,
                'statistics': {
                    'max_concentration': max_concentration,
                    'avg_concentration': avg_concentration,
                    'num_grid_points': len(grid),
                    'num_exceedances': len(exceedances),
                    'threshold': threshold
                },
                'exceedances': exceedances
            }
        
        # Assemble overall results
        result = {
            'run_id': run_id,
            'execution_time': datetime.now().isoformat(),
            'pollutant_results': pollutant_results,
            'model_parameters': run_data.get('parameters', {}),
            'spatial_domain': run_data.get('spatial_domain', {}),
            'temporal_domain': {
                'start_time': run_data.get('start_time'),
                'end_time': run_data.get('end_time')
            }
        }
        
        # Write result to file
        result_file = os.path.join(self.working_dir, f"{run_id}_result.json")
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        return result
    
    def _generate_mock_data(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock modeling system data for demonstration"""
        from random import choice, randint, random
        
        mock_data = []
        
        # Sample model types
        model_types = [
            "gaussian_plume", 
            "lagrangian_puff", 
            "computational_fluid_dynamics", 
            "box_model"
        ]
        
        # Sample pollutants
        pollutants = [
            "PM25", "PM10", "OZONE", "NO2", "SO2", "CO", "LEAD"
        ]
        
        # Sample statuses
        statuses = ["COMPLETED", "FAILED", "RUNNING", "QUEUED"]
        
        # Generate mock data
        for i in range(count):
            # Pick a model type
            model_type = choice(model_types)
            
            # Generate run ID
            run_id = f"RUN-{100000 + i}"
            
            # Pick a status
            status = choice(statuses)
            
            # Generate timestamps
            start_time = datetime.now().replace(hour=randint(0, 23), minute=randint(0, 59), second=randint(0, 59))
            execution_time = (start_time.timestamp() + randint(60, 3600)) if status == "COMPLETED" else None
            
            # Generate mock result
            result = {
                'run_id': run_id,
                'model_type': model_type,
                'status': status,
                'start_time': start_time.isoformat(),
                'execution_time': datetime.fromtimestamp(execution_time).isoformat() if execution_time else None,
                'parameters': {
                    'grid_resolution': choice([0.01, 0.05, 0.1]),
                    'time_resolution': choice([1, 3, 6]),
                    'use_terrain': choice([True, False]),
                    'include_background': choice([True, False])
                }
            }
            
            # Add pollutant results if completed
            if status == "COMPLETED":
                pollutant_results = {}
                
                # Pick 1-3 random pollutants
                selected_pollutants = [choice(pollutants) for _ in range(randint(1, 3))]
                
                for pollutant in selected_pollutants:
                    # Generate random statistics
                    max_concentration = random() * 100
                    avg_concentration = max_concentration * random() * 0.5
                    num_grid_points = randint(100, 1000)
                    num_exceedances = randint(0, int(num_grid_points * 0.1))
                    
                    pollutant_results[pollutant] = {
                        'statistics': {
                            'max_concentration': max_concentration,
                            'avg_concentration': avg_concentration,
                            'num_grid_points': num_grid_points,
                            'num_exceedances': num_exceedances
                        }
                    }
                
                result['pollutant_results'] = pollutant_results
            
            # Add error details if failed
            if status == "FAILED":
                result['error'] = choice([
                    "Invalid input parameters",
                    "Meteorological data not found",
                    "Execution timeout",
                    "Internal server error",
                    "Source data validation failed"
                ])
            
            mock_data.append(result)
        
        return mock_data


class ModelResultAdapter(ExternalSystemAdapter):
    """
    Adapter for processing model results.
    
    Provides methods to generate visualizations, post-process results,
    and export data to various formats.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the adapter.
        
        Args:
            config: Configuration dictionary with connection details
        """
        self.config = config
        self.api_url = config.get('api_url')
        self.api_key = config.get('api_key')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.timeout = config.get('timeout', 60)
        self.visualization_defaults = config.get('visualization_defaults', {})
        self.output_dir = config.get('output_dir', '/tmp/epa_modeling/visualizations')
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"ModelResultAdapter initialized for {self.api_url}")
    
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from result processing system.
        
        Args:
            **kwargs: Query parameters for the request
            
        Returns:
            List of data records from the result processing system
            
        Raises:
            ConnectionError: If connection to the system fails
        """
        try:
            # In a real implementation, this would make an API call to the result processing system
            # For demonstration, we return mock data
            if not self.api_url:
                logger.warning("API URL not configured, returning mock data")
                return self._generate_mock_data(kwargs.get('count', 5))
            
            endpoint = kwargs.get('endpoint', 'visualizations')
            url = f"{self.api_url}/{endpoint}"
            
            logger.info(f"Fetching data from {url} with params: {kwargs}")
            
            # This is where an actual API call would happen
            # response = requests.get(url, headers=self.headers, params=kwargs, timeout=self.timeout)
            # response.raise_for_status()
            # return response.json()
            
            # For demonstration, return mock data
            return self._generate_mock_data(kwargs.get('count', 5))
            
        except Exception as e:
            logger.error(f"Error fetching data from result processing system: {str(e)}")
            raise ConnectionError(f"Failed to connect to result processing system: {str(e)}")
    
    def send_data(self, data: Any) -> bool:
        """
        Send data to result processing system.
        
        Args:
            data: Data to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a real implementation, this would make an API call to the result processing system
            # For demonstration, we just log the data
            if not self.api_url:
                logger.warning("API URL not configured, simulating successful send")
                logger.debug(f"Would send data: {json.dumps(data, default=str)}")
                return True
            
            endpoint = data.get('endpoint', 'process')
            url = f"{self.api_url}/{endpoint}"
            
            if 'endpoint' in data:
                data_to_send = {k: v for k, v in data.items() if k != 'endpoint'}
            else:
                data_to_send = data
                
            logger.info(f"Sending data to {url}")
            
            # This is where an actual API call would happen
            # response = requests.post(url, headers=self.headers, json=data_to_send, timeout=self.timeout)
            # response.raise_for_status()
            # return True
            
            # For demonstration, return success
            logger.debug(f"Would send data: {json.dumps(data_to_send, default=str)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending data to result processing system: {str(e)}")
            return False
    
    def generate_visualization(self, visualization_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a visualization from model results.
        
        Args:
            visualization_data: Data for the visualization
            
        Returns:
            Dictionary with visualization result
            
        Raises:
            RuntimeError: If visualization generation fails
        """
        try:
            # In a real implementation, this would generate a visualization
            # For demonstration, we'll simulate it
            if not self.api_url:
                logger.warning("API URL not configured, simulating visualization generation")
                return self._simulate_visualization(visualization_data)
            
            # Prepare visualization data for the API
            vis_config = {
                **self.visualization_defaults,
                **visualization_data
            }
            
            endpoint = 'visualize'
            url = f"{self.api_url}/{endpoint}"
            
            logger.info(f"Generating visualization via {url}")
            
            # This is where an actual API call would happen
            # response = requests.post(url, headers=self.headers, json=vis_config, timeout=self.timeout)
            # response.raise_for_status()
            # return response.json()
            
            # For demonstration, simulate visualization
            return self._simulate_visualization(visualization_data)
            
        except Exception as e:
            logger.error(f"Error generating visualization: {str(e)}")
            raise RuntimeError(f"Visualization generation failed: {str(e)}")
    
    def export_results(self, result_id: str, format: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Export model results to a specific format.
        
        Args:
            result_id: ID of the model result to export
            format: Export format (e.g., csv, shapefile, netcdf)
            options: Optional export options
            
        Returns:
            Dictionary with export result
            
        Raises:
            RuntimeError: If export fails
        """
        try:
            # In a real implementation, this would export the results
            # For demonstration, we'll simulate it
            if not self.api_url:
                logger.warning("API URL not configured, simulating result export")
                return self._simulate_export(result_id, format, options)
            
            # Prepare export configuration
            export_config = {
                'result_id': result_id,
                'format': format,
                'options': options or {}
            }
            
            endpoint = 'export'
            url = f"{self.api_url}/{endpoint}"
            
            logger.info(f"Exporting result {result_id} to {format} via {url}")
            
            # This is where an actual API call would happen
            # response = requests.post(url, headers=self.headers, json=export_config, timeout=self.timeout)
            # response.raise_for_status()
            # return response.json()
            
            # For demonstration, simulate export
            return self._simulate_export(result_id, format, options)
            
        except Exception as e:
            logger.error(f"Error exporting result {result_id} to {format}: {str(e)}")
            raise RuntimeError(f"Result export failed: {str(e)}")
    
    def _simulate_visualization(self, visualization_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate visualization generation for demonstration.
        
        Args:
            visualization_data: Data for the visualization
            
        Returns:
            Dictionary with simulated visualization result
        """
        # Get visualization type and model run ID
        vis_type = visualization_data.get('result_type', 'concentration')
        run_id = visualization_data.get('model_run_id', f"run-{int(datetime.now().timestamp())}")
        pollutant = visualization_data.get('pollutant_type', 'PM25')
        
        # Generate unique visualization ID
        vis_id = f"vis-{run_id}-{pollutant}-{vis_type}"
        
        # Create a mock visualization file
        visualization_file = os.path.join(self.output_dir, f"{vis_id}.png")
        with open(visualization_file, 'w') as f:
            f.write(f"Simulated visualization for {vis_type} of {pollutant} from run {run_id}")
        
        # Create result
        result = {
            'visualization_id': vis_id,
            'visualization_url': visualization_file,
            'visualization_type': vis_type,
            'pollutant_type': pollutant,
            'model_run_id': run_id,
            'created_at': datetime.now().isoformat(),
            'format': 'png',
            'size': {
                'width': 800,
                'height': 600
            }
        }
        
        return result
    
    def _simulate_export(
        self, 
        result_id: str, 
        format: str, 
        options: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Simulate result export for demonstration.
        
        Args:
            result_id: ID of the model result to export
            format: Export format
            options: Export options
            
        Returns:
            Dictionary with simulated export result
        """
        # Create a mock export file
        export_file = os.path.join(self.output_dir, f"{result_id}.{format}")
        with open(export_file, 'w') as f:
            f.write(f"Simulated export of result {result_id} to {format} format")
        
        # Create result
        result = {
            'export_id': f"export-{result_id}-{format}",
            'result_id': result_id,
            'format': format,
            'file_url': export_file,
            'file_size': os.path.getsize(export_file),
            'created_at': datetime.now().isoformat(),
            'options': options or {}
        }
        
        return result
    
    def _generate_mock_data(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock result processing system data for demonstration"""
        from random import choice, randint
        
        mock_data = []
        
        # Sample visualization types
        vis_types = [
            "concentration_map", 
            "exceedance_map", 
            "time_series", 
            "3d_plume"
        ]
        
        # Sample pollutants
        pollutants = [
            "PM25", "PM10", "OZONE", "NO2", "SO2", "CO", "LEAD"
        ]
        
        # Sample formats
        formats = ["png", "jpg", "svg", "pdf"]
        
        # Generate mock data
        for i in range(count):
            # Pick a visualization type and pollutant
            vis_type = choice(vis_types)
            pollutant = choice(pollutants)
            format = choice(formats)
            
            # Generate visualization ID and run ID
            vis_id = f"VIS-{100000 + i}"
            run_id = f"RUN-{200000 + i % 3}"
            
            # Generate mock visualization
            data = {
                'visualization_id': vis_id,
                'visualization_type': vis_type,
                'pollutant_type': pollutant,
                'model_run_id': run_id,
                'created_at': datetime.now().isoformat(),
                'format': format,
                'file_size': randint(10000, 5000000),
                'visualization_url': f"/tmp/epa_modeling/visualizations/{vis_id}.{format}",
                'parameters': {
                    'color_scheme': choice(["viridis", "plasma", "inferno", "magma", "cividis"]),
                    'resolution': choice(["low", "medium", "high"]),
                    'show_exceedances': choice([True, False]),
                    'include_basemap': choice([True, False])
                }
            }
            
            mock_data.append(data)
        
        return mock_data