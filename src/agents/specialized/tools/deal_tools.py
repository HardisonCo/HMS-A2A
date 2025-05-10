#!/usr/bin/env python3
"""
MCP-Compliant Deal Tools

This module provides MCP-compliant tools for creating, managing, and visualizing
deal-based collaborations between specialized agents.
"""

import os
import sys
import json
import uuid
import logging
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
import networkx as nx
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from specialized_agents.collaboration.deals import Deal, Problem, Solution, Player, Transaction
from specialized_agents.standards_validation import StandardsValidator
from specialized_agents.tools.tool_interface import (
    tool_decorator, 
    ToolCategory, 
    BaseMCPTool,
    CollaborationTool,
    ToolContext
)

# Configure logging
logger = logging.getLogger(__name__)


class DealStatus(str, Enum):
    """Status of a deal."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DealCreateInput(BaseModel):
    """Input schema for creating a deal."""
    name: str
    description: str
    domains: List[str]
    players: Optional[List[Dict[str, Any]]] = None
    status: DealStatus = DealStatus.DRAFT
    metadata: Optional[Dict[str, Any]] = None


class ProblemInput(BaseModel):
    """Input schema for adding a problem."""
    deal_dict: Dict[str, Any]
    problem_name: str
    problem_description: str
    constraints: Optional[List[str]] = None
    success_criteria: Optional[List[str]] = None
    owner: Optional[str] = None


class SolutionInput(BaseModel):
    """Input schema for proposing a solution."""
    deal_dict: Dict[str, Any]
    problem_id: str
    solution_name: str
    solution_description: str
    approach: str
    proposed_by: str
    resources_needed: Optional[List[str]] = None
    estimated_effort: Optional[str] = None


class TransactionInput(BaseModel):
    """Input schema for creating a transaction."""
    deal_dict: Dict[str, Any]
    transaction_type: str
    sender: str
    receiver: str
    resources: Dict[str, Any]
    solution_id: Optional[str] = None
    conditions: Optional[List[str]] = None


class DealVisualizationInput(BaseModel):
    """Input schema for visualizing a deal."""
    deal_dict: Dict[str, Any]
    format: str = "text"
    include_metadata: bool = False


class DealEvaluationInput(BaseModel):
    """Input schema for evaluating a solution."""
    deal_dict: Dict[str, Any]
    solution_id: str
    evaluator: str
    meets_criteria: bool
    evaluation_notes: str
    suggested_improvements: Optional[List[str]] = None


class DealFinalizationInput(BaseModel):
    """Input schema for finalizing a deal."""
    deal_dict: Dict[str, Any]
    finalized_by: str
    require_human_review: bool = True


@tool_decorator(
    name="create_deal",
    description="Create a new collaboration deal between agents",
    tool_type="collaboration",
    collaboration_type="deal_creation",
    domains=["agent_collaboration", "deal_making"],
    standards=["DealFramework"],
    tags=["deal", "collaboration", "creation"],
    require_human_review=False
)
def create_deal(
    name: str,
    description: str,
    domains: List[str],
    players: Optional[List[Dict[str, Any]]] = None,
    status: str = "draft",
    metadata: Optional[Dict[str, Any]] = None,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Create a new Deal for agent collaboration.

    Args:
        name: Name of the deal
        description: Description of the deal purpose
        domains: List of domains the deal pertains to
        players: Optional list of initial players in the deal
        status: Initial status of the deal
        metadata: Additional metadata for the deal
        context: Tool execution context

    Returns:
        Dict representation of the created Deal
    """
    validator = StandardsValidator()
    
    # Validate inputs against deal framework standards
    validator.validate_field("deal_name", name, ["DealFramework"])
    validator.validate_field("deal_domains", domains, ["DealFramework"])
    
    # Create the deal with a unique ID if not provided in metadata
    if metadata is None:
        metadata = {}
    if "id" not in metadata:
        metadata["id"] = str(uuid.uuid4())
    if "created_at" not in metadata:
        metadata["created_at"] = datetime.now().isoformat()
    if "creator_domain" not in metadata and context:
        metadata["creator_domain"] = context.calling_domain
        
    # Create the deal
    deal = Deal(
        name=name, 
        description=description, 
        domains=domains, 
        status=status,
        metadata=metadata
    )
    
    # Add initial players if provided
    if players:
        for player_data in players:
            player = Player(
                name=player_data["name"],
                role=player_data.get("role", "contributor"),
                capabilities=player_data.get("capabilities", []),
                domain=player_data.get("domain", "general")
            )
            deal.add_player(player)
    
    return deal.to_dict()


