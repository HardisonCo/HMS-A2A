"""
Market Network Integration for the Multi-Agent Collaboration (MAC) Architecture.

This module integrates the enhanced economic system with the existing Moneyball deal model
and other economic components, creating a cohesive market network for agent collaboration.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import logging
import json
import numpy as np
import networkx as nx
from uuid import uuid4
import datetime
import asyncio

# MAC Imports
from mac.economist_agent import EconomistAgent, ResourceType
from mac.market_models import Market, MarketType, MarketMechanism, Order, Transaction, ImportCertificateSystem
from mac.network_effects import AgentNetwork, NetworkType, EffectType, KnowledgeDiffusionModel

# Moneyball Model Imports
import moneyball_deal_model as mdm
from moneyball_deal_model import (
    Intent, Solution, Stakeholder, FinancingStructure, ExecutionPlan, Deal,
    calculate_deal_value_function, calculate_stakeholder_dvf, is_win_win_deal
)

# Other economic components
import deal_monitoring_system as dms
import deploy_moneyball_model as dmm
import o3_deal_optimization as o3do
import formal_verification_framework as fvf


class MarketNetworkIntegrator:
    """
    Integrates the MAC architecture's economic components with the Moneyball deal model,
    creating a market network that combines network effects, marketplace transactions,
    and SaaS workflows.
    """
    
    def __init__(
        self,
        economist_agent: EconomistAgent,
        config_path: Optional[str] = None
    ):
        """
        Initialize the Market Network Integrator.
        
        Args:
            economist_agent: Reference to the EconomistAgent
            config_path: Path to configuration file (optional)
        """
        self.economist = economist_agent
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger("MAC.MarketNetworkIntegrator")
        
        # Deal registry
        self.deals = {}
        
        # Formal verification framework
        self.verification_framework = fvf.FormalVerificationFramework()
        
        # Deal monitoring system
        self.monitoring_system = dms.DealMonitoringSystem()
        
        # O3 optimization modules
        self.deal_optimizer = o3do.DealOptimizer()
        
        # Network graph for stakeholder and deal relationships
        self.deal_network = nx.MultiDiGraph()
        
        self.logger.info("Market Network Integrator initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        config = {
            "deal_value_threshold": 60.0,
            "stakeholder_match_threshold": 0.7,
            "enable_formal_verification": True,
            "monitoring_frequency": 5,  # time steps
            "network_analysis_depth": 3,  # degrees
            "certificate_trading_enabled": True
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    config.update(loaded_config)
            except Exception as e:
                logging.error(f"Error loading configuration: {str(e)}")
        
        return config
    
    async def register_agent_with_market_network(
        self, 
        agent_id: str, 
        capabilities: List[str], 
        resource_needs: Dict[str, float],
        value_preferences: Dict[str, float],
        stakeholder_type: str = "autonomous_agent",
        risk_tolerance: float = 0.6
    ) -> Dict[str, Any]:
        """
        Register an agent with the market network.
        
        Args:
            agent_id: Agent ID
            capabilities: List of agent capabilities
            resource_needs: Resource requirements
            value_preferences: Value preferences for different dimensions
            stakeholder_type: Type of stakeholder (e.g., "autonomous_agent", "government", "corporate")
            risk_tolerance: Risk tolerance level [0,1]
            
        Returns:
            Registration information
        """
        # First register with the economist agent
        econ_registration = await self.economist.register_agent(
            agent_id=agent_id,
            capabilities=capabilities,
            resource_needs=resource_needs
        )
        
        # Create a Moneyball stakeholder object
        stakeholder = Stakeholder(
            id=agent_id,
            name=f"Agent {agent_id}",
            type=stakeholder_type,
            capabilities={cap: 0.8 for cap in capabilities},  # Default high capability in declared areas
            value_preferences=value_preferences,
            risk_tolerance=risk_tolerance,
            participation_costs={"financial": 100.0, "time": 50.0},  # Default costs
            expected_returns={key: 150.0 for key in value_preferences}  # Default expected returns
        )
        
        # Add to deal network
        self.deal_network.add_node(
            agent_id, 
            type="agent",
            capabilities=capabilities,
            knowledge=econ_registration.get("knowledge_levels", {}),
            certificate_balance=econ_registration.get("import_certificates", 100.0)
        )
        
        # Add edges to other agents based on knowledge overlap and capabilities
        self._update_agent_network_connections(agent_id, capabilities)
        
        self.logger.info(f"Agent {agent_id} registered with market network")
        
        # Return combined registration info
        return {
            **econ_registration,
            "stakeholder_profile": {
                "type": stakeholder_type,
                "risk_tolerance": risk_tolerance,
                "value_preferences": value_preferences
            },
            "network_position": {
                "centrality": nx.degree_centrality(self.deal_network).get(agent_id, 0.0),
                "neighbors": list(self.deal_network.neighbors(agent_id))
            }
        }
    
    def _update_agent_network_connections(self, agent_id: str, capabilities: List[str]) -> None:
        """
        Update network connections based on capability overlap.
        
        Args:
            agent_id: Agent ID
            capabilities: Agent capabilities
        """
        # Find other agents with complementary capabilities
        for node, data in self.deal_network.nodes(data=True):
            if node == agent_id or data.get("type") != "agent":
                continue
                
            node_capabilities = data.get("capabilities", [])
            
            # Calculate capability overlap score
            overlap = set(capabilities).intersection(set(node_capabilities))
            complement = set(capabilities).symmetric_difference(set(node_capabilities))
            
            if overlap:
                # Shared capabilities - collaboration potential
                weight = len(overlap) / max(len(capabilities), len(node_capabilities))
                if weight > 0.2:  # Minimum threshold for connection
                    self.deal_network.add_edge(
                        agent_id, node, 
                        type="collaboration", 
                        weight=weight,
                        shared_capabilities=list(overlap)
                    )
            
            if complement:
                # Complementary capabilities - service potential
                weight = len(complement) / (len(capabilities) + len(node_capabilities))
                if weight > 0.3:  # Higher threshold for service relationship
                    self.deal_network.add_edge(
                        agent_id, node, 
                        type="service", 
                        weight=weight,
                        complementary_capabilities=list(complement)
                    )
    
    async def create_deal_from_intent(
        self,
        problem_statement: str,
        value_dimensions: List[str],
        stakeholder_ids: List[str],
        constraints: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new deal from an intent statement.
        
        Args:
            problem_statement: Description of the problem or opportunity
            value_dimensions: List of value dimensions for this deal
            stakeholder_ids: List of stakeholder IDs to include
            constraints: Optional constraints (budget, timeline, etc.)
            
        Returns:
            Deal information or None if creation failed
        """
        # Create intent
        intent_vector = np.random.rand(len(value_dimensions))  # Simplified
        intent_vector = intent_vector / np.linalg.norm(intent_vector)
        
        intent = Intent(
            id=f"INT-{uuid4().hex[:8]}",
            description=problem_statement,
            intent_vector=intent_vector,
            value_dimensions=value_dimensions,
            constraints=constraints or {},
            context={"dimensions": value_dimensions}
        )
        
        # Get stakeholders
        stakeholders = {}
        for stakeholder_id in stakeholder_ids:
            # Fetch from economist agent's network or create new
            if stakeholder_id in self.deal_network:
                node_data = self.deal_network.nodes[stakeholder_id]
                stakeholders[stakeholder_id] = Stakeholder(
                    id=stakeholder_id,
                    name=f"Agent {stakeholder_id}",
                    type=node_data.get("type", "autonomous_agent"),
                    capabilities={cap: 0.8 for cap in node_data.get("capabilities", [])},
                    value_preferences={dim: 1.0/len(value_dimensions) for dim in value_dimensions},
                    risk_tolerance=0.6,
                    participation_costs={"financial": 100.0, "time": 50.0},
                    expected_returns={dim: 150.0 for dim in value_dimensions}
                )
        
        if not stakeholders:
            self.logger.error("No valid stakeholders found for deal creation")
            return None
        
        # Create solution (simplified)
        solution = Solution(
            id=f"SOL-{uuid4().hex[:8]}",
            description=f"Solution for: {problem_statement[:30]}...",
            solution_vector=intent_vector * 0.9 + np.random.rand(len(intent_vector)) * 0.1,
            potential_value=np.random.uniform(80, 120),
            intent_id=intent.id,
            implementation_difficulty=np.random.uniform(0.3, 0.7),
            time_horizon=np.random.randint(6, 18)
        )
        
        # Create financing structure
        cost_total = solution.potential_value * 0.7  # Total cost as 70% of potential value
        stakeholder_count = len(stakeholders)
        
        # Equal cost distribution (simplified)
        cost_per_stakeholder = cost_total / stakeholder_count
        cost_allocation = {sh_id: cost_per_stakeholder for sh_id in stakeholders}
        
        # Returns distribution (simplified)
        returns_total = solution.potential_value * 1.3  # Total returns as 130% of potential value
        returns_per_dim = returns_total / len(value_dimensions)
        returns_allocation = {
            sh_id: {dim: returns_per_dim / stakeholder_count for dim in value_dimensions}
            for sh_id in stakeholders
        }
        
        financing = FinancingStructure(
            cost_allocation=cost_allocation,
            returns_allocation=returns_allocation,
            timeline={sh_id: {0: cost_per_stakeholder} for sh_id in stakeholders},
            conditions={},
            risk_sharing={sh_id: 1.0 / stakeholder_count for sh_id in stakeholders}
        )
        
        # Create execution plan (simplified)
        responsibility_matrix = {
            sh_id: {"task1": 1.0 / stakeholder_count, "task2": 1.0 / stakeholder_count}
            for sh_id in stakeholders
        }
        
        expertise_allocation = {
            "task1": {sh_id: 0.8 for sh_id in stakeholders},
            "task2": {sh_id: 0.8 for sh_id in stakeholders}
        }
        
        execution = ExecutionPlan(
            responsibility_matrix=responsibility_matrix,
            timeline={0: ["task1"], 1: ["task2"]},
            milestones={"m1": {"task": "task1", "period": 0}, "m2": {"task": "task2", "period": 1}},
            expertise_allocation=expertise_allocation
        )
        
        # Create deal
        deal = Deal(
            id=f"DEAL-{uuid4().hex[:8]}",
            name=f"Deal: {problem_statement[:30]}...",
            intent=intent,
            solution=solution,
            stakeholders=stakeholders,
            financing=financing,
            execution=execution,
            status="draft",
            creation_date=datetime.datetime.now(),
            update_date=datetime.datetime.now(),
            metrics={}
        )
        
        # Calculate deal metrics
        try:
            deal.metrics["dvf"] = calculate_deal_value_function(
                intent, solution, stakeholders, financing, execution
            )
            deal.metrics["win_win_status"] = is_win_win_deal(deal)
        except Exception as e:
            self.logger.error(f"Error calculating deal metrics: {str(e)}")
            deal.metrics["dvf"] = 0.0
            deal.metrics["win_win_status"] = False
        
        # Formal verification if enabled
        if self.config["enable_formal_verification"]:
            verification_result = self.verification_framework.verify_deal(deal)
            deal.metrics["verification_status"] = verification_result.get("status", "failed")
            deal.metrics["verification_details"] = verification_result
        
        # Apply O3 optimization
        optimized_deal = self.deal_optimizer.optimize_deal(deal)
        
        # Store the deal
        self.deals[optimized_deal.id] = optimized_deal
        
        # Update deal network
        self._update_deal_network(optimized_deal)
        
        self.logger.info(f"Created and optimized deal {optimized_deal.id} with DVF {optimized_deal.metrics.get('dvf', 0.0)}")
        
        # Return deal info
        return {
            "deal_id": optimized_deal.id,
            "name": optimized_deal.name,
            "status": optimized_deal.status,
            "metrics": optimized_deal.metrics,
            "stakeholders": list(optimized_deal.stakeholders.keys()),
            "intent": optimized_deal.intent.description,
            "solution": optimized_deal.solution.description,
            "potential_value": optimized_deal.solution.potential_value,
            "total_cost": optimized_deal.financing.total_cost,
            "total_returns": optimized_deal.financing.total_returns,
            "duration": optimized_deal.execution.duration
        }
    
    def _update_deal_network(self, deal: Deal) -> None:
        """
        Update the deal network with a new deal.
        
        Args:
            deal: The deal to add to the network
        """
        # Add deal node
        self.deal_network.add_node(
            deal.id,
            type="deal",
            name=deal.name,
            status=deal.status,
            dvf=deal.metrics.get("dvf", 0.0),
            win_win=deal.metrics.get("win_win_status", False),
            creation_date=deal.creation_date
        )
        
        # Add edges to stakeholders
        for stakeholder_id in deal.stakeholders:
            # Stakeholder to deal
            cost = deal.financing.cost_allocation.get(stakeholder_id, 0.0)
            returns = sum(deal.financing.returns_allocation.get(stakeholder_id, {}).values())
            
            self.deal_network.add_edge(
                stakeholder_id, deal.id,
                type="participation",
                cost=cost,
                returns=returns,
                net_value=returns - cost,
                risk=deal.financing.risk_sharing.get(stakeholder_id, 0.0)
            )
            
            # Deal to stakeholder
            self.deal_network.add_edge(
                deal.id, stakeholder_id,
                type="benefit",
                value=returns
            )
            
            # Update relationships between stakeholders
            for other_id in deal.stakeholders:
                if stakeholder_id != other_id:
                    # Check if they already have a relationship
                    if self.deal_network.has_edge(stakeholder_id, other_id):
                        # Update weight
                        for _, _, data in self.deal_network.edges([stakeholder_id, other_id], data=True):
                            if data.get("type") == "collaboration":
                                data["weight"] += 0.1
                                data["deals"].append(deal.id)
                    else:
                        # Create new relationship
                        self.deal_network.add_edge(
                            stakeholder_id, other_id,
                            type="collaboration",
                            weight=0.1,
                            deals=[deal.id]
                        )
    
    async def analyze_market_network(self) -> Dict[str, Any]:
        """
        Analyze the current state of the market network.
        
        Returns:
            Analysis results
        """
        # Economic metrics from economist agent
        economic_report = await self.economist.generate_economic_report()
        
        # Network analysis
        network_metrics = self._analyze_network()
        
        # Deal performance metrics
        deal_metrics = self._analyze_deals()
        
        # Overall resource utilization
        resource_utilization = economic_report.get("resource_utilization", {})
        
        # Certificate market metrics
        certificate_metrics = economic_report.get("certificate_system", {})
        
        # Combine all metrics
        analysis = {
            "timestamp": datetime.datetime.now().isoformat(),
            "economic_metrics": {
                "efficiency": economic_report.get("economic_metrics", {}).get("efficiency", 0.0),
                "fairness": economic_report.get("economic_metrics", {}).get("fairness", 0.0),
                "innovation": economic_report.get("economic_metrics", {}).get("innovation", 0.0),
                "collaboration": economic_report.get("economic_metrics", {}).get("collaboration", 0.0)
            },
            "network_metrics": network_metrics,
            "deal_metrics": deal_metrics,
            "resource_utilization": {
                resource: data.get("utilization_rate", 0.0)
                for resource, data in resource_utilization.items()
            },
            "certificate_market": {
                "current_price": certificate_metrics.get("current_price", 1.0),
                "price_trend": certificate_metrics.get("trend", "stable"),
                "total_certificates": certificate_metrics.get("certificates", {}).get("active", 0),
                "total_certificate_value": certificate_metrics.get("certificate_value", {}).get("active", 0.0)
            },
            "knowledge_diffusion": economic_report.get("knowledge_diffusion", {}),
            "system_health": economic_report.get("system_health", "good")
        }
        
        self.logger.info(f"Analyzed market network. Health: {analysis['system_health']}")
        
        return analysis
    
    def _analyze_network(self) -> Dict[str, Any]:
        """
        Analyze the deal network.
        
        Returns:
            Network analysis metrics
        """
        network = self.deal_network
        
        # Basic network metrics
        metrics = {
            "node_count": network.number_of_nodes(),
            "edge_count": network.number_of_edges(),
            "density": nx.density(network),
            "agent_count": sum(1 for _, data in network.nodes(data=True) if data.get("type") == "agent"),
            "deal_count": sum(1 for _, data in network.nodes(data=True) if data.get("type") == "deal"),
            "average_degree": sum(dict(network.degree()).values()) / network.number_of_nodes() if network.number_of_nodes() > 0 else 0
        }
        
        # Calculate centrality measures
        try:
            degree_centrality = nx.degree_centrality(network)
            metrics["centralization"] = max(degree_centrality.values()) - sum(degree_centrality.values()) / len(degree_centrality) if degree_centrality else 0
            
            # Top agents by centrality
            agent_centrality = {node: centrality for node, centrality in degree_centrality.items() 
                              if network.nodes[node].get("type") == "agent"}
            top_agents = sorted(agent_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            metrics["top_central_agents"] = [{"agent_id": a[0], "centrality": a[1]} for a in top_agents]
            
            # Community detection
            try:
                communities = list(nx.community.greedy_modularity_communities(network.to_undirected()))
                metrics["community_count"] = len(communities)
                metrics["community_sizes"] = [len(c) for c in communities]
                metrics["modularity"] = nx.community.modularity(network.to_undirected(), communities)
            except:
                # Community detection might fail on directed graphs
                metrics["community_count"] = 0
        except Exception as e:
            self.logger.error(f"Error in network analysis: {str(e)}")
        
        return metrics
    
    def _analyze_deals(self) -> Dict[str, Any]:
        """
        Analyze the current deals.
        
        Returns:
            Deal analysis metrics
        """
        metrics = {
            "deal_count": len(self.deals),
            "active_deals": sum(1 for d in self.deals.values() if d.status == "active"),
            "completed_deals": sum(1 for d in self.deals.values() if d.status == "completed"),
            "failed_deals": sum(1 for d in self.deals.values() if d.status == "failed"),
            "avg_dvf": sum(d.metrics.get("dvf", 0.0) for d in self.deals.values()) / len(self.deals) if self.deals else 0,
            "win_win_ratio": sum(1 for d in self.deals.values() if d.metrics.get("win_win_status", False)) / len(self.deals) if self.deals else 0,
            "total_value": sum(d.solution.potential_value for d in self.deals.values()),
            "total_cost": sum(d.financing.total_cost for d in self.deals.values()),
            "expected_roi": sum((d.financing.total_returns - d.financing.total_cost) / d.financing.total_cost 
                              if d.financing.total_cost > 0 else 0 for d in self.deals.values()) / len(self.deals) if self.deals else 0
        }
        
        # Top deals by DVF
        top_deals = sorted(self.deals.values(), key=lambda d: d.metrics.get("dvf", 0.0), reverse=True)[:5]
        metrics["top_deals"] = [
            {
                "deal_id": d.id,
                "name": d.name,
                "dvf": d.metrics.get("dvf", 0.0),
                "win_win": d.metrics.get("win_win_status", False),
                "status": d.status
            }
            for d in top_deals
        ]
        
        return metrics
    
    async def facilitate_market_transaction(
        self,
        buying_agent_id: str,
        selling_agent_id: str,
        resource_type: str,
        quantity: float,
        proposed_price: float
    ) -> Dict[str, Any]:
        """
        Facilitate a market transaction between agents.
        
        Args:
            buying_agent_id: ID of buying agent
            selling_agent_id: ID of selling agent
            resource_type: Type of resource to trade
            quantity: Amount to trade
            proposed_price: Proposed price per unit
            
        Returns:
            Transaction result
        """
        # Check if agents exist in the network
        if not (self.deal_network.has_node(buying_agent_id) and self.deal_network.has_node(selling_agent_id)):
            return {"success": False, "message": "One or both agents not found in the network"}
        
        # Check if resource type exists
        if resource_type not in [r.value for r in ResourceType.__members__.values()]:
            return {"success": False, "message": f"Invalid resource type: {resource_type}"}
        
        # Get the appropriate market
        market = self.economist.markets.get(resource_type)
        if not market:
            return {"success": False, "message": f"No market available for resource type: {resource_type}"}
        
        # Create buy order
        buy_order = Order(
            order_id=f"BUY-{uuid4().hex[:8]}",
            agent_id=buying_agent_id,
            order_type="buy",
            market_type=MarketType.RESOURCE_MARKET,
            asset_type=resource_type,
            quantity=quantity,
            price=proposed_price,
            time_in_force=10  # Valid for 10 time steps
        )
        
        # Create sell order
        sell_order = Order(
            order_id=f"SELL-{uuid4().hex[:8]}",
            agent_id=selling_agent_id,
            order_type="sell",
            market_type=MarketType.RESOURCE_MARKET,
            asset_type=resource_type,
            quantity=quantity,
            price=proposed_price,
            time_in_force=10  # Valid for 10 time steps
        )
        
        # Add orders to market
        market.add_order(buy_order)
        market.add_order(sell_order)
        
        # Match orders
        transactions = market.match_orders()
        
        # If no transactions, run market step to try matching again
        if not transactions:
            transactions = market.step()
        
        if not transactions:
            return {
                "success": False,
                "message": "Orders could not be matched",
                "buy_order": buy_order.order_id,
                "sell_order": sell_order.order_id
            }
        
        # Process transaction effects
        for tx in transactions:
            # Update agent relationship in network
            if self.deal_network.has_edge(buying_agent_id, selling_agent_id):
                # Update existing edge
                edge_data = self.deal_network.get_edge_data(buying_agent_id, selling_agent_id)
                if edge_data and "transactions" in edge_data:
                    edge_data["transactions"].append(tx.transaction_id)
                    edge_data["transaction_volume"] = edge_data.get("transaction_volume", 0) + tx.value
                    edge_data["transaction_count"] = edge_data.get("transaction_count", 0) + 1
            else:
                # Create new edge
                self.deal_network.add_edge(
                    buying_agent_id, selling_agent_id,
                    type="transaction",
                    transactions=[tx.transaction_id],
                    transaction_volume=tx.value,
                    transaction_count=1
                )
            
            # Reciprocal edge
            if self.deal_network.has_edge(selling_agent_id, buying_agent_id):
                edge_data = self.deal_network.get_edge_data(selling_agent_id, buying_agent_id)
                if edge_data and "transactions" in edge_data:
                    edge_data["transactions"].append(tx.transaction_id)
                    edge_data["transaction_volume"] = edge_data.get("transaction_volume", 0) + tx.value
                    edge_data["transaction_count"] = edge_data.get("transaction_count", 0) + 1
            else:
                self.deal_network.add_edge(
                    selling_agent_id, buying_agent_id,
                    type="transaction",
                    transactions=[tx.transaction_id],
                    transaction_volume=tx.value,
                    transaction_count=1
                )
        
        # Return transaction results
        return {
            "success": True,
            "message": f"Transaction completed: {len(transactions)} orders matched",
            "transactions": [
                {
                    "transaction_id": tx.transaction_id,
                    "buyer": tx.buyer_id,
                    "seller": tx.seller_id,
                    "resource_type": tx.asset_type,
                    "quantity": tx.quantity,
                    "price": tx.price,
                    "total_value": tx.value,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                for tx in transactions
            ],
            "market_data": market.get_market_data()
        }
    
    async def propose_optimal_deals(self, agent_id: str, count: int = 3) -> List[Dict[str, Any]]:
        """
        Propose optimal deals for an agent based on their profile.
        
        Args:
            agent_id: Agent ID
            count: Number of deals to propose
            
        Returns:
            List of proposed deals
        """
        # Check if agent exists
        if not self.deal_network.has_node(agent_id):
            self.logger.error(f"Agent {agent_id} not found in network")
            return []
        
        # Get agent information
        agent_data = self.deal_network.nodes[agent_id]
        capabilities = agent_data.get("capabilities", [])
        knowledge = agent_data.get("knowledge", {})
        
        # Get agent's neighbors and their deals
        neighbors = list(self.deal_network.neighbors(agent_id))
        neighbor_deals = set()
        for neighbor in neighbors:
            # Look for deals this neighbor is involved in
            for _, deal_id, data in self.deal_network.out_edges(neighbor, data=True):
                if data.get("type") == "participation" and self.deal_network.nodes[deal_id].get("type") == "deal":
                    neighbor_deals.add(deal_id)
        
        # Get all deals
        all_deals = [d for d in self.deals.values() if d.status in ["draft", "proposed", "active"]]
        if not all_deals:
            return []
        
        # Calculate deal scores for this agent
        scored_deals = []
        for deal in all_deals:
            # Skip deals the agent is already part of
            if agent_id in deal.stakeholders:
                continue
                
            # Calculate capability match
            deal_required_capabilities = []
            for task_alloc in deal.execution.expertise_allocation.values():
                for s_id, score in task_alloc.items():
                    if score > 0.7 and s_id in deal.stakeholders:
                        stakeholder = deal.stakeholders[s_id]
                        for cap, cap_score in stakeholder.capabilities.items():
                            if cap_score > 0.7:
                                deal_required_capabilities.append(cap)
            
            capability_match = len(set(capabilities).intersection(set(deal_required_capabilities))) / max(1, len(deal_required_capabilities))
            
            # Calculate value dimension match
            value_match = sum(1 for dim in deal.intent.value_dimensions if dim in agent_data.get("value_preferences", {})) / max(1, len(deal.intent.value_dimensions))
            
            # Knowledge relevance
            knowledge_match = sum(knowledge.get(dim, 0) for dim in deal.intent.value_dimensions) / max(1, len(deal.intent.value_dimensions))
            
            # Network factor - deals involving neighbors get a boost
            network_factor = 1.2 if deal.id in neighbor_deals else 1.0
            
            # Combined score
            score = (capability_match * 0.4 + value_match * 0.3 + knowledge_match * 0.3) * network_factor
            
            # Calculate potential returns for this agent
            # Simplified: Distribute returns equally among existing stakeholders plus this one
            total_returns = deal.financing.total_returns
            stakeholder_count = len(deal.stakeholders) + 1
            potential_returns = total_returns / stakeholder_count
            
            # Calculate potential costs
            # Simplified: Distribute remaining costs equally
            total_cost = deal.financing.total_cost
            allocated_cost = sum(deal.financing.cost_allocation.values())
            remaining_cost = max(0, total_cost - allocated_cost)
            potential_cost = remaining_cost
            
            # Calculate ROI
            potential_roi = (potential_returns - potential_cost) / potential_cost if potential_cost > 0 else float('inf')
            
            scored_deals.append({
                "deal_id": deal.id,
                "name": deal.name,
                "score": score,
                "capability_match": capability_match,
                "value_match": value_match,
                "knowledge_match": knowledge_match,
                "network_factor": network_factor,
                "potential_returns": potential_returns,
                "potential_cost": potential_cost,
                "potential_roi": potential_roi,
                "intent": deal.intent.description,
                "solution": deal.solution.description,
                "dvf": deal.metrics.get("dvf", 0.0),
                "win_win": deal.metrics.get("win_win_status", False)
            })
        
        # Sort by score and return top N
        scored_deals.sort(key=lambda x: x["score"], reverse=True)
        
        top_deals = scored_deals[:count]
        self.logger.info(f"Proposed {len(top_deals)} optimal deals for agent {agent_id}")
        
        return top_deals
    
    async def propose_market_transactions(self, agent_id: str, count: int = 3) -> List[Dict[str, Any]]:
        """
        Propose optimal market transactions for an agent.
        
        Args:
            agent_id: Agent ID
            count: Number of transactions to propose
            
        Returns:
            List of proposed transactions
        """
        # Check if agent exists
        if not self.deal_network.has_node(agent_id):
            self.logger.error(f"Agent {agent_id} not found in network")
            return []
        
        # Get agent information
        agent_data = self.deal_network.nodes[agent_id]
        
        # Get resource needs from economist agent
        agent_resources = self.economist.economic_model["agent_resources"].get(agent_id, {})
        
        # Identify resources with high need and low allocation
        resource_gaps = {}
        for res_type, res_data in agent_resources.items():
            need = res_data.get("needs", 0.0)
            allocated = res_data.get("allocated", 0.0)
            
            if need > allocated:
                gap = need - allocated
                resource_gaps[res_type] = gap
        
        # Sort resources by gap size
        priority_resources = sorted(resource_gaps.items(), key=lambda x: x[1], reverse=True)
        
        # Find potential sellers for each resource
        proposed_transactions = []
        
        for res_type, gap in priority_resources:
            if len(proposed_transactions) >= count:
                break
                
            # Get market data for this resource
            market = self.economist.markets.get(res_type)
            if not market:
                continue
                
            market_data = market.get_market_data()
            best_ask = market_data.get("best_ask")
            
            # If no ask, create a transaction at the last price or default
            if best_ask is None:
                best_ask = market_data.get("last_price", 1.0)
            
            # Find agents with excess of this resource
            potential_sellers = []
            for node, data in self.deal_network.nodes(data=True):
                if data.get("type") != "agent" or node == agent_id:
                    continue
                    
                seller_resources = self.economist.economic_model["agent_resources"].get(node, {})
                seller_res_data = seller_resources.get(res_type, {})
                
                seller_need = seller_res_data.get("needs", 0.0)
                seller_allocated = seller_res_data.get("allocated", 0.0)
                
                # Check if seller has excess resources
                if seller_allocated > seller_need * 1.2:  # 20% buffer
                    excess = seller_allocated - seller_need
                    potential_sellers.append((node, excess))
            
            # Sort sellers by excess amount
            potential_sellers.sort(key=lambda x: x[1], reverse=True)
            
            # Propose transaction with best seller
            if potential_sellers:
                best_seller, excess = potential_sellers[0]
                
                # Calculate quantity (minimum of gap and excess)
                quantity = min(gap, excess)
                
                proposed_transactions.append({
                    "resource_type": res_type,
                    "seller_id": best_seller,
                    "buyer_id": agent_id,
                    "quantity": quantity,
                    "proposed_price": best_ask,
                    "total_value": quantity * best_ask,
                    "market_data": market_data
                })
        
        # If we still need more proposals, check for knowledge/service transactions
        if len(proposed_transactions) < count:
            # Get agent's knowledge levels
            agent_knowledge = self.economist.knowledge_model.agent_knowledge.get(agent_id, {})
            
            # Find knowledge domains where agent is weak
            knowledge_gaps = []
            for domain, level in agent_knowledge.items():
                if level < 0.5:  # Below average knowledge
                    knowledge_gaps.append((domain, 0.5 - level))
            
            # Sort by gap size
            knowledge_gaps.sort(key=lambda x: x[1], reverse=True)
            
            # Propose knowledge transfer transactions
            for domain, gap in knowledge_gaps:
                if len(proposed_transactions) >= count:
                    break
                    
                # Find agents with high knowledge in this domain
                experts = []
                for node, node_data in self.deal_network.nodes(data=True):
                    if node_data.get("type") != "agent" or node == agent_id:
                        continue
                        
                    node_knowledge = self.economist.knowledge_model.agent_knowledge.get(node, {})
                    domain_level = node_knowledge.get(domain, 0.0)
                    
                    if domain_level > 0.7:  # Expert threshold
                        experts.append((node, domain_level))
                
                # Sort by expertise level
                experts.sort(key=lambda x: x[1], reverse=True)
                
                if experts:
                    best_expert, expertise_level = experts[0]
                    
                    # Calculate price based on knowledge market rate
                    knowledge_market = self.economist.markets.get("knowledge")
                    knowledge_price = 50.0  # Default price
                    
                    if knowledge_market:
                        market_data = knowledge_market.get_market_data()
                        knowledge_price = market_data.get("last_price", 50.0)
                    
                    # Propose knowledge transaction
                    proposed_transactions.append({
                        "resource_type": "knowledge",
                        "domain": domain,
                        "seller_id": best_expert,
                        "buyer_id": agent_id,
                        "quantity": 1.0,  # Knowledge transfer is a unit
                        "proposed_price": knowledge_price * expertise_level,  # Price scales with expertise
                        "total_value": knowledge_price * expertise_level,
                        "transaction_type": "knowledge_transfer"
                    })
        
        self.logger.info(f"Proposed {len(proposed_transactions)} market transactions for agent {agent_id}")
        
        return proposed_transactions
    
    async def visualize_market_network(self) -> Dict[str, Any]:
        """
        Generate network visualization data.
        
        Returns:
            Visualization data
        """
        G = self.deal_network
        
        # Extract nodes with type info
        nodes = []
        for node, data in G.nodes(data=True):
            node_type = data.get("type", "unknown")
            
            # Calculate size based on centrality/degree
            size = G.degree(node)
            
            # Create node data
            node_data = {
                "id": node,
                "type": node_type,
                "size": size,
                **{k: v for k, v in data.items() if k not in ["type"]}
            }
            
            nodes.append(node_data)
        
        # Extract edges
        edges = []
        for source, target, data in G.edges(data=True):
            edge_type = data.get("type", "unknown")
            
            # Calculate edge width based on weight/transactions
            width = data.get("weight", 1.0)
            if "transaction_volume" in data:
                width = min(5, max(1, data["transaction_volume"] / 1000))
            
            # Create edge data
            edge_data = {
                "source": source,
                "target": target,
                "type": edge_type,
                "width": width,
                **{k: v for k, v in data.items() if k not in ["type", "weight"]}
            }
            
            edges.append(edge_data)
        
        # Get community data from network
        try:
            communities = list(nx.community.greedy_modularity_communities(G.to_undirected()))
            community_mapping = {}
            for i, community in enumerate(communities):
                for node in community:
                    community_mapping[node] = i
            
            # Add community info to nodes
            for node in nodes:
                node["community"] = community_mapping.get(node["id"], 0)
        except:
            # Community detection might fail
            pass
        
        # Get economic agent network visualization
        agent_network_viz = self.economist.agent_network.get_network_visualization_data()
        
        # Return combined visualization data
        return {
            "nodes": nodes,
            "edges": edges,
            "agent_network": agent_network_viz,
            "stats": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "agent_count": sum(1 for n in nodes if n["type"] == "agent"),
                "deal_count": sum(1 for n in nodes if n["type"] == "deal"),
                "transaction_count": sum(1 for e in edges if e["type"] == "transaction")
            }
        }


async def integrate_economic_components(economist_agent: EconomistAgent) -> MarketNetworkIntegrator:
    """
    Integrate all economic components into a cohesive market network.
    
    Args:
        economist_agent: The EconomistAgent instance
        
    Returns:
        Configured MarketNetworkIntegrator
    """
    # Create integrator
    integrator = MarketNetworkIntegrator(economist_agent)
    
    # Initialize with sample agents if none exist
    if not integrator.deal_network.nodes:
        # Register demo agents
        await integrator.register_agent_with_market_network(
            agent_id="architect_agent",
            capabilities=["architecture_design", "system_design", "requirements_analysis"],
            resource_needs={
                "compute": 200.0,
                "memory": 400.0,
                "specialized_knowledge": 100.0
            },
            value_preferences={
                "technical": 0.7,
                "economic": 0.2,
                "security": 0.1
            },
            stakeholder_type="autonomous_agent",
            risk_tolerance=0.6
        )
        
        await integrator.register_agent_with_market_network(
            agent_id="developer_agent",
            capabilities=["code_generation", "testing", "debugging"],
            resource_needs={
                "compute": 300.0,
                "memory": 200.0,
                "specialized_knowledge": 50.0
            },
            value_preferences={
                "technical": 0.6,
                "economic": 0.3,
                "operational": 0.1
            },
            stakeholder_type="autonomous_agent",
            risk_tolerance=0.7
        )
        
        await integrator.register_agent_with_market_network(
            agent_id="verification_agent",
            capabilities=["testing", "verification", "security_analysis"],
            resource_needs={
                "compute": 150.0,
                "memory": 100.0,
                "specialized_knowledge": 80.0
            },
            value_preferences={
                "security": 0.6,
                "technical": 0.3,
                "operational": 0.1
            },
            stakeholder_type="autonomous_agent",
            risk_tolerance=0.5
        )
        
        # Create initial deals
        await integrator.create_deal_from_intent(
            problem_statement="Design and implement a secure API authentication system",
            value_dimensions=["technical", "security", "operational"],
            stakeholder_ids=["architect_agent", "developer_agent", "verification_agent"]
        )
    
    return integrator


def test_market_network_integration():
    """Run a test of the market network integration."""
    import asyncio
    from mac.economist_agent import EconomistAgent, create_economist
    
    async def run_test():
        # Create economist agent
        economist = create_economist(config_path=None)
        
        # Create integrator
        integrator = await integrate_economic_components(economist)
        
        # Generate a report
        report = await integrator.analyze_market_network()
        print(f"Market Network Analysis Report:")
        print(f"- System Health: {report['system_health']}")
        print(f"- Efficiency: {report['economic_metrics']['efficiency']:.2f}")
        print(f"- Deal Count: {report['deal_metrics']['deal_count']}")
        print(f"- Network Density: {report['network_metrics']['density']:.2f}")
        
        # Propose a transaction
        transactions = await integrator.propose_market_transactions("developer_agent")
        if transactions:
            print(f"\nProposed Transaction: {transactions[0]}")
        
        # Propose deals
        deals = await integrator.propose_optimal_deals("verification_agent")
        if deals:
            print(f"\nProposed Deal: {deals[0]['name']}")
        
        # Visualize network
        viz_data = await integrator.visualize_market_network()
        print(f"\nNetwork Visualization:")
        print(f"- Nodes: {viz_data['stats']['node_count']}")
        print(f"- Edges: {viz_data['stats']['edge_count']}")
        
        return report
    
    # Run the test
    loop = asyncio.get_event_loop()
    report = loop.run_until_complete(run_test())
    return report


if __name__ == "__main__":
    test_result = test_market_network_integration()
    print("\nTest completed successfully")