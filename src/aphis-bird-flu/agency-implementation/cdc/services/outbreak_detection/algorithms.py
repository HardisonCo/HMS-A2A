"""
Outbreak detection algorithms for the CDC implementation.
Implements statistical methods for detecting disease outbreaks.
"""
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import date, datetime, timedelta
from abc import ABC, abstractmethod
import logging
import numpy as np
from enum import Enum
from scipy import stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DetectionLevel(str, Enum):
    """Detection levels for outbreak detection"""
    NORMAL = "normal"
    ALERT = "alert"
    WARNING = "warning"
    OUTBREAK = "outbreak"


class DetectionAlgorithm(ABC):
    """Base class for outbreak detection algorithms"""
    
    @abstractmethod
    def analyze(self, data: Any) -> Dict[str, Any]:
        """Analyze data for potential outbreaks"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the algorithm"""
        pass


class CumulativeSumDetector(DetectionAlgorithm):
    """
    Cumulative Sum (CUSUM) detector for early outbreak detection,
    detecting shifts in the mean of a process.
    """
    
    def __init__(
        self,
        baseline_mean: float,
        target_shift: float,
        std_dev: Optional[float] = None,
        k: float = 0.5,
        h: float = 5.0,
        reset_on_signal: bool = False
    ):
        """
        Initialize CUSUM detector.
        
        Args:
            baseline_mean: Expected baseline mean
            target_shift: Target shift to detect (in standard deviations)
            std_dev: Standard deviation of the process (if None, estimated from data)
            k: Reference value (typically half the target shift)
            h: Decision threshold
            reset_on_signal: Whether to reset the CUSUM statistic after a signal
        """
        self.baseline_mean = baseline_mean
        self.target_shift = target_shift
        self.std_dev = std_dev
        self.k = k if k is not None else target_shift / 2
        self.h = h
        self.reset_on_signal = reset_on_signal
        
        # State variables
        self.cusum_pos = 0.0  # Upper CUSUM statistic
        self.cusum_neg = 0.0  # Lower CUSUM statistic
        self.n = 0  # Number of observations
        self.sum_x = 0.0  # Sum of observations
        self.sum_x2 = 0.0  # Sum of squared observations
        self.history = []  # History of CUSUM statistics
        
        logger.info(f"CUSUM detector initialized with baseline={baseline_mean}, target_shift={target_shift}, k={k}, h={h}")
    
    def update(self, value: float) -> Tuple[str, float, float]:
        """
        Update the detector with a new observation.
        
        Args:
            value: New observation
            
        Returns:
            Tuple of (decision, cusum_pos, cusum_neg)
        """
        # Update statistics for mean and variance estimation
        self.n += 1
        self.sum_x += value
        self.sum_x2 += value * value
        
        # Estimate standard deviation if not provided
        if self.std_dev is None:
            if self.n > 1:
                # Sample standard deviation
                variance = (self.sum_x2 - (self.sum_x ** 2) / self.n) / (self.n - 1)
                self.std_dev = np.sqrt(max(0.0001, variance))  # Prevent negative variance
            else:
                # Default to 1.0 until we have enough data
                self.std_dev = 1.0
        
        # Standardize the observation
        z = (value - self.baseline_mean) / self.std_dev if self.std_dev > 0 else 0
        
        # Update CUSUM statistics
        self.cusum_pos = max(0, self.cusum_pos + z - self.k)
        self.cusum_neg = max(0, self.cusum_neg - z - self.k)
        
        # Record history
        self.history.append({
            'n': self.n,
            'value': value,
            'z': z,
            'cusum_pos': self.cusum_pos,
            'cusum_neg': self.cusum_neg,
            'timestamp': datetime.now().isoformat()
        })
        
        # Trim history if too long
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        # Make decision
        decision = "continue"
        if self.cusum_pos >= self.h:
            decision = "increase"
            if self.reset_on_signal:
                self.cusum_pos = 0.0
        elif self.cusum_neg >= self.h:
            decision = "decrease"
            if self.reset_on_signal:
                self.cusum_neg = 0.0
        
        return decision, self.cusum_pos, self.cusum_neg
    
    def analyze(self, data: List[float]) -> Dict[str, Any]:
        """
        Analyze a series of values for potential outbreaks.
        
        Args:
            data: List of values to analyze
            
        Returns:
            Analysis results
        """
        results = []
        decisions = []
        
        for value in data:
            decision, cusum_pos, cusum_neg = self.update(value)
            results.append({
                'value': value,
                'cusum_pos': cusum_pos,
                'cusum_neg': cusum_neg,
                'decision': decision
            })
            decisions.append(decision)
        
        # Determine overall detection level
        detection_level = DetectionLevel.NORMAL
        if 'increase' in decisions:
            detection_level = DetectionLevel.OUTBREAK
        
        return {
            'algorithm': 'CUSUM',
            'detection_level': detection_level.value,
            'results': results,
            'parameters': {
                'baseline_mean': self.baseline_mean,
                'target_shift': self.target_shift,
                'k': self.k,
                'h': self.h,
                'std_dev': self.std_dev
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the detector.
        
        Returns:
            Dictionary with current status
        """
        detection_level = DetectionLevel.NORMAL
        if self.cusum_pos >= self.h:
            detection_level = DetectionLevel.OUTBREAK
        elif self.cusum_pos >= self.h * 0.7:
            detection_level = DetectionLevel.WARNING
        elif self.cusum_pos >= self.h * 0.5:
            detection_level = DetectionLevel.ALERT
        
        return {
            'algorithm': 'CUSUM',
            'detection_level': detection_level.value,
            'current_statistics': {
                'cusum_pos': self.cusum_pos,
                'cusum_neg': self.cusum_neg,
                'n': self.n,
                'mean': self.sum_x / self.n if self.n > 0 else None,
                'std_dev': self.std_dev
            },
            'parameters': {
                'baseline_mean': self.baseline_mean,
                'target_shift': self.target_shift,
                'k': self.k,
                'h': self.h
            },
            'recent_history': self.history[-5:] if self.history else []
        }


class GroupSequentialDetector(DetectionAlgorithm):
    """
    Group sequential detection for outbreaks, based on group sequential
    testing methods from clinical trials
    """
    
    def __init__(
        self,
        baseline_rate: float,
        effect_size: float,
        max_stages: int = 5,
        alpha: float = 0.05,
        boundary_type: str = "obrien_fleming"
    ):
        """
        Initialize group sequential detector.
        
        Args:
            baseline_rate: Expected baseline rate of positive detections
            effect_size: Minimum effect size to detect
            max_stages: Maximum number of analysis stages
            alpha: Type I error rate
            boundary_type: Type of boundary to use ("obrien_fleming" or "pocock")
        """
        self.baseline_rate = baseline_rate
        self.effect_size = effect_size
        self.max_stages = max_stages
        self.alpha = alpha
        self.boundary_type = boundary_type
        
        # Calculate boundaries
        self.efficacy_boundaries = self._calculate_boundaries()
        
        # State variables
        self.current_stage = 0
        self.cumulative_positives = 0
        self.cumulative_total = 0
        self.stage_results = []
        
        logger.info(f"Group Sequential detector initialized with baseline={baseline_rate}, effect_size={effect_size}, max_stages={max_stages}")
    
    def _calculate_boundaries(self) -> List[float]:
        """
        Calculate efficacy boundaries based on boundary type.
        
        Returns:
            List of z-statistic boundaries for each stage
        """
        boundaries = []
        
        if self.boundary_type == "obrien_fleming":
            # O'Brien-Fleming boundaries
            for i in range(1, self.max_stages + 1):
                # Information fraction
                t = i / self.max_stages
                
                # Critical value
                c = stats.norm.ppf(1 - self.alpha / 2)
                
                # Boundary
                boundary = c / np.sqrt(t)
                boundaries.append(boundary)
        
        elif self.boundary_type == "pocock":
            # Pocock boundaries (constant)
            # Approximate adjustment for multiple looks
            adjusted_alpha = self.alpha / self.max_stages
            boundary = stats.norm.ppf(1 - adjusted_alpha / 2)
            boundaries = [boundary] * self.max_stages
        
        else:
            raise ValueError(f"Unknown boundary type: {self.boundary_type}")
        
        return boundaries
    
    def update(self, positives: int, total: int) -> Tuple[str, float, float]:
        """
        Update the detector with new data for the current stage.
        
        Args:
            positives: Number of positive detections in this batch
            total: Total number of samples in this batch
            
        Returns:
            Tuple of (decision, z_statistic, p_value)
        """
        if self.current_stage >= self.max_stages:
            return "completed", 0.0, 1.0
        
        # Update cumulative counts
        self.cumulative_positives += positives
        self.cumulative_total += total
        
        if self.cumulative_total == 0:
            return "continue", 0.0, 1.0
        
        # Calculate observed rate
        observed_rate = self.cumulative_positives / self.cumulative_total
        
        # Calculate standard error
        se = np.sqrt(self.baseline_rate * (1 - self.baseline_rate) / self.cumulative_total)
        
        # Calculate z-statistic
        z_stat = (observed_rate - self.baseline_rate) / se if se > 0 else 0
        
        # Calculate p-value
        p_value = 1 - stats.norm.cdf(z_stat)
        
        # Get current boundary
        current_boundary = self.efficacy_boundaries[self.current_stage]
        
        # Record stage result
        self.stage_results.append({
            'stage': self.current_stage + 1,
            'positives': positives,
            'total': total,
            'cumulative_positives': self.cumulative_positives,
            'cumulative_total': self.cumulative_total,
            'observed_rate': observed_rate,
            'z_statistic': z_stat,
            'p_value': p_value,
            'boundary': current_boundary,
            'timestamp': datetime.now().isoformat()
        })
        
        # Make decision
        decision = "continue"
        if z_stat >= current_boundary:
            decision = "outbreak"
        
        # Advance to next stage
        self.current_stage += 1
        
        # Check if we've reached the final stage
        if self.current_stage >= self.max_stages and decision == "continue":
            decision = "no_outbreak"
        
        return decision, z_stat, p_value
    
    def analyze(self, data: List[Dict[str, int]]) -> Dict[str, Any]:
        """
        Analyze a series of positive/total counts for potential outbreaks.
        
        Args:
            data: List of dictionaries with 'positives' and 'total' counts
            
        Returns:
            Analysis results
        """
        results = []
        decisions = []
        
        for batch in data:
            positives = batch.get('positives', 0)
            total = batch.get('total', 0)
            
            decision, z_stat, p_value = self.update(positives, total)
            
            results.append({
                'positives': positives,
                'total': total,
                'decision': decision,
                'z_statistic': z_stat,
                'p_value': p_value
            })
            
            decisions.append(decision)
        
        # Determine overall detection level
        detection_level = DetectionLevel.NORMAL
        if 'outbreak' in decisions:
            detection_level = DetectionLevel.OUTBREAK
        elif self.current_stage < self.max_stages:
            if any(result['z_statistic'] >= self.efficacy_boundaries[self.current_stage] * 0.7 for result in self.stage_results):
                detection_level = DetectionLevel.WARNING
            elif any(result['z_statistic'] >= self.efficacy_boundaries[self.current_stage] * 0.5 for result in self.stage_results):
                detection_level = DetectionLevel.ALERT
        
        return {
            'algorithm': 'Group Sequential',
            'detection_level': detection_level.value,
            'current_stage': self.current_stage,
            'max_stages': self.max_stages,
            'results': results,
            'parameters': {
                'baseline_rate': self.baseline_rate,
                'effect_size': self.effect_size,
                'boundary_type': self.boundary_type,
                'alpha': self.alpha
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the detector.
        
        Returns:
            Dictionary with current status
        """
        detection_level = DetectionLevel.NORMAL
        
        if self.current_stage > 0 and self.stage_results:
            last_result = self.stage_results[-1]
            last_boundary = self.efficacy_boundaries[self.current_stage - 1]
            
            if last_result['z_statistic'] >= last_boundary:
                detection_level = DetectionLevel.OUTBREAK
            elif last_result['z_statistic'] >= last_boundary * 0.7:
                detection_level = DetectionLevel.WARNING
            elif last_result['z_statistic'] >= last_boundary * 0.5:
                detection_level = DetectionLevel.ALERT
        
        return {
            'algorithm': 'Group Sequential',
            'detection_level': detection_level.value,
            'current_statistics': {
                'current_stage': self.current_stage,
                'max_stages': self.max_stages,
                'cumulative_positives': self.cumulative_positives,
                'cumulative_total': self.cumulative_total,
                'observed_rate': self.cumulative_positives / self.cumulative_total if self.cumulative_total > 0 else None
            },
            'parameters': {
                'baseline_rate': self.baseline_rate,
                'effect_size': self.effect_size,
                'boundary_type': self.boundary_type,
                'alpha': self.alpha,
                'boundaries': self.efficacy_boundaries
            },
            'stage_results': self.stage_results
        }


class SpaceTimeClusterDetector(DetectionAlgorithm):
    """
    Space-time cluster detection algorithm for identifying geographic clusters of disease cases.
    Based on a simplified implementation of space-time scan statistics.
    """
    
    def __init__(
        self,
        baseline_rate: float,
        alpha: float = 0.05,
        max_radius: float = 100.0,  # in km
        max_time_window: int = 14    # in days
    ):
        """
        Initialize spatiotemporal cluster detector.
        
        Args:
            baseline_rate: Expected baseline rate of positive detections
            alpha: Significance level
            max_radius: Maximum radius for spatial clusters (in km)
            max_time_window: Maximum time window for temporal clusters (in days)
        """
        self.baseline_rate = baseline_rate
        self.alpha = alpha
        self.max_radius = max_radius
        self.max_time_window = max_time_window
        
        # State variables
        self.cases = []  # List of (date, location, positive) tuples
        self.clusters = []  # Detected clusters
        
        logger.info(f"Space-Time Cluster detector initialized with baseline={baseline_rate}, max_radius={max_radius}, max_time_window={max_time_window}")
    
    def add_case(self, 
                case_date: Union[date, str], 
                location: Tuple[float, float],
                positive: bool) -> None:
        """
        Add a case to the detector.
        
        Args:
            case_date: Date of the case
            location: (latitude, longitude) coordinates
            positive: Whether the case is positive
        """
        # Convert date string to date if needed
        if isinstance(case_date, str):
            case_date = date.fromisoformat(case_date)
        
        # Add case to list
        self.cases.append((case_date, location, positive))
    
    def _haversine_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """
        Calculate the Haversine distance between two points on the Earth.
        
        Args:
            loc1: (latitude, longitude) of point 1
            loc2: (latitude, longitude) of point 2
            
        Returns:
            Distance in kilometers
        """
        # Convert latitude and longitude to radians
        lat1, lon1 = np.radians(loc1)
        lat2, lon2 = np.radians(loc2)
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        r = 6371  # Earth radius in kilometers
        
        return c * r
    
    def detect_clusters(self, reference_date: Union[date, str] = None) -> List[Dict[str, Any]]:
        """
        Detect spatiotemporal clusters of cases.
        
        Args:
            reference_date: Reference date for time window (defaults to today)
            
        Returns:
            List of detected clusters with their properties
        """
        if not self.cases:
            return []
        
        # Use current date if reference date not provided
        if reference_date is None:
            reference_date = date.today()
        elif isinstance(reference_date, str):
            reference_date = date.fromisoformat(reference_date)
        
        # Calculate time range
        min_date = reference_date - timedelta(days=self.max_time_window)
        
        # Filter cases within time window
        recent_cases = [(d, loc, pos) for d, loc, pos in self.cases if d >= min_date]
        
        if not recent_cases:
            return []
        
        # Get all unique locations
        unique_locations = list(set(loc for _, loc, _ in recent_cases))
        
        # Detect clusters for each potential center
        clusters = []
        
        for center in unique_locations:
            # Try different radii
            for radius in np.linspace(10.0, self.max_radius, 10):
                # Calculate which cases are in the cluster
                cluster_cases = []
                for case_date, location, positive in recent_cases:
                    # Check if within radius
                    distance = self._haversine_distance(center, location)
                    if distance <= radius:
                        cluster_cases.append((case_date, location, positive))
                
                if not cluster_cases:
                    continue
                
                # Calculate cluster statistics
                total_cases = len(cluster_cases)
                positives = sum(1 for _, _, pos in cluster_cases if pos)
                
                # Calculate expected number of cases
                expected = total_cases * self.baseline_rate
                
                # Calculate log-likelihood ratio
                if positives == 0:
                    llr = 0
                elif positives == total_cases:
                    llr = total_cases * np.log(1 / self.baseline_rate)
                else:
                    observed_rate = positives / total_cases
                    llr = (
                        positives * np.log(observed_rate / self.baseline_rate) +
                        (total_cases - positives) * np.log((1 - observed_rate) / (1 - self.baseline_rate))
                    ) if observed_rate > self.baseline_rate else 0
                
                # Skip if not significant
                if llr <= 0:
                    continue
                
                # Calculate p-value using chi-squared approximation
                p_value = 1 - stats.chi2.cdf(2 * llr, 1)
                
                # Add to clusters if significant
                if p_value <= self.alpha:
                    # Find date range
                    start_date = min(d for d, _, _ in cluster_cases)
                    end_date = max(d for d, _, _ in cluster_cases)
                    
                    clusters.append({
                        'center': center,
                        'radius': radius,
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'total_cases': total_cases,
                        'positives': positives,
                        'expected': expected,
                        'observed_rate': positives / total_cases,
                        'relative_risk': (positives / total_cases) / self.baseline_rate,
                        'log_likelihood_ratio': llr,
                        'p_value': p_value,
                        'detection_date': datetime.now().isoformat()
                    })
        
        # Sort clusters by log-likelihood ratio (descending)
        clusters.sort(key=lambda x: x['log_likelihood_ratio'], reverse=True)
        
        # Store clusters
        self.clusters = clusters
        
        return clusters
    
    def analyze(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze case data for potential spatial clusters.
        
        Args:
            data: List of dictionaries with 'date', 'location', and 'positive' fields
            
        Returns:
            Analysis results
        """
        # Add cases to the detector
        for case in data:
            self.add_case(
                case_date=case.get('date'),
                location=case.get('location'),
                positive=case.get('positive', True)
            )
        
        # Detect clusters
        detected_clusters = self.detect_clusters()
        
        # Determine overall detection level
        detection_level = DetectionLevel.NORMAL
        
        if detected_clusters:
            # Check for high-risk clusters
            high_risk = any(c['relative_risk'] > 3.0 for c in detected_clusters)
            medium_risk = any(2.0 < c['relative_risk'] <= 3.0 for c in detected_clusters)
            low_risk = any(1.5 < c['relative_risk'] <= 2.0 for c in detected_clusters)
            
            if high_risk:
                detection_level = DetectionLevel.OUTBREAK
            elif medium_risk:
                detection_level = DetectionLevel.WARNING
            elif low_risk:
                detection_level = DetectionLevel.ALERT
        
        return {
            'algorithm': 'Space-Time Cluster',
            'detection_level': detection_level.value,
            'clusters': detected_clusters,
            'parameters': {
                'baseline_rate': self.baseline_rate,
                'alpha': self.alpha,
                'max_radius': self.max_radius,
                'max_time_window': self.max_time_window
            },
            'case_count': len(self.cases)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the detector.
        
        Returns:
            Dictionary with current status
        """
        # Determine detection level from most recent clusters
        detection_level = DetectionLevel.NORMAL
        
        if self.clusters:
            # Check for high-risk clusters
            high_risk = any(c['relative_risk'] > 3.0 for c in self.clusters)
            medium_risk = any(2.0 < c['relative_risk'] <= 3.0 for c in self.clusters)
            low_risk = any(1.5 < c['relative_risk'] <= 2.0 for c in self.clusters)
            
            if high_risk:
                detection_level = DetectionLevel.OUTBREAK
            elif medium_risk:
                detection_level = DetectionLevel.WARNING
            elif low_risk:
                detection_level = DetectionLevel.ALERT
        
        return {
            'algorithm': 'Space-Time Cluster',
            'detection_level': detection_level.value,
            'current_statistics': {
                'total_cases': len(self.cases),
                'recent_cases': sum(1 for d, _, _ in self.cases if d >= date.today() - timedelta(days=self.max_time_window)),
                'clusters_detected': len(self.clusters)
            },
            'parameters': {
                'baseline_rate': self.baseline_rate,
                'alpha': self.alpha,
                'max_radius': self.max_radius,
                'max_time_window': self.max_time_window
            },
            'recent_clusters': self.clusters[:5] if self.clusters else []
        }