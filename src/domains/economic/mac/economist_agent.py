"""
Economist Agent for the Multi-Agent Collaboration (MAC) Model.

This module implements the economic optimization component of the MAC architecture,
responsible for resource allocation, incentive design, and implementing the economic
model defined in econ.data to manage the economy of specialized agents.

The Economist Agent utilizes Agent-Based Computational Economics (ACE) principles
to model the multi-agent system as a complex adaptive system with dynamic agent
interactions, bounded rationality, and emergent behavior. It simulates economic
processes through agent interactions according to rules and incentives, allowing
for adaptation and learning over time without imposing equilibrium conditions.
"""

from typing import Dict, List, Any, Optional, Callable, Tuple, Set, Union, Protocol
import logging
import time
import json
import asyncio
import math
import random
import numpy as np
from uuid import uuid4
from enum import Enum
from collections import defaultdict, deque

# A2A Imports
from a2a.core import Agent, Task, TaskResult
from graph.cort_react_agent import CoRTReactAgent

# MAC Imports
from mac.environment import StateStore
from mac.verification import ExternalChecker
from mac.human_interface import HumanQueryInterface
from mac.market_models import Market, MarketType, MarketMechanism, Order, Transaction, ImportCertificateSystem
from mac.network_effects import AgentNetwork, NetworkType, EffectType, KnowledgeDiffusionModel


class ResourceType(Enum):
    """Types of resources in the economic model."""
    COMPUTE = "compute"
    MEMORY = "memory"
    TIME = "time"
    SPECIALIZED_KNOWLEDGE = "specialized_knowledge"
    HUMAN_ATTENTION = "human_attention"


class IncentiveType(Enum):
    """Types of incentives in the economic model."""
    ALLOCATION_PRIORITY = "allocation_priority"
    EXECUTION_SPEED = "execution_speed"
    QUALITY_REWARD = "quality_reward"
    COLLABORATION_BONUS = "collaboration_bonus"
    SPECIALIZATION_REWARD = "specialization_reward"