@tool_decorator(
    name="add_problem",
    description="Add a problem to an existing deal",
    tool_type="collaboration",
    collaboration_type="deal_management",
    domains=["agent_collaboration", "deal_making"],
    standards=["DealFramework"],
    tags=["deal", "collaboration", "problem"],
    require_human_review=False
)
def add_problem(
    deal_dict: Dict[str, Any],
    problem_name: str,
    problem_description: str,
    constraints: Optional[List[str]] = None,
    success_criteria: Optional[List[str]] = None,
    owner: Optional[str] = None,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Add a problem to an existing deal.

    Args:
        deal_dict: Dictionary representation of a Deal
        problem_name: Name of the problem
        problem_description: Description of the problem
        constraints: Optional list of constraints
        success_criteria: Optional list of success criteria
        owner: Optional name of the problem owner (must be an existing player)
        context: Tool execution context

    Returns:
        Updated Deal dictionary
    """
    validator = StandardsValidator()
    
    # Validate problem definition against standards
    validator.validate_field("problem_definition", problem_description, ["DealFramework"])
    
    # Reconstruct the Deal object from dict
    deal = Deal.from_dict(deal_dict)
    
    # Check if the deal is in a state where problems can be added
    if deal.status not in ["draft", "in_progress"]:
        raise ValueError(f"Cannot add problems to a deal in '{deal.status}' status")
    
    # Create and add the problem with metadata
    problem = Problem(
        name=problem_name,
        description=problem_description,
        constraints=constraints or [],
        success_criteria=success_criteria or [],
        metadata={
            "created_at": datetime.now().isoformat(),
            "creator_domain": context.calling_domain if context else "unknown"
        }
    )
    
    deal.add_problem(problem)
    
    # Assign owner if provided
    if owner:
        deal.assign_problem_owner(problem.id, owner)
    
    # Update deal status if it was in draft
    if deal.status == "draft":
        deal.status = "in_progress"
        deal.metadata["updated_at"] = datetime.now().isoformat()
    
    return deal.to_dict()


@tool_decorator(
    name="propose_solution",
    description="Propose a solution to a problem in a deal",
    tool_type="collaboration",
    collaboration_type="deal_management",
    domains=["agent_collaboration", "deal_making"],
    standards=["DealFramework"],
    tags=["deal", "collaboration", "solution"],
    require_human_review=False
)
def propose_solution(
    deal_dict: Dict[str, Any],
    problem_id: str,
    solution_name: str,
    solution_description: str,
    approach: str,
    proposed_by: str,
    resources_needed: Optional[List[str]] = None,
    estimated_effort: Optional[str] = None,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Propose a solution to a problem in a deal.

    Args:
        deal_dict: Dictionary representation of a Deal
        problem_id: ID of the problem to solve
        solution_name: Name of the proposed solution
        solution_description: Description of the solution
        approach: Approach to be taken
        proposed_by: Name of the player proposing the solution
        resources_needed: Optional list of resources needed
        estimated_effort: Optional estimation of effort required
        context: Tool execution context

    Returns:
        Updated Deal dictionary
    """
    validator = StandardsValidator()
    
    # Validate solution against standards
    validator.validate_field("solution_proposal", solution_description, ["DealFramework"])
    
    # Reconstruct the Deal object from dict
    deal = Deal.from_dict(deal_dict)
    
    # Check if the deal is in a state where solutions can be added
    if deal.status not in ["in_progress"]:
        raise ValueError(f"Cannot add solutions to a deal in '{deal.status}' status")
    
    # Verify problem exists
    problem_exists = False
    for node, data in deal.graph.nodes(data=True):
        if data.get("type") == "problem" and node == problem_id:
            problem_exists = True
            break
    
    if not problem_exists:
        raise ValueError(f"Problem with ID {problem_id} not found in the deal")
    
    # Verify player exists
    player_exists = False
    for node, data in deal.graph.nodes(data=True):
        if data.get("type") == "player" and data.get("name") == proposed_by:
            player_exists = True
            break
    
    if not player_exists:
        raise ValueError(f"Player {proposed_by} not found in the deal")
    
    # Create and add the solution with metadata
    solution = Solution(
        name=solution_name,
        description=solution_description,
        approach=approach,
        resources_needed=resources_needed or [],
        estimated_effort=estimated_effort or "Unknown",
        metadata={
            "created_at": datetime.now().isoformat(),
            "proposer_domain": context.calling_domain if context else "unknown"
        }
    )
    
    # Add solution and link to problem
    deal.add_solution(solution, problem_id, proposed_by)
    
    # Update deal metadata
    deal.metadata["updated_at"] = datetime.now().isoformat()
    if "solution_count" not in deal.metadata:
        deal.metadata["solution_count"] = 0
    deal.metadata["solution_count"] += 1
    
    return deal.to_dict()


@tool_decorator(
    name="create_transaction",
    description="Create a transaction between players in a deal",
    tool_type="collaboration",
    collaboration_type="resource_exchange",
    domains=["agent_collaboration", "deal_making"],
    standards=["DealFramework"],
    tags=["deal", "collaboration", "transaction"],
    require_human_review=True
)
def create_transaction(
    deal_dict: Dict[str, Any],
    transaction_type: str,
    sender: str,
    receiver: str,
    resources: Dict[str, Any],
    solution_id: Optional[str] = None,
    conditions: Optional[List[str]] = None,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Create a transaction between players in a deal.

    Args:
        deal_dict: Dictionary representation of a Deal
        transaction_type: Type of transaction (e.g., "resource_exchange", "approval")
        sender: Name of the sender player
        receiver: Name of the receiver player
        resources: Dictionary of resources being exchanged
        solution_id: Optional ID of a solution this transaction relates to
        conditions: Optional list of conditions for the transaction
        context: Tool execution context

    Returns:
        Updated Deal dictionary
    """
    validator = StandardsValidator()
    
    # Validate transaction against standards
    validator.validate_field("transaction_creation", transaction_type, ["DealFramework"])
    
    # Reconstruct the Deal object from dict
    deal = Deal.from_dict(deal_dict)
    
    # Check if the deal is in a state where transactions can be added
    if deal.status not in ["in_progress"]:
        raise ValueError(f"Cannot add transactions to a deal in '{deal.status}' status")
    
    # Verify sender exists
    sender_exists = False
    for node, data in deal.graph.nodes(data=True):
        if data.get("type") == "player" and data.get("name") == sender:
            sender_exists = True
            break
    
    if not sender_exists:
        raise ValueError(f"Sender {sender} not found in the deal")
    
    # Verify receiver exists
    receiver_exists = False
    for node, data in deal.graph.nodes(data=True):
        if data.get("type") == "player" and data.get("name") == receiver:
            receiver_exists = True
            break
    
    if not receiver_exists:
        raise ValueError(f"Receiver {receiver} not found in the deal")
    
    # If solution_id is provided, verify it exists
    if solution_id:
        solution_exists = False
        for node, data in deal.graph.nodes(data=True):
            if data.get("type") == "solution" and node == solution_id:
                solution_exists = True
                break
        
        if not solution_exists:
            raise ValueError(f"Solution with ID {solution_id} not found in the deal")
    
    # Create and add the transaction with metadata
    transaction = Transaction(
        name=f"Transaction: {transaction_type}",
        transaction_type=transaction_type,
        amount=resources.get("amount", 0),
        from_player=sender,
        to_player=receiver,
        currency=resources.get("currency", "USD"),
        description=resources.get("description", ""),
        terms=conditions or [],
        related_resources=[resources],
        metadata={
            "created_at": datetime.now().isoformat(),
            "creator_domain": context.calling_domain if context else "unknown",
            "requires_approval": True
        }
    )
    
    # Add transaction and link to solution if provided
    deal.add_transaction(transaction, solution_id)
    
    # Update deal metadata
    deal.metadata["updated_at"] = datetime.now().isoformat()
    if "transaction_count" not in deal.metadata:
        deal.metadata["transaction_count"] = 0
    deal.metadata["transaction_count"] += 1
    
    return deal.to_dict()


@tool_decorator(
    name="evaluate_solution",
    description="Evaluate a proposed solution against problem constraints",
    tool_type="collaboration",
    collaboration_type="evaluation",
    domains=["agent_collaboration", "deal_making"],
    standards=["DealFramework"],
    tags=["deal", "collaboration", "evaluation"],
    require_human_review=False
)
def evaluate_solution(
    deal_dict: Dict[str, Any],
    solution_id: str,
    evaluator: str,
    meets_criteria: bool,
    evaluation_notes: str,
    suggested_improvements: Optional[List[str]] = None,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Evaluate a proposed solution against problem constraints.

    Args:
        deal_dict: Dictionary representation of a Deal
        solution_id: ID of the solution to evaluate
        evaluator: Name of the player evaluating the solution
        meets_criteria: Whether the solution meets success criteria
        evaluation_notes: Notes on the evaluation
        suggested_improvements: Optional list of suggested improvements
        context: Tool execution context

    Returns:
        Updated Deal dictionary with evaluation results
    """
    validator = StandardsValidator()
    
    # Validate evaluation against standards
    validator.validate_field("solution_evaluation", evaluation_notes, ["DealFramework"])
    
    # Reconstruct the Deal object from dict
    deal = Deal.from_dict(deal_dict)
    
    # Check if the deal is in a state where evaluations can be added
    if deal.status not in ["in_progress"]:
        raise ValueError(f"Cannot evaluate solutions in a deal with '{deal.status}' status")
    
    # Verify solution exists
    solution_exists = False
    solution_node = None
    for node, data in deal.graph.nodes(data=True):
        if data.get("type") == "solution" and node == solution_id:
            solution_exists = True
            solution_node = node
            break
    
    if not solution_exists:
        raise ValueError(f"Solution with ID {solution_id} not found in the deal")
    
    # Verify evaluator exists
    evaluator_exists = False
    evaluator_node = None
    for node, data in deal.graph.nodes(data=True):
        if data.get("type") == "player" and data.get("name") == evaluator:
            evaluator_exists = True
            evaluator_node = node
            break
    
    if not evaluator_exists:
        raise ValueError(f"Evaluator {evaluator} not found in the deal")
    
    # Get the problem for this solution
    problem_node = None
    for s, t, d in deal.graph.edges(data=True):
        if s == solution_node and d.get("relationship") == "solves":
            problem_node = t
            break
    
    if not problem_node:
        raise ValueError(f"Solution {solution_id} is not linked to any problem")
    
    # Add evaluation data to the solution
    deal.graph.nodes[solution_node]["evaluation"] = {
        "evaluator": evaluator,
        "meets_criteria": meets_criteria,
        "evaluation_notes": evaluation_notes,
        "suggested_improvements": suggested_improvements or [],
        "evaluation_date": datetime.now().isoformat(),
        "evaluator_domain": context.calling_domain if context else "unknown"
    }
    
    # Add evaluation edge
    deal.graph.add_edge(
        evaluator_node,
        solution_node,
        relationship="evaluated",
        date=datetime.now().isoformat()
    )
    
    # Update solution status
    if meets_criteria:
        deal.graph.nodes[solution_node]["status"] = "accepted"
    else:
        deal.graph.nodes[solution_node]["status"] = "needs_improvement"
    
    # Update deal metadata
    deal.metadata["updated_at"] = datetime.now().isoformat()
    
    return deal.to_dict()


@tool_decorator(
    name="visualize_deal",
    description="Generate a visualization of the deal graph",
    tool_type="collaboration",
    collaboration_type="visualization",
    domains=["agent_collaboration", "deal_making"],
    standards=["DealFramework"],
    tags=["deal", "collaboration", "visualization"],
    require_human_review=False
)
def visualize_deal(
    deal_dict: Dict[str, Any],
    format: str = "text",
    include_metadata: bool = False,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Generate a visualization of the deal graph.

    Args:
        deal_dict: Dictionary representation of a Deal
        format: Format of the visualization ("text", "json", or "dot")
        include_metadata: Whether to include detailed metadata in the visualization
        context: Tool execution context

    Returns:
        Visualization result in the specified format
    """
    # Reconstruct the Deal object from dict
    deal = Deal.from_dict(deal_dict)
    
    # Get the graph from the deal
    graph = deal.graph
    
    visualization = None
    
    if format == "text":
        # Generate a text representation
        output = []
        output.append(f"DEAL: {deal.name}")
        output.append(f"Description: {deal.description}")
        output.append(f"Status: {deal.status}")
        output.append(f"Domains: {', '.join(deal.domains)}")
        
        if include_metadata and deal.metadata:
            output.append("\nMETADATA:")
            for key, value in deal.metadata.items():
                output.append(f"  - {key}: {value}")
        
        output.append("\nPLAYERS:")
        for node, data in graph.nodes(data=True):
            if data.get('type') == 'player':
                output.append(f"  - {data.get('name')} ({data.get('role')})")
                if include_metadata and "capabilities" in data:
                    output.append(f"    Capabilities: {', '.join(data.get('capabilities', []))}")
        
        output.append("\nPROBLEMS:")
        for node, data in graph.nodes(data=True):
            if data.get('type') == 'problem':
                output.append(f"  - {data.get('name')}")
                output.append(f"    Description: {data.get('description')}")
                
                if data.get('constraints'):
                    output.append(f"    Constraints: {', '.join(data.get('constraints'))}")
                
                if data.get('success_criteria'):
                    output.append(f"    Success Criteria: {', '.join(data.get('success_criteria'))}")
                
                # Find owner if exists
                for s, t, d in graph.edges(data=True):
                    if t == node and d.get('relationship') == 'owns':
                        owner = graph.nodes[s].get('name')
                        output.append(f"    Owner: {owner}")
        
        output.append("\nSOLUTIONS:")
        for node, data in graph.nodes(data=True):
            if data.get('type') == 'solution':
                output.append(f"  - {data.get('name')}")
                output.append(f"    Description: {data.get('description')}")
                output.append(f"    Approach: {data.get('approach')}")
                
                if data.get('status'):
                    output.append(f"    Status: {data.get('status')}")
                
                # Find problem it solves
                for s, t, d in graph.edges(data=True):
                    if s == node and d.get('relationship') == 'solves':
                        problem = graph.nodes[t].get('name')
                        output.append(f"    Solves: {problem}")
                
                # Find who proposed it
                for s, t, d in graph.edges(data=True):
                    if t == node and d.get('relationship') == 'proposed':
                        proposer = graph.nodes[s].get('name')
                        output.append(f"    Proposed by: {proposer}")
                
                # Show evaluation if exists
                if 'evaluation' in data:
                    eval_data = data['evaluation']
                    output.append(f"    Evaluated by: {eval_data.get('evaluator')}")
                    output.append(f"    Meets criteria: {eval_data.get('meets_criteria')}")
                    output.append(f"    Evaluation notes: {eval_data.get('evaluation_notes')}")
        
        output.append("\nTRANSACTIONS:")
        for node, data in graph.nodes(data=True):
            if data.get('type') == 'transaction':
                output.append(f"  - {data.get('transaction_type')} ({data.get('name', 'Unnamed')})")
                output.append(f"    Status: {data.get('status')}")
                output.append(f"    Amount: {data.get('amount')} {data.get('currency')}")
                
                # Find sender and receiver
                sender = data.get('from_player')
                receiver = data.get('to_player')
                
                if sender and receiver:
                    output.append(f"    From {sender} to {receiver}")
                
                if data.get('description'):
                    output.append(f"    Description: {data.get('description')}")
        
        visualization = "\n".join(output)
        
    elif format == "json":
        # Return a structured JSON representation
        nodes = []
        for node, data in graph.nodes(data=True):
            node_data = {
                "id": node,
                "type": data.get("type"),
                "name": data.get("name", "Unknown"),
                "data": {k: v for k, v in data.items() if k not in ["type", "name"]}
            }
            nodes.append(node_data)
            
        edges = []
        for s, t, data in graph.edges(data=True):
            edge_data = {
                "source": s,
                "target": t,
                "relationship": data.get("relationship", "unknown")
            }
            if include_metadata:
                edge_data["data"] = {k: v for k, v in data.items() if k != "relationship"}
            edges.append(edge_data)
            
        deal_data = {
            "deal_name": deal.name,
            "deal_description": deal.description,
            "deal_status": deal.status,
            "deal_domains": deal.domains,
            "nodes": nodes,
            "edges": edges
        }
        
        if include_metadata:
            deal_data["metadata"] = deal.metadata
        
        visualization = deal_data
        
    elif format == "dot":
        # Generate a DOT format for Graphviz
        lines = ['digraph DealGraph {']
        lines.append('  rankdir=LR;')
        lines.append('  node [shape=box, style=filled];')
        
        # Add nodes with different colors by type
        for node, data in graph.nodes(data=True):
            node_type = data.get('type', 'unknown')
            name = data.get('name', node)
            
            if node_type == 'player':
                color = 'lightblue'
            elif node_type == 'problem':
                color = 'salmon'
            elif node_type == 'solution':
                color = 'lightgreen'
            elif node_type == 'transaction':
                color = 'lightyellow'
            else:
                color = 'white'
            
            # Add status to label if available
            label = name
            if 'status' in data:
                label = f"{name} ({data['status']})"
            
            lines.append(f'  "{node}" [label="{label}", fillcolor="{color}"];')
        
        # Add edges with labels
        for s, t, data in graph.edges(data=True):
            relationship = data.get('relationship', '')
            lines.append(f'  "{s}" -> "{t}" [label="{relationship}"];')
        
        lines.append('}')
        visualization = '\n'.join(lines)
        
    else:
        raise ValueError(f"Unsupported visualization format: {format}")
    
    # Return result with appropriate type based on format
    if format == "json":
        return visualization
    else:
        return {"visualization": visualization, "format": format}


@tool_decorator(
    name="finalize_deal",
    description="Finalize a deal after all requirements are met",
    tool_type="collaboration",
    collaboration_type="deal_management",
    domains=["agent_collaboration", "deal_making"],
    standards=["DealFramework"],
    tags=["deal", "collaboration", "finalization"],
    require_human_review=True
)
def finalize_deal(
    deal_dict: Dict[str, Any],
    finalized_by: str,
    require_human_review: bool = True,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Finalize a deal after all requirements are met.

    Args:
        deal_dict: Dictionary representation of a Deal
        finalized_by: Name of the player finalizing the deal
        require_human_review: Whether human review is required before finalization
        context: Tool execution context

    Returns:
        Updated Deal dictionary with finalization status
    """
    validator = StandardsValidator()
    
    # Reconstruct the Deal object from dict
    deal = Deal.from_dict(deal_dict)
    
    # Check if the deal is in a state where it can be finalized
    if deal.status not in ["in_progress"]:
        raise ValueError(f"Cannot finalize a deal with '{deal.status}' status")
    
    # Verify finalizer exists
    finalizer_exists = False
    for node, data in deal.graph.nodes(data=True):
        if data.get("type") == "player" and data.get("name") == finalized_by:
            finalizer_exists = True
            break
    
    if not finalizer_exists:
        raise ValueError(f"Finalizer {finalized_by} not found in the deal")
    
    # Check if all problems have solutions
    problems_without_solutions = []
    for node, data in deal.graph.nodes(data=True):
        if data.get('type') == 'problem':
            has_solution = False
            for s, t, d in deal.graph.edges(data=True):
                if t == node and d.get('relationship') == 'solves':
                    has_solution = True
                    break
            
            if not has_solution:
                problems_without_solutions.append(data.get('name'))
    
    if problems_without_solutions:
        problem_list = ", ".join(problems_without_solutions)
        validator.add_violation(
            standard="DealFramework",
            rule="finalization",
            message=f"Cannot finalize deal: Problems without solutions: {problem_list}",
            severity="high"
        )
        
        # Return deal with validation errors
        deal_dict["validation_errors"] = validator.get_violations()
        return deal_dict
    
    # Check if all transactions are approved
    pending_transactions = []
    for node, data in deal.graph.nodes(data=True):
        if data.get('type') == 'transaction' and data.get('status') == 'pending':
            pending_transactions.append(data.get('name', node))
    
    if pending_transactions:
        transaction_list = ", ".join(pending_transactions)
        validator.add_violation(
            standard="DealFramework",
            rule="finalization",
            message=f"Cannot finalize deal: Pending transactions: {transaction_list}",
            severity="medium"
        )
        
        # Return deal with validation errors
        deal_dict["validation_errors"] = validator.get_violations()
        return deal_dict
    
    # Check if human review is needed and required
    if require_human_review:
        deal.status = "pending_review"
        deal.metadata["finalized_by"] = finalized_by
        deal.metadata["finalization_requested_at"] = datetime.now().isoformat()
        deal.metadata["requires_human_approval"] = True
        deal.metadata["finalizer_domain"] = context.calling_domain if context else "unknown"
        
        return deal.to_dict()
    else:
        # Finalize the deal
        deal.status = "completed"
        deal.metadata["finalized_by"] = finalized_by
        deal.metadata["finalized_at"] = datetime.now().isoformat()
        deal.metadata["finalizer_domain"] = context.calling_domain if context else "unknown"
        
        return deal.to_dict()


class DealToolsRegistry:
    """Registry of MCP-compliant deal tools."""
    
    @staticmethod
    def register_tools():
        """Register all deal tools with the MCP Tool Registry."""
        from specialized_agents.tools.mcp_registry import registry
        
        # The tools are registered via decorators, but we can explicitly add them here if needed
        # Additional initialization can be done here
        
        logger.info("Deal tools registered with MCP Tool Registry")
        
        # Return list of registered tool names
        return [
            "create_deal",
            "add_problem",
            "propose_solution",
            "create_transaction",
            "evaluate_solution",
            "visualize_deal",
            "finalize_deal"
        ]


# Register tools when module is imported
DealToolsRegistry.register_tools()