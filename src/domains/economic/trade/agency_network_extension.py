"""
Agency Network Extension for the Trade Balance System.

This module implements the AgencyNetworkExtension class which connects
government agency agents (USTDA, USITC) with the market network architecture
and provides integration of policy-based deals with win-win calculations.
"""

import datetime
import uuid
from typing import Dict, List, Optional, Any, Union

from trade_balance.interfaces import (
    IAgencyNetworkExtension, IUSTDAAgent, IUSITCAgent,
    EntityProfile, ValueComponent, GovernancePolicy, EconomicModel
)
from trade_balance.ustda_agent import USTDAAgent
from trade_balance.usitc_agent import USITCAgent
from trade_balance.win_win_framework import WinWinCalculator, create_entity_profile


class AgencyNetworkExtension:
    """
    Extends the Market Network architecture to incorporate specialized 
    government agency agents (USTDA, USITC) and win-win calculation.
    """
    
    def __init__(
        self,
        market_integrator: Any,
        config_path: Optional[str] = None
    ):
        """
        Initialize the Agency Network Extension.
        
        Args:
            market_integrator: The market network integrator
            config_path: Optional path to configuration file
        """
        self._integrator = market_integrator
        self._ustda_agent = USTDAAgent()
        self._usitc_agent = USITCAgent()
        self._win_win_calculator = WinWinCalculator()
        
        # Initialize registry
        self._agencies: Dict[str, Dict[str, Any]] = {}
        self._deals: Dict[str, Dict[str, Any]] = {}
        self._stakeholders: Dict[str, EntityProfile] = {}
        
        # Load configuration if provided
        self._config: Dict[str, Any] = {}
        if config_path:
            self._load_config(config_path)
        else:
            # Default configuration
            self._config = {
                "default_optimization_constraints": {
                    "min_positive_value": 10.0,
                    "min_positive_margin": 1.0
                }
            }
    
    @property
    def integrator(self):
        """Get market network integrator."""
        return self._integrator
    
    @property
    def ustda_agent(self) -> IUSTDAAgent:
        """Get USTDA agent."""
        return self._ustda_agent
    
    @property
    def usitc_agent(self) -> IUSITCAgent:
        """Get USITC agent."""
        return self._usitc_agent
    
    def _load_config(self, config_path: str):
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
        """
        # In a real implementation, this would load from a file
        # For now, just use default configuration
        self._config = {
            "default_optimization_constraints": {
                "min_positive_value": 10.0,
                "min_positive_margin": 1.0
            }
        }
    
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
            agency_type: Type of agency
            capabilities: List of agency capabilities
            value_dimensions: Value dimension weights
            
        Returns:
            Registration result
        """
        # Create entity profile for the agency
        agency_profile = create_entity_profile(
            entity_id=agency_id,
            entity_name=f"{agency_type} Agency",
            entity_type="government",
            dimensions=value_dimensions
        )
        
        # Store in stakeholders registry
        self._stakeholders[agency_id] = agency_profile
        
        # Register with the network integrator
        attributes = {
            "type": "agency",
            "agency_type": agency_type,
            "capabilities": capabilities,
            "value_dimensions": value_dimensions
        }
        
        success = await self._integrator.add_agent(agency_id, attributes)
        
        # Store in agencies registry
        if success:
            self._agencies[agency_id] = {
                "agency_id": agency_id,
                "agency_type": agency_type,
                "capabilities": capabilities,
                "value_dimensions": value_dimensions,
                "registration_time": datetime.datetime.now().isoformat(),
                "status": "active"
            }
        
        return {
            "success": success,
            "agency_id": agency_id,
            "registered_capabilities": capabilities,
            "message": "Agency registered successfully" if success else "Failed to register agency"
        }
    
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
        # Get the policy from USTDA
        policy = self.ustda_agent.get_policy(policy_id)
        if not policy:
            return {
                "success": False,
                "error": f"Policy {policy_id} not found",
                "market_id": market_id
            }
        
        # Get market from integrator
        market = await self._integrator.get_market(market_id)
        if not market:
            return {
                "success": False,
                "error": f"Market {market_id} not found",
                "policy_id": policy_id
            }
        
        # Apply policy to market - implementation depends on policy type
        policy_effects = {}
        
        if policy.policy_type.value == "import_certificate":
            # Apply import certificate policy
            policy_effects = await self._apply_import_certificate_policy(policy, market)
        elif policy.policy_type.value == "tariff":
            # Apply tariff policy
            policy_effects = await self._apply_tariff_policy(policy, market)
        elif policy.policy_type.value == "regulatory":
            # Apply regulatory policy
            policy_effects = await self._apply_regulatory_policy(policy, market)
        elif policy.policy_type.value == "subsidy":
            # Apply subsidy policy
            policy_effects = await self._apply_subsidy_policy(policy, market)
        else:
            return {
                "success": False,
                "error": f"Unsupported policy type: {policy.policy_type.value}",
                "policy_id": policy_id,
                "market_id": market_id
            }
        
        # Return policy application results
        return {
            "success": True,
            "policy_id": policy_id,
            "market_id": market_id,
            "policy_type": policy.policy_type.value,
            "effects": policy_effects,
            "message": f"Policy {policy.title} applied to market {market_id}"
        }
    
    async def _apply_import_certificate_policy(
        self,
        policy: GovernancePolicy,
        market: Any
    ) -> Dict[str, Any]:
        """
        Apply import certificate policy to a market.
        
        Args:
            policy: The policy to apply
            market: The market to apply the policy to
            
        Returns:
            Policy effects
        """
        # Extract policy parameters
        certificate_duration = policy.parameters.get("certificate_duration", 180)
        initial_allocation = policy.parameters.get("initial_allocation", 100.0)
        transfer_fee = policy.parameters.get("transfer_fee", 0.005)
        
        # Apply to market mechanism
        # In a real implementation, this would modify market rules
        # For now, just return the effects it would have
        
        return {
            "certificate_requirement": "All imports require certificates",
            "certificate_duration": certificate_duration,
            "initial_allocation": initial_allocation,
            "transfer_fee": transfer_fee,
            "estimated_market_impact": {
                "volume_change": -0.05,  # Estimated 5% reduction in volume
                "price_change": 0.03,    # Estimated 3% increase in price
                "balance_improvement": 0.15  # Estimated 15% improvement in trade balance
            }
        }
    
    async def _apply_tariff_policy(
        self,
        policy: GovernancePolicy,
        market: Any
    ) -> Dict[str, Any]:
        """
        Apply tariff policy to a market.
        
        Args:
            policy: The policy to apply
            market: The market to apply the policy to
            
        Returns:
            Policy effects
        """
        # Extract policy parameters
        tariff_rate = policy.parameters.get("tariff_rate", 0.05)
        
        # Apply to market mechanism
        return {
            "tariff_rate": tariff_rate,
            "estimated_market_impact": {
                "volume_change": -0.07 * tariff_rate / 0.05,  # Estimated volume reduction
                "price_change": 0.05 * tariff_rate / 0.05,    # Estimated price increase
                "revenue_generation": market.get_market_price("default") * 
                                     market.get_market_volume() * tariff_rate
            }
        }
    
    async def _apply_regulatory_policy(
        self,
        policy: GovernancePolicy,
        market: Any
    ) -> Dict[str, Any]:
        """
        Apply regulatory policy to a market.
        
        Args:
            policy: The policy to apply
            market: The market to apply the policy to
            
        Returns:
            Policy effects
        """
        # Extract policy parameters
        stringency = policy.parameters.get("stringency", 0.5)
        
        # Apply to market mechanism
        return {
            "regulatory_stringency": stringency,
            "estimated_market_impact": {
                "volume_change": -0.03 * stringency,  # Estimated volume reduction
                "compliance_cost": market.get_market_volume() * 0.02 * stringency,
                "quality_improvement": 0.1 * stringency
            }
        }
    
    async def _apply_subsidy_policy(
        self,
        policy: GovernancePolicy,
        market: Any
    ) -> Dict[str, Any]:
        """
        Apply subsidy policy to a market.
        
        Args:
            policy: The policy to apply
            market: The market to apply the policy to
            
        Returns:
            Policy effects
        """
        # Extract policy parameters
        subsidy_rate = policy.parameters.get("subsidy_rate", 0.1)
        
        # Apply to market mechanism
        return {
            "subsidy_rate": subsidy_rate,
            "estimated_market_impact": {
                "volume_change": 0.05 * subsidy_rate / 0.1,  # Estimated volume increase
                "price_change": -0.03 * subsidy_rate / 0.1,  # Estimated price decrease
                "fiscal_cost": market.get_market_volume() * subsidy_rate
            }
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
        # Check if deal exists
        if deal_id not in self._deals:
            return {
                "success": False,
                "error": f"Deal {deal_id} not found"
            }
        
        deal = self._deals[deal_id]
        
        # Get the model from USITC
        model = self.usitc_agent.get_model(model_id)
        if not model:
            return {
                "success": False,
                "error": f"Model {model_id} not found"
            }
        
        # Prepare inputs for the model
        inputs = {
            "deal_id": deal_id,
            "deal_name": deal["title"],
            "value": deal["value"],
            "sectors": deal.get("sectors", []),
            "stakeholder_count": len(deal.get("stakeholders", [])),
            "timeline": deal.get("timeline", 5)  # 5-year default
        }
        
        # Run the model
        results = self.usitc_agent.run_model(model_id, inputs)
        
        # Create an assessment
        assessment_data = {
            "deal_id": deal_id,
            "title": f"Economic Impact Assessment of {deal['title']}",
            "model_id": model_id,
            "status": "completed",
            "results": results,
            "metrics": {
                "gdp_impact": results["economic_impact"]["gdp_impact"],
                "job_creation": results["economic_impact"]["job_creation"],
                "trade_balance_effect": results["economic_impact"]["trade_balance_effect"],
                "confidence_level": 1.0 - results["risk_assessment"]["risk_score"]
            }
        }
        
        assessment = self.usitc_agent.create_assessment(assessment_data)
        
        # Update deal with assessment results
        self._deals[deal_id]["economic_assessment"] = {
            "assessment_id": assessment.assessment_id,
            "results": results,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "deal_id": deal_id,
            "assessment_id": assessment.assessment_id,
            "model_id": model_id,
            "economic_impact": results["economic_impact"],
            "risk_assessment": results["risk_assessment"]
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
        # Check if deal exists
        if deal_id not in self._deals:
            return {
                "success": False,
                "error": f"Deal {deal_id} not found"
            }
        
        deal = self._deals[deal_id]
        
        # Get stakeholder profiles and value components
        entity_profiles = {}
        value_components = {}
        
        for stakeholder_id, stakeholder_data in deal.get("stakeholders", {}).items():
            # Get entity profile
            if stakeholder_id in self._stakeholders:
                entity_profiles[stakeholder_id] = self._stakeholders[stakeholder_id]
            else:
                # Create profile if not exists
                entity_profiles[stakeholder_id] = create_entity_profile(
                    entity_id=stakeholder_id,
                    entity_name=stakeholder_data.get("name", f"Entity {stakeholder_id}"),
                    entity_type=stakeholder_data.get("type", "corporate")
                )
                # Store for future use
                self._stakeholders[stakeholder_id] = entity_profiles[stakeholder_id]
            
            # Get value components
            value_components[stakeholder_id] = stakeholder_data.get("value_components", {})
        
        # Analyze for win-win status
        analysis = self._win_win_calculator.analyze_win_win_deal(entity_profiles, value_components)
        
        # If not win-win and adjustments requested, optimize value distribution
        if not analysis["is_win_win"] and apply_adjustments:
            constraints = self._config.get("default_optimization_constraints", {})
            
            # Optimize value distribution
            optimized_components = self._win_win_calculator.optimize_value_distribution(
                entity_profiles, value_components, constraints
            )
            
            # Update deal with optimized components
            for stakeholder_id, components in optimized_components.items():
                if stakeholder_id in deal.get("stakeholders", {}):
                    deal["stakeholders"][stakeholder_id]["value_components"] = components
                else:
                    # Create new stakeholder entry if needed
                    deal["stakeholders"][stakeholder_id] = {
                        "name": f"Entity {stakeholder_id}",
                        "type": "corporate" if not stakeholder_id.startswith("GOV") else "government",
                        "value_components": components
                    }
            
            # Re-analyze with optimized components
            analysis = self._win_win_calculator.analyze_win_win_deal(entity_profiles, optimized_components)
            
            # Store update in deals registry
            self._deals[deal_id] = deal
            
            return {
                "success": True,
                "deal_id": deal_id,
                "original_win_win": False,
                "optimized": True,
                "is_win_win": analysis["is_win_win"],
                "entity_values": analysis["entity_values"],
                "value_distribution": analysis["value_distribution"],
                "optimized_components": optimized_components
            }
        else:
            # Return analysis without optimization
            return {
                "success": True,
                "deal_id": deal_id,
                "is_win_win": analysis["is_win_win"],
                "entity_values": analysis["entity_values"],
                "negative_entities": analysis["negative_entities"],
                "improvement_opportunities": analysis["improvement_opportunities"],
                "value_distribution": analysis["value_distribution"]
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
        # Check if agency exists
        if agency_id not in self._agencies:
            return {
                "success": False,
                "error": f"Agency {agency_id} not found"
            }
        
        agency = self._agencies[agency_id]
        
        # Generate deal ID
        deal_id = f"DEAL-{uuid.uuid4().hex[:8]}"
        
        # Create initial deal structure
        deal = {
            "id": deal_id,
            "title": f"Policy-Based Deal: {problem_statement[:30]}...",
            "problem_statement": problem_statement,
            "lead_agency": agency_id,
            "created_at": datetime.datetime.now().isoformat(),
            "status": "draft",
            "stakeholders": {},
            "value": 0.0  # Will be calculated based on stakeholder value
        }
        
        # If policy is specified, include it
        if policy_id:
            policy = self.ustda_agent.get_policy(policy_id)
            if policy:
                deal["policy"] = {
                    "id": policy_id,
                    "title": policy.title,
                    "type": policy.policy_type.value
                }
        
        # Add stakeholders
        for stakeholder_id in stakeholder_ids:
            if stakeholder_id in self._stakeholders:
                # Use existing stakeholder
                profile = self._stakeholders[stakeholder_id]
                
                # Create empty value components
                deal["stakeholders"][stakeholder_id] = {
                    "name": profile.name,
                    "type": profile.type.value,
                    "value_components": {}
                }
            else:
                # Create placeholder for new stakeholder
                deal["stakeholders"][stakeholder_id] = {
                    "name": f"Stakeholder {stakeholder_id}",
                    "type": "corporate",  # Default type
                    "value_components": {}
                }
        
        # Get Moneyball opportunities for initial value propositions
        opportunities = self.ustda_agent.get_moneyball_opportunities()
        
        # Use opportunities to create initial value components
        if opportunities:
            # Take top opportunity
            top_opportunity = opportunities[0]
            
            # Create value components for each stakeholder
            for stakeholder_id, stakeholder_data in deal["stakeholders"].items():
                component_id = f"moneyball_{top_opportunity['sector']}_{stakeholder_id}"
                
                # Different value for different stakeholder types
                base_value = 10000.0  # Base value
                
                if stakeholder_data["type"] == "government":
                    value = base_value * 1.2  # Higher value for government
                    dimension = "economic"
                elif stakeholder_data["type"] == "corporate":
                    value = base_value * top_opportunity["growth_potential"]  # Growth-based value
                    dimension = "economic"
                elif stakeholder_data["type"] == "ngo":
                    value = base_value * top_opportunity["development_potential"]  # Development-based value
                    dimension = "social"
                else:  # civilian
                    value = base_value * 0.8  # Lower direct value
                    dimension = "economic"
                
                # Create the value component
                stakeholder_data["value_components"][component_id] = {
                    "dimension": dimension,
                    "amount": value,
                    "timeline": [(0, value * 0.2), (1, value * 0.3), (2, value * 0.5)],  # Simple timeline
                    "probability": 0.8,
                    "verification_method": "standard",
                    "is_quantifiable": True,
                    "network_effects": {}
                }
            
            # Set deal value based on top opportunity
            deal["value"] = top_opportunity["current_volume"] * top_opportunity["growth_potential"]
            deal["sectors"] = [top_opportunity["sector"]]
        
        # Store in deals registry
        self._deals[deal_id] = deal
        
        return {
            "success": True,
            "deal_id": deal_id,
            "title": deal["title"],
            "stakeholders": list(deal["stakeholders"].keys()),
            "value": deal["value"],
            "sectors": deal.get("sectors", []),
            "message": "Policy-based deal created successfully"
        }