class _SimpleEconomicAgent:
    """
    A simple implementation of an economic agent for ACE simulations.
    
    This agent follows the EconomicAgent protocol and implements
    bounded rationality with adaptive learning for ACE simulations.
    """
    
    def __init__(
        self, 
        agent_id: str,
        capabilities: List[str],
        resource_needs: Dict[str, float],
        utility_weights: Dict[str, float]
    ):
        """
        Initialize a simple economic agent.
        
        Args:
            agent_id: ID of the agent
            capabilities: List of agent capabilities
            resource_needs: Dictionary of resource requirements
            utility_weights: Dictionary of utility weights for different resources
        """
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.base_resource_needs = resource_needs.copy()
        self.resource_needs = resource_needs.copy()
        self.utility_weights = utility_weights
        
        # Agent state
        self.utility = 0.0
        self.history = deque(maxlen=10)
        
        # Learning parameters
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        self.discount_factor = 0.9
        
        # Strategy parameters
        self.strategy = {
            "risk_aversion": 0.5,  # 0 = risk-seeking, 1 = risk-averse
            "cooperation": 0.5,     # 0 = competitive, 1 = cooperative
            "adaptability": 0.5,    # 0 = rigid, 1 = adaptive
            "specialization": 0.5,  # 0 = generalist, 1 = specialist
            "time_preference": 0.5  # 0 = short-term, 1 = long-term
        }
    
    def calculate_utility(self, allocation: Dict[str, float]) -> float:
        """
        Calculate agent's utility based on resource allocation.
        
        Uses a Cobb-Douglas utility function with diminishing returns.
        
        Args:
            allocation: Resource allocation to agent
            
        Returns:
            Utility value
        """
        if not allocation:
            return 0.0
        
        # Calculate utility for each resource
        resource_utilities = []
        
        for resource_type, amount in allocation.items():
            if resource_type not in self.utility_weights:
                continue
                
            # Get the need for this resource
            need = self.resource_needs.get(resource_type, 0.0)
            
            # Skip if no need
            if need == 0.0:
                continue
            
            # Calculate fulfillment ratio (with diminishing returns)
            fulfillment = min(1.0, amount / need)
            weight = self.utility_weights.get(resource_type, 0.1)
            
            # Apply diminishing returns (sqrt function)
            utility = weight * math.sqrt(fulfillment)
            resource_utilities.append(utility)
        
        # If no resources were allocated, return 0
        if not resource_utilities:
            return 0.0
        
        # Calculate total utility (sum of resource utilities)
        total_utility = sum(resource_utilities)
        
        # Store utility
        self.utility = total_utility
        
        return total_utility
    
    def make_decision(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a decision based on current state.
        
        Args:
            state: Current simulation state
            
        Returns:
            Decision dictionary
        """
        # Extract relevant state information
        resources = state.get("resources", {})
        
        # Adjust resource request based on strategy
        resource_request = {}
        
        for resource_type, need in self.resource_needs.items():
            if resource_type not in resources:
                continue
                
            # Get resource price
            price = resources[resource_type].get("price", 1.0)
            
            # Apply strategy adjustments
            
            # Risk aversion: higher risk aversion means requesting more than needed
            risk_factor = 1.0 + (self.strategy["risk_aversion"] * 0.5)
            
            # Time preference: higher time preference means requesting less now
            time_factor = 1.0 - (self.strategy["time_preference"] * 0.3)
            
            # Price sensitivity: higher prices reduce demand
            price_factor = max(0.5, 1.0 - (price - 1.0) * 0.2)
            
            # Calculate adjusted request
            adjusted_need = need * risk_factor * time_factor * price_factor
            
            # Add exploration noise (with bounded rationality)
            if random.random() < self.exploration_rate:
                noise = random.uniform(-0.2, 0.2) * adjusted_need
                adjusted_need = max(0, adjusted_need + noise)
            
            resource_request[resource_type] = adjusted_need
        
        return {
            "resource_request": resource_request,
            "strategy": self.strategy
        }
    
    def update_strategy(self, outcome: Dict[str, Any]) -> None:
        """
        Update strategy based on outcome.
        
        Args:
            outcome: Outcome of the decision
        """
        # Extract relevant outcome information
        utility = outcome.get("utility", 0.0)
        net_benefit = outcome.get("net_benefit", 0.0)
        allocation = outcome.get("allocation", {})
        
        # Store history
        self.history.append({
            "strategy": self.strategy.copy(),
            "utility": utility,
            "net_benefit": net_benefit,
            "allocation": allocation
        })
        
        # If we don't have enough history, skip update
        if len(self.history) < 2:
            return
        
        # Calculate utility change
        previous_utility = self.history[-2]["utility"]
        utility_change = utility - previous_utility
        
        # Extract previous strategy
        previous_strategy = self.history[-2]["strategy"]
        
        # For each strategy parameter, adjust based on utility change
        for param, value in self.strategy.items():
            # Calculate parameter change
            param_change = value - previous_strategy.get(param, 0.5)
            
            # If parameter change and utility change have same sign, reinforce
            if (param_change > 0 and utility_change > 0) or (param_change < 0 and utility_change < 0):
                # Positive reinforcement (move more in that direction)
                adjustment = self.learning_rate * abs(utility_change)
                if param_change > 0:
                    self.strategy[param] = min(1.0, value + adjustment)
                else:
                    self.strategy[param] = max(0.0, value - adjustment)
            else:
                # Negative reinforcement (move in opposite direction)
                adjustment = self.learning_rate * abs(utility_change)
                if param_change > 0:
                    self.strategy[param] = max(0.0, value - adjustment)
                else:
                    self.strategy[param] = min(1.0, value + adjustment)
        
        # Reduce exploration rate over time (exploitation)
        self.exploration_rate = max(0.05, self.exploration_rate * 0.99)
    
    def get_resources_needed(self) -> Dict[str, float]:
        """
        Get resources needed by the agent.
        
        Returns:
            Dictionary of resource needs
        """
        return self.resource_needs


class EconomicAgent(Protocol):
    """
    Protocol for economic agents in ACE simulations.
    
    This protocol defines the interface for agents that participate
    in the agent-based computational economics simulations.
    """
    
    def calculate_utility(self, allocation: Dict[str, float]) -> float:
        """Calculate agent's utility based on resource allocation."""
        ...
    
    def make_decision(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Make a decision based on current state."""
        ...
    
    def update_strategy(self, outcome: Dict[str, Any]) -> None:
        """Update strategy based on outcome."""
        ...
    
    def get_resources_needed(self) -> Dict[str, float]:
        """Get resources needed by the agent."""
        ...


class ACESimulation:
    """
    Agent-Based Computational Economics Simulation.
    
    This class implements a simulation environment for agent-based
    computational economics, allowing for modeling complex economic
    interactions between agents.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the ACE simulation.
        
        Args:
            config: Configuration parameters
        """
        self.config = config or {}
        self.agents = {}
        self.resources = {}
        self.state_history = deque(maxlen=self.config.get("history_length", 100))
        self.current_state = {}
        self.time_step = 0
        self.logger = logging.getLogger("MAC.ACESimulation")
    
    def add_agent(self, agent_id: str, agent: Any) -> None:
        """
        Add an agent to the simulation.
        
        Args:
            agent_id: Agent identifier
            agent: Agent instance
        """
        self.agents[agent_id] = agent
    
    def add_resource(self, resource_type: str, amount: float) -> None:
        """
        Add a resource to the simulation.
        
        Args:
            resource_type: Type of resource
            amount: Amount available
        """
        self.resources[resource_type] = {
            "total": amount,
            "available": amount,
            "price": 1.0,
            "history": deque(maxlen=self.config.get("history_length", 100))
        }
    
    def run_step(self) -> Dict[str, Any]:
        """
        Run a single simulation step.
        
        Returns:
            Current state after step
        """
        # 1. Agents observe current state
        self.current_state = self._create_current_state()
        
        # 2. Agents make decisions
        decisions = {}
        for agent_id, agent in self.agents.items():
            try:
                decisions[agent_id] = agent.make_decision(self.current_state)
            except Exception as e:
                self.logger.error(f"Error in agent {agent_id} decision making: {str(e)}")
                decisions[agent_id] = {"error": str(e)}
        
        # 3. Apply decisions to resources
        allocations = self._allocate_resources(decisions)
        
        # 4. Calculate outcomes
        outcomes = self._calculate_outcomes(decisions, allocations)
        
        # 5. Agents update strategies
        for agent_id, agent in self.agents.items():
            try:
                agent.update_strategy(outcomes.get(agent_id, {}))
            except Exception as e:
                self.logger.error(f"Error in agent {agent_id} strategy update: {str(e)}")
        
        # 6. Update prices based on supply and demand
        self._update_prices(allocations)
        
        # 7. Update state history
        self.state_history.append({
            "time_step": self.time_step,
            "state": self.current_state.copy(),
            "decisions": decisions.copy(),
            "allocations": allocations.copy(),
            "outcomes": outcomes.copy(),
            "prices": {r: self.resources[r]["price"] for r in self.resources},
        })
        
        # 8. Increment time step
        self.time_step += 1
        
        return self.current_state
    
    def run_simulation(self, steps: int) -> List[Dict[str, Any]]:
        """
        Run the simulation for a number of steps.
        
        Args:
            steps: Number of steps to run
            
        Returns:
            Simulation history
        """
        self.logger.info(f"Running ACE simulation for {steps} steps")
        
        results = []
        for _ in range(steps):
            state = self.run_step()
            results.append(state)
        
        return results
    
    def _create_current_state(self) -> Dict[str, Any]:
        """
        Create the current state of the simulation.
        
        Returns:
            Current state
        """
        return {
            "time_step": self.time_step,
            "resources": {r: {
                "available": self.resources[r]["available"],
                "price": self.resources[r]["price"]
            } for r in self.resources},
            "agents": {a: {
                "utility": getattr(self.agents[a], "utility", 0.0),
                "resources_needed": getattr(self.agents[a], "get_resources_needed", lambda: {})()
            } for a in self.agents}
        }
    
    def _allocate_resources(self, decisions: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """
        Allocate resources based on agent decisions.
        
        Args:
            decisions: Agent decisions
            
        Returns:
            Resource allocations
        """
        # Extract resource requests from decisions
        requests = {}
        for agent_id, decision in decisions.items():
            resource_request = decision.get("resource_request", {})
            requests[agent_id] = resource_request
        
        # Implement allocation algorithm (could be market-based, priority-based, etc.)
        allocations = {}
        for agent_id, request in requests.items():
            agent_allocation = {}
            
            for resource_type, amount in request.items():
                if resource_type not in self.resources:
                    continue
                    
                # Calculate how much the agent can afford and what's available
                available = self.resources[resource_type]["available"]
                allocated = min(amount, available)
                
                # Update resource
                self.resources[resource_type]["available"] -= allocated
                
                # Record allocation
                agent_allocation[resource_type] = allocated
            
            allocations[agent_id] = agent_allocation
        
        return allocations
    
    def _calculate_outcomes(
        self, 
        decisions: Dict[str, Dict[str, Any]], 
        allocations: Dict[str, Dict[str, float]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate outcomes for each agent based on decisions and allocations.
        
        Args:
            decisions: Agent decisions
            allocations: Resource allocations
            
        Returns:
            Agent outcomes
        """
        outcomes = {}
        
        for agent_id, agent in self.agents.items():
            # Calculate utility based on allocation
            try:
                utility = agent.calculate_utility(allocations.get(agent_id, {}))
            except Exception as e:
                self.logger.error(f"Error calculating utility for agent {agent_id}: {str(e)}")
                utility = 0.0
            
            # Calculate cost based on resource prices
            cost = 0.0
            for resource_type, amount in allocations.get(agent_id, {}).items():
                if resource_type in self.resources:
                    cost += amount * self.resources[resource_type]["price"]
            
            # Calculate net benefit
            net_benefit = utility - cost
            
            # Record outcome
            outcomes[agent_id] = {
                "utility": utility,
                "cost": cost,
                "net_benefit": net_benefit,
                "allocation": allocations.get(agent_id, {})
            }
        
        return outcomes
    
    def _update_prices(self, allocations: Dict[str, Dict[str, float]]) -> None:
        """
        Update resource prices based on supply and demand.
        
        Args:
            allocations: Resource allocations
        """
        for resource_type, resource in self.resources.items():
            # Calculate total demand
            demand = sum(allocation.get(resource_type, 0) for allocation in allocations.values())
            
            # Calculate supply
            supply = resource["total"]
            
            # Calculate utilization
            utilization = demand / supply if supply > 0 else 1.0
            
            # Update price using a simple supply-demand model
            # When utilization is high, price increases; when low, price decreases
            price_sensitivity = self.config.get("price_sensitivity", 0.1)
            new_price = resource["price"] * (1 + price_sensitivity * (utilization - 0.7))
            
            # Ensure price stays positive and within reasonable bounds
            new_price = max(0.1, min(10.0, new_price))
            
            # Update resource price
            resource["price"] = new_price
            resource["history"].append((self.time_step, new_price))
    
    def get_simulation_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the simulation.
        
        Returns:
            Simulation statistics
        """
        # Calculate resource utilization
        resource_stats = {}
        for resource_type, resource in self.resources.items():
            utilization = 1 - (resource["available"] / resource["total"])
            price_history = list(resource["history"])
            
            resource_stats[resource_type] = {
                "utilization": utilization,
                "price": resource["price"],
                "price_trend": self._calculate_trend([p for _, p in price_history])
            }
        
        # Calculate agent statistics
        agent_stats = {}
        for agent_id, agent in self.agents.items():
            agent_stats[agent_id] = {
                "utility": getattr(agent, "utility", 0.0),
                "resources": getattr(agent, "get_resources_needed", lambda: {})()
            }
        
        # Overall system statistics
        system_stats = {
            "efficiency": self._calculate_system_efficiency(),
            "fairness": self._calculate_system_fairness(),
            "stability": self._calculate_system_stability()
        }
        
        return {
            "time_step": self.time_step,
            "resources": resource_stats,
            "agents": agent_stats,
            "system": system_stats
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """
        Calculate trend from a series of values.
        
        Args:
            values: List of values
            
        Returns:
            Trend description
        """
        if not values or len(values) < 2:
            return "stable"
        
        # Calculate percentage change
        recent_values = values[-5:] if len(values) >= 5 else values
        first, last = recent_values[0], recent_values[-1]
        change = (last - first) / first if first != 0 else 0
        
        if change > 0.1:
            return "strongly_rising"
        elif change > 0.03:
            return "rising"
        elif change < -0.1:
            return "strongly_falling"
        elif change < -0.03:
            return "falling"
        else:
            return "stable"
    
    def _calculate_system_efficiency(self) -> float:
        """
        Calculate overall system efficiency.
        
        Returns:
            Efficiency metric [0, 1]
        """
        # Simple efficiency measure: average resource utilization
        if not self.resources:
            return 0.0
        
        total_utilization = 0.0
        for resource in self.resources.values():
            utilization = 1 - (resource["available"] / resource["total"])
            total_utilization += utilization
        
        return total_utilization / len(self.resources)
    
    def _calculate_system_fairness(self) -> float:
        """
        Calculate system fairness using Gini coefficient.
        
        Returns:
            Fairness metric [0, 1] where 1 is most fair
        """
        if not self.agents or len(self.state_history) == 0:
            return 1.0
        
        # Get the latest outcomes
        latest_state = self.state_history[-1]
        outcomes = latest_state.get("outcomes", {})
        
        # Extract utilities
        utilities = [outcomes.get(agent_id, {}).get("utility", 0.0) for agent_id in self.agents]
        
        if not utilities or sum(utilities) == 0:
            return 1.0
        
        # Calculate Gini coefficient
        utilities = sorted(utilities)
        n = len(utilities)
        numerator = sum((i+1) * x for i, x in enumerate(utilities))
        denominator = sum(utilities) * n
        gini = (2 * numerator / denominator) - (n + 1) / n if denominator > 0 else 0
        
        # Convert to fairness (1 - Gini)
        return 1 - gini
    
    def _calculate_system_stability(self) -> float:
        """
        Calculate system stability based on price volatility.
        
        Returns:
            Stability metric [0, 1] where 1 is most stable
        """
        if not self.resources or len(self.state_history) < 2:
            return 1.0
        
        # Calculate price volatility for each resource
        volatilities = []
        for resource in self.resources.values():
            price_history = [p for _, p in resource["history"]]
            if len(price_history) < 2:
                continue
            
            # Calculate average percentage change
            changes = []
            for i in range(1, len(price_history)):
                prev, curr = price_history[i-1], price_history[i]
                if prev != 0:
                    changes.append(abs(curr - prev) / prev)
            
            # Average volatility for this resource
            avg_change = sum(changes) / len(changes) if changes else 0
            volatilities.append(avg_change)
        
        if not volatilities:
            return 1.0
        
        # Overall stability is inverse of average volatility, bounded to [0, 1]
        avg_volatility = sum(volatilities) / len(volatilities)
        stability = math.exp(-5 * avg_volatility)  # Exponential decay function
        
        return stability


class EconomistAgent:
    """
    Economist Agent implementation for the MAC architecture.
    
    The Economist Agent manages resource allocation and incentives within the multi-agent system:
    1. Implementing the economic model from econ.data
    2. Allocating resources across agents based on task priorities
    3. Designing and managing incentive mechanisms to optimize system behavior
    4. Computing task value and prioritization using the Moneyball-Buffett model
    5. Tracking resource usage and performance metrics across the system
    6. Running agent-based computational economics (ACE) simulations for forecasting
    7. Adapting economic policies based on simulation outcomes
    
    This agent ensures efficient operation of the multi-agent system by applying
    economic principles to agent coordination and resource management, using ACE
    to model the system as a complex adaptive system with dynamic agent interactions,
    bounded rationality, and emergent behavior.
    """
    
    def __init__(
        self, 
        name: str = "MAC-Economist",
        supervisor_agent = None,
        coordinator_agent = None,
        state_store: Optional[StateStore] = None,
        human_interface: Optional[HumanQueryInterface] = None,
        config: Dict[str, Any] = None,
        econ_data_path: Optional[str] = None
    ):
        """
        Initialize the Economist Agent.
        
        Args:
            name: Name of the economist agent
            supervisor_agent: Reference to the SupervisorAgent
            coordinator_agent: Reference to the CoordinatorAgent
            state_store: Environment/State Store for persistent memory
            human_interface: Interface for human-in-the-loop interactions
            config: Additional configuration parameters
            econ_data_path: Path to econ.data file (optional)
        """
        self.name = name
        self.config = config or {}
        self.supervisor = supervisor_agent
        self.coordinator = coordinator_agent
        self.state_store = state_store
        self.human_interface = human_interface
        
        # Initialize economic model
        self.economic_model = {
            "resource_pool": self._initialize_resource_pool(),
            "agent_resources": {},
            "agent_performance": {},
            "task_valuations": {},
            "incentive_mechanisms": self._initialize_incentive_mechanisms(),
            "price_signals": {},
            "trade_balance": 0.0,
            "metrics": {
                "efficiency": 0.0,
                "fairness": 0.0,
                "innovation": 0.0,
                "collaboration": 0.0
            }
        }
        
        # Initialize WAR score parameters
        self.war_score_params = {
            "sector_weights": {},
            "agreement_impacts": {},
            "deficit_reduction_potentials": {}
        }
        
        # Load economic model data if path provided
        if econ_data_path:
            self._load_econ_data(econ_data_path)
        
        # Set up logging
        self.logger = logging.getLogger(f"MAC.{name}")
        self.logger.info(f"Initialized MAC Economist Agent: {name}")
        
        # Initialize tracking structures
        self.resource_allocation_history = []
        self.task_valuation_history = []
        self.agent_performance_history = []
        self.incentive_distribution_history = []
        
        # Initialize advanced market mechanisms
        self._initialize_markets()
        
        # Initialize agent network for modeling relationships
        self._initialize_agent_network()
        
        # Initialize knowledge diffusion model
        self._initialize_knowledge_model()
        
        # Integration with trading system
        self.import_certificate_system = ImportCertificateSystem(
            initial_price=1.0,
            certificate_duration=100,
            config=self.config.get("import_certificates", {})
        )
        
        # Initialize ACE simulation
        self.simulation_config = self.config.get("ace_simulation", {})
        self.ace_simulation = ACESimulation(config=self.simulation_config)
        self.simulation_history = {}
        self.simulation_forecasts = {}
        self.adaptive_policies = {}
        
        # Whether to adapt economic policies based on simulations
        self.enable_adaptive_policies = self.config.get("enable_adaptive_policies", True)
        
        # Learning rate for policy adaptation
        self.policy_learning_rate = self.config.get("policy_learning_rate", 0.1)
        
        # Initialize ACE simulation resources
        self._initialize_ace_simulation()
        
        self.logger.info("Initialized ACE simulation capabilities")
    
    def _initialize_markets(self) -> None:
        """Initialize markets for different resource types."""
        self.markets = {}
        
        # Create resource markets
        for resource_type in ResourceType.__members__.values():
            market_id = f"market_{resource_type.value}"
            self.markets[resource_type.value] = Market(
                market_id=market_id,
                market_type=MarketType.RESOURCE_MARKET,
                asset_type=resource_type.value,
                mechanism=MarketMechanism.CONTINUOUS_DOUBLE_AUCTION,
                config={
                    "history_length": 100,
                    "price_sensitivity": 0.1
                }
            )
        
        # Create task market
        self.markets["task"] = Market(
            market_id="market_task",
            market_type=MarketType.TASK_MARKET,
            asset_type="task",
            mechanism=MarketMechanism.NEGOTIATION,
            config={
                "history_length": 100,
                "bargaining_steps": 5
            }
        )
        
        # Create knowledge market
        self.markets["knowledge"] = Market(
            market_id="market_knowledge",
            market_type=MarketType.KNOWLEDGE_MARKET,
            asset_type="knowledge",
            mechanism=MarketMechanism.DEALER,
            config={
                "history_length": 100,
                "dealer_spread": 0.1
            }
        )
        
        self.logger.info(f"Initialized {len(self.markets)} markets for economic simulation")
    
    def _initialize_agent_network(self) -> None:
        """Initialize the agent relationship network."""
        self.agent_network = AgentNetwork(
            network_id=f"{self.name}_network",
            network_type=NetworkType.SCALE_FREE,
            config={
                "initial_nodes": 10,
                "new_edges": 2
            }
        )
        
        # Add network effects
        self.agent_network.add_network_effect(
            effect_id="collaboration_effect",
            effect_type=EffectType.DIRECT,
            strength=0.3,
            config={
                "resource_types": ["specialized_knowledge", "compute"],
                "model": "metcalfe"
            }
        )
        
        self.agent_network.add_network_effect(
            effect_id="learning_effect",
            effect_type=EffectType.LEARNING,
            strength=0.2,
            config={
                "resource_types": ["specialized_knowledge"],
                "knowledge_attribute": "knowledge_level",
                "learning_rate": 0.1
            }
        )
        
        self.agent_network.add_network_effect(
            effect_id="congestion_effect",
            effect_type=EffectType.CONGESTION,
            strength=0.2,
            config={
                "resource_types": ["compute", "memory"],
                "compute_capacity": 1000.0,
                "memory_capacity": 2000.0,
                "congestion_threshold": 0.7
            }
        )
        
        self.logger.info("Initialized agent network with network effects")
    
    def _initialize_knowledge_model(self) -> None:
        """Initialize the knowledge diffusion model."""
        self.knowledge_model = KnowledgeDiffusionModel(
            network=self.agent_network,
            config={
                "learning_rates": {
                    "default": 0.1
                }
            }
        )
        
        # Add knowledge domains
        self.knowledge_model.add_knowledge_domain(
            domain_id="architecture",
            complexity=0.7
        )
        
        self.knowledge_model.add_knowledge_domain(
            domain_id="development",
            complexity=0.5,
            prerequisites=["architecture"]
        )
        
        self.knowledge_model.add_knowledge_domain(
            domain_id="verification",
            complexity=0.6,
            prerequisites=["development"]
        )
        
        self.knowledge_model.add_knowledge_domain(
            domain_id="coordination",
            complexity=0.4
        )
        
        self.knowledge_model.add_knowledge_domain(
            domain_id="economic_optimization",
            complexity=0.8
        )
        
        self.logger.info("Initialized knowledge diffusion model with domains")
        
    def _initialize_ace_simulation(self) -> None:
        """Initialize the ACE simulation with resources and default economic agents."""
        # Add resources to simulation
        for resource_type, resource_data in self.economic_model["resource_pool"].items():
            self.ace_simulation.add_resource(
                resource_type=resource_type,
                amount=resource_data["total"]
            )
        
        # Other initialization for ACE will be done when agents are registered
    
    def _initialize_resource_pool(self) -> Dict[str, Any]:
        """
        Initialize the resource pool based on default allocations.
        
        Returns:
            Dictionary with resource pool configuration
        """
        return {
            ResourceType.COMPUTE.value: {
                "total": 1000.0,
                "available": 1000.0,
                "unit_cost": 0.1,
                "allocation_strategy": "priority_based"
            },
            ResourceType.MEMORY.value: {
                "total": 2000.0,
                "available": 2000.0,
                "unit_cost": 0.05,
                "allocation_strategy": "fair_share"
            },
            ResourceType.TIME.value: {
                "total": 10000.0,  # in seconds
                "available": 10000.0,
                "unit_cost": 0.01,
                "allocation_strategy": "deadline_based"
            },
            ResourceType.SPECIALIZED_KNOWLEDGE.value: {
                "total": 500.0,
                "available": 500.0,
                "unit_cost": 0.5,
                "allocation_strategy": "expertise_based"
            },
            ResourceType.HUMAN_ATTENTION.value: {
                "total": 100.0,
                "available": 100.0,
                "unit_cost": 2.0,
                "allocation_strategy": "critical_tasks_only"
            }
        }
    
    def _initialize_incentive_mechanisms(self) -> Dict[str, Any]:
        """
        Initialize incentive mechanisms for the system.
        
        Returns:
            Dictionary with incentive mechanism configuration
        """
        return {
            IncentiveType.ALLOCATION_PRIORITY.value: {
                "weight": 0.3,
                "formula": "priority_score = task_value * 0.7 + agent_performance * 0.3",
                "triggers": ["task_completion", "resource_request"]
            },
            IncentiveType.EXECUTION_SPEED.value: {
                "weight": 0.2,
                "formula": "speed_bonus = baseline * (1 + completion_time_ratio)",
                "triggers": ["task_completion"]
            },
            IncentiveType.QUALITY_REWARD.value: {
                "weight": 0.25,
                "formula": "quality_score = verification_score * 0.8 + review_score * 0.2",
                "triggers": ["verification_complete", "human_review"]
            },
            IncentiveType.COLLABORATION_BONUS.value: {
                "weight": 0.15,
                "formula": "collab_bonus = base_reward * num_collaborators * 0.1",
                "triggers": ["task_completion"]
            },
            IncentiveType.SPECIALIZATION_REWARD.value: {
                "weight": 0.1,
                "formula": "spec_reward = base_reward * expertise_level * 0.2",
                "triggers": ["task_completion"]
            }
        }
    
    def _load_econ_data(self, econ_data_path: str) -> None:
        """
        Load and parse the economic model from econ.data.
        
        Args:
            econ_data_path: Path to the econ.data file
        """
        try:
            # In a real implementation, this would parse the economic model
            # defined in the econ.data file, which appears to be a large document
            # describing economic principles, formulas, and models
            
            # For now, we'll set up some default parameters based on what we can see
            # from the initial portion of econ.data
            
            # Initialize WAR score parameters
            self.war_score_params = {
                "sector_weights": {
                    "development": 0.4,
                    "operations": 0.3,
                    "governance": 0.2,
                    "research": 0.1
                },
                "agreement_impacts": {
                    "high": 100,
                    "medium": 50,
                    "low": 25,
                    "neutral": 0,
                    "negative_low": -25,
                    "negative_medium": -50,
                    "negative_high": -100
                },
                "deficit_reduction_potentials": {
                    "high": 1.0,
                    "medium": 0.7,
                    "low": 0.4,
                    "minimal": 0.1
                }
            }
            
            # Initialize DRP parameters with a default margin of safety
            self.drp_params = {
                "margin_of_safety": 0.8,  # Buffett-style conservative factor
                "confidence_weights": {
                    "high": 0.9,
                    "medium": 0.7,
                    "low": 0.5,
                    "experimental": 0.3
                },
                "implementation_rates": {
                    "high": 0.95,
                    "medium": 0.8,
                    "low": 0.6,
                    "experimental": 0.4
                }
            }
            
            # Initialize SPS parameters
            self.sps_params = {
                "deficit_weight": 0.4,
                "jobs_weight": 0.3,
                "growth_weight": 0.2,
                "ease_weight": 0.1
            }
            
            # Initialize Deal Value Function parameters
            self.dvf_params = {
                "intrinsic_value_weight": 0.5,
                "probability_weight": 0.2,
                "confidence_weight": 0.15,
                "margin_of_safety_weight": 0.15,
                "transaction_cost_factor": 0.1
            }
            
            self.logger.info(f"Loaded economic model parameters from {econ_data_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading economic model from {econ_data_path}: {str(e)}")
    
    async def register_agent(self, agent_id: str, capabilities: List[str], resource_needs: Dict[str, float]) -> Dict[str, Any]:
        """
        Register an agent with the economic system.
        
        Args:
            agent_id: ID of the agent
            capabilities: List of agent capabilities
            resource_needs: Dictionary of resource requirements
            
        Returns:
            Registration information
        """
        # Initialize agent's resource allocation
        self.economic_model["agent_resources"][agent_id] = {
            resource_type: {
                "allocated": 0.0,
                "used": 0.0,
                "efficiency": 1.0,
                "needs": resource_needs.get(resource_type, 0.0)
            }
            for resource_type in ResourceType.__members__.values()
        }
        
        # Initialize agent's performance metrics
        self.economic_model["agent_performance"][agent_id] = {
            "task_completion_rate": 1.0,
            "quality_score": 0.9,
            "efficiency_score": 1.0,
            "collaboration_score": 0.8,
            "specialization_level": 1.0,
            "tasks_completed": 0,
            "total_value_created": 0.0
        }
        
        # Register with import certificate system
        cert = self.import_certificate_system.issue_certificate(
            agent_id=agent_id, 
            export_value=100.0  # Initial allocation
        )
        
        # Register agent with ACE simulation
        self._register_ace_agent(agent_id, capabilities, resource_needs)
        
        # Add agent to the network
        self.agent_network.add_agent(
            agent_id=agent_id,
            attributes={
                "capabilities": capabilities,
                "resource_needs": resource_needs,
                "knowledge_level": 0.3,  # Initial knowledge level
                "strategy": "balanced",  # Default strategy
                "cluster": random.randint(0, 3)  # Random cluster assignment
            }
        )
        
        # Initialize agent's knowledge
        knowledge_domains = {}
        
        # Set initial knowledge based on capabilities
        if "architecture_design" in capabilities:
            knowledge_domains["architecture"] = 0.7
        else:
            knowledge_domains["architecture"] = 0.2
            
        if "code_generation" in capabilities:
            knowledge_domains["development"] = 0.6
        else:
            knowledge_domains["development"] = 0.2
            
        if "verification" in capabilities:
            knowledge_domains["verification"] = 0.6
        else:
            knowledge_domains["verification"] = 0.1
            
        if "coordination" in capabilities:
            knowledge_domains["coordination"] = 0.8
        else:
            knowledge_domains["coordination"] = 0.3
            
        if "economic_analysis" in capabilities:
            knowledge_domains["economic_optimization"] = 0.7
        else:
            knowledge_domains["economic_optimization"] = 0.1
        
        # Register with knowledge model
        self.knowledge_model.initialize_agent_knowledge(
            agent_id=agent_id,
            domains=knowledge_domains,
            learning_rate=0.1
        )
        
        self.logger.info(f"Registered agent {agent_id} with the economic system")
        
        return {
            "agent_id": agent_id,
            "resource_allocation": self.economic_model["agent_resources"][agent_id],
            "import_certificates": cert["value"],
            "knowledge_levels": knowledge_domains,
            "network_position": {
                "neighbors": len(self.agent_network.get_neighbors(agent_id)),
                "centrality": list(self.agent_network.calculate_centrality().get(agent_id, 0.0))
            }
        }
        
    def _register_ace_agent(self, agent_id: str, capabilities: List[str], resource_needs: Dict[str, float]) -> None:
        """
        Register an agent with the ACE simulation.
        
        Args:
            agent_id: ID of the agent
            capabilities: List of agent capabilities
            resource_needs: Dictionary of resource requirements
        """
        # Create a simple economic agent that follows the protocol
        ace_agent = _SimpleEconomicAgent(
            agent_id=agent_id,
            capabilities=capabilities,
            resource_needs=resource_needs,
            utility_weights=self._calculate_utility_weights(capabilities)
        )
        
        # Add agent to simulation
        self.ace_simulation.add_agent(agent_id, ace_agent)
        
    def _calculate_utility_weights(self, capabilities: List[str]) -> Dict[str, float]:
        """
        Calculate utility weights based on agent capabilities.
        
        Args:
            capabilities: List of agent capabilities
            
        Returns:
            Dictionary of utility weights for different resources
        """
        # Default weights
        weights = {
            ResourceType.COMPUTE.value: 0.3,
            ResourceType.MEMORY.value: 0.3,
            ResourceType.TIME.value: 0.2,
            ResourceType.SPECIALIZED_KNOWLEDGE.value: 0.1,
            ResourceType.HUMAN_ATTENTION.value: 0.1
        }
        
        # Adjust weights based on capabilities
        if "code_generation" in capabilities or "architecture_design" in capabilities:
            # Development agents value compute more
            weights[ResourceType.COMPUTE.value] = 0.4
            weights[ResourceType.MEMORY.value] = 0.3
            
        if "infrastructure_management" in capabilities or "deployment" in capabilities:
            # Operations agents value memory more
            weights[ResourceType.MEMORY.value] = 0.4
            weights[ResourceType.COMPUTE.value] = 0.3
            
        if "policy_enforcement" in capabilities or "compliance_assessment" in capabilities:
            # Governance agents value specialized knowledge more
            weights[ResourceType.SPECIALIZED_KNOWLEDGE.value] = 0.3
            weights[ResourceType.COMPUTE.value] = 0.2
            weights[ResourceType.MEMORY.value] = 0.2
            
        return weights
    
    async def allocate_resources(self, task_id: str, agent_id: str, resource_requests: Dict[str, float]) -> Dict[str, Any]:
        """
        Allocate resources to an agent for a specific task.
        
        Args:
            task_id: ID of the task
            agent_id: ID of the agent
            resource_requests: Dictionary of requested resources
            
        Returns:
            Allocation information
        """
        if agent_id not in self.economic_model["agent_resources"]:
            raise ValueError(f"Agent {agent_id} not registered with the economic system")
        
        # Calculate task value if not already done
        if task_id not in self.economic_model["task_valuations"]:
            await self.calculate_task_value(task_id)
        
        task_value = self.economic_model["task_valuations"][task_id]["total_value"]
        
        # Initialize allocation result
        allocation_result = {
            "task_id": task_id,
            "agent_id": agent_id,
            "allocations": {},
            "total_cost": 0.0,
            "allocation_score": 0.0
        }
        
        # Allocate each requested resource
        for resource_type, requested_amount in resource_requests.items():
            if resource_type not in self.economic_model["resource_pool"]:
                self.logger.warning(f"Resource type {resource_type} not recognized, skipping")
                continue
            
            resource_pool = self.economic_model["resource_pool"][resource_type]
            available = resource_pool["available"]
            
            # Calculate allocation based on task value and resource availability
            allocation_strategy = resource_pool["allocation_strategy"]
            allocation_amount = self._calculate_allocation(
                resource_type=resource_type,
                requested_amount=requested_amount,
                available_amount=available,
                task_value=task_value,
                agent_id=agent_id,
                allocation_strategy=allocation_strategy
            )
            
            # Update resource pool
            resource_pool["available"] -= allocation_amount
            
            # Update agent's resources
            self.economic_model["agent_resources"][agent_id][resource_type]["allocated"] += allocation_amount
            
            # Calculate cost
            cost = allocation_amount * resource_pool["unit_cost"]
            allocation_result["total_cost"] += cost
            
            # Add to result
            allocation_result["allocations"][resource_type] = {
                "requested": requested_amount,
                "allocated": allocation_amount,
                "unit_cost": resource_pool["unit_cost"],
                "cost": cost
            }
        
        # Calculate overall allocation score (how well needs were met)
        if resource_requests:
            total_requested = sum(resource_requests.values())
            total_allocated = sum(allocation["allocated"] for allocation in allocation_result["allocations"].values())
            allocation_result["allocation_score"] = total_allocated / total_requested if total_requested > 0 else 1.0
        else:
            allocation_result["allocation_score"] = 1.0
        
        # Record allocation history
        self.resource_allocation_history.append({
            "timestamp": time.time(),
            "task_id": task_id,
            "agent_id": agent_id,
            "allocation_result": allocation_result
        })
        
        # Update state store if available
        if self.state_store:
            self.state_store.record_resource_allocation(
                task_id=task_id,
                agent_id=agent_id,
                allocation=allocation_result
            )
        
        self.logger.info(f"Allocated resources for task {task_id} to agent {agent_id} with score {allocation_result['allocation_score']:.2f}")
        
        return allocation_result
    
    def _calculate_allocation(
        self, 
        resource_type: str, 
        requested_amount: float,
        available_amount: float,
        task_value: float,
        agent_id: str,
        allocation_strategy: str
    ) -> float:
        """
        Calculate resource allocation based on the specified strategy.
        
        Args:
            resource_type: Type of resource
            requested_amount: Amount requested
            available_amount: Amount available in the pool
            task_value: Value of the task
            agent_id: ID of the requesting agent
            allocation_strategy: Allocation strategy to use
            
        Returns:
            Amount to allocate
        """
        # Default to giving what was requested if available
        base_allocation = min(requested_amount, available_amount)
        
        # Apply strategy-specific adjustments
        if allocation_strategy == "priority_based":
            # Higher value tasks get closer to their requested amount
            priority_factor = min(1.0, task_value / 100.0)
            return base_allocation * (0.5 + 0.5 * priority_factor)
            
        elif allocation_strategy == "fair_share":
            # Everyone gets an equal share of the resource pool
            agent_count = len(self.economic_model["agent_resources"])
            fair_share = self.economic_model["resource_pool"][resource_type]["total"] / max(1, agent_count)
            already_allocated = self.economic_model["agent_resources"][agent_id][resource_type]["allocated"]
            fair_allocation = max(0, min(base_allocation, fair_share - already_allocated))
            return fair_allocation
            
        elif allocation_strategy == "deadline_based":
            # Time-critical tasks get more resources
            task_urgency = self.economic_model["task_valuations"].get(
                agent_id, {}).get("urgency", 0.5)
            return base_allocation * (0.7 + 0.3 * task_urgency)
            
        elif allocation_strategy == "expertise_based":
            # Agents with higher specialization in the task area get more knowledge resources
            specialization = self.economic_model["agent_performance"][agent_id]["specialization_level"]
            return base_allocation * (0.6 + 0.4 * specialization)
            
        elif allocation_strategy == "critical_tasks_only":
            # Human attention only goes to the most valuable/critical tasks
            if task_value > 80:  # Critical threshold
                return base_allocation
            else:
                return base_allocation * (task_value / 80)
        
        # Default fallback
        return base_allocation
    
    async def calculate_task_value(self, task_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate the economic value of a task using the Moneyball-Buffett model.
        
        Args:
            task_id: ID of the task to evaluate
            metadata: Additional task metadata
            
        Returns:
            Task valuation result
        """
        # Get task from state store if available
        task = None
        if self.state_store:
            task = await self.state_store.get_task(task_id)
        
        # Extract task information
        task_info = metadata or {}
        if task:
            task_info.update(task)
        
        # Initialize valuation result
        valuation = {
            "task_id": task_id,
            "base_value": 50.0,  # Default midpoint value
            "war_score": 0.0,    # Weighted Agreement Return
            "drp": 0.0,          # Deficit Reduction Potential
            "sps": 0.0,          # Sector Prioritization Score
            "modifiers": {},
            "total_value": 0.0,
            "confidence": 0.8,
            "timestamp": time.time()
        }
        
        # Extract domain and task complexity
        domain = task_info.get("domain", "default")
        complexity = task_info.get("complexity", "medium")
        
        # Calculate WAR score (Weighted Agreement Return)
        war_score = self._calculate_war_score(task_info)
        
        # Calculate DRP (Deficit Reduction Potential)
        drp = self._calculate_drp(task_info)
        
        # Calculate SPS (Sector Prioritization Score)
        sps = self._calculate_sps(task_info)
        
        # Apply base value modifications
        base_modifiers = {
            "domain_priority": self.war_score_params["sector_weights"].get(domain, 0.25),
            "complexity_factor": {"low": 0.8, "medium": 1.0, "high": 1.2, "very_high": 1.4}.get(complexity, 1.0),
            "war_score_impact": (war_score / 100.0) * 0.3,  # WAR score influence (30%)
            "drp_impact": (drp / 100.0) * 0.4,              # DRP influence (40%)
            "sps_impact": (sps / 100.0) * 0.3               # SPS influence (30%)
        }
        
        # Calculate total value
        modified_value = valuation["base_value"]
        for modifier_name, modifier_value in base_modifiers.items():
            if modifier_name in ["war_score_impact", "drp_impact", "sps_impact"]:
                modified_value += valuation["base_value"] * modifier_value
            else:
                modified_value *= modifier_value
        
        # Record scores
        valuation["war_score"] = war_score
        valuation["drp"] = drp
        valuation["sps"] = sps
        valuation["modifiers"] = base_modifiers
        valuation["total_value"] = modified_value
        
        # Store valuation in economic model
        self.economic_model["task_valuations"][task_id] = valuation
        
        # Record valuation history
        self.task_valuation_history.append({
            "timestamp": time.time(),
            "task_id": task_id,
            "valuation": valuation
        })
        
        # Update state store if available
        if self.state_store:
            self.state_store.record_task_valuation(task_id, valuation)
        
        self.logger.info(f"Calculated task value for {task_id}: {valuation['total_value']:.2f}")
        
        return valuation
    
    def _calculate_war_score(self, task_info: Dict[str, Any]) -> float:
        """
        Calculate the Weighted Agreement Return (WAR) score.
        
        WAR = ∑(wi * ai * di)
        
        where:
        - wi: Sector weight
        - ai: Agreement impact [-100, 100]
        - di: Deficit reduction potential [0, 1]
        
        Args:
            task_info: Task information
            
        Returns:
            WAR score
        """
        domain = task_info.get("domain", "default")
        impact = task_info.get("impact", "medium")
        deficit_reduction = task_info.get("deficit_reduction", "medium")
        
        # Get parameters
        sector_weight = self.war_score_params["sector_weights"].get(domain, 0.25)
        agreement_impact = self.war_score_params["agreement_impacts"].get(impact, 50)
        drp_factor = self.war_score_params["deficit_reduction_potentials"].get(deficit_reduction, 0.7)
        
        # Calculate WAR score
        war_score = sector_weight * agreement_impact * drp_factor
        
        # Normalize to range [-100, 100]
        normalized_war = max(-100, min(100, war_score * 100))
        
        return normalized_war
    
    def _calculate_drp(self, task_info: Dict[str, Any]) -> float:
        """
        Calculate the Deficit Reduction Potential (DRP).
        
        DRP = B - ∑(pi * ci * ri) * M
        
        where:
        - B: Baseline deficit
        - pi: Policy effect
        - ci: Confidence
        - ri: Implementation rate
        - M: Margin of safety factor [0, 1]
        
        Args:
            task_info: Task information
            
        Returns:
            DRP score [0, 100]
        """
        # For simplicity, we'll use a simplified calculation
        baseline = 100  # Maximum potential
        
        policy_effect = {"high": 0.8, "medium": 0.5, "low": 0.3}.get(
            task_info.get("effect", "medium"), 0.5)
        
        confidence = self.drp_params["confidence_weights"].get(
            task_info.get("confidence", "medium"), 0.7)
        
        implementation_rate = self.drp_params["implementation_rates"].get(
            task_info.get("implementation_likelihood", "medium"), 0.8)
        
        margin_of_safety = self.drp_params["margin_of_safety"]
        
        # Calculate DRP
        reduction = policy_effect * confidence * implementation_rate
        drp = baseline - (baseline * reduction * margin_of_safety)
        
        # Normalize to range [0, 100]
        normalized_drp = max(0, min(100, 100 - drp))
        
        return normalized_drp
    
    def _calculate_sps(self, task_info: Dict[str, Any]) -> float:
        """
        Calculate the Sector Prioritization Score (SPS).
        
        SPS = 0.4*D + 0.3*J + 0.2*G + 0.1*E
        
        where:
        - D: Deficit impact
        - J: Jobs impact
        - G: Growth impact
        - E: Ease of implementation
        
        Args:
            task_info: Task information
            
        Returns:
            SPS score [0, 100]
        """
        # Extract impact factors from task info or use defaults
        deficit_impact = {"high": 90, "medium": 60, "low": 30}.get(
            task_info.get("deficit_impact", "medium"), 60)
        
        jobs_impact = {"high": 90, "medium": 60, "low": 30}.get(
            task_info.get("jobs_impact", "medium"), 60)
        
        growth_impact = {"high": 90, "medium": 60, "low": 30}.get(
            task_info.get("growth_impact", "medium"), 60)
        
        ease = {"high": 90, "medium": 60, "low": 30}.get(
            task_info.get("ease", "medium"), 60)
        
        # Calculate SPS
        sps = (
            self.sps_params["deficit_weight"] * deficit_impact +
            self.sps_params["jobs_weight"] * jobs_impact +
            self.sps_params["growth_weight"] * growth_impact +
            self.sps_params["ease_weight"] * ease
        )
        
        # Ensure it's in range [0, 100]
        normalized_sps = max(0, min(100, sps))
        
        return normalized_sps
    
    async def update_agent_performance(self, agent_id: str, task_id: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an agent's performance metrics based on task execution.
        
        Args:
            agent_id: ID of the agent
            task_id: ID of the completed task
            performance_data: Task performance metrics
            
        Returns:
            Updated performance metrics
        """
        if agent_id not in self.economic_model["agent_performance"]:
            raise ValueError(f"Agent {agent_id} not registered with the economic system")
        
        agent_perf = self.economic_model["agent_performance"][agent_id]
        
        # Extract performance metrics
        completion_status = performance_data.get("status", "completed")
        quality_score = performance_data.get("quality_score", 0.9)
        execution_time = performance_data.get("execution_time", 100.0)
        expected_time = performance_data.get("expected_time", 100.0)
        collaboration = performance_data.get("collaboration_score", 0.8)
        
        # Get task value
        task_value = 50.0  # Default value
        if task_id in self.economic_model["task_valuations"]:
            task_value = self.economic_model["task_valuations"][task_id]["total_value"]
        
        # Update metrics
        if completion_status == "completed":
            # Successful completion
            agent_perf["tasks_completed"] += 1
            agent_perf["total_value_created"] += task_value
            
            # Update completion rate (use exponential moving average)
            alpha = 0.3  # Weighting for new data
            agent_perf["task_completion_rate"] = (
                (1 - alpha) * agent_perf["task_completion_rate"] + alpha * 1.0
            )
            
            # Update quality score
            agent_perf["quality_score"] = (
                (1 - alpha) * agent_perf["quality_score"] + alpha * quality_score
            )
            
            # Update efficiency score based on execution time vs. expected time
            efficiency = expected_time / execution_time if execution_time > 0 else 1.0
            efficiency = min(2.0, max(0.5, efficiency))  # Cap between 0.5 and 2.0
            agent_perf["efficiency_score"] = (
                (1 - alpha) * agent_perf["efficiency_score"] + alpha * efficiency
            )
            
            # Update collaboration score
            agent_perf["collaboration_score"] = (
                (1 - alpha) * agent_perf["collaboration_score"] + alpha * collaboration
            )
            
            # Update specialization level based on task domain
            task_domain = performance_data.get("domain", "default")
            if task_domain in agent_perf.get("domain_expertise", {}):
                # Enhance expertise in this domain
                agent_perf.setdefault("domain_expertise", {})[task_domain] = (
                    agent_perf["domain_expertise"][task_domain] * 0.9 + 0.1
                )
                # Recalculate overall specialization level
                agent_perf["specialization_level"] = max(
                    agent_perf.get("domain_expertise", {}).values()
                ) if agent_perf.get("domain_expertise") else 1.0
        else:
            # Failed completion
            alpha = 0.2  # Lower impact of failures
            agent_perf["task_completion_rate"] = (
                (1 - alpha) * agent_perf["task_completion_rate"] + alpha * 0.0
            )
        
        # Record performance update
        self.agent_performance_history.append({
            "timestamp": time.time(),
            "agent_id": agent_id,
            "task_id": task_id,
            "performance_update": agent_perf.copy()
        })
        
        # Update state store if available
        if self.state_store:
            self.state_store.update_agent_performance(agent_id, agent_perf)
        
        self.logger.info(f"Updated performance metrics for agent {agent_id} after task {task_id}")
        
        return agent_perf
    
    async def distribute_incentives(self, agent_id: str, task_id: str) -> Dict[str, Any]:
        """
        Calculate and distribute incentives to an agent based on task performance.
        
        Args:
            agent_id: ID of the agent
            task_id: ID of the completed task
            
        Returns:
            Incentive distribution result
        """
        if agent_id not in self.economic_model["agent_performance"]:
            raise ValueError(f"Agent {agent_id} not registered with the economic system")
        
        # Get agent performance
        agent_perf = self.economic_model["agent_performance"][agent_id]
        
        # Get task valuation
        task_value = 50.0  # Default value
        if task_id in self.economic_model["task_valuations"]:
            task_value = self.economic_model["task_valuations"][task_id]["total_value"]
        
        # Initialize incentives
        incentives = {
            "task_id": task_id,
            "agent_id": agent_id,
            "base_reward": task_value,
            "incentives": {},
            "total_reward": 0.0
        }
        
        # Calculate each incentive type
        for incentive_type, mechanism in self.economic_model["incentive_mechanisms"].items():
            incentive_value = 0.0
            
            if incentive_type == IncentiveType.ALLOCATION_PRIORITY.value:
                # Priority bonus based on task value and agent performance
                incentive_value = task_value * 0.1 * (
                    0.7 * (task_value / 100.0) + 
                    0.3 * agent_perf["efficiency_score"]
                )
                
            elif incentive_type == IncentiveType.EXECUTION_SPEED.value:
                # Speed bonus based on efficiency
                speed_factor = agent_perf["efficiency_score"]
                incentive_value = task_value * 0.05 * (1 + max(0, speed_factor - 1.0))
                
            elif incentive_type == IncentiveType.QUALITY_REWARD.value:
                # Quality reward based on quality score
                incentive_value = task_value * 0.1 * agent_perf["quality_score"]
                
            elif incentive_type == IncentiveType.COLLABORATION_BONUS.value:
                # Collaboration bonus
                collab_factor = agent_perf["collaboration_score"]
                collaborator_count = 1  # Default if not available
                incentive_value = task_value * 0.05 * collab_factor * collaborator_count * 0.1
                
            elif incentive_type == IncentiveType.SPECIALIZATION_REWARD.value:
                # Specialization reward
                spec_level = agent_perf["specialization_level"]
                incentive_value = task_value * 0.05 * spec_level * 0.2
            
            # Add to incentives
            incentives["incentives"][incentive_type] = incentive_value
            incentives["total_reward"] += incentive_value
        
        # Add base reward
        incentives["total_reward"] += incentives["base_reward"]
        
        # Update import certificates (reward)
        if agent_id in self.import_certificates:
            self.import_certificates[agent_id]["earned"] += incentives["total_reward"]
            self.import_certificates[agent_id]["available"] += incentives["total_reward"]
        
        # Record incentive distribution
        self.incentive_distribution_history.append({
            "timestamp": time.time(),
            "agent_id": agent_id,
            "task_id": task_id,
            "incentives": incentives
        })
        
        # Update state store if available
        if self.state_store:
            self.state_store.record_incentive_distribution(agent_id, task_id, incentives)
        
        self.logger.info(f"Distributed incentives to agent {agent_id} for task {task_id}: {incentives['total_reward']:.2f}")
        
        return incentives
    
    async def trade_certificates(self, buying_agent_id: str, selling_agent_id: str, quantity: float) -> Dict[str, Any]:
        """
        Execute a trade of import certificates between agents.
        
        Args:
            buying_agent_id: ID of the agent buying certificates
            selling_agent_id: ID of the agent selling certificates
            quantity: Quantity of certificates to trade
            
        Returns:
            Trade execution result
        """
        if buying_agent_id not in self.import_certificates:
            raise ValueError(f"Buying agent {buying_agent_id} not registered with the certificate system")
        
        if selling_agent_id not in self.import_certificates:
            raise ValueError(f"Selling agent {selling_agent_id} not registered with the certificate system")
        
        # Check if seller has enough certificates
        seller_certs = self.import_certificates[selling_agent_id]
        if seller_certs["available"] < quantity:
            raise ValueError(f"Selling agent {selling_agent_id} has insufficient certificates ({seller_certs['available']} < {quantity})")
        
        # Calculate current certificate price
        price = self._calculate_certificate_price()
        trade_value = price * quantity
        
        # Execute the trade
        self.import_certificates[selling_agent_id]["available"] -= quantity
        self.import_certificates[buying_agent_id]["available"] += quantity
        
        # Record the trade
        trade = {
            "timestamp": time.time(),
            "buying_agent": buying_agent_id,
            "selling_agent": selling_agent_id,
            "quantity": quantity,
            "price": price,
            "total_value": trade_value
        }
        
        self.trade_history.append(trade)
        
        # Update state store if available
        if self.state_store:
            self.state_store.record_certificate_trade(trade)
        
        self.logger.info(f"Executed certificate trade: {selling_agent_id} -> {buying_agent_id}, {quantity} units at {price:.2f} each")
        
        return trade
    
    def _calculate_certificate_price(self) -> float:
        """
        Calculate the current price of import certificates based on supply and demand.
        
        Returns:
            Current certificate price
        """
        # In a real implementation, this would use the model from econ.data:
        # P_IC = α * (GDP / (Imports - Exports)) + β
        
        # For simplicity, we'll use a basic supply-demand model
        total_available = sum(certs["available"] for certs in self.import_certificates.values())
        total_earned = sum(certs["earned"] for certs in self.import_certificates.values())
        total_used = sum(certs["used"] for certs in self.import_certificates.values())
        
        # Basic supply-demand ratio (with bounds to prevent division by zero)
        supply_demand_ratio = (total_available + 1) / (total_used + 1)
        
        # Base price with dynamic adjustment
        alpha = 0.5  # Sensitivity parameter
        beta = 1.0   # Base price
        price = beta * math.exp(-alpha * (supply_demand_ratio - 1))
        
        # Bound the price to reasonable limits
        price = max(0.1, min(10.0, price))
        
        # Update the current price in the system
        self.current_certificate_price = price
        
        # Record price in history
        timestamp = time.time()
        if "price_history" not in self.certificate_prices:
            self.certificate_prices["price_history"] = []
        
        self.certificate_prices["price_history"].append({
            "timestamp": timestamp,
            "price": price,
            "supply_demand_ratio": supply_demand_ratio
        })
        
        # Update state store if available
        if self.state_store:
            self.state_store.update_certificate_price(price, timestamp)
        
        return price
    
    async def calculate_deal_value(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the value of a potential deal using the Deal Value Function (DVF).
        
        DVF = ∑(Vi * Wi * Pi * Ci * Mi) - TC
        
        where:
        - Vi: Intrinsic value
        - Wi: Weight
        - Pi: Probability
        - Ci: Confidence
        - Mi: Margin of safety
        - TC: Transaction costs
        
        Args:
            deal_data: Deal information
            
        Returns:
            Deal valuation result
        """
        # Extract deal components
        intrinsic_value = deal_data.get("intrinsic_value", 100.0)
        weight = deal_data.get("weight", 1.0)
        probability = deal_data.get("probability", 0.8)
        confidence = deal_data.get("confidence", 0.7)
        margin_of_safety = deal_data.get("margin_of_safety", self.drp_params["margin_of_safety"])
        transaction_costs = deal_data.get("transaction_costs", 10.0)
        
        # Calculate DVF
        dvf = intrinsic_value * weight * probability * confidence * margin_of_safety - transaction_costs
        
        # Check if this is a win-win deal
        stakeholders = deal_data.get("stakeholders", {})
        stakeholder_dvfs = {}
        is_win_win = True
        
        for stakeholder_id, stakeholder_data in stakeholders.items():
            stakeholder_value = stakeholder_data.get("intrinsic_value", intrinsic_value * 0.5)
            stakeholder_weight = stakeholder_data.get("weight", weight)
            stakeholder_probability = stakeholder_data.get("probability", probability)
            stakeholder_confidence = stakeholder_data.get("confidence", confidence)
            stakeholder_margin = stakeholder_data.get("margin_of_safety", margin_of_safety)
            stakeholder_tc = stakeholder_data.get("transaction_costs", transaction_costs * 0.5)
            
            stakeholder_dvf = (
                stakeholder_value * stakeholder_weight * 
                stakeholder_probability * stakeholder_confidence * 
                stakeholder_margin - stakeholder_tc
            )
            
            stakeholder_dvfs[stakeholder_id] = stakeholder_dvf
            
            # Check if positive DVF for this stakeholder
            if stakeholder_dvf <= 0:
                is_win_win = False
        
        # Create result
        deal_valuation = {
            "deal_id": deal_data.get("id", str(uuid4())),
            "dvf": dvf,
            "stakeholder_dvfs": stakeholder_dvfs,
            "is_win_win": is_win_win,
            "components": {
                "intrinsic_value": intrinsic_value,
                "weight": weight,
                "probability": probability,
                "confidence": confidence,
                "margin_of_safety": margin_of_safety,
                "transaction_costs": transaction_costs
            }
        }
        
        self.logger.info(f"Calculated deal value: {dvf:.2f} (Win-Win: {is_win_win})")
        
        return deal_valuation
    
    async def update_economic_metrics(self) -> Dict[str, Any]:
        """
        Update system-wide economic metrics.
        
        Returns:
            Updated metrics
        """
        # Calculate efficiency metric
        avg_efficiency = 0.0
        if self.economic_model["agent_performance"]:
            efficiencies = [perf["efficiency_score"] for perf in self.economic_model["agent_performance"].values()]
            avg_efficiency = sum(efficiencies) / len(efficiencies)
        
        # Calculate fairness metric (distribution of resources)
        fairness = 0.0
        if self.economic_model["agent_resources"]:
            # Calculate Gini coefficient of resource allocation
            resource_allocations = []
            for agent_resources in self.economic_model["agent_resources"].values():
                total_allocation = sum(r["allocated"] for r in agent_resources.values())
                resource_allocations.append(total_allocation)
            
            # Sort allocations
            resource_allocations.sort()
            
            # Calculate Gini coefficient
            n = len(resource_allocations)
            numerator = sum((i+1) * x for i, x in enumerate(resource_allocations))
            denominator = sum(resource_allocations) * n
            gini = (2 * numerator / denominator) - (n + 1) / n if denominator > 0 else 0
            
            # Convert to fairness (1 - Gini)
            fairness = 1 - gini
        
        # Calculate innovation metric (based on new capabilities/techniques used)
        innovation = 0.7  # Placeholder for actual innovation calculation
        
        # Calculate collaboration metric
        avg_collaboration = 0.0
        if self.economic_model["agent_performance"]:
            collaborations = [perf["collaboration_score"] for perf in self.economic_model["agent_performance"].values()]
            avg_collaboration = sum(collaborations) / len(collaborations)
        
        # Update metrics
        self.economic_model["metrics"] = {
            "efficiency": avg_efficiency,
            "fairness": fairness,
            "innovation": innovation,
            "collaboration": avg_collaboration,
            "timestamp": time.time()
        }
        
        # Update state store if available
        if self.state_store:
            self.state_store.update_economic_metrics(self.economic_model["metrics"])
        
        self.logger.info(f"Updated economic metrics: efficiency={avg_efficiency:.2f}, fairness={fairness:.2f}")
        
        return self.economic_model["metrics"]
    
    async def run_ace_simulation(self, steps: int = 20) -> Dict[str, Any]:
        """
        Run the ACE simulation for forecasting and policy optimization.
        
        Args:
            steps: Number of simulation steps to run
            
        Returns:
            Simulation results
        """
        self.logger.info(f"Running ACE simulation for {steps} steps")
        
        # Run simulation
        simulation_results = self.ace_simulation.run_simulation(steps)
        
        # Get final statistics
        statistics = self.ace_simulation.get_simulation_statistics()
        
        # Store simulation history
        simulation_id = f"sim_{int(time.time())}"
        self.simulation_history[simulation_id] = {
            "id": simulation_id,
            "timestamp": time.time(),
            "steps": steps,
            "results": simulation_results,
            "statistics": statistics
        }
        
        # Generate forecasts based on simulation
        forecasts = self._generate_forecasts_from_simulation(simulation_id)
        self.simulation_forecasts[simulation_id] = forecasts
        
        # Adapt policies if enabled
        if self.enable_adaptive_policies:
            self._adapt_policies_from_simulation(simulation_id)
        
        # Update state store if available
        if self.state_store:
            self.state_store.record_simulation_results(
                simulation_id=simulation_id,
                statistics=statistics,
                forecasts=forecasts
            )
        
        self.logger.info(f"Completed ACE simulation {simulation_id}: efficiency={statistics['system']['efficiency']:.2f}, fairness={statistics['system']['fairness']:.2f}")
        
        return {
            "simulation_id": simulation_id,
            "steps": steps,
            "statistics": statistics,
            "forecasts": forecasts
        }
    
    def _generate_forecasts_from_simulation(self, simulation_id: str) -> Dict[str, Any]:
        """
        Generate forecasts based on simulation results.
        
        Args:
            simulation_id: ID of the simulation
            
        Returns:
            Forecast data
        """
        simulation = self.simulation_history.get(simulation_id)
        if not simulation:
            return {}
        
        statistics = simulation["statistics"]
        
        # Extract resource price trends
        resource_forecasts = {}
        for resource_type, resource_stats in statistics["resources"].items():
            trend = resource_stats["price_trend"]
            current_price = resource_stats["price"]
            
            # Simple trend-based forecast
            if trend == "strongly_rising":
                forecasted_price = current_price * 1.2
            elif trend == "rising":
                forecasted_price = current_price * 1.1
            elif trend == "falling":
                forecasted_price = current_price * 0.9
            elif trend == "strongly_falling":
                forecasted_price = current_price * 0.8
            else:  # stable
                forecasted_price = current_price
            
            resource_forecasts[resource_type] = {
                "current_price": current_price,
                "forecasted_price": forecasted_price,
                "trend": trend
            }
        
        # Forecast system metrics
        system_metrics = statistics["system"]
        system_forecasts = {
            "efficiency": system_metrics["efficiency"],
            "fairness": system_metrics["fairness"],
            "stability": system_metrics["stability"],
            "health_forecast": self._forecast_system_health(system_metrics)
        }
        
        # Generate policy recommendations
        policy_recommendations = self._generate_policy_recommendations(statistics)
        
        return {
            "resource_forecasts": resource_forecasts,
            "system_forecasts": system_forecasts,
            "policy_recommendations": policy_recommendations,
            "forecast_timestamp": time.time(),
            "forecast_horizon": "short_term"  # Could be short_term, medium_term, long_term
        }
    
    def _forecast_system_health(self, system_metrics: Dict[str, float]) -> str:
        """
        Forecast system health based on metrics.
        
        Args:
            system_metrics: System metrics
            
        Returns:
            Forecasted health status
        """
        # Calculate health score from metrics
        efficiency = system_metrics.get("efficiency", 0.0)
        fairness = system_metrics.get("fairness", 1.0)
        stability = system_metrics.get("stability", 1.0)
        
        # Weighted health score
        health_score = (
            efficiency * 0.4 + 
            fairness * 0.4 + 
            stability * 0.2
        )
        
        # Determine health status
        if health_score >= 0.8:
            return "excellent"
        elif health_score >= 0.7:
            return "good"
        elif health_score >= 0.6:
            return "fair"
        elif health_score >= 0.5:
            return "concerning"
        else:
            return "critical"
    
    def _generate_policy_recommendations(self, statistics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate policy recommendations based on simulation statistics.
        
        Args:
            statistics: Simulation statistics
            
        Returns:
            List of policy recommendations
        """
        recommendations = []
        
        # Check resource utilization
        for resource_type, resource_stats in statistics["resources"].items():
            utilization = resource_stats.get("utilization", 0.0)
            price = resource_stats.get("price", 1.0)
            
            # High utilization suggests increasing supply
            if utilization > 0.9:
                recommendations.append({
                    "type": "resource_allocation",
                    "resource": resource_type,
                    "action": "increase_supply",
                    "amount": 0.2,  # Increase by 20%
                    "reason": f"High utilization ({utilization:.2f}) indicates potential resource shortage",
                    "priority": "high"
                })
            
            # Low utilization suggests decreasing supply
            elif utilization < 0.3:
                recommendations.append({
                    "type": "resource_allocation",
                    "resource": resource_type,
                    "action": "decrease_supply",
                    "amount": 0.1,  # Decrease by 10%
                    "reason": f"Low utilization ({utilization:.2f}) indicates resource waste",
                    "priority": "medium"
                })
        
        # Check system metrics
        system_metrics = statistics["system"]
        
        # Low fairness suggests adjusting allocation algorithm
        if system_metrics.get("fairness", 1.0) < 0.6:
            recommendations.append({
                "type": "system_policy",
                "policy": "allocation_algorithm",
                "action": "adjust_fairness_weight",
                "amount": 0.2,  # Increase fairness weight by 20%
                "reason": "Low fairness score indicates potential inequality in resource allocation",
                "priority": "high"
            })
        
        # Low stability suggests reducing price sensitivity
        if system_metrics.get("stability", 1.0) < 0.6:
            recommendations.append({
                "type": "system_policy",
                "policy": "price_adjustment",
                "action": "reduce_price_sensitivity",
                "amount": 0.1,  # Reduce price sensitivity by 10%
                "reason": "Low stability indicates high price volatility",
                "priority": "medium"
            })
        
        return recommendations
    
    def _adapt_policies_from_simulation(self, simulation_id: str) -> None:
        """
        Adapt economic policies based on simulation results.
        
        Args:
            simulation_id: ID of the simulation
        """
        if not self.enable_adaptive_policies:
            return
        
        forecasts = self.simulation_forecasts.get(simulation_id)
        if not forecasts:
            return
        
        policy_recommendations = forecasts.get("policy_recommendations", [])
        
        for recommendation in policy_recommendations:
            # Process resource allocation recommendations
            if recommendation["type"] == "resource_allocation" and recommendation["priority"] == "high":
                resource_type = recommendation["resource"]
                action = recommendation["action"]
                amount = recommendation["amount"]
                
                if action == "increase_supply" and resource_type in self.economic_model["resource_pool"]:
                    # Increase resource supply
                    current_total = self.economic_model["resource_pool"][resource_type]["total"]
                    increase = current_total * amount
                    self.economic_model["resource_pool"][resource_type]["total"] += increase
                    self.economic_model["resource_pool"][resource_type]["available"] += increase
                    
                    self.logger.info(f"Adapted policy: Increased {resource_type} supply by {amount*100:.0f}%")
                    
                elif action == "decrease_supply" and resource_type in self.economic_model["resource_pool"]:
                    # Decrease resource supply (careful not to go below what's allocated)
                    current_total = self.economic_model["resource_pool"][resource_type]["total"]
                    current_available = self.economic_model["resource_pool"][resource_type]["available"]
                    
                    # Calculate how much is allocated
                    allocated = current_total - current_available
                    
                    # Only decrease up to what's available (don't remove allocated resources)
                    decrease = min(current_available, current_total * amount)
                    
                    self.economic_model["resource_pool"][resource_type]["total"] -= decrease
                    self.economic_model["resource_pool"][resource_type]["available"] -= decrease
                    
                    self.logger.info(f"Adapted policy: Decreased {resource_type} supply by {amount*100:.0f}%")
            
            # Process system policy recommendations
            elif recommendation["type"] == "system_policy" and recommendation["priority"] == "high":
                policy = recommendation["policy"]
                action = recommendation["action"]
                amount = recommendation["amount"]
                
                if policy == "allocation_algorithm" and action == "adjust_fairness_weight":
                    # Update fairness weight in the adaptive policies
                    self.adaptive_policies["fairness_weight"] = self.adaptive_policies.get("fairness_weight", 1.0) + amount
                    self.logger.info(f"Adapted policy: Increased fairness weight by {amount*100:.0f}%")
                    
                elif policy == "price_adjustment" and action == "reduce_price_sensitivity":
                    # Update price sensitivity in the adaptive policies
                    self.adaptive_policies["price_sensitivity"] = max(
                        0.05, 
                        self.adaptive_policies.get("price_sensitivity", 0.1) - amount
                    )
                    self.logger.info(f"Adapted policy: Reduced price sensitivity by {amount*100:.0f}%")
        
        # Store the changes
        self.adaptive_policies["last_updated"] = time.time()
        self.adaptive_policies["last_simulation_id"] = simulation_id
        
        # Update state store if available
        if self.state_store:
            self.state_store.update_economic_policies(self.adaptive_policies)

    async def generate_economic_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report on the economic status of the system.
        
        Returns:
            Economic report
        """
        # Update metrics before generating report
        await self.update_economic_metrics()
        
        # Update network and knowledge models
        self.agent_network.calculate_network_statistics()
        self.knowledge_model.update_knowledge(steps=1)
        knowledge_stats = self.knowledge_model.get_knowledge_statistics()
        
        # Get certificate system state
        certificate_state = self.import_certificate_system.get_system_state()
        trade_balance = certificate_state["trade_balance"]
        
        # Calculate resource utilization
        resource_utilization = {}
        for resource_type, pool in self.economic_model["resource_pool"].items():
            utilized = pool["total"] - pool["available"]
            utilization_rate = utilized / pool["total"] if pool["total"] > 0 else 0
            
            # Add market data if available
            market_data = None
            if resource_type in self.markets:
                market_data = self.markets[resource_type].get_market_data()
            
            resource_utilization[resource_type] = {
                "total": pool["total"],
                "utilized": utilized,
                "utilization_rate": utilization_rate,
                "market": market_data
            }
        
        # Calculate top performers
        top_performers = []
        if self.economic_model["agent_performance"]:
            # Sort by total value created
            sorted_agents = sorted(
                self.economic_model["agent_performance"].items(),
                key=lambda x: x[1]["total_value_created"],
                reverse=True
            )
            top_performers = [
                {
                    "agent_id": agent_id,
                    "total_value_created": perf["total_value_created"],
                    "tasks_completed": perf["tasks_completed"],
                    "efficiency_score": perf["efficiency_score"],
                    "centrality": self.agent_network.calculate_centrality().get(agent_id, 0.0),
                    "knowledge": {
                        domain: level for domain, level in 
                        self.knowledge_model.agent_knowledge.get(agent_id, {}).items()
                        if level > 0.5  # Only include domains with significant knowledge
                    }
                }
                for agent_id, perf in sorted_agents[:5]  # Top 5
            ]
        
        # Get certificate price from system
        certificate_price = certificate_state.get("current_price", 1.0)
        
        # Calculate price trend
        price_history = certificate_state.get("market", {}).get("price_history", [])
        price_trend = "stable"
        price_change = 0.0
        
        if price_history and len(price_history) >= 2:
            current_price = price_history[-1]
            previous_price = price_history[-2]
            price_change = (current_price - previous_price) / previous_price if previous_price else 0
            
            if price_change > 0.05:
                price_trend = "rising"
            elif price_change < -0.05:
                price_trend = "falling"
        
        # Run a simulation for forecasting
        simulation_results = None
        if len(self.economic_model["agent_resources"]) > 0:
            simulation_results = await self.run_ace_simulation(steps=10)
        
        # Get network visualization data
        network_data = self.agent_network.get_network_visualization_data()
        
        # Identify emerging knowledge clusters
        knowledge_gaps = self.knowledge_model.find_knowledge_gaps()
        
        # Create report
        report = {
            "timestamp": time.time(),
            "economic_metrics": self.economic_model["metrics"],
            "trade_balance": trade_balance,
            "resource_utilization": resource_utilization,
            "top_performers": top_performers,
            "network_statistics": self.agent_network.statistics,
            "knowledge_statistics": knowledge_stats,
            "certificate_system": {
                "certificates": certificate_state["certificates"],
                "certificate_value": certificate_state["certificate_value"],
                "current_price": certificate_price,
                "trend": price_trend,
                "change": price_change
            },
            "market_summary": {
                name: market.get_market_data() 
                for name, market in self.markets.items()
            },
            "task_valuation_summary": {
                "count": len(self.economic_model["task_valuations"]),
                "average_value": sum(v["total_value"] for v in self.economic_model["task_valuations"].values()) / 
                                max(1, len(self.economic_model["task_valuations"]))
            },
            "system_health": self._calculate_system_health(),
            "forecasts": simulation_results["forecasts"] if simulation_results else None,
            "adaptive_policies": self.adaptive_policies,
            "network_visualization": network_data,
            "knowledge_gaps": knowledge_gaps,
            "knowledge_diffusion": {
                "average_knowledge_level": knowledge_stats["overall"]["mean"],
                "knowledge_inequality": 1.0 - knowledge_stats["overall"]["std"] / knowledge_stats["overall"]["mean"] 
                                        if knowledge_stats["overall"]["mean"] > 0 else 0.0,
                "expertise_distribution": knowledge_stats.get("expertise_distribution", {})
            }
        }
        
        # Update state store if available
        if self.state_store:
            self.state_store.record_economic_report(report)
        
        self.logger.info(f"Generated economic report: balance={trade_balance:.2f}, system_health={report['system_health']}")
        
        return report
    
    def _calculate_system_health(self) -> str:
        """
        Calculate overall system health based on economic metrics.
        
        Returns:
            System health status
        """
        metrics = self.economic_model["metrics"]
        
        # Calculate weighted score
        health_score = (
            metrics["efficiency"] * 0.3 +
            metrics["fairness"] * 0.3 +
            metrics["innovation"] * 0.2 +
            metrics["collaboration"] * 0.2
        )
        
        # Determine health status
        if health_score >= 0.8:
            return "excellent"
        elif health_score >= 0.7:
            return "good"
        elif health_score >= 0.6:
            return "fair"
        elif health_score >= 0.5:
            return "concerning"
        else:
            return "critical"


# Factory function for creating economist
def create_economist(
    supervisor_agent = None,
    coordinator_agent = None,
    state_store: Optional[StateStore] = None,
    human_interface: Optional[HumanQueryInterface] = None,
    config_path: Optional[str] = None,
    econ_data_path: Optional[str] = None
) -> EconomistAgent:
    """
    Create and configure an Economist Agent.
    
    Args:
        supervisor_agent: Reference to the SupervisorAgent
        coordinator_agent: Reference to the CoordinatorAgent
        state_store: Environment/State Store for persistent memory
        human_interface: Human-in-the-loop interface
        config_path: Path to configuration file
        econ_data_path: Path to econ.data file
        
    Returns:
        Configured EconomistAgent
    """
    # Load configuration if path provided
    config = {}
    if config_path:
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logging.error(f"Error loading economist configuration: {str(e)}")
    
    # Create economist
    economist = EconomistAgent(
        name=config.get("name", "MAC-Economist"),
        supervisor_agent=supervisor_agent,
        coordinator_agent=coordinator_agent,
        state_store=state_store,
        human_interface=human_interface,
        config=config,
        econ_data_path=econ_data_path
    )
    
    # Register state store with economist reference if needed
    if state_store:
        state_store.register_economist(economist)
    
    return economist