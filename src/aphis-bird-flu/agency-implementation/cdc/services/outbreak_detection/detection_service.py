"""
Outbreak Detection Service for the CDC implementation.

This service provides functionality for detecting disease outbreaks using
various statistical algorithms and methods.
"""
from typing import Dict, List, Any, Optional, Union, Type
from datetime import date, datetime, timedelta
import logging
import uuid
import json

from agency_implementation.cdc.models.human_disease import (
    HumanDiseaseCase, Cluster, DiseaseType, RiskLevel, TransmissionMode
)
from .repository import OutbreakRepository
from .algorithms import (
    DetectionAlgorithm, CumulativeSumDetector, GroupSequentialDetector, 
    SpaceTimeClusterDetector, DetectionLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutbreakDetectionService:
    """
    Service for detecting and managing disease outbreaks.
    
    This service provides functionality for:
    1. Running detection algorithms on case data
    2. Managing outbreak clusters
    3. Notification of detected outbreaks
    4. Historical outbreak analysis
    """
    
    def __init__(
        self,
        repository: OutbreakRepository,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the service.
        
        Args:
            repository: Repository for clusters and detection results
            config: Service configuration
        """
        self.repository = repository
        self.config = config or {}
        
        # Initialize detectors
        self.detectors: Dict[str, DetectionAlgorithm] = {}
        self._initialize_detectors()
        
        # Notification thresholds
        self.notification_thresholds = self.config.get('notification_thresholds', {
            'alert': 0.7,  # Alert at 70% of outbreak threshold
            'warning': 0.9  # Warning at 90% of outbreak threshold
        })
        
        # Auto-create clusters
        self.auto_create_clusters = self.config.get('auto_create_clusters', True)
        
        logger.info("OutbreakDetectionService initialized")
    
    def _initialize_detectors(self) -> None:
        """Initialize detection algorithms based on configuration"""
        detector_configs = self.config.get('detectors', {})
        
        # Initialize CUSUM detector if configured
        if 'cusum' in detector_configs:
            config = detector_configs['cusum']
            self.detectors['cusum'] = CumulativeSumDetector(
                baseline_mean=config.get('baseline_mean', 0.1),
                target_shift=config.get('target_shift', 0.05),
                std_dev=config.get('std_dev'),
                k=config.get('k', 0.5),
                h=config.get('h', 5.0),
                reset_on_signal=config.get('reset_on_signal', False)
            )
            logger.info("CUSUM detector initialized")
        
        # Initialize GroupSequential detector if configured
        if 'group_sequential' in detector_configs:
            config = detector_configs['group_sequential']
            self.detectors['group_sequential'] = GroupSequentialDetector(
                baseline_rate=config.get('baseline_rate', 0.1),
                effect_size=config.get('effect_size', 0.05),
                max_stages=config.get('max_stages', 5),
                alpha=config.get('alpha', 0.05),
                boundary_type=config.get('boundary_type', 'obrien_fleming')
            )
            logger.info("Group Sequential detector initialized")
        
        # Initialize SpaceTimeCluster detector if configured
        if 'space_time_cluster' in detector_configs:
            config = detector_configs['space_time_cluster']
            self.detectors['space_time_cluster'] = SpaceTimeClusterDetector(
                baseline_rate=config.get('baseline_rate', 0.1),
                alpha=config.get('alpha', 0.05),
                max_radius=config.get('max_radius', 100.0),
                max_time_window=config.get('max_time_window', 14)
            )
            logger.info("Space-Time Cluster detector initialized")
        
        # If no detectors configured, initialize defaults
        if not self.detectors:
            logger.warning("No detectors configured, initializing defaults")
            self.detectors['cusum'] = CumulativeSumDetector(baseline_mean=0.1, target_shift=0.05)
            self.detectors['group_sequential'] = GroupSequentialDetector(baseline_rate=0.1, effect_size=0.05)
            self.detectors['space_time_cluster'] = SpaceTimeClusterDetector(baseline_rate=0.1)
    
    def detect_outbreaks(self, cases: List[HumanDiseaseCase]) -> Dict[str, Any]:
        """
        Run detection algorithms on a set of cases.
        
        Args:
            cases: List of disease cases to analyze
            
        Returns:
            Dictionary with detection results
        """
        results = {}
        overall_level = DetectionLevel.NORMAL
        detected_clusters = []
        
        if not cases:
            logger.warning("No cases provided for outbreak detection")
            return {
                'detection_level': overall_level.value,
                'results': results,
                'clusters': [],
                'timestamp': datetime.now().isoformat()
            }
        
        logger.info(f"Running outbreak detection on {len(cases)} cases")
        
        # Prepare data for different detector types
        daily_counts = self._aggregate_daily_case_counts(cases)
        case_rates = self._calculate_case_rates(daily_counts)
        geo_data = self._prepare_spatial_case_data(cases)
        
        # Run CUSUM detector if available
        if 'cusum' in self.detectors:
            cusum_detector = self.detectors['cusum']
            cusum_results = cusum_detector.analyze(case_rates)
            results['cusum'] = cusum_results
            
            # Update detection level
            cusum_level = DetectionLevel(cusum_results['detection_level'])
            overall_level = max(overall_level, cusum_level)
            
            # Store results
            self.repository.store_detection_result('cusum', cusum_results)
        
        # Run Group Sequential detector if available
        if 'group_sequential' in self.detectors:
            gs_detector = self.detectors['group_sequential']
            gs_data = [{'positives': day['cases'], 'total': day['total']} for day in daily_counts]
            gs_results = gs_detector.analyze(gs_data)
            results['group_sequential'] = gs_results
            
            # Update detection level
            gs_level = DetectionLevel(gs_results['detection_level'])
            overall_level = max(overall_level, gs_level)
            
            # Store results
            self.repository.store_detection_result('group_sequential', gs_results)
        
        # Run Space-Time Cluster detector if available and geo data exists
        if 'space_time_cluster' in self.detectors and geo_data:
            st_detector = self.detectors['space_time_cluster']
            st_results = st_detector.analyze(geo_data)
            results['space_time_cluster'] = st_results
            
            # Update detection level
            st_level = DetectionLevel(st_results['detection_level'])
            overall_level = max(overall_level, st_level)
            
            # Get detected clusters and convert to format for auto-creation
            if 'clusters' in st_results and st_results['clusters']:
                detected_clusters = st_results['clusters']
            
            # Store results
            self.repository.store_detection_result('space_time_cluster', st_results)
        
        # Auto-create clusters if configured and clusters detected
        created_clusters = []
        if self.auto_create_clusters and detected_clusters:
            created_clusters = self._create_clusters_from_detection(cases, detected_clusters)
        
        return {
            'detection_level': overall_level.value,
            'results': results,
            'clusters': [c.to_dict() for c in created_clusters],
            'timestamp': datetime.now().isoformat()
        }
    
    def _aggregate_daily_case_counts(self, cases: List[HumanDiseaseCase]) -> List[Dict[str, Any]]:
        """
        Aggregate daily case counts from a list of cases.
        
        Args:
            cases: List of disease cases
            
        Returns:
            List of daily case counts
        """
        daily_counts = {}
        
        for case in cases:
            # Get report date
            report_date = case.report_date
            if isinstance(report_date, str):
                report_date = date.fromisoformat(report_date)
            
            date_str = report_date.isoformat()
            
            if date_str not in daily_counts:
                daily_counts[date_str] = {'date': date_str, 'cases': 0, 'total': 0}
            
            daily_counts[date_str]['total'] += 1
            
            # Count confirmed and probable cases
            if hasattr(case, 'classification'):
                if case.classification.value in ['confirmed', 'probable']:
                    daily_counts[date_str]['cases'] += 1
        
        # Convert to list sorted by date
        result = sorted(daily_counts.values(), key=lambda x: x['date'])
        return result
    
    def _calculate_case_rates(self, daily_counts: List[Dict[str, Any]]) -> List[float]:
        """
        Calculate daily case rates from daily counts.
        
        Args:
            daily_counts: List of daily case count dictionaries
            
        Returns:
            List of daily case rates
        """
        rates = []
        
        for day in daily_counts:
            if day['total'] > 0:
                rate = day['cases'] / day['total']
            else:
                rate = 0
            rates.append(rate)
        
        return rates
    
    def _prepare_spatial_case_data(self, cases: List[HumanDiseaseCase]) -> List[Dict[str, Any]]:
        """
        Prepare case data for spatial analysis.
        
        Args:
            cases: List of disease cases
            
        Returns:
            List of dictionaries with date, location and positive status
        """
        geo_data = []
        
        for case in cases:
            # Skip cases without location
            if not hasattr(case, 'location') or not case.location:
                continue
            
            # Get report date
            report_date = case.report_date
            if isinstance(report_date, str):
                report_date = date.fromisoformat(report_date)
            
            # Determine if case is positive (confirmed or probable)
            positive = False
            if hasattr(case, 'classification'):
                if case.classification.value in ['confirmed', 'probable']:
                    positive = True
            
            # Get location
            location = (case.location.latitude, case.location.longitude)
            
            geo_data.append({
                'date': report_date,
                'location': location,
                'positive': positive
            })
        
        return geo_data
    
    def _create_clusters_from_detection(
        self, 
        cases: List[HumanDiseaseCase], 
        detected_clusters: List[Dict[str, Any]]
    ) -> List[Cluster]:
        """
        Create cluster entities from detection results.
        
        Args:
            cases: List of disease cases
            detected_clusters: List of detected cluster dictionaries
            
        Returns:
            List of created Cluster entities
        """
        created_clusters = []
        
        for i, detected in enumerate(detected_clusters):
            # Skip if no significant risk
            if detected.get('relative_risk', 0) < 1.2:
                continue
            
            # Find disease type (take most common in the cases)
            disease_counts = {}
            for case in cases:
                if hasattr(case, 'disease_type'):
                    disease_type = case.disease_type.value
                    disease_counts[disease_type] = disease_counts.get(disease_type, 0) + 1
            
            disease_type = max(disease_counts.items(), key=lambda x: x[1])[0] if disease_counts else 'unknown'
            
            # Get start and end dates
            start_date = detected.get('start_date')
            end_date = detected.get('end_date')
            
            # Determine risk level based on relative risk
            relative_risk = detected.get('relative_risk', 0)
            if relative_risk >= 3.0:
                risk_level = RiskLevel.HIGH
            elif relative_risk >= 2.0:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Get cluster center location
            center = detected.get('center')
            location = None
            if center:
                from agency_implementation.cdc.models.base import GeoLocation
                location = GeoLocation(latitude=center[0], longitude=center[1])
            
            # Find cases in this cluster
            cluster_cases = []
            radius = detected.get('radius', 0)
            
            for case in cases:
                # Skip cases without location
                if not hasattr(case, 'location') or not case.location:
                    continue
                
                # Get case date
                case_date = case.report_date
                if isinstance(case_date, str):
                    case_date = date.fromisoformat(case_date)
                
                # Check if date is in range
                in_date_range = False
                if start_date and end_date:
                    cluster_start = date.fromisoformat(start_date) if isinstance(start_date, str) else start_date
                    cluster_end = date.fromisoformat(end_date) if isinstance(end_date, str) else end_date
                    in_date_range = cluster_start <= case_date <= cluster_end
                else:
                    in_date_range = True
                
                if not in_date_range:
                    continue
                
                # Check if location is in radius
                in_radius = False
                if center and radius:
                    from .algorithms import SpaceTimeClusterDetector
                    detector = SpaceTimeClusterDetector(baseline_rate=0.1)  # Temporary instance for distance calculation
                    case_loc = (case.location.latitude, case.location.longitude)
                    distance = detector._haversine_distance(center, case_loc)
                    in_radius = distance <= radius
                else:
                    in_radius = True
                
                if in_radius:
                    cluster_cases.append(case.id)
            
            # Skip if no cases found
            if not cluster_cases:
                continue
            
            # Create cluster entity
            cluster = Cluster(
                name=f"Cluster {i+1} - {disease_type}",
                disease_type=disease_type,
                cases=cluster_cases,
                start_date=start_date,
                end_date=end_date,
                location=location,
                status="active",
                risk_level=risk_level,
                transmission_mode=TransmissionMode.UNKNOWN,
                common_exposures=[],
                notes=f"Automatically created from detection with relative risk {relative_risk:.2f}"
            )
            
            # Save cluster
            created_cluster = self.repository.create(cluster)
            created_clusters.append(created_cluster)
            
            logger.info(f"Created cluster {created_cluster.id} with {len(cluster_cases)} cases")
        
        return created_clusters
    
    def get_cluster(self, cluster_id: str) -> Optional[Cluster]:
        """
        Get a cluster by ID.
        
        Args:
            cluster_id: The ID of the cluster to retrieve
            
        Returns:
            The cluster if found, None otherwise
        """
        return self.repository.get_by_id(cluster_id)
    
    def get_all_clusters(self) -> List[Cluster]:
        """
        Get all clusters.
        
        Returns:
            List of all clusters
        """
        return self.repository.get_all()
    
    def create_cluster(self, cluster_data: Dict[str, Any]) -> Cluster:
        """
        Create a new outbreak cluster.
        
        Args:
            cluster_data: Dictionary with cluster data
            
        Returns:
            The created cluster
            
        Raises:
            ValueError: If cluster data is invalid
        """
        # Validate required fields
        required_fields = ['name', 'disease_type', 'cases', 'start_date']
        for field in required_fields:
            if field not in cluster_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create the cluster
        cluster = Cluster(**cluster_data)
        
        # Save the cluster
        created_cluster = self.repository.create(cluster)
        
        logger.info(f"Created new cluster with ID: {created_cluster.id}")
        return created_cluster
    
    def update_cluster(self, cluster_id: str, updates: Dict[str, Any]) -> Optional[Cluster]:
        """
        Update an existing cluster.
        
        Args:
            cluster_id: ID of the cluster to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated cluster or None if cluster not found
            
        Raises:
            ValueError: If updates are invalid
        """
        # Get the cluster
        cluster = self.repository.get_by_id(cluster_id)
        if not cluster:
            logger.warning(f"Cluster not found for update: {cluster_id}")
            return None
        
        # Update the cluster
        for key, value in updates.items():
            setattr(cluster, key, value)
            
        # Update timestamp
        cluster.updated_at = datetime.now().isoformat()
        
        # Save the updated cluster
        updated_cluster = self.repository.update(cluster)
        
        logger.info(f"Updated cluster with ID: {cluster_id}")
        return updated_cluster
    
    def close_cluster(self, cluster_id: str) -> Optional[Cluster]:
        """
        Close an outbreak cluster.
        
        Args:
            cluster_id: ID of the cluster to close
            
        Returns:
            The updated cluster or None if cluster not found
        """
        # Get the cluster
        cluster = self.repository.get_by_id(cluster_id)
        if not cluster:
            logger.warning(f"Cluster not found to close: {cluster_id}")
            return None
        
        # Close the cluster
        cluster.close_cluster()
        
        # Save the updated cluster
        updated_cluster = self.repository.update(cluster)
        
        logger.info(f"Closed cluster with ID: {cluster_id}")
        return updated_cluster
    
    def add_case_to_cluster(self, cluster_id: str, case_id: str) -> Optional[Cluster]:
        """
        Add a case to a cluster.
        
        Args:
            cluster_id: ID of the cluster
            case_id: ID of the case to add
            
        Returns:
            The updated cluster or None if cluster not found
        """
        # Get the cluster
        cluster = self.repository.get_by_id(cluster_id)
        if not cluster:
            logger.warning(f"Cluster not found to add case: {cluster_id}")
            return None
        
        # Add the case
        cluster.add_case(case_id)
        
        # Save the updated cluster
        updated_cluster = self.repository.update(cluster)
        
        logger.info(f"Added case {case_id} to cluster {cluster_id}")
        return updated_cluster
    
    def remove_case_from_cluster(self, cluster_id: str, case_id: str) -> Optional[Cluster]:
        """
        Remove a case from a cluster.
        
        Args:
            cluster_id: ID of the cluster
            case_id: ID of the case to remove
            
        Returns:
            The updated cluster or None if cluster not found
        """
        # Get the cluster
        cluster = self.repository.get_by_id(cluster_id)
        if not cluster:
            logger.warning(f"Cluster not found to remove case: {cluster_id}")
            return None
        
        # Remove the case
        cluster.remove_case(case_id)
        
        # Save the updated cluster
        updated_cluster = self.repository.update(cluster)
        
        logger.info(f"Removed case {case_id} from cluster {cluster_id}")
        return updated_cluster
    
    def find_clusters_by_disease(self, disease_type: Union[DiseaseType, str]) -> List[Cluster]:
        """
        Find clusters by disease type.
        
        Args:
            disease_type: The disease type to filter by
            
        Returns:
            List of clusters with the specified disease type
        """
        return self.repository.find_by_disease_type(disease_type)
    
    def find_active_clusters(self) -> List[Cluster]:
        """
        Find active (non-closed) clusters.
        
        Returns:
            List of active clusters
        """
        return self.repository.find_active_clusters()
    
    def find_clusters_by_date_range(self, start_date: Union[date, str], end_date: Union[date, str]) -> List[Cluster]:
        """
        Find clusters within a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            
        Returns:
            List of clusters within the date range
        """
        return self.repository.find_by_date_range(start_date, end_date)
    
    def find_clusters_for_case(self, case_id: str) -> List[Cluster]:
        """
        Find clusters containing a specific case.
        
        Args:
            case_id: The case ID to search for
            
        Returns:
            List of clusters containing the case
        """
        return self.repository.find_by_case_id(case_id)
    
    def get_detection_status(self) -> Dict[str, Any]:
        """
        Get the current status of all detection algorithms.
        
        Returns:
            Dictionary with status for each algorithm
        """
        status = {}
        overall_level = DetectionLevel.NORMAL
        
        for name, detector in self.detectors.items():
            algorithm_status = detector.get_status()
            status[name] = algorithm_status
            
            # Update overall detection level
            algorithm_level = DetectionLevel(algorithm_status['detection_level'])
            overall_level = max(overall_level, algorithm_level)
        
        return {
            'overall_detection_level': overall_level.value,
            'algorithms': status,
            'active_clusters': len(self.repository.find_active_clusters()),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_outbreak_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate a summary of outbreak activity over a time period.
        
        Args:
            days: Number of days to include in the summary
            
        Returns:
            Dictionary with outbreak summary
        """
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get clusters in date range
        clusters = self.repository.find_by_date_range(start_date, end_date)
        
        # Get detection results from repository
        detection_results = self.repository.get_all_detection_results()
        
        # Filter to recent detection results
        recent_results = {}
        for algo_id, result in detection_results.items():
            if 'timestamp' in result:
                result_date = datetime.fromisoformat(result['timestamp']).date()
                if result_date >= start_date:
                    recent_results[algo_id] = result
        
        # Count by disease type
        disease_counts = {}
        for cluster in clusters:
            if hasattr(cluster, 'disease_type'):
                disease_type = cluster.disease_type.value if hasattr(cluster.disease_type, 'value') else str(cluster.disease_type)
                disease_counts[disease_type] = disease_counts.get(disease_type, 0) + 1
        
        # Count by risk level
        risk_counts = {}
        for cluster in clusters:
            if hasattr(cluster, 'risk_level'):
                risk_level = cluster.risk_level.value if hasattr(cluster.risk_level, 'value') else str(cluster.risk_level)
                risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        # Get total case count across all clusters
        total_cases = 0
        for cluster in clusters:
            if hasattr(cluster, 'cases'):
                total_cases += len(cluster.cases)
        
        # Get most recent detection level
        current_detection_level = DetectionLevel.NORMAL
        for _, result in recent_results.items():
            if 'detection_level' in result:
                level = DetectionLevel(result['detection_level'])
                current_detection_level = max(current_detection_level, level)
        
        return {
            'time_period': f"{start_date.isoformat()} to {end_date.isoformat()}",
            'clusters_detected': len(clusters),
            'by_disease': disease_counts,
            'by_risk_level': risk_counts,
            'total_cases': total_cases,
            'current_detection_level': current_detection_level.value,
            'active_clusters': len(self.repository.find_active_clusters()),
            'generated_at': datetime.now().isoformat()
        }