"""
Agency Integration for MAC Market Network Architecture

This module integrates specialized government agency agents (like USTDA and USITC)
and the win-win calculation framework into the MAC market network architecture.
"""

import os
import sys
import json
import logging
import datetime
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from uuid import uuid4
import numpy as np

# Add parent directory to path for imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import MAC components
from mac.economist_agent import EconomistAgent, ResourceType
from mac.market_models import (
    Market, MarketType, MarketMechanism, Order, Transaction, ImportCertificateSystem
)
from mac.network_effects import (
    AgentNetwork, NetworkType, EffectType, KnowledgeDiffusionModel
)
from mac.market_integration import MarketNetworkIntegrator

# Import Win-Win calculation framework
import sys
from win_win_calculation_framework import (
    EntityProfile, ValueComponent, EntityValue,
    government_value_translation, corporate_value_translation,
    ngo_value_translation, civilian_value_translation
)

# Import agency agents (assuming they're moved to HMS-A2A or paths adjusted)
try:
    from ustda_agent import (
        GovernancePolicy, ProgramActivity, USTDAAgent
    )
    from usitc_agent import (
        EconomicModel, TradeImpactAssessment, USITCAgent
    )
    # Use actual imports if files are available
    AGENCY_IMPORTS_AVAILABLE = True
except ImportError:
    # Define minimal versions of necessary classes if imports aren't available
    AGENCY_IMPORTS_AVAILABLE = False
    
    class GovernancePolicy:
        """Minimal implementation of GovernancePolicy."""
        def __init__(self, policy_id, title, description, policy_type, **kwargs):
            self.policy_id = policy_id
            self.title = title
            self.description = description
            self.policy_type = policy_type
            self.parameters = {}
            self.status = kwargs.get("status", "draft")
        
        def to_dict(self):
            return {
                "policy_id": self.policy_id,
                "title": self.title,
                "description": self.description,
                "policy_type": self.policy_type,
                "status": self.status,
                "parameters": self.parameters
            }
    
    class EconomicModel:
        """Minimal implementation of EconomicModel."""
        def __init__(self, model_id, title, description, model_type, **kwargs):
            self.model_id = model_id
            self.title = title
            self.description = description
            self.model_type = model_type
            self.parameters = {}
        
        def run_model(self, inputs):
            """Simulate running an economic model."""
            return {
                "gdp_impact": inputs.get("value", 100) * 0.05,
                "job_creation": inputs.get("value", 100) * 0.2,
                "trade_balance_effect": inputs.get("value", 100) * 0.1,
                "timestamp": datetime.datetime.now().isoformat()
            }


