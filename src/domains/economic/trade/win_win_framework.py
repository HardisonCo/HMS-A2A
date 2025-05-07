"""
Win-Win Calculation Framework for the Trade Balance System.

This module implements the core Win-Win calculation framework, providing
entity-specific value translation, time and risk adjustment calculations,
and value distribution optimization.
"""

import math
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Union
from uuid import uuid4

from trade_balance.interfaces import (
    EntityProfile, ValueComponent, EntityValue, EntityType,
    IValueTranslator, IWinWinCalculator, Result
)


class GovernmentValueTranslator:
    """Implements value translation for government entities."""
    
    def translate_value(
        self, 
        value_components: Dict[str, ValueComponent],
        entity_profile: EntityProfile
    ) -> Tuple[float, Dict[str, float]]:
        """
        Translate value components into government-specific value.
        
        Args:
            value_components: Dictionary of value components
            entity_profile: Government entity profile
            
        Returns:
            Tuple of (total value, component values dictionary)
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


class CorporateValueTranslator:
    """Implements value translation for corporate entities."""
    
    def translate_value(
        self, 
        value_components: Dict[str, ValueComponent],
        entity_profile: EntityProfile
    ) -> Tuple[float, Dict[str, float]]:
        """
        Translate value components into corporate-specific value.
        
        Args:
            value_components: Dictionary of value components
            entity_profile: Corporate entity profile
            
        Returns:
            Tuple of (total value, component values dictionary)
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


class NGOValueTranslator:
    """Implements value translation for NGO entities."""
    
    def translate_value(
        self, 
        value_components: Dict[str, ValueComponent],
        entity_profile: EntityProfile
    ) -> Tuple[float, Dict[str, float]]:
        """
        Translate value components into NGO-specific value.
        
        Args:
            value_components: Dictionary of value components
            entity_profile: NGO entity profile
            
        Returns:
            Tuple of (total value, component values dictionary)
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


class CivilianValueTranslator:
    """Implements value translation for civilian entities."""
    
    def translate_value(
        self, 
        value_components: Dict[str, ValueComponent],
        entity_profile: EntityProfile
    ) -> Tuple[float, Dict[str, float]]:
        """
        Translate value components into civilian-specific value.
        
        Args:
            value_components: Dictionary of value components
            entity_profile: Civilian entity profile
            
        Returns:
            Tuple of (total value, component values dictionary)
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


class WinWinCalculator(IWinWinCalculator):
    """
    Implements the Win-Win calculation framework for assessing and
    optimizing value distribution among entities.
    """
    
    def __init__(self):
        """Initialize with entity-specific value translators."""
        self.translators = {
            EntityType.GOVERNMENT: GovernmentValueTranslator(),
            EntityType.CORPORATE: CorporateValueTranslator(),
            EntityType.NGO: NGOValueTranslator(),
            EntityType.CIVILIAN: CivilianValueTranslator()
        }
    
    def calculate_entity_value(
        self,
        entity_profile: EntityProfile,
        value_components: Dict[str, ValueComponent],
        historical_data: Optional[Dict[str, List[float]]] = None,
        superset_data: Optional[Dict[str, List[float]]] = None
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
        # Use appropriate translator based on entity type
        translator = self.translators.get(entity_profile.type)
        if not translator:
            # Default to averaging component values if no specific translator
            total_value = sum(comp.amount for comp in value_components.values())
            component_values = {
                comp_id: comp.amount for comp_id, comp in value_components.items()
            }
        else:
            total_value, component_values = translator.translate_value(
                value_components, entity_profile
            )
        
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
    
    def is_win_win(
        self,
        entity_values: Dict[str, EntityValue]
    ) -> bool:
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
        self,
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
            entity_values[entity_id] = self.calculate_entity_value(profile, value_components)
        
        # Check if already win-win
        if self.is_win_win(entity_values):
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
                component_id = f"ext_value_{entity_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
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
                component_id = f"redist_{excess_entity_id}_{negative_entity_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
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
            optimized_entity_values[entity_id] = self.calculate_entity_value(profile, value_components)
        
        if self.is_win_win(optimized_entity_values):
            return optimized_components
        
        # If still not win-win, add minimal value to remaining negative entities
        for entity_id, value in optimized_entity_values.items():
            if not value.is_win:
                # Create a new value component with positive value
                component_id = f"ext_value_{entity_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
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
    
    def analyze_win_win_deal(
        self,
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
            entity_values[entity_id] = self.calculate_entity_value(profile, components)
        
        # Determine win-win status
        is_deal_win_win = self.is_win_win(entity_values)
        
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
                        'entity_type': profile.type.value,
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


# Helper functions to create entities and components

def create_entity_profile(
    entity_id: str,
    entity_name: str,
    entity_type: Union[EntityType, str],
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
    # Convert string entity type to enum if needed
    if isinstance(entity_type, str):
        entity_type = EntityType(entity_type)
    
    # Default dimensions based on entity type
    if dimensions is None:
        if entity_type == EntityType.GOVERNMENT:
            dimensions = {
                'budget_impact': 0.3,
                'mission_alignment': 0.3,
                'constituent_benefit': 0.3,
                'political_capital': 0.1
            }
        elif entity_type == EntityType.CORPORATE:
            dimensions = {
                'revenue_impact': 0.4,
                'cost_reduction': 0.3,
                'market_position': 0.2,
                'risk_reduction': 0.1
            }
        elif entity_type == EntityType.NGO:
            dimensions = {
                'mission_impact': 0.5,
                'beneficiary_value': 0.3,
                'donor_satisfaction': 0.1,
                'operational_capacity': 0.1
            }
        elif entity_type == EntityType.CIVILIAN:
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