"""
Win-Win Calculation Framework for Moneyball Deal Model

This module implements the mathematical framework for win-win calculations
across different entity types (government, corporate, NGO, civilian).
It provides entity-specific value translation and calculation functions
to ensure that all parties in a deal receive positive value.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional, Union
from dataclasses import dataclass
import math
import json
import datetime

# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class EntityProfile:
    """Profile for an entity participating in a deal."""
    id: str
    name: str
    type: str  # 'government', 'corporate', 'ngo', 'civilian'
    dimensions: Dict[str, float]  # Value dimension weights
    time_preference: float  # Discount rate for time
    risk_preference: float  # Risk aversion factor
    resource_constraints: Dict[str, float]  # Constraints on resources
    performance_metrics: Dict[str, List[float]]  # Historical performance

@dataclass
class ValueComponent:
    """Component of value for an entity."""
    dimension: str
    amount: float
    timeline: List[Tuple[int, float]]  # List of (period, amount) tuples
    probability: float
    verification_method: str
    is_quantifiable: bool
    network_effects: Dict[str, float]  # Impact on other dimensions

@dataclass
class EntityValue:
    """Total value assessment for an entity."""
    entity_id: str
    entity_type: str
    components: Dict[str, ValueComponent]
    total_value: float
    time_adjusted_value: float
    risk_adjusted_value: float
    is_win: bool
    confidence: float

# =============================================================================
# Entity-Specific Value Translation
# =============================================================================

def government_value_translation(
    value_components: Dict[str, ValueComponent],
    entity_profile: EntityProfile
) -> Tuple[float, Dict[str, float]]:
    """
    Translate value components into government-specific value.
    
    Args:
        value_components: Dictionary of value components
        entity_profile: Government entity profile
        
    Returns:
        Total value and component values
    """
    component_values = {}
    
    # Government-specific value dimensions
    gov_dimensions = {
        'budget_impact': entity_profile.dimensions.get('budget_impact', 0.3),
        'mission_alignment': entity_profile.dimensions.get('mission_alignment', 0.3),
        'constituent_benefit': entity_profile.dimensions.get('constituent_benefit', 0.3),
        'political_capital': entity_profile.dimensions.get('political_capital', 0.1)
    }
    
    # Calculate value for each component
    for component_id, component in value_components.items():
        # Translate component dimension to government dimensions
        if component.dimension == 'economic':
            gov_value = component.amount * (
                0.6 * gov_dimensions['budget_impact'] +
                0.2 * gov_dimensions['mission_alignment'] +
                0.1 * gov_dimensions['constituent_benefit'] +
                0.1 * gov_dimensions['political_capital']
            )
        elif component.dimension == 'social':
            gov_value = component.amount * (
                0.1 * gov_dimensions['budget_impact'] +
                0.3 * gov_dimensions['mission_alignment'] +
                0.5 * gov_dimensions['constituent_benefit'] +
                0.1 * gov_dimensions['political_capital']
            )
        elif component.dimension == 'environmental':
            gov_value = component.amount * (
                0.1 * gov_dimensions['budget_impact'] +
                0.4 * gov_dimensions['mission_alignment'] +
                0.3 * gov_dimensions['constituent_benefit'] +
                0.2 * gov_dimensions['political_capital']
            )
        elif component.dimension == 'security':
            gov_value = component.amount * (
                0.2 * gov_dimensions['budget_impact'] +
                0.4 * gov_dimensions['mission_alignment'] +
                0.1 * gov_dimensions['constituent_benefit'] +
                0.3 * gov_dimensions['political_capital']
            )
        else:
            # Default translation for other dimensions
            gov_value = component.amount * 0.5
        
        # Apply risk adjustment
        risk_adjusted = gov_value * component.probability ** (1 + entity_profile.risk_preference)
        
        # Apply time adjustment
        time_adjusted = 0.0
        for period, period_amount in component.timeline:
            time_adjusted += period_amount * (1 / (1 + entity_profile.time_preference)) ** period
        
        # Scale to original total
        if sum(amount for _, amount in component.timeline) > 0:
            scaling_factor = gov_value / sum(amount for _, amount in component.timeline)
            time_adjusted *= scaling_factor
        else:
            time_adjusted = gov_value
        
        # Store component value
        component_values[component_id] = min(risk_adjusted, time_adjusted)
    
    # Calculate total value
    total_value = sum(component_values.values())
    
    return total_value, component_values

def corporate_value_translation(
    value_components: Dict[str, ValueComponent],
    entity_profile: EntityProfile
) -> Tuple[float, Dict[str, float]]:
    """
    Translate value components into corporate-specific value.
    
    Args:
        value_components: Dictionary of value components
        entity_profile: Corporate entity profile
        
    Returns:
        Total value and component values
    """
    component_values = {}
    
    # Corporate-specific value dimensions
    corp_dimensions = {
        'revenue_impact': entity_profile.dimensions.get('revenue_impact', 0.4),
        'cost_reduction': entity_profile.dimensions.get('cost_reduction', 0.3),
        'market_position': entity_profile.dimensions.get('market_position', 0.2),
        'risk_reduction': entity_profile.dimensions.get('risk_reduction', 0.1)
    }
    
    # Calculate value for each component
    for component_id, component in value_components.items():
        # Translate component dimension to corporate dimensions
        if component.dimension == 'economic':
            corp_value = component.amount * (
                0.5 * corp_dimensions['revenue_impact'] +
                0.3 * corp_dimensions['cost_reduction'] +
                0.1 * corp_dimensions['market_position'] +
                0.1 * corp_dimensions['risk_reduction']
            )
        elif component.dimension == 'social':
            corp_value = component.amount * (
                0.1 * corp_dimensions['revenue_impact'] +
                0.1 * corp_dimensions['cost_reduction'] +
                0.6 * corp_dimensions['market_position'] +
                0.2 * corp_dimensions['risk_reduction']
            )
        elif component.dimension == 'environmental':
            corp_value = component.amount * (
                0.1 * corp_dimensions['revenue_impact'] +
                0.2 * corp_dimensions['cost_reduction'] +
                0.3 * corp_dimensions['market_position'] +
                0.4 * corp_dimensions['risk_reduction']
            )
        elif component.dimension == 'security':
            corp_value = component.amount * (
                0.1 * corp_dimensions['revenue_impact'] +
                0.1 * corp_dimensions['cost_reduction'] +
                0.2 * corp_dimensions['market_position'] +
                0.6 * corp_dimensions['risk_reduction']
            )
        else:
            # Default translation for other dimensions
            corp_value = component.amount * 0.5
        
        # Apply risk adjustment
        risk_adjusted = corp_value * component.probability ** (1 + entity_profile.risk_preference)
        
        # Apply time adjustment
        time_adjusted = 0.0
        for period, period_amount in component.timeline:
            time_adjusted += period_amount * (1 / (1 + entity_profile.time_preference)) ** period
        
        # Scale to original total
        if sum(amount for _, amount in component.timeline) > 0:
            scaling_factor = corp_value / sum(amount for _, amount in component.timeline)
            time_adjusted *= scaling_factor
        else:
            time_adjusted = corp_value
        
        # Store component value
        component_values[component_id] = min(risk_adjusted, time_adjusted)
    
    # Calculate total value
    total_value = sum(component_values.values())
    
    return total_value, component_values

def ngo_value_translation(
    value_components: Dict[str, ValueComponent],
    entity_profile: EntityProfile
) -> Tuple[float, Dict[str, float]]:
    """
    Translate value components into NGO-specific value.
    
    Args:
        value_components: Dictionary of value components
        entity_profile: NGO entity profile
        
    Returns:
        Total value and component values
    """
    component_values = {}
    
    # NGO-specific value dimensions
    ngo_dimensions = {
        'mission_impact': entity_profile.dimensions.get('mission_impact', 0.5),
        'beneficiary_value': entity_profile.dimensions.get('beneficiary_value', 0.3),
        'donor_satisfaction': entity_profile.dimensions.get('donor_satisfaction', 0.1),
        'operational_capacity': entity_profile.dimensions.get('operational_capacity', 0.1)
    }
    
    # Calculate value for each component
    for component_id, component in value_components.items():
        # Translate component dimension to NGO dimensions
        if component.dimension == 'economic':
            ngo_value = component.amount * (
                0.2 * ngo_dimensions['mission_impact'] +
                0.3 * ngo_dimensions['beneficiary_value'] +
                0.2 * ngo_dimensions['donor_satisfaction'] +
                0.3 * ngo_dimensions['operational_capacity']
            )
        elif component.dimension == 'social':
            ngo_value = component.amount * (
                0.4 * ngo_dimensions['mission_impact'] +
                0.4 * ngo_dimensions['beneficiary_value'] +
                0.1 * ngo_dimensions['donor_satisfaction'] +
                0.1 * ngo_dimensions['operational_capacity']
            )
        elif component.dimension == 'environmental':
            ngo_value = component.amount * (
                0.5 * ngo_dimensions['mission_impact'] +
                0.3 * ngo_dimensions['beneficiary_value'] +
                0.1 * ngo_dimensions['donor_satisfaction'] +
                0.1 * ngo_dimensions['operational_capacity']
            )
        elif component.dimension == 'security':
            ngo_value = component.amount * (
                0.4 * ngo_dimensions['mission_impact'] +
                0.3 * ngo_dimensions['beneficiary_value'] +
                0.2 * ngo_dimensions['donor_satisfaction'] +
                0.1 * ngo_dimensions['operational_capacity']
            )
        else:
            # Default translation for other dimensions
            ngo_value = component.amount * 0.5
        
        # Apply risk adjustment
        risk_adjusted = ngo_value * component.probability ** (1 + entity_profile.risk_preference)
        
        # Apply time adjustment
        time_adjusted = 0.0
        for period, period_amount in component.timeline:
            time_adjusted += period_amount * (1 / (1 + entity_profile.time_preference)) ** period
        
        # Scale to original total
        if sum(amount for _, amount in component.timeline) > 0:
            scaling_factor = ngo_value / sum(amount for _, amount in component.timeline)
            time_adjusted *= scaling_factor
        else:
            time_adjusted = ngo_value
        
        # Store component value
        component_values[component_id] = min(risk_adjusted, time_adjusted)
    
    # Calculate total value
    total_value = sum(component_values.values())
    
    return total_value, component_values

def civilian_value_translation(
    value_components: Dict[str, ValueComponent],
    entity_profile: EntityProfile
) -> Tuple[float, Dict[str, float]]:
    """
    Translate value components into civilian-specific value.
    
    Args:
        value_components: Dictionary of value components
        entity_profile: Civilian entity profile
        
    Returns:
        Total value and component values
    """
    component_values = {}
    
    # Civilian-specific value dimensions
    civilian_dimensions = {
        'direct_benefit': entity_profile.dimensions.get('direct_benefit', 0.5),
        'cost_savings': entity_profile.dimensions.get('cost_savings', 0.3),
        'service_improvement': entity_profile.dimensions.get('service_improvement', 0.1),
        'future_opportunity': entity_profile.dimensions.get('future_opportunity', 0.1)
    }
    
    # Calculate value for each component
    for component_id, component in value_components.items():
        # Translate component dimension to civilian dimensions
        if component.dimension == 'economic':
            civilian_value = component.amount * (
                0.3 * civilian_dimensions['direct_benefit'] +
                0.5 * civilian_dimensions['cost_savings'] +
                0.1 * civilian_dimensions['service_improvement'] +
                0.1 * civilian_dimensions['future_opportunity']
            )
        elif component.dimension == 'social':
            civilian_value = component.amount * (
                0.4 * civilian_dimensions['direct_benefit'] +
                0.1 * civilian_dimensions['cost_savings'] +
                0.4 * civilian_dimensions['service_improvement'] +
                0.1 * civilian_dimensions['future_opportunity']
            )
        elif component.dimension == 'environmental':
            civilian_value = component.amount * (
                0.3 * civilian_dimensions['direct_benefit'] +
                0.2 * civilian_dimensions['cost_savings'] +
                0.3 * civilian_dimensions['service_improvement'] +
                0.2 * civilian_dimensions['future_opportunity']
            )
        elif component.dimension == 'security':
            civilian_value = component.amount * (
                0.5 * civilian_dimensions['direct_benefit'] +
                0.1 * civilian_dimensions['cost_savings'] +
                0.1 * civilian_dimensions['service_improvement'] +
                0.3 * civilian_dimensions['future_opportunity']
            )
        else:
            # Default translation for other dimensions
            civilian_value = component.amount * 0.5
        
        # Apply risk adjustment
        # Civilians typically have higher risk aversion
        risk_adjusted = civilian_value * component.probability ** (1 + entity_profile.risk_preference)
        
        # Apply time adjustment
        # Civilians typically have higher time preference (want benefits sooner)
        time_adjusted = 0.0
        for period, period_amount in component.timeline:
            time_adjusted += period_amount * (1 / (1 + entity_profile.time_preference)) ** period
        
        # Scale to original total
        if sum(amount for _, amount in component.timeline) > 0:
            scaling_factor = civilian_value / sum(amount for _, amount in component.timeline)
            time_adjusted *= scaling_factor
        else:
            time_adjusted = civilian_value
        
        # Store component value
        component_values[component_id] = min(risk_adjusted, time_adjusted)
    
    # Calculate total value
    total_value = sum(component_values.values())
    
    return total_value, component_values

def calculate_log_std_deviation_value(
    value: float,
    historical_values: List[float],
    superset_values: List[float]
) -> float:
    """
    Calculate the log STD deviation value as described in the requirements.
    
    Value = log(|value - weighted_recursive_avg|) / log(mean_of_deviation_from_superset_avg)
    
    Args:
        value: Current value
        historical_values: Time series of historical values for this entity
        superset_values: Values from the superset (e.g., all entities of this type)
        
    Returns:
        Calculated log STD deviation value
    """
    # Calculate weighted recursive average
    # Recent values have higher weights
    if not historical_values:
        weighted_recursive_avg = value
    else:
        weights = [1 / (i + 1) for i in range(len(historical_values))]
        weight_sum = sum(weights)
        weighted_recursive_avg = sum(v * w for v, w in zip(historical_values, weights)) / weight_sum
    
    # Calculate mean of deviation from superset average
    if not superset_values:
        mean_deviation_from_superset = 1.0  # Default if no superset available
    else:
        superset_avg = sum(superset_values) / len(superset_values)
        mean_deviation_from_superset = sum(abs(v - superset_avg) for v in superset_values) / len(superset_values)
    
    # Calculate log STD deviation value
    # Avoid log(0) and division by zero
    value_deviation = abs(value - weighted_recursive_avg)
    if value_deviation == 0:
        value_deviation = 0.0001  # Small non-zero value
    
    if mean_deviation_from_superset == 0:
        mean_deviation_from_superset = 0.0001  # Small non-zero value
    
    log_std_value = math.log(value_deviation) / math.log(mean_deviation_from_superset)
    
    return log_std_value

# =============================================================================
# Value Translation Matrices
# =============================================================================

def create_translation_matrix(source_domain: str, target_domain: str) -> np.ndarray:
    """
    Create a translation matrix between domains.
    
    Args:
        source_domain: Source domain
        target_domain: Target domain
        
    Returns:
        Translation matrix as numpy array
    """
    # Predefined translation matrices
    matrices = {
        # Economic to other domains
        ('economic', 'social'): np.array([
            [0.3, 0.1, 0.4, 0.2],
            [0.1, 0.5, 0.2, 0.2],
            [0.4, 0.2, 0.3, 0.1],
            [0.2, 0.2, 0.1, 0.5]
        ]),
        ('economic', 'environmental'): np.array([
            [0.4, 0.1, 0.3, 0.2],
            [0.2, 0.3, 0.3, 0.2],
            [0.1, 0.2, 0.5, 0.2],
            [0.3, 0.4, 0.1, 0.2]
        ]),
        ('economic', 'security'): np.array([
            [0.5, 0.1, 0.2, 0.2],
            [0.3, 0.3, 0.2, 0.2],
            [0.1, 0.2, 0.5, 0.2],
            [0.1, 0.4, 0.1, 0.4]
        ]),
        
        # Social to other domains
        ('social', 'economic'): np.array([
            [0.2, 0.2, 0.4, 0.2],
            [0.1, 0.4, 0.3, 0.2],
            [0.3, 0.3, 0.2, 0.2],
            [0.4, 0.1, 0.1, 0.4]
        ]),
        ('social', 'environmental'): np.array([
            [0.2, 0.3, 0.3, 0.2],
            [0.2, 0.4, 0.2, 0.2],
            [0.3, 0.2, 0.4, 0.1],
            [0.3, 0.1, 0.1, 0.5]
        ]),
        ('social', 'security'): np.array([
            [0.1, 0.2, 0.5, 0.2],
            [0.2, 0.3, 0.3, 0.2],
            [0.4, 0.1, 0.1, 0.4],
            [0.3, 0.4, 0.1, 0.2]
        ]),
        
        # Environmental to other domains
        ('environmental', 'economic'): np.array([
            [0.2, 0.2, 0.3, 0.3],
            [0.1, 0.2, 0.4, 0.3],
            [0.3, 0.4, 0.2, 0.1],
            [0.4, 0.2, 0.1, 0.3]
        ]),
        ('environmental', 'social'): np.array([
            [0.3, 0.3, 0.2, 0.2],
            [0.2, 0.4, 0.2, 0.2],
            [0.2, 0.2, 0.5, 0.1],
            [0.3, 0.1, 0.1, 0.5]
        ]),
        ('environmental', 'security'): np.array([
            [0.1, 0.1, 0.5, 0.3],
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.2, 0.1, 0.2],
            [0.3, 0.5, 0.1, 0.1]
        ]),
        
        # Security to other domains
        ('security', 'economic'): np.array([
            [0.4, 0.2, 0.2, 0.2],
            [0.3, 0.3, 0.2, 0.2],
            [0.2, 0.3, 0.4, 0.1],
            [0.1, 0.2, 0.2, 0.5]
        ]),
        ('security', 'social'): np.array([
            [0.2, 0.2, 0.5, 0.1],
            [0.1, 0.3, 0.3, 0.3],
            [0.5, 0.2, 0.1, 0.2],
            [0.2, 0.3, 0.1, 0.4]
        ]),
        ('security', 'environmental'): np.array([
            [0.2, 0.1, 0.5, 0.2],
            [0.1, 0.4, 0.2, 0.3],
            [0.4, 0.3, 0.2, 0.1],
            [0.3, 0.2, 0.1, 0.4]
        ])
    }
    
    # Create key for lookup
    key = (source_domain, target_domain)
    
    # Return matrix if it exists
    if key in matrices:
        return matrices[key]
    
    # If no specific matrix is defined, return identity matrix
    return np.eye(4)

def translate_value_vector(value_vector: np.ndarray, source_domain: str, target_domain: str) -> np.ndarray:
    """
    Translate a value vector from one domain to another.
    
    Args:
        value_vector: Value vector in source domain
        source_domain: Source domain
        target_domain: Target domain
        
    Returns:
        Translated value vector in target domain
    """
    # If domains are the same, no translation needed
    if source_domain == target_domain:
        return value_vector
    
    # Get translation matrix
    translation_matrix = create_translation_matrix(source_domain, target_domain)
    
    # Apply translation matrix
    translated_vector = np.dot(translation_matrix, value_vector)
    
    return translated_vector

# =============================================================================
# Win-Win Calculation
# =============================================================================

def calculate_entity_value(
    entity_profile: EntityProfile,
    value_components: Dict[str, ValueComponent],
    historical_data: Dict[str, List[float]] = None,
    superset_data: Dict[str, List[float]] = None
) -> EntityValue:
    """
    Calculate the total value for an entity.
    
    Args:
        entity_profile: Entity profile
        value_components: Dictionary of value components
        historical_data: Historical value data for this entity
        superset_data: Value data for the superset of entities
        
    Returns:
        EntityValue object
    """
    # Use appropriate translation function based on entity type
    if entity_profile.type == 'government':
        total_value, component_values = government_value_translation(
            value_components, entity_profile)
    elif entity_profile.type == 'corporate':
        total_value, component_values = corporate_value_translation(
            value_components, entity_profile)
    elif entity_profile.type == 'ngo':
        total_value, component_values = ngo_value_translation(
            value_components, entity_profile)
    elif entity_profile.type == 'civilian':
        total_value, component_values = civilian_value_translation(
            value_components, entity_profile)
    else:
        # Default to averaging component values
        component_values = {}
        for component_id, component in value_components.items():
            component_values[component_id] = component.amount
        total_value = sum(component_values.values())
    
    # Calculate time-adjusted value
    time_adjusted_value = 0.0
    for component_id, component in value_components.items():
        for period, amount in component.timeline:
            time_adjusted_value += amount * (1 / (1 + entity_profile.time_preference)) ** period
    
    # Adjust for component values
    if sum(component_values.values()) > 0:
        scaling_factor = total_value / sum(component_values.values())
        time_adjusted_value *= scaling_factor
    
    # Calculate risk-adjusted value
    risk_adjusted_value = 0.0
    for component_id, component in value_components.items():
        risk_adjusted_value += component_values[component_id] * component.probability ** (
            1 + entity_profile.risk_preference)
    
    # Determine if this is a "win" for the entity
    is_win = total_value > 0 and time_adjusted_value > 0 and risk_adjusted_value > 0
    
    # Calculate confidence in the value assessment
    if not value_components:
        confidence = 0.0
    else:
        # Average of component probabilities, weighted by component values
        confidence = sum(
            component_values[c_id] * component.probability 
            for c_id, component in value_components.items()
        ) / sum(component_values.values()) if sum(component_values.values()) > 0 else 0.0
    
    # Create EntityValue object
    entity_value = EntityValue(
        entity_id=entity_profile.id,
        entity_type=entity_profile.type,
        components=value_components,
        total_value=total_value,
        time_adjusted_value=time_adjusted_value,
        risk_adjusted_value=risk_adjusted_value,
        is_win=is_win,
        confidence=confidence
    )
    
    return entity_value

def is_win_win(entity_values: Dict[str, EntityValue]) -> bool:
    """
    Determine if a deal satisfies the win-win condition for all entities.
    
    Args:
        entity_values: Dictionary of EntityValue objects by entity ID
        
    Returns:
        True if the deal is win-win, False otherwise
    """
    for entity_id, entity_value in entity_values.items():
        if not entity_value.is_win:
            return False
    
    return True

def optimize_value_distribution(
    entity_profiles: Dict[str, EntityProfile],
    initial_value_components: Dict[str, Dict[str, ValueComponent]],
    constraints: Dict[str, Any]
) -> Dict[str, Dict[str, ValueComponent]]:
    """
    Optimize the distribution of value among entities to ensure win-win.
    
    Args:
        entity_profiles: Dictionary of entity profiles by entity ID
        initial_value_components: Dictionary of value components by entity ID
        constraints: Dictionary of optimization constraints
        
    Returns:
        Optimized value components by entity ID
    """
    # Calculate initial entity values
    entity_values = {}
    for entity_id, profile in entity_profiles.items():
        value_components = initial_value_components.get(entity_id, {})
        entity_values[entity_id] = calculate_entity_value(profile, value_components)
    
    # Check if already win-win
    if is_win_win(entity_values):
        return initial_value_components
    
    # Identify entities with negative value
    negative_entities = []
    for entity_id, value in entity_values.items():
        if not value.is_win:
            negative_entities.append(entity_id)
    
    # Identify entities with excess value
    excess_entities = []
    for entity_id, value in entity_values.items():
        if value.is_win and value.total_value > constraints.get('min_positive_value', 10.0):
            excess_entities.append(entity_id)
    
    # If no excess entities, add value from external source
    if not excess_entities:
        # Add minimal value to negative entities
        optimized_components = initial_value_components.copy()
        
        for entity_id in negative_entities:
            # Create a new value component with positive value
            component_id = f"ext_value_{entity_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create value component with minimal positive value
            component = ValueComponent(
                dimension='economic',
                amount=abs(entity_values[entity_id].total_value) + constraints.get('min_positive_margin', 1.0),
                timeline=[(0, abs(entity_values[entity_id].total_value) + constraints.get('min_positive_margin', 1.0))],
                probability=0.95,
                verification_method='external_verification',
                is_quantifiable=True,
                network_effects={}
            )
            
            # Add component to entity's value components
            if entity_id not in optimized_components:
                optimized_components[entity_id] = {}
            
            optimized_components[entity_id][component_id] = component
        
        return optimized_components
    
    # Redistribute value from excess entities to negative entities
    optimized_components = initial_value_components.copy()
    
    # Calculate total negative value needed
    total_negative_value = 0.0
    for entity_id in negative_entities:
        total_negative_value += abs(entity_values[entity_id].total_value) + constraints.get('min_positive_margin', 1.0)
    
    # Calculate total excess value available
    total_excess_value = 0.0
    for entity_id in excess_entities:
        excess_value = entity_values[entity_id].total_value - constraints.get('min_positive_value', 10.0)
        total_excess_value += max(0, excess_value)
    
    # Calculate redistribution factor
    redistribution_factor = min(1.0, total_excess_value / total_negative_value)
    
    # Redistribute value
    for excess_entity_id in excess_entities:
        excess_value = entity_values[excess_entity_id].total_value - constraints.get('min_positive_value', 10.0)
        if excess_value <= 0:
            continue
        
        # Calculate share of excess value to redistribute from this entity
        share_factor = excess_value / total_excess_value
        value_to_redistribute = share_factor * total_negative_value * redistribution_factor
        
        # Reduce value components proportionally
        total_component_value = sum(component.amount for component in 
                                   optimized_components.get(excess_entity_id, {}).values())
        
        if total_component_value > 0:
            for component_id, component in optimized_components.get(excess_entity_id, {}).items():
                # Calculate reduction for this component
                reduction_factor = value_to_redistribute / total_component_value
                new_amount = component.amount * (1 - reduction_factor)
                
                # Update component amount
                optimized_components[excess_entity_id][component_id] = ValueComponent(
                    dimension=component.dimension,
                    amount=new_amount,
                    timeline=[(period, amount * (1 - reduction_factor)) for period, amount in component.timeline],
                    probability=component.probability,
                    verification_method=component.verification_method,
                    is_quantifiable=component.is_quantifiable,
                    network_effects=component.network_effects
                )
        
        # Redistribute to negative entities
        for negative_entity_id in negative_entities:
            # Calculate share of value to add to this entity
            negative_value_needed = abs(entity_values[negative_entity_id].total_value) + constraints.get('min_positive_margin', 1.0)
            neg_share_factor = negative_value_needed / total_negative_value
            value_to_add = value_to_redistribute * neg_share_factor
            
            # Create a new value component with redistributed value
            component_id = f"redist_{excess_entity_id}_{negative_entity_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create value component
            component = ValueComponent(
                dimension='economic',
                amount=value_to_add,
                timeline=[(0, value_to_add)],
                probability=0.9,
                verification_method='redistribution_verification',
                is_quantifiable=True,
                network_effects={}
            )
            
            # Add component to entity's value components
            if negative_entity_id not in optimized_components:
                optimized_components[negative_entity_id] = {}
            
            optimized_components[negative_entity_id][component_id] = component
    
    # Verify if optimized distribution is win-win
    optimized_entity_values = {}
    for entity_id, profile in entity_profiles.items():
        value_components = optimized_components.get(entity_id, {})
        optimized_entity_values[entity_id] = calculate_entity_value(profile, value_components)
    
    if is_win_win(optimized_entity_values):
        return optimized_components
    
    # If still not win-win, add minimal value to remaining negative entities
    for entity_id, value in optimized_entity_values.items():
        if not value.is_win:
            # Create a new value component with positive value
            component_id = f"ext_value_{entity_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create value component with minimal positive value
            component = ValueComponent(
                dimension='economic',
                amount=abs(value.total_value) + constraints.get('min_positive_margin', 1.0),
                timeline=[(0, abs(value.total_value) + constraints.get('min_positive_margin', 1.0))],
                probability=0.95,
                verification_method='external_verification',
                is_quantifiable=True,
                network_effects={}
            )
            
            # Add component to entity's value components
            if entity_id not in optimized_components:
                optimized_components[entity_id] = {}
            
            optimized_components[entity_id][component_id] = component
    
    return optimized_components

# =============================================================================
# Win-Win Analysis
# =============================================================================

def create_entity_profile(
    entity_id: str,
    entity_name: str,
    entity_type: str,
    dimensions: Dict[str, float] = None,
    time_preference: float = 0.1,
    risk_preference: float = 0.5,
    resource_constraints: Dict[str, float] = None,
    performance_metrics: Dict[str, List[float]] = None
) -> EntityProfile:
    """
    Create an entity profile with default values if not provided.
    
    Args:
        entity_id: Entity ID
        entity_name: Entity name
        entity_type: Entity type ('government', 'corporate', 'ngo', 'civilian')
        dimensions: Value dimension weights
        time_preference: Discount rate for time
        risk_preference: Risk aversion factor
        resource_constraints: Constraints on resources
        performance_metrics: Historical performance
        
    Returns:
        EntityProfile object
    """
    # Default dimensions based on entity type
    if dimensions is None:
        if entity_type == 'government':
            dimensions = {
                'budget_impact': 0.3,
                'mission_alignment': 0.3,
                'constituent_benefit': 0.3,
                'political_capital': 0.1
            }
        elif entity_type == 'corporate':
            dimensions = {
                'revenue_impact': 0.4,
                'cost_reduction': 0.3,
                'market_position': 0.2,
                'risk_reduction': 0.1
            }
        elif entity_type == 'ngo':
            dimensions = {
                'mission_impact': 0.5,
                'beneficiary_value': 0.3,
                'donor_satisfaction': 0.1,
                'operational_capacity': 0.1
            }
        elif entity_type == 'civilian':
            dimensions = {
                'direct_benefit': 0.5,
                'cost_savings': 0.3,
                'service_improvement': 0.1,
                'future_opportunity': 0.1
            }
        else:
            dimensions = {
                'economic': 0.25,
                'social': 0.25,
                'environmental': 0.25,
                'security': 0.25
            }
    
    # Default resource constraints
    if resource_constraints is None:
        resource_constraints = {
            'financial': 1000.0,
            'time': 100.0,
            'personnel': 10.0
        }
    
    # Default performance metrics
    if performance_metrics is None:
        performance_metrics = {
            'economic': [],
            'social': [],
            'environmental': [],
            'security': []
        }
    
    # Create and return profile
    return EntityProfile(
        id=entity_id,
        name=entity_name,
        type=entity_type,
        dimensions=dimensions,
        time_preference=time_preference,
        risk_preference=risk_preference,
        resource_constraints=resource_constraints,
        performance_metrics=performance_metrics
    )

def create_value_component(
    dimension: str,
    amount: float,
    timeline: List[Tuple[int, float]] = None,
    probability: float = 0.8,
    verification_method: str = 'standard',
    is_quantifiable: bool = True,
    network_effects: Dict[str, float] = None
) -> ValueComponent:
    """
    Create a value component.
    
    Args:
        dimension: Value dimension
        amount: Total amount of value
        timeline: List of (period, amount) tuples
        probability: Probability of realizing value
        verification_method: Method for verifying value realization
        is_quantifiable: Whether the value is quantifiable
        network_effects: Impact on other dimensions
        
    Returns:
        ValueComponent object
    """
    # Default timeline (all value in period 0)
    if timeline is None:
        timeline = [(0, amount)]
    
    # Default network effects
    if network_effects is None:
        network_effects = {}
    
    # Create and return component
    return ValueComponent(
        dimension=dimension,
        amount=amount,
        timeline=timeline,
        probability=probability,
        verification_method=verification_method,
        is_quantifiable=is_quantifiable,
        network_effects=network_effects
    )

def analyze_win_win_deal(
    entity_profiles: Dict[str, EntityProfile],
    value_components: Dict[str, Dict[str, ValueComponent]]
) -> Dict[str, Any]:
    """
    Analyze a deal for win-win status and suggest improvements.
    
    Args:
        entity_profiles: Dictionary of entity profiles by entity ID
        value_components: Dictionary of value components by entity ID
        
    Returns:
        Dictionary with analysis results
    """
    # Calculate entity values
    entity_values = {}
    for entity_id, profile in entity_profiles.items():
        components = value_components.get(entity_id, {})
        entity_values[entity_id] = calculate_entity_value(profile, components)
    
    # Determine win-win status
    is_deal_win_win = is_win_win(entity_values)
    
    # Identify entities with negative value
    negative_entities = []
    for entity_id, value in entity_values.items():
        if not value.is_win:
            negative_entities.append(entity_id)
    
    # Calculate improvement opportunities
    improvement_opportunities = []
    
    if not is_deal_win_win:
        for entity_id in negative_entities:
            profile = entity_profiles[entity_id]
            value = entity_values[entity_id]
            
            # Identify dimensions with most negative impact
            dimension_values = {}
            for component_id, component in value_components.get(entity_id, {}).items():
                if component.dimension not in dimension_values:
                    dimension_values[component.dimension] = 0.0
                dimension_values[component.dimension] += component.amount
            
            # Sort dimensions by value
            sorted_dimensions = sorted(dimension_values.items(), key=lambda x: x[1])
            
            # Identify most negative dimension
            if sorted_dimensions and sorted_dimensions[0][1] < 0:
                negative_dimension = sorted_dimensions[0][0]
                
                # Suggest improvement
                improvement_opportunities.append({
                    'entity_id': entity_id,
                    'entity_type': profile.type,
                    'negative_value': value.total_value,
                    'focus_dimension': negative_dimension,
                    'required_improvement': abs(value.total_value) + 1.0  # Add small margin
                })
    
    # Calculate value distribution metrics
    total_value = sum(value.total_value for value in entity_values.values())
    value_distribution = {entity_id: value.total_value / total_value if total_value else 0.0
                         for entity_id, value in entity_values.items()}
    
    # Calculate Gini coefficient for value inequality
    gini = 0.0
    if len(entity_values) > 1:
        values = list(value.total_value for value in entity_values.values())
        values.sort()
        n = len(values)
        gini_sum = sum((2 * i - n - 1) * values[i] for i in range(n))
        gini = abs(gini_sum) / (n * sum(values)) if sum(values) else 0.0
    
    # Return analysis results
    return {
        'is_win_win': is_deal_win_win,
        'entity_values': {entity_id: {
            'total_value': value.total_value,
            'time_adjusted_value': value.time_adjusted_value,
            'risk_adjusted_value': value.risk_adjusted_value,
            'is_win': value.is_win,
            'confidence': value.confidence
        } for entity_id, value in entity_values.items()},
        'negative_entities': negative_entities,
        'improvement_opportunities': improvement_opportunities,
        'value_distribution': value_distribution,
        'value_inequality_gini': gini
    }

# =============================================================================
# Main
# =============================================================================

def main():
    """Example usage of the win-win calculation framework."""
    # Create entity profiles
    entity_profiles = {
        'gov_1': create_entity_profile(
            entity_id='gov_1',
            entity_name='Government Agency',
            entity_type='government',
            time_preference=0.05,
            risk_preference=0.3
        ),
        'corp_1': create_entity_profile(
            entity_id='corp_1',
            entity_name='Technology Corporation',
            entity_type='corporate',
            time_preference=0.1,
            risk_preference=0.4
        ),
        'ngo_1': create_entity_profile(
            entity_id='ngo_1',
            entity_name='Environmental NGO',
            entity_type='ngo',
            time_preference=0.08,
            risk_preference=0.6
        ),
        'civ_1': create_entity_profile(
            entity_id='civ_1',
            entity_name='Community Group',
            entity_type='civilian',
            time_preference=0.15,
            risk_preference=0.7
        )
    }
    
    # Create value components
    value_components = {
        'gov_1': {
            'comp_1': create_value_component(
                dimension='economic',
                amount=100.0,
                timeline=[(0, 20.0), (1, 30.0), (2, 50.0)],
                probability=0.9
            ),
            'comp_2': create_value_component(
                dimension='social',
                amount=50.0,
                timeline=[(1, 20.0), (2, 30.0)],
                probability=0.8
            )
        },
        'corp_1': {
            'comp_3': create_value_component(
                dimension='economic',
                amount=200.0,
                timeline=[(0, 50.0), (1, 75.0), (2, 75.0)],
                probability=0.85
            ),
            'comp_4': create_value_component(
                dimension='environmental',
                amount=-30.0,  # Negative value in this dimension
                timeline=[(0, -10.0), (1, -10.0), (2, -10.0)],
                probability=0.7
            )
        },
        'ngo_1': {
            'comp_5': create_value_component(
                dimension='environmental',
                amount=80.0,
                timeline=[(1, 30.0), (2, 50.0)],
                probability=0.75
            ),
            'comp_6': create_value_component(
                dimension='social',
                amount=40.0,
                timeline=[(0, 10.0), (1, 30.0)],
                probability=0.8
            )
        },
        'civ_1': {
            'comp_7': create_value_component(
                dimension='social',
                amount=60.0,
                timeline=[(0, 10.0), (1, 20.0), (2, 30.0)],
                probability=0.7
            ),
            'comp_8': create_value_component(
                dimension='economic',
                amount=-20.0,  # Negative value in this dimension
                timeline=[(0, -5.0), (1, -5.0), (2, -10.0)],
                probability=0.9
            )
        }
    }
    
    # Analyze deal
    analysis = analyze_win_win_deal(entity_profiles, value_components)
    
    # Print results
    print("Win-Win Analysis Results:")
    print(f"  Is win-win: {analysis['is_win_win']}")
    print("  Entity values:")
    for entity_id, values in analysis['entity_values'].items():
        is_win = values['is_win']
        print(f"    {entity_id}: {values['total_value']:.2f} ({'WIN' if is_win else 'LOSE'})")
    
    print("\nImprovement opportunities:")
    for opportunity in analysis['improvement_opportunities']:
        print(f"  {opportunity['entity_id']} needs {opportunity['required_improvement']:.2f} more value in {opportunity['focus_dimension']}")
    
    print(f"\nValue inequality (Gini): {analysis['value_inequality_gini']:.2f}")
    
    # Optimize if not win-win
    if not analysis['is_win_win']:
        print("\nOptimizing value distribution to achieve win-win...")
        optimized_components = optimize_value_distribution(
            entity_profiles, value_components, {'min_positive_value': 10.0, 'min_positive_margin': 1.0})
        
        # Analyze optimized deal
        optimized_analysis = analyze_win_win_deal(entity_profiles, optimized_components)
        
        # Print optimized results
        print("\nOptimized Win-Win Analysis Results:")
        print(f"  Is win-win: {optimized_analysis['is_win_win']}")
        print("  Entity values:")
        for entity_id, values in optimized_analysis['entity_values'].items():
            is_win = values['is_win']
            print(f"    {entity_id}: {values['total_value']:.2f} ({'WIN' if is_win else 'LOSE'})")

if __name__ == "__main__":
    main()