class AgencyNetworkExtension:
    """
    Extends the Market Network architecture to incorporate specialized 
    government agency agents (USTDA, USITC) and win-win calculation.
    """
    
    def __init__(
        self,
        market_integrator: MarketNetworkIntegrator,
        config_path: Optional[str] = None
    ):
        """
        Initialize the Agency Network Extension.
        
        Args:
            market_integrator: The MarketNetworkIntegrator to extend
            config_path: Path to configuration file (optional)
        """
        self.integrator = market_integrator
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger("MAC.AgencyNetworkExtension")
        
        # Initialize agency policies and models
        self.policies = {}
        self.economic_models = {}
        
        # Initialize entity profiles for win-win calculations
        self.entity_profiles = {}
        
        # Connect to economist agent
        self.economist = market_integrator.economist
        
        # Initialize agency agents if imports available
        if AGENCY_IMPORTS_AVAILABLE:
            self.ustda_agent = USTDAAgent()
            self.usitc_agent = USITCAgent()
        else:
            self.ustda_agent = None
            self.usitc_agent = None
        
        self.logger.info("Agency Network Extension initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        config = {
            "agency_influence_weight": 0.3,
            "policy_application_threshold": 0.7,
            "economic_model_confidence": 0.8,
            "win_win_requirement": True,
            "import_certificate_enabled": True,
            "cross_agency_collaboration": True
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    config.update(loaded_config)
            except Exception as e:
                logging.error(f"Error loading configuration: {str(e)}")
        
        return config
    
    async def register_agency(
        self,
        agency_id: str,
        agency_type: str,
        capabilities: List[str],
        value_dimensions: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Register a government agency with the market network.
        
        Args:
            agency_id: ID of the agency
            agency_type: Type of agency (e.g., "trade_development", "trade_commission")
            capabilities: List of agency capabilities
            value_dimensions: Value dimension weights
            
        Returns:
            Registration result
        """
        # Define agency-specific resource needs
        resource_needs = {
            "compute": 250.0,
            "memory": 300.0,
            "specialized_knowledge": 150.0,
            "human_attention": 50.0
        }
        
        # Register with economist agent
        registration = await self.integrator.register_agent_with_market_network(
            agent_id=agency_id,
            capabilities=capabilities,
            resource_needs=resource_needs,
            value_preferences=value_dimensions,
            stakeholder_type="government",
            risk_tolerance=0.4  # Agencies tend to be risk-averse
        )
        
        # Create entity profile for win-win calculations
        entity_profile = EntityProfile(
            id=agency_id,
            name=f"Agency {agency_id}",
            type="government",
            dimensions=value_dimensions,
            time_preference=0.05,  # Government agencies often have lower discount rates
            risk_preference=0.3,   # Risk aversion factor (higher = more averse)
            resource_constraints=resource_needs,
            performance_metrics={}  # Will be populated as the agency operates
        )
        
        self.entity_profiles[agency_id] = entity_profile
        
        # Special handling for specific agency types
        if agency_type == "trade_development" and agency_id.startswith("USTDA"):
            policy_id = f"POL-{uuid4().hex[:8]}"
            policy = GovernancePolicy(
                policy_id=policy_id,
                title="Import Certificate Trading System",
                description="Framework for balanced trade through certificate trading",
                policy_type="import_certificate",
                status="active"
            )
            policy.add_parameter("certificate_duration", 120)
            policy.add_parameter("initial_allocation", 100.0)
            
            self.policies[policy_id] = policy
            
            # Add to registration info
            registration["policies"] = [policy.to_dict()]
        
        elif agency_type == "trade_commission" and agency_id.startswith("USITC"):
            model_id = f"MOD-{uuid4().hex[:8]}"
            model = EconomicModel(
                model_id=model_id,
                title="Trade Impact Assessment Model",
                description="Evaluates economic impacts of trade deals",
                model_type="general_equilibrium"
            )
            
            self.economic_models[model_id] = model
            
            # Add to registration info
            registration["economic_models"] = [model_id]
        
        self.logger.info(f"Registered agency {agency_id} of type {agency_type}")
        
        return registration
    
    async def apply_policy_to_market(
        self,
        policy_id: str,
        market_id: str
    ) -> Dict[str, Any]:
        """
        Apply a government policy to a specific market.
        
        Args:
            policy_id: ID of the policy to apply
            market_id: ID of the market to apply the policy to
            
        Returns:
            Policy application results
        """
        if policy_id not in self.policies:
            return {"success": False, "message": f"Policy {policy_id} not found"}
        
        policy = self.policies[policy_id]
        
        # Get the market from economist agent
        market = None
        for res_type, mkt in self.economist.markets.items():
            if mkt.market_id == market_id:
                market = mkt
                break
        
        if not market:
            return {"success": False, "message": f"Market {market_id} not found"}
        
        # Apply policy based on type
        if policy.policy_type == "import_certificate" and policy.status == "active":
            # Apply import certificate policy to market
            
            # Modify market parameters
            if market.mechanism == MarketMechanism.CONTINUOUS_DOUBLE_AUCTION:
                # Adjust market configuration
                market.config["certificate_required"] = True
                market.config["certificate_validator"] = lambda order: (
                    order.order_type != "buy" or
                    self.economist.import_certificate_system.validate_import(
                        order.agent_id, order.quantity * order.price
                    )
                )
            
            # Update policy status
            policy.update_status("implemented", f"Applied to market {market_id}")
            
            return {
                "success": True,
                "message": f"Applied import certificate policy to market {market_id}",
                "effects": {
                    "certificate_requirement": True,
                    "market_mechanism": market.mechanism.value,
                    "implementation_date": datetime.datetime.now().isoformat()
                }
            }
            
        elif policy.policy_type == "tariff" and policy.status == "active":
            # Apply tariff policy
            tariff_rate = policy.parameters.get("tariff_rate", 0.1)
            
            # Modify market parameters for tariff
            if hasattr(market, "config"):
                market.config["tariff_rate"] = tariff_rate
                market.config["tariff_calculator"] = lambda order, price, quantity: (
                    tariff_rate * price * quantity if order.order_type == "buy" else 0
                )
            
            # Update policy status
            policy.update_status("implemented", f"Applied to market {market_id}")
            
            return {
                "success": True,
                "message": f"Applied tariff policy (rate: {tariff_rate}) to market {market_id}",
                "effects": {
                    "tariff_rate": tariff_rate,
                    "estimated_impact": tariff_rate * market.statistics.get("volume", 0),
                    "implementation_date": datetime.datetime.now().isoformat()
                }
            }
        
        return {
            "success": False,
            "message": f"Policy type {policy.policy_type} or status {policy.status} not applicable"
        }
    
    async def evaluate_deal_economic_impact(
        self,
        deal_id: str,
        model_id: str
    ) -> Dict[str, Any]:
        """
        Evaluate the economic impact of a deal using an economic model.
        
        Args:
            deal_id: ID of the deal to evaluate
            model_id: ID of the economic model to use
            
        Returns:
            Economic impact assessment
        """
        if model_id not in self.economic_models:
            return {"success": False, "message": f"Economic model {model_id} not found"}
        
        model = self.economic_models[model_id]
        
        # Get the deal from integrator
        if deal_id not in self.integrator.deals:
            return {"success": False, "message": f"Deal {deal_id} not found"}
        
        deal = self.integrator.deals[deal_id]
        
        # Extract deal parameters for economic model
        model_inputs = {
            "deal_id": deal_id,
            "deal_name": deal.name,
            "value": deal.solution.potential_value,
            "stakeholder_count": len(deal.stakeholders),
            "timeline": deal.execution.duration,
            "sectors": [dim for dim in deal.intent.value_dimensions],
            "implementation_difficulty": deal.solution.implementation_difficulty
        }
        
        # Run economic model
        model_results = model.run_model(model_inputs)
        
        # Store results in deal metrics
        if not hasattr(deal.metrics, "economic_impacts"):
            deal.metrics["economic_impacts"] = {}
        
        deal.metrics["economic_impacts"][model_id] = model_results
        
        # Update the deal
        self.integrator.deals[deal_id] = deal
        
        return {
            "success": True,
            "deal_id": deal_id,
            "model_id": model_id,
            "economic_impact": model_results,
            "integrated_with_deal": True,
            "assessment_date": datetime.datetime.now().isoformat()
        }
    
    async def calculate_win_win_status(
        self,
        deal_id: str,
        apply_adjustments: bool = False
    ) -> Dict[str, Any]:
        """
        Apply the win-win calculation framework to a deal.
        
        Args:
            deal_id: ID of the deal to evaluate
            apply_adjustments: Whether to apply automatic adjustments if not win-win
            
        Returns:
            Win-win calculation results
        """
        if deal_id not in self.integrator.deals:
            return {"success": False, "message": f"Deal {deal_id} not found"}
        
        deal = self.integrator.deals[deal_id]
        
        # Map deal components to win-win framework
        entity_values = {}
        for stakeholder_id, stakeholder in deal.stakeholders.items():
            # Get entity profile or create if not exists
            if stakeholder_id not in self.entity_profiles:
                self.entity_profiles[stakeholder_id] = EntityProfile(
                    id=stakeholder_id,
                    name=stakeholder.name,
                    type=stakeholder.type,
                    dimensions={dim: pref for dim, pref in stakeholder.value_preferences.items()},
                    time_preference=0.1,  # Default discount rate
                    risk_preference=1.0 - stakeholder.risk_tolerance,  # Convert risk tolerance to risk aversion
                    resource_constraints={},
                    performance_metrics={}
                )
            
            entity_profile = self.entity_profiles[stakeholder_id]
            
            # Map deal value components to win-win framework
            value_components = {}
            for dim in deal.intent.value_dimensions:
                component_id = f"comp_{stakeholder_id}_{dim}"
                
                # Calculate value for this dimension
                returns = deal.financing.returns_allocation.get(stakeholder_id, {}).get(dim, 0.0)
                
                # Timeline based on execution plan
                timeline = []
                for period, tasks in deal.execution.timeline.items():
                    period_value = returns / len(deal.execution.timeline) if deal.execution.timeline else returns
                    timeline.append((period, period_value))
                
                # Create value component
                value_components[component_id] = ValueComponent(
                    dimension=dim,
                    amount=returns,
                    timeline=timeline,
                    probability=1.0 - deal.solution.implementation_difficulty,
                    verification_method="execution_metrics",
                    is_quantifiable=True,
                    network_effects={}  # Will be populated below
                )
            
            # Add network effects
            for comp_id, component in value_components.items():
                # Calculate network effects between dimensions
                for other_dim in deal.intent.value_dimensions:
                    if other_dim != component.dimension:
                        # Simple heuristic: 10% spillover effect between dimensions
                        component.network_effects[other_dim] = 0.1 * component.amount
            
            # Calculate entity-specific value
            if stakeholder.type == "government":
                total_value, component_values = government_value_translation(
                    value_components, entity_profile
                )
            elif stakeholder.type == "corporate":
                total_value, component_values = corporate_value_translation(
                    value_components, entity_profile
                )
            elif stakeholder.type == "ngo":
                total_value, component_values = ngo_value_translation(
                    value_components, entity_profile
                )
            elif stakeholder.type == "civilian":
                total_value, component_values = civilian_value_translation(
                    value_components, entity_profile
                )
            else:
                # Default translation
                total_value = sum(comp.amount for comp in value_components.values())
                component_values = {
                    comp_id: comp.amount for comp_id, comp in value_components.items()
                }
            
            # Calculate time-adjusted value
            discount_rate = entity_profile.time_preference
            time_adjusted_value = 0.0
            for comp_id, component in value_components.items():
                for period, amount in component.timeline:
                    time_adjusted_value += amount / ((1 + discount_rate) ** period)
            
            # Calculate risk-adjusted value
            risk_factor = entity_profile.risk_preference
            risk_adjusted_value = total_value * (1 - risk_factor * deal.solution.implementation_difficulty)
            
            # Determine if this is a win for the entity
            costs = deal.financing.cost_allocation.get(stakeholder_id, 0.0)
            is_win = risk_adjusted_value > costs
            
            # Create entity value
            entity_values[stakeholder_id] = EntityValue(
                entity_id=stakeholder_id,
                entity_type=stakeholder.type,
                components=value_components,
                total_value=total_value,
                time_adjusted_value=time_adjusted_value,
                risk_adjusted_value=risk_adjusted_value,
                is_win=is_win,
                confidence=1.0 - deal.solution.implementation_difficulty
            )
        
        # Determine if deal is win-win
        is_win_win = all(ev.is_win for ev in entity_values.values())
        
        # Apply adjustments if requested and not win-win
        adjustments_applied = False
        if apply_adjustments and not is_win_win:
            # Identify entities that are not winning
            losing_entities = [
                entity_id for entity_id, entity_value in entity_values.items()
                if not entity_value.is_win
            ]
            
            # Apply adjustments
            for entity_id in losing_entities:
                # Get current costs and returns
                costs = deal.financing.cost_allocation.get(entity_id, 0.0)
                
                # Calculate needed value to make this a win
                entity_value = entity_values[entity_id]
                value_gap = costs - entity_value.risk_adjusted_value
                
                if value_gap > 0:
                    # Reduce costs by 50% of the gap
                    cost_reduction = value_gap * 0.5
                    new_cost = max(0.1, costs - cost_reduction)
                    
                    # Increase returns by 50% of the gap
                    returns_increase = value_gap * 0.5
                    current_returns = sum(
                        returns for dim, returns in 
                        deal.financing.returns_allocation.get(entity_id, {}).items()
                    )
                    
                    # Distribute returns increase proportionally across dimensions
                    for dim in deal.financing.returns_allocation.get(entity_id, {}):
                        current_dim_returns = deal.financing.returns_allocation[entity_id][dim]
                        proportion = current_dim_returns / current_returns if current_returns > 0 else 1.0 / len(deal.financing.returns_allocation[entity_id])
                        deal.financing.returns_allocation[entity_id][dim] += returns_increase * proportion
                    
                    # Update costs
                    deal.financing.cost_allocation[entity_id] = new_cost
                    
                    adjustments_applied = True
            
            if adjustments_applied:
                # Recalculate win-win status
                return await self.calculate_win_win_status(deal_id, False)
        
        # Update deal metrics
        deal.metrics["win_win_status"] = is_win_win
        deal.metrics["win_win_analysis"] = {
            entity_id: {
                "is_win": ev.is_win,
                "total_value": ev.total_value,
                "risk_adjusted_value": ev.risk_adjusted_value,
                "costs": deal.financing.cost_allocation.get(entity_id, 0.0)
            }
            for entity_id, ev in entity_values.items()
        }
        
        # Update the deal
        self.integrator.deals[deal_id] = deal
        
        return {
            "success": True,
            "deal_id": deal_id,
            "is_win_win": is_win_win,
            "entity_values": {
                entity_id: {
                    "is_win": ev.is_win,
                    "total_value": ev.total_value,
                    "time_adjusted_value": ev.time_adjusted_value,
                    "risk_adjusted_value": ev.risk_adjusted_value,
                    "costs": deal.financing.cost_allocation.get(entity_id, 0.0),
                    "net_value": ev.risk_adjusted_value - deal.financing.cost_allocation.get(entity_id, 0.0)
                }
                for entity_id, ev in entity_values.items()
            },
            "adjustments_applied": adjustments_applied,
            "analysis_date": datetime.datetime.now().isoformat()
        }
    
    async def create_policy_based_deal(
        self,
        agency_id: str,
        problem_statement: str,
        stakeholder_ids: List[str],
        policy_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a deal based on agency policy priorities.
        
        Args:
            agency_id: ID of the agency creating the deal
            problem_statement: Problem statement for the deal
            stakeholder_ids: List of stakeholder IDs to include
            policy_id: Optional policy ID to apply to the deal
            
        Returns:
            Deal creation results
        """
        # Ensure agency exists
        if agency_id not in self.entity_profiles:
            return {"success": False, "message": f"Agency {agency_id} not found"}
        
        # Get policy if specified
        policy = None
        if policy_id and policy_id in self.policies:
            policy = self.policies[policy_id]
        
        # Extract value dimensions from problem statement
        value_dimensions = ["economic", "social", "technological", "environmental"]
        
        # Create deal
        deal_result = await self.integrator.create_deal_from_intent(
            problem_statement=problem_statement,
            value_dimensions=value_dimensions,
            stakeholder_ids=[agency_id] + [sid for sid in stakeholder_ids if sid != agency_id]
        )
        
        if not deal_result:
            return {"success": False, "message": "Failed to create deal"}
        
        deal_id = deal_result["deal_id"]
        
        # Apply policy effects if policy specified
        policy_effects = {}
        if policy:
            if policy.policy_type == "import_certificate":
                # Apply import certificate requirements
                deal = self.integrator.deals[deal_id]
                
                # Modify financing to require certificates
                for stakeholder_id in deal.stakeholders:
                    # Check if stakeholder has certificates
                    has_certificates = self.economist.import_certificate_system.validate_import(
                        stakeholder_id, deal.financing.cost_allocation.get(stakeholder_id, 0.0)
                    )
                    
                    if not has_certificates:
                        # Reduce returns based on certificate availability
                        certificate_penalty = 0.2  # 20% reduction
                        for dim in deal.financing.returns_allocation.get(stakeholder_id, {}):
                            deal.financing.returns_allocation[stakeholder_id][dim] *= (1 - certificate_penalty)
                
                # Update deal
                self.integrator.deals[deal_id] = deal
                
                policy_effects["type"] = "import_certificate_requirements"
                policy_effects["certificate_penalty"] = 0.2
            
            elif policy.policy_type == "tariff":
                # Apply tariff effects
                tariff_rate = policy.parameters.get("tariff_rate", 0.1)
                
                deal = self.integrator.deals[deal_id]
                
                # Add tariff costs to financing
                for stakeholder_id, stakeholder in deal.stakeholders.items():
                    if stakeholder.type != "government":
                        # Calculate tariff
                        returns = sum(deal.financing.returns_allocation.get(stakeholder_id, {}).values())
                        tariff_amount = returns * tariff_rate
                        
                        # Add to costs
                        deal.financing.cost_allocation[stakeholder_id] = (
                            deal.financing.cost_allocation.get(stakeholder_id, 0.0) + tariff_amount
                        )
                        
                        # Add tariff revenue to agency
                        if agency_id in deal.financing.returns_allocation:
                            for dim in deal.financing.returns_allocation[agency_id]:
                                deal.financing.returns_allocation[agency_id][dim] *= (1 + 0.1)  # 10% boost
                
                # Update deal
                self.integrator.deals[deal_id] = deal
                
                policy_effects["type"] = "tariff_applied"
                policy_effects["tariff_rate"] = tariff_rate
        
        # Apply economic analysis
        economic_impacts = {}
        for model_id in self.economic_models:
            impact_result = await self.evaluate_deal_economic_impact(deal_id, model_id)
            if impact_result.get("success", False):
                economic_impacts[model_id] = impact_result["economic_impact"]
        
        # Check win-win status
        win_win_result = await self.calculate_win_win_status(deal_id, True)
        
        return {
            "success": True,
            "deal_id": deal_id,
            "deal_details": deal_result,
            "policy_effects": policy_effects,
            "economic_impacts": economic_impacts,
            "win_win_analysis": win_win_result.get("entity_values", {}) if win_win_result.get("success", False) else {},
            "is_win_win": win_win_result.get("is_win_win", False) if win_win_result.get("success", False) else False
        }


async def setup_agency_integration(market_integrator: MarketNetworkIntegrator) -> AgencyNetworkExtension:
    """
    Set up agency integration with the market network.
    
    Args:
        market_integrator: The market network integrator
        
    Returns:
        Configured AgencyNetworkExtension
    """
    # Create extension
    extension = AgencyNetworkExtension(market_integrator)
    
    # Register USTDA agent
    await extension.register_agency(
        agency_id="USTDA-001",
        agency_type="trade_development",
        capabilities=["policy_development", "trade_facilitation", "project_financing"],
        value_dimensions={
            "economic": 0.4,
            "diplomatic": 0.3,
            "technological": 0.2,
            "environmental": 0.1
        }
    )
    
    # Register USITC agent
    await extension.register_agency(
        agency_id="USITC-001",
        agency_type="trade_commission",
        capabilities=["economic_analysis", "trade_impact_assessment", "regulatory_compliance"],
        value_dimensions={
            "economic": 0.5,
            "legal": 0.3,
            "competitive": 0.1,
            "social": 0.1
        }
    )
    
    return extension


def test_agency_integration():
    """Run a test of the agency integration."""
    import asyncio
    from mac.economist_agent import EconomistAgent, create_economist
    from mac.market_integration import MarketNetworkIntegrator, integrate_economic_components
    
    async def run_test():
        # Create economist agent
        economist = create_economist(config_path=None)
        
        # Create market network integrator
        integrator = await integrate_economic_components(economist)
        
        # Create agency extension
        extension = await setup_agency_integration(integrator)
        
        # Create a policy-based deal
        deal_result = await extension.create_policy_based_deal(
            agency_id="USTDA-001",
            problem_statement="Develop renewable energy infrastructure with technology transfer component",
            stakeholder_ids=["developer_agent", "verification_agent"]
        )
        
        print(f"Created policy-based deal: {deal_result['deal_id']}")
        print(f"Win-Win status: {deal_result['is_win_win']}")
        
        # Evaluate with economic model
        if extension.economic_models:
            model_id = list(extension.economic_models.keys())[0]
            impact_result = await extension.evaluate_deal_economic_impact(
                deal_id=deal_result['deal_id'],
                model_id=model_id
            )
            
            print(f"Economic impact assessment: {impact_result['economic_impact']}")
        
        return deal_result
    
    # Run the test
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(run_test())
    return result


if __name__ == "__main__":
    test_result = test_agency_integration()
    print("\nTest completed successfully")
"""