"""
Repository implementation for the Outbreak Detection service.
Provides data access operations for outbreaks and clusters.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import date, datetime
import json
import os
import logging

from agency_implementation.cdc.models.base import CDCRepository
from agency_implementation.cdc.models.human_disease import Cluster, DiseaseType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutbreakRepository(CDCRepository):
    """
    Repository for disease outbreak clusters.
    
    Implements data access operations for Cluster entities.
    In a real implementation, this would interact with a database,
    but for this implementation we use an in-memory store.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the repository.
        
        Args:
            storage_path: Optional path to store data (for persistence)
        """
        self.storage_path = storage_path
        self.clusters: Dict[str, Cluster] = {}
        self.detection_results: Dict[str, Dict[str, Any]] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"OutbreakRepository initialized with {len(self.clusters)} clusters")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for cluster_data in data.get('clusters', []):
                cluster = Cluster.from_dict(cluster_data)
                self.clusters[cluster.id] = cluster
                
            self.detection_results = data.get('detection_results', {})
                
            logger.info(f"Loaded {len(self.clusters)} clusters and {len(self.detection_results)} detection results from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'clusters': [cluster.to_dict() for cluster in self.clusters.values()],
                'detection_results': self.detection_results,
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.clusters)} clusters to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[Cluster]:
        """
        Get a cluster by its ID.
        
        Args:
            entity_id: The ID of the cluster to retrieve
            
        Returns:
            The cluster if found, None otherwise
        """
        return self.clusters.get(entity_id)
    
    def get_all(self) -> List[Cluster]:
        """
        Get all clusters.
        
        Returns:
            List of all clusters
        """
        return list(self.clusters.values())
    
    def create(self, entity: Cluster) -> Cluster:
        """
        Create a new cluster.
        
        Args:
            entity: The cluster to create
            
        Returns:
            The created cluster
        """
        self.clusters[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: Cluster) -> Cluster:
        """
        Update an existing cluster.
        
        Args:
            entity: The cluster to update
            
        Returns:
            The updated cluster
            
        Raises:
            ValueError: If the cluster does not exist
        """
        if entity.id not in self.clusters:
            raise ValueError(f"Cluster with ID {entity.id} does not exist")
            
        self.clusters[entity.id] = entity
        entity.updated_at = datetime.now().isoformat()
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """
        Delete a cluster by ID.
        
        Args:
            entity_id: The ID of the cluster to delete
            
        Returns:
            True if the cluster was deleted, False otherwise
        """
        if entity_id in self.clusters:
            del self.clusters[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[Cluster]:
        """
        Find clusters matching criteria.
        
        Args:
            criteria: Dictionary of field-value pairs to match
            
        Returns:
            List of matching clusters
        """
        results = []
        
        for cluster in self.clusters.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(cluster, key) or getattr(cluster, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(cluster)
                
        return results
    
    def find_by_jurisdiction(self, jurisdiction: str) -> List[Cluster]:
        """
        Find clusters by jurisdiction.
        
        Args:
            jurisdiction: The jurisdiction to filter by
            
        Returns:
            List of clusters in the specified jurisdiction
        """
        return [cluster for cluster in self.clusters.values() 
                if hasattr(cluster, 'regions') and jurisdiction in cluster.regions]
    
    def find_reportable(self) -> List[Cluster]:
        """
        Find reportable clusters.
        
        Returns:
            List of reportable clusters
        """
        return [cluster for cluster in self.clusters.values() 
                if hasattr(cluster, 'risk_level') and cluster.risk_level.value == 'high']
    
    def find_by_disease_type(self, disease_type: Union[DiseaseType, str]) -> List[Cluster]:
        """
        Find clusters by disease type.
        
        Args:
            disease_type: The disease type to filter by
            
        Returns:
            List of clusters with the specified disease type
        """
        if isinstance(disease_type, str):
            disease_type = DiseaseType(disease_type)
            
        return [cluster for cluster in self.clusters.values() 
                if hasattr(cluster, 'disease_type') and cluster.disease_type == disease_type]
    
    def find_active_clusters(self) -> List[Cluster]:
        """
        Find active (non-closed) clusters.
        
        Returns:
            List of active clusters
        """
        return [cluster for cluster in self.clusters.values() 
                if hasattr(cluster, 'status') and cluster.status != 'closed']
    
    def find_by_date_range(self, 
                          start_date: Union[date, str], 
                          end_date: Union[date, str]) -> List[Cluster]:
        """
        Find clusters with start dates within a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            
        Returns:
            List of clusters within the date range
        """
        # Convert string dates to date objects if needed
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
            
        results = []
        
        for cluster in self.clusters.values():
            if not hasattr(cluster, 'start_date'):
                continue
                
            cluster_date = cluster.start_date
            
            # Convert string date to date object if needed
            if isinstance(cluster_date, str):
                cluster_date = date.fromisoformat(cluster_date)
                
            if start_date <= cluster_date <= end_date:
                results.append(cluster)
                
        return results
    
    def find_by_case_id(self, case_id: str) -> List[Cluster]:
        """
        Find clusters containing a specific case.
        
        Args:
            case_id: The case ID to search for
            
        Returns:
            List of clusters containing the case
        """
        return [cluster for cluster in self.clusters.values() 
                if hasattr(cluster, 'cases') and case_id in cluster.cases]
    
    def store_detection_result(self, algorithm_id: str, result: Dict[str, Any]) -> None:
        """
        Store a detection algorithm result.
        
        Args:
            algorithm_id: Identifier for the detection algorithm
            result: Detection result data
        """
        # Add timestamp if not present
        if 'timestamp' not in result:
            result['timestamp'] = datetime.now().isoformat()
            
        # Store the result
        self.detection_results[algorithm_id] = result
        self._save_to_storage()
        
        logger.debug(f"Stored detection result for algorithm {algorithm_id}")
    
    def get_detection_result(self, algorithm_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a stored detection result.
        
        Args:
            algorithm_id: Identifier for the detection algorithm
            
        Returns:
            The detection result if found, None otherwise
        """
        return self.detection_results.get(algorithm_id)
    
    def get_all_detection_results(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all stored detection results.
        
        Returns:
            Dictionary of all detection results
        """
        return self.detection_results
    
    def generate_report(self, criteria: Dict[str, Any], format_type: str = "json") -> Any:
        """
        Generate a formatted report based on criteria.
        
        Args:
            criteria: Dictionary of criteria to filter clusters
            format_type: Format of the report (json, csv, etc.)
            
        Returns:
            Report data in the specified format
        """
        # Find clusters matching criteria
        clusters = self.find(criteria)
        
        if format_type == "json":
            return {
                "report_date": datetime.now().isoformat(),
                "criteria": criteria,
                "total_clusters": len(clusters),
                "clusters": [cluster.to_dict() for cluster in clusters]
            }
        elif format_type == "summary":
            # Group by disease type
            disease_counts = {}
            status_counts = {}
            
            for cluster in clusters:
                # Count by disease type
                disease_type = cluster.disease_type.value if hasattr(cluster, 'disease_type') else "unknown"
                disease_counts[disease_type] = disease_counts.get(disease_type, 0) + 1
                
                # Count by status
                status = cluster.status if hasattr(cluster, 'status') else "unknown"
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                "report_date": datetime.now().isoformat(),
                "criteria": criteria,
                "total_clusters": len(clusters),
                "by_disease": disease_counts,
                "by_status": status_counts
            }
        else:
            raise ValueError(f"Unsupported report format: {format_type}")