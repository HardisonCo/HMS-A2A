"""
Adaptive sampling strategies for the APHIS Bird Flu Tracking System.
This module implements adaptive resource allocation algorithms based on
response-adaptive randomization techniques from clinical trials.
"""
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ...models.surveillance import SurveillanceSite, RiskLevel


class AdaptiveSamplingStrategy:
    """Base class for adaptive sampling strategies"""
    
    def __init__(self, 
                exploration_weight: float = 0.2, 
                decay_factor: float = 0.95,
                min_allocation: float = 0.05):
        """
        Initialize adaptive sampling strategy
        
        Args:
            exploration_weight: Weight given to exploration vs. exploitation (0-1)
            decay_factor: Factor to decay exploration over time (0-1)
            min_allocation: Minimum allocation for any site (0-1)
        """
        self.exploration_weight = exploration_weight
        self.decay_factor = decay_factor
        self.min_allocation = min_allocation
        self.iteration = 0
    
    def allocate(self, 
                sites: Dict[str, SurveillanceSite], 
                historical_results: Dict[str, List[Dict[str, Any]]],
                total_resources: int) -> Dict[str, int]:
        """
        Allocate sampling resources across surveillance sites
        
        Args:
            sites: Dictionary mapping site IDs to SurveillanceSite objects
            historical_results: Dictionary mapping site IDs to lists of previous sampling results
            total_resources: Total number of samples to allocate
            
        Returns:
            Dictionary mapping site IDs to number of samples to collect
        """
        # This method should be overridden by subclasses
        raise NotImplementedError("Subclasses must implement this method")
    
    def _normalize_allocations(self, allocations: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize allocations to sum to 1.0 while respecting minimum allocation
        
        Args:
            allocations: Dictionary mapping site IDs to allocation proportions
            
        Returns:
            Normalized allocations
        """
        # Apply minimum allocation
        for site_id in allocations:
            if allocations[site_id] < self.min_allocation:
                allocations[site_id] = self.min_allocation
        
        # Normalize to sum to 1.0
        total_allocation = sum(allocations.values())
        return {site_id: alloc / total_allocation for site_id, alloc in allocations.items()}
    
    def _get_current_exploration_weight(self) -> float:
        """
        Get the current exploration weight, decaying over time
        
        Returns:
            Current exploration weight
        """
        return self.exploration_weight * (self.decay_factor ** self.iteration)


class RiskBasedSamplingStrategy(AdaptiveSamplingStrategy):
    """Sampling strategy that allocates resources based on site risk levels"""
    
    def __init__(self, risk_weights: Optional[Dict[RiskLevel, float]] = None, **kwargs):
        """
        Initialize risk-based sampling strategy
        
        Args:
            risk_weights: Dictionary mapping risk levels to weights
            **kwargs: Additional arguments for AdaptiveSamplingStrategy
        """
        super().__init__(**kwargs)
        
        # Default risk weights if not provided
        self.risk_weights = risk_weights or {
            RiskLevel.NEGLIGIBLE: 1.0,
            RiskLevel.LOW: 2.0,
            RiskLevel.MEDIUM: 4.0,
            RiskLevel.HIGH: 8.0,
            RiskLevel.VERY_HIGH: 16.0,
            RiskLevel.UNKNOWN: 2.0
        }
    
    def allocate(self, 
                sites: Dict[str, SurveillanceSite], 
                historical_results: Dict[str, List[Dict[str, Any]]],
                total_resources: int) -> Dict[str, int]:
        """
        Allocate sampling resources based on site risk levels
        
        Args:
            sites: Dictionary mapping site IDs to SurveillanceSite objects
            historical_results: Dictionary mapping site IDs to lists of previous sampling results
            total_resources: Total number of samples to allocate
            
        Returns:
            Dictionary mapping site IDs to number of samples to collect
        """
        # Calculate raw allocations based on risk
        raw_allocations = {}
        
        for site_id, site in sites.items():
            # Get risk level
            risk_level = site.risk_level
            
            # Get risk weight
            risk_weight = self.risk_weights[risk_level]
            
            # Add exploration bonus for sites with less historical data
            exploration_bonus = 0
            if site_id in historical_results:
                # Less exploration for frequently sampled sites
                exploration_bonus = 1.0 / (1.0 + len(historical_results[site_id]))
            else:
                # Maximum exploration for never-sampled sites
                exploration_bonus = 1.0
            
            # Calculate raw allocation
            exploration_weight = self._get_current_exploration_weight()
            raw_allocations[site_id] = (1 - exploration_weight) * risk_weight + exploration_weight * exploration_bonus
        
        # Normalize allocations
        normalized_allocations = self._normalize_allocations(raw_allocations)
        
        # Convert to integer sample counts
        sample_counts = {}
        remaining_samples = total_resources
        
        for site_id, allocation in normalized_allocations.items():
            # Calculate raw sample count
            samples = int(allocation * total_resources)
            
            # Ensure at least 1 sample for each site
            samples = max(1, samples)
            
            sample_counts[site_id] = samples
            remaining_samples -= samples
        
        # Distribute any remaining samples to highest-risk sites
        if remaining_samples > 0:
            # Sort sites by risk level
            sorted_sites = sorted(
                sites.items(),
                key=lambda x: self.risk_weights[x[1].risk_level],
                reverse=True
            )
            
            # Distribute remaining samples
            for i in range(remaining_samples):
                if i < len(sorted_sites):
                    site_id = sorted_sites[i][0]
                    sample_counts[site_id] += 1
        
        # Increment iteration counter
        self.iteration += 1
        
        return sample_counts


class ResponseAdaptiveSamplingStrategy(AdaptiveSamplingStrategy):
    """
    Sampling strategy that adapts based on previous detection results,
    similar to response-adaptive randomization in clinical trials
    """
    
    def __init__(self, 
                alpha: float = 0.1, 
                beta: float = 0.1,
                detection_bonus: float = 2.0, 
                **kwargs):
        """
        Initialize response-adaptive sampling strategy
        
        Args:
            alpha: Prior alpha parameter for Beta distribution
            beta: Prior beta parameter for Beta distribution
            detection_bonus: Multiplier for sites with positive detections
            **kwargs: Additional arguments for AdaptiveSamplingStrategy
        """
        super().__init__(**kwargs)
        self.alpha = alpha
        self.beta = beta
        self.detection_bonus = detection_bonus
        
        # Track posterior parameters for each site
        self.posteriors: Dict[str, Tuple[float, float]] = {}
    
    def _get_posterior(self, 
                      site_id: str, 
                      historical_results: Dict[str, List[Dict[str, Any]]]) -> Tuple[float, float]:
        """
        Calculate posterior distribution parameters for a site
        
        Args:
            site_id: Site identifier
            historical_results: Dictionary mapping site IDs to lists of previous sampling results
            
        Returns:
            Tuple of (alpha, beta) posterior parameters
        """
        # Start with prior
        alpha = self.alpha
        beta = self.beta
        
        # Update with historical results
        if site_id in historical_results:
            for result in historical_results[site_id]:
                # Get number of positive and negative samples
                positives = result.get('positives', 0)
                total = result.get('total', 0)
                
                if total > 0:
                    negatives = total - positives
                    
                    # Update posterior
                    alpha += positives
                    beta += negatives
        
        return (alpha, beta)
    
    def allocate(self, 
                sites: Dict[str, SurveillanceSite], 
                historical_results: Dict[str, List[Dict[str, Any]]],
                total_resources: int) -> Dict[str, int]:
        """
        Allocate sampling resources based on previous detection results
        
        Args:
            sites: Dictionary mapping site IDs to SurveillanceSite objects
            historical_results: Dictionary mapping site IDs to lists of previous sampling results
            total_resources: Total number of samples to allocate
            
        Returns:
            Dictionary mapping site IDs to number of samples to collect
        """
        # Calculate raw allocations based on posterior distributions
        raw_allocations = {}
        
        for site_id, site in sites.items():
            # Get posterior parameters
            alpha, beta = self._get_posterior(site_id, historical_results)
            
            # Store posterior for future reference
            self.posteriors[site_id] = (alpha, beta)
            
            # Calculate expected detection probability
            detection_prob = alpha / (alpha + beta) if (alpha + beta) > 0 else 0.5
            
            # Calculate information value (variance of Beta distribution)
            information_value = (alpha * beta) / ((alpha + beta)**2 * (alpha + beta + 1))
            
            # Apply detection bonus if detection probability is high
            if detection_prob > 0.5:
                information_value *= self.detection_bonus
            
            # Add risk-based component
            risk_weight = 1.0
            if hasattr(site, 'risk_level') and isinstance(site.risk_level, RiskLevel):
                # Use a simplified risk weight scale
                risk_mapping = {
                    RiskLevel.NEGLIGIBLE: 0.5,
                    RiskLevel.LOW: 1.0,
                    RiskLevel.MEDIUM: 1.5,
                    RiskLevel.HIGH: 2.0,
                    RiskLevel.VERY_HIGH: 2.5,
                    RiskLevel.UNKNOWN: 1.0
                }
                risk_weight = risk_mapping.get(site.risk_level, 1.0)
            
            # Add exploration component
            exploration_bonus = 1.0 / (alpha + beta)
            exploration_weight = self._get_current_exploration_weight()
            
            # Calculate raw allocation
            raw_allocations[site_id] = (
                (1 - exploration_weight) * information_value * risk_weight + 
                exploration_weight * exploration_bonus
            )
        
        # Normalize allocations
        normalized_allocations = self._normalize_allocations(raw_allocations)
        
        # Convert to integer sample counts
        sample_counts = {}
        remaining_samples = total_resources
        
        for site_id, allocation in normalized_allocations.items():
            # Calculate raw sample count
            samples = int(allocation * total_resources)
            
            # Ensure at least 1 sample for each site
            samples = max(1, samples)
            
            sample_counts[site_id] = samples
            remaining_samples -= samples
        
        # Distribute any remaining samples based on highest allocation
        if remaining_samples > 0:
            # Sort sites by allocation
            sorted_sites = sorted(
                normalized_allocations.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Distribute remaining samples
            for i in range(remaining_samples):
                if i < len(sorted_sites):
                    site_id = sorted_sites[i][0]
                    sample_counts[site_id] += 1
        
        # Increment iteration counter
        self.iteration += 1
        
        return sample_counts


class ThompsonSamplingSamplingStrategy(AdaptiveSamplingStrategy):
    """
    Sampling strategy using Thompson sampling for multi-armed bandit optimization,
    balancing exploration and exploitation automatically
    """
    
    def __init__(self, 
                alpha: float = 1.0, 
                beta: float = 1.0,
                num_samples: int = 1000,
                **kwargs):
        """
        Initialize Thompson sampling strategy
        
        Args:
            alpha: Prior alpha parameter for Beta distribution
            beta: Prior beta parameter for Beta distribution
            num_samples: Number of samples to draw from posterior distributions
            **kwargs: Additional arguments for AdaptiveSamplingStrategy
        """
        super().__init__(**kwargs)
        self.alpha = alpha
        self.beta = beta
        self.num_samples = num_samples
        
        # Track posterior parameters for each site
        self.posteriors: Dict[str, Tuple[float, float]] = {}
    
    def _get_posterior(self, 
                      site_id: str, 
                      historical_results: Dict[str, List[Dict[str, Any]]]) -> Tuple[float, float]:
        """
        Calculate posterior distribution parameters for a site
        
        Args:
            site_id: Site identifier
            historical_results: Dictionary mapping site IDs to lists of previous sampling results
            
        Returns:
            Tuple of (alpha, beta) posterior parameters
        """
        # Start with prior
        alpha = self.alpha
        beta = self.beta
        
        # Update with historical results
        if site_id in historical_results:
            for result in historical_results[site_id]:
                # Get number of positive and negative samples
                positives = result.get('positives', 0)
                total = result.get('total', 0)
                
                if total > 0:
                    negatives = total - positives
                    
                    # Update posterior
                    alpha += positives
                    beta += negatives
        
        return (alpha, beta)
    
    def allocate(self, 
                sites: Dict[str, SurveillanceSite], 
                historical_results: Dict[str, List[Dict[str, Any]]],
                total_resources: int) -> Dict[str, int]:
        """
        Allocate sampling resources using Thompson sampling
        
        Args:
            sites: Dictionary mapping site IDs to SurveillanceSite objects
            historical_results: Dictionary mapping site IDs to lists of previous sampling results
            total_resources: Total number of samples to allocate
            
        Returns:
            Dictionary mapping site IDs to number of samples to collect
        """
        if not sites:
            return {}
        
        # Get posteriors for each site
        posteriors = {}
        for site_id in sites:
            posteriors[site_id] = self._get_posterior(site_id, historical_results)
            self.posteriors[site_id] = posteriors[site_id]
        
        # Perform Thompson sampling
        site_ids = list(sites.keys())
        allocation_counts = {site_id: 0 for site_id in site_ids}
        
        # Draw samples from posterior distributions and choose the site with highest value
        for _ in range(self.num_samples):
            # Draw a sample from each site's posterior distribution
            samples = {}
            for site_id in site_ids:
                alpha, beta = posteriors[site_id]
                # Draw a random sample from Beta distribution
                samples[site_id] = np.random.beta(alpha, beta)
            
            # Select the site with the highest sample
            selected_site = max(samples, key=samples.get)
            allocation_counts[selected_site] += 1
        
        # Convert allocation counts to normalized proportions
        total_counts = sum(allocation_counts.values())
        normalized_allocations = {
            site_id: count / total_counts for site_id, count in allocation_counts.items()
        }
        
        # Apply minimum allocation
        normalized_allocations = self._normalize_allocations(normalized_allocations)
        
        # Convert to integer sample counts
        sample_counts = {}
        remaining_samples = total_resources
        
        for site_id, allocation in normalized_allocations.items():
            # Calculate raw sample count
            samples = int(allocation * total_resources)
            
            # Ensure at least 1 sample for each site
            samples = max(1, samples)
            
            sample_counts[site_id] = samples
            remaining_samples -= samples
        
        # Distribute any remaining samples
        if remaining_samples > 0:
            # Sort sites by allocation
            sorted_sites = sorted(
                normalized_allocations.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Distribute remaining samples
            for i in range(remaining_samples):
                if i < len(sorted_sites):
                    site_id = sorted_sites[i][0]
                    sample_counts[site_id] += 1
        
        # Increment iteration counter
        self.iteration += 1
        
        return sample_counts


# Factory function to create sampling strategy based on strategy name
def create_sampling_strategy(strategy_name: str, **kwargs) -> AdaptiveSamplingStrategy:
    """
    Create a sampling strategy based on strategy name
    
    Args:
        strategy_name: Name of the strategy to create
        **kwargs: Additional arguments for the strategy
        
    Returns:
        Instantiated sampling strategy
    """
    strategies = {
        'risk_based': RiskBasedSamplingStrategy,
        'response_adaptive': ResponseAdaptiveSamplingStrategy,
        'thompson_sampling': ThompsonSamplingSamplingStrategy
    }
    
    if strategy_name not in strategies:
        raise ValueError(f"Unknown sampling strategy: {strategy_name}")
    
    return strategies[strategy_name](**kwargs)