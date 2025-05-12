"""
Sequential outbreak detection algorithms for the APHIS Bird Flu Tracking System.
This module implements statistical methods for early outbreak detection based on
group sequential testing approaches from clinical trials.
"""
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
from datetime import date, datetime, timedelta

from scipy import stats


class DetectionLevel(str, Enum):
    """Detection levels for outbreak detection"""
    NORMAL = "normal"
    ALERT = "alert"
    WARNING = "warning"
    OUTBREAK = "outbreak"


class SequentialProbabilityRatioTest:
    """
    Sequential Probability Ratio Test (SPRT) for early outbreak detection,
    based on Wald's sequential analysis technique
    """
    
    def __init__(
        self,
        baseline_rate: float,
        target_rate: float,
        alpha: float = 0.05,
        beta: float = 0.2
    ):
        """
        Initialize SPRT detector
        
        Args:
            baseline_rate: Expected baseline rate of positive detections
            target_rate: Target rate to detect (outbreak threshold)
            alpha: Type I error rate
            beta: Type II error rate
        """
        self.baseline_rate = baseline_rate
        self.target_rate = target_rate
        self.alpha = alpha
        self.beta = beta
        
        # Calculate decision boundaries
        self.upper_bound = np.log((1 - beta) / alpha)
        self.lower_bound = np.log(beta / (1 - alpha))
    
    def update(self, positives: int, total: int) -> Tuple[str, float]:
        """
        Update the test with new data
        
        Args:
            positives: Number of positive detections
            total: Total number of samples
            
        Returns:
            Tuple of (decision, log_likelihood_ratio)
        """
        if total == 0:
            return "continue", 0.0
        
        # Calculate observed rate
        observed_rate = positives / total
        
        # Calculate log-likelihood ratio
        if positives == 0:
            # Avoid log(0) issues
            llr = total * np.log((1 - self.baseline_rate) / (1 - self.target_rate))
        elif positives == total:
            # Avoid log(0) issues
            llr = total * np.log(self.baseline_rate / self.target_rate)
        else:
            llr = (
                positives * np.log(self.baseline_rate / self.target_rate) +
                (total - positives) * np.log((1 - self.baseline_rate) / (1 - self.target_rate))
            )
        
        # Make decision
        if llr >= self.upper_bound:
            return "reject_null", llr  # Outbreak detected
        elif llr <= self.lower_bound:
            return "accept_null", llr  # No outbreak
        else:
            return "continue", llr  # Continue monitoring


class GroupSequentialDetector:
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
        beta: float = 0.2,
        boundary_type: str = "obrien_fleming"
    ):
        """
        Initialize group sequential detector
        
        Args:
            baseline_rate: Expected baseline rate of positive detections
            effect_size: Minimum effect size to detect
            max_stages: Maximum number of analysis stages
            alpha: Type I error rate
            beta: Type II error rate
            boundary_type: Type of boundary to use ("obrien_fleming" or "pocock")
        """
        self.baseline_rate = baseline_rate
        self.effect_size = effect_size
        self.max_stages = max_stages
        self.alpha = alpha
        self.beta = beta
        self.boundary_type = boundary_type
        
        # Calculate boundaries
        self.efficacy_boundaries = self._calculate_boundaries()
        
        # State variables
        self.current_stage = 0
        self.cumulative_positives = 0
        self.cumulative_total = 0
        self.stage_results = []
    
    def _calculate_boundaries(self) -> List[float]:
        """
        Calculate efficacy boundaries based on boundary type
        
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
        Update the detector with new data for the current stage
        
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
            'boundary': current_boundary
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


class CUSUMDetector:
    """
    Cumulative Sum (CUSUM) detector for early outbreak detection,
    detecting shifts in the mean of a process
    """
    
    def __init__(
        self,
        baseline_mean: float,
        target_shift: float,
        std_dev: float = None,
        k: float = 0.5,
        h: float = 5.0,
        reset_on_signal: bool = False
    ):
        """
        Initialize CUSUM detector
        
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
    
    def update(self, value: float) -> Tuple[str, float, float]:
        """
        Update the detector with a new observation
        
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
        z = (value - self.baseline_mean) / self.std_dev
        
        # Update CUSUM statistics
        self.cusum_pos = max(0, self.cusum_pos + z - self.k)
        self.cusum_neg = max(0, self.cusum_neg - z - self.k)
        
        # Record history
        self.history.append({
            'n': self.n,
            'value': value,
            'z': z,
            'cusum_pos': self.cusum_pos,
            'cusum_neg': self.cusum_neg
        })
        
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


class SpatioTemporalScanDetector:
    """
    Simple implementation of a spatiotemporal scan statistic for outbreak detection,
    inspired by Kulldorff's space-time scan statistic
    """
    
    def __init__(
        self,
        baseline_rate: float,
        alpha: float = 0.05,
        max_radius: float = 100.0,  # in km
        max_time_window: int = 14   # in days
    ):
        """
        Initialize spatiotemporal scan detector
        
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
    
    def add_case(self, 
                case_date: Union[date, str], 
                location: Tuple[float, float],
                positive: bool) -> None:
        """
        Add a case to the detector
        
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
        Calculate the Haversine distance between two points on the Earth
        
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
        Detect spatiotemporal clusters of cases
        
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
                        'p_value': p_value
                    })
        
        # Sort clusters by log-likelihood ratio (descending)
        clusters.sort(key=lambda x: x['log_likelihood_ratio'], reverse=True)
        
        return clusters


class OutbreakDetector:
    """
    Comprehensive outbreak detector combining multiple detection methods
    """
    
    def __init__(
        self,
        baseline_rate: float,
        target_shift: float,
        spatial_enabled: bool = True,
        cusum_enabled: bool = True,
        sequential_enabled: bool = True,
        alpha: float = 0.05
    ):
        """
        Initialize outbreak detector
        
        Args:
            baseline_rate: Expected baseline rate of positive detections
            target_shift: Target shift to detect
            spatial_enabled: Whether to enable spatial detection
            cusum_enabled: Whether to enable CUSUM detection
            sequential_enabled: Whether to enable sequential detection
            alpha: Significance level
        """
        self.baseline_rate = baseline_rate
        self.target_shift = target_shift
        self.alpha = alpha
        
        # Initialize detectors
        if sequential_enabled:
            self.sprt = SequentialProbabilityRatioTest(
                baseline_rate=baseline_rate,
                target_rate=baseline_rate + target_shift,
                alpha=alpha
            )
            
            self.gs_detector = GroupSequentialDetector(
                baseline_rate=baseline_rate,
                effect_size=target_shift,
                alpha=alpha
            )
        else:
            self.sprt = None
            self.gs_detector = None
        
        if cusum_enabled:
            self.cusum = CUSUMDetector(
                baseline_mean=baseline_rate,
                target_shift=target_shift,
                reset_on_signal=True
            )
        else:
            self.cusum = None
        
        if spatial_enabled:
            self.spatial_detector = SpatioTemporalScanDetector(
                baseline_rate=baseline_rate,
                alpha=alpha
            )
        else:
            self.spatial_detector = None
        
        # Detection state
        self.current_level = DetectionLevel.NORMAL
        self.detection_history = []
    
    def update(self, 
              positives: int, 
              total: int, 
              date_value: Union[date, str] = None,
              locations: Optional[List[Tuple[float, float]]] = None) -> DetectionLevel:
        """
        Update the detector with new data
        
        Args:
            positives: Number of positive detections
            total: Total number of samples
            date_value: Date of the samples (for spatial detection)
            locations: List of (latitude, longitude) coordinates for each sample
            
        Returns:
            Current detection level
        """
        if total == 0:
            return self.current_level
        
        # Convert date string to date if needed
        if isinstance(date_value, str):
            date_value = date.fromisoformat(date_value)
        elif date_value is None:
            date_value = date.today()
        
        # Calculate observed rate
        observed_rate = positives / total
        
        # Update SPRT detector
        sprt_decision = None
        if self.sprt:
            sprt_decision, sprt_llr = self.sprt.update(positives, total)
        
        # Update group sequential detector
        gs_decision = None
        if self.gs_detector:
            gs_decision, gs_zstat, gs_pvalue = self.gs_detector.update(positives, total)
        
        # Update CUSUM detector
        cusum_decision = None
        if self.cusum:
            # Convert binary data to a rate for CUSUM
            cusum_decision, cusum_pos, cusum_neg = self.cusum.update(observed_rate)
        
        # Update spatial detector
        spatial_clusters = []
        if self.spatial_detector and locations:
            # Add cases to spatial detector
            for i in range(total):
                is_positive = i < positives  # Assume first 'positives' samples are positive
                if i < len(locations):
                    self.spatial_detector.add_case(date_value, locations[i], is_positive)
            
            # Detect clusters
            spatial_clusters = self.spatial_detector.detect_clusters(date_value)
        
        # Determine detection level based on all detectors
        new_level = DetectionLevel.NORMAL
        
        # Check SPRT
        if sprt_decision == "reject_null":
            new_level = max(new_level, DetectionLevel.WARNING)
        
        # Check group sequential
        if gs_decision == "outbreak":
            new_level = max(new_level, DetectionLevel.OUTBREAK)
        
        # Check CUSUM
        if cusum_decision == "increase":
            new_level = max(new_level, DetectionLevel.ALERT)
        
        # Check spatial clusters
        if spatial_clusters:
            # Check if any high-risk clusters
            high_risk_clusters = [c for c in spatial_clusters if c['relative_risk'] > 2.0]
            if high_risk_clusters:
                new_level = max(new_level, DetectionLevel.WARNING)
            
            # Check if any very high-risk clusters
            very_high_risk_clusters = [c for c in spatial_clusters if c['relative_risk'] > 3.0]
            if very_high_risk_clusters:
                new_level = max(new_level, DetectionLevel.OUTBREAK)
        
        # Record detection history
        history_entry = {
            'date': date_value.isoformat(),
            'positives': positives,
            'total': total,
            'observed_rate': observed_rate,
            'sprt_decision': sprt_decision,
            'gs_decision': gs_decision,
            'cusum_decision': cusum_decision,
            'spatial_clusters': len(spatial_clusters),
            'detection_level': new_level.value
        }
        
        self.detection_history.append(history_entry)
        
        # Update current level
        self.current_level = new_level
        
        return self.current_level
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the detector
        
        Returns:
            Dictionary with current status
        """
        return {
            'detection_level': self.current_level.value,
            'detection_history': self.detection_history[-10:] if self.detection_history else [],
            'baseline_rate': self.baseline_rate,
            'target_shift': self.target_shift
        }