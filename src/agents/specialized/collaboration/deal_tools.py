"""
MCP Tools for Deal-based Collaboration.

This module provides MCP-compliant tools for working with the Deals framework.
"""
from typing import Dict, List, Any, Optional, Union
import json
import networkx as nx

from ..tools_base import StandardsCompliantTool
from ..standards_validation import StandardsValidator
from ..mcp_registry import register_tool

from .deals import Deal, Problem, Solution, Player, Transaction


class DealTools:
    """Collection of MCP-compliant tools for working with Deals."""

    @register_tool(
        name="create_deal",
        description="Create a new collaboration deal between agents",
        domains=["agent_collaboration", "deal_making"],
        standard="DealFramework"
    )
    def create_deal(
        name: str,
        description: str,
        domains: List[str],
        players: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Deal for agent collaboration.

        Args:
            name: Name of the deal
            description: Description of the deal purpose
            domains: List of domains the deal pertains to
            players: Optional list of initial players in the deal

        Returns:
            Dict representation of the created Deal
        """
        validator = StandardsValidator()
        
        # Validate inputs against deal framework standards
        validator.validate_field("deal_name", name, ["DealFramework"])
        validator.validate_field("deal_domains", domains, ["DealFramework"])
        
        deal = Deal(name=name, description=description, domains=domains)
        
        # Add initial players if provided
        if players:
            for player_data in players:
                player = Player(
                    name=player_data["name"],
                    role=player_data.get("role", "contributor"),
                    capabilities=player_data.get("capabilities", [])
                )
                deal.add_player(player)
        
        return deal.to_dict()

    @register_tool(
        name="add_problem",
        description="Add a problem to an existing deal",
        domains=["agent_collaboration", "deal_making"],
        standard="DealFramework"
    )
    def add_problem(
        deal_dict: Dict[str, Any],
        problem_name: str,
        problem_description: str,
        constraints: Optional[List[str]] = None,
        success_criteria: Optional[List[str]] = None,
        owner: Optional[str] = None
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

        Returns:
            Updated Deal dictionary
        """
        validator = StandardsValidator()
        
        # Validate problem definition against standards
        validator.validate_field("problem_definition", problem_description, ["DealFramework"])
        
        # Reconstruct the Deal object from dict
        deal = Deal.from_dict(deal_dict)
        
        # Create and add the problem
        problem = Problem(
            name=problem_name,
            description=problem_description,
            constraints=constraints or [],
            success_criteria=success_criteria or []
        )
        
        deal.add_problem(problem)
        
        # Assign owner if provided
        if owner:
            deal.assign_problem_owner(problem.id, owner)
        
        return deal.to_dict()

    @register_tool(
        name="propose_solution",
        description="Propose a solution to a problem in a deal",
        domains=["agent_collaboration", "deal_making"],
        standard="DealFramework"
    )
    def propose_solution(
        deal_dict: Dict[str, Any],
        problem_id: str,
        solution_name: str,
        solution_description: str,
        approach: str,
        proposed_by: str,
        resources_needed: Optional[List[str]] = None,
        estimated_effort: Optional[str] = None
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

        Returns:
            Updated Deal dictionary
        """
        validator = StandardsValidator()
        
        # Validate solution against standards
        validator.validate_field("solution_proposal", solution_description, ["DealFramework"])
        
        # Reconstruct the Deal object from dict
        deal = Deal.from_dict(deal_dict)
        
        # Create and add the solution
        solution = Solution(
            name=solution_name,
            description=solution_description,
            approach=approach,
            resources_needed=resources_needed or [],
            estimated_effort=estimated_effort or "Unknown"
        )
        
        # Add solution and link to problem
        deal.add_solution(solution, problem_id, proposed_by)
        
        return deal.to_dict()

    @register_tool(
        name="create_transaction",
        description="Create a transaction between players in a deal",
        domains=["agent_collaboration", "deal_making"],
        standard="DealFramework"
    )
    def create_transaction(
        deal_dict: Dict[str, Any],
        transaction_type: str,
        sender: str,
        receiver: str,
        resources: Dict[str, Any],
        solution_id: Optional[str] = None,
        conditions: Optional[List[str]] = None
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

        Returns:
            Updated Deal dictionary
        """
        validator = StandardsValidator()
        
        # Validate transaction against standards
        validator.validate_field("transaction_creation", transaction_type, ["DealFramework"])
        
        # Reconstruct the Deal object from dict
        deal = Deal.from_dict(deal_dict)
        
        # Create and add the transaction
        transaction = Transaction(
            transaction_type=transaction_type,
            sender=sender,
            receiver=receiver,
            resources=resources,
            conditions=conditions or []
        )
        
        # Add transaction and link to solution if provided
        deal.add_transaction(transaction, solution_id)
        
        return deal.to_dict()

    @register_tool(
        name="evaluate_solution",
        description="Evaluate a proposed solution against problem constraints",
        domains=["agent_collaboration", "deal_making"],
        standard="DealFramework"
    )
    def evaluate_solution(
        deal_dict: Dict[str, Any],
        solution_id: str,
        evaluator: str,
        meets_criteria: bool,
        evaluation_notes: str,
        suggested_improvements: Optional[List[str]] = None
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

        Returns:
            Updated Deal dictionary with evaluation results
        """
        validator = StandardsValidator()
        
        # Validate evaluation against standards
        validator.validate_field("solution_evaluation", evaluation_notes, ["DealFramework"])
        
        # Reconstruct the Deal object from dict
        deal = Deal.from_dict(deal_dict)
        
        # Record the evaluation
        deal.evaluate_solution(
            solution_id=solution_id,
            evaluator=evaluator,
            meets_criteria=meets_criteria,
            evaluation_notes=evaluation_notes,
            suggested_improvements=suggested_improvements or []
        )
        
        return deal.to_dict()

    @register_tool(
        name="visualize_deal",
        description="Generate a visualization of the deal graph",
        domains=["agent_collaboration", "deal_making"],
        standard="DealFramework"
    )
    def visualize_deal(
        deal_dict: Dict[str, Any],
        format: str = "text"
    ) -> str:
        """
        Generate a visualization of the deal graph.

        Args:
            deal_dict: Dictionary representation of a Deal
            format: Format of the visualization ("text", "json", or "dot")

        Returns:
            String representation of the deal visualization
        """
        # Reconstruct the Deal object from dict
        deal = Deal.from_dict(deal_dict)
        
        # Get the graph from the deal
        graph = deal.graph
        
        if format == "text":
            # Generate a text representation
            output = []
            output.append(f"DEAL: {deal.name}")
            output.append(f"Description: {deal.description}")
            output.append(f"Domains: {', '.join(deal.domains)}")
            output.append("\nPLAYERS:")
            
            for node, data in graph.nodes(data=True):
                if data.get('type') == 'player':
                    output.append(f"  - {data.get('name')} ({data.get('role')})")
            
            output.append("\nPROBLEMS:")
            for node, data in graph.nodes(data=True):
                if data.get('type') == 'problem':
                    output.append(f"  - {data.get('name')}")
                    output.append(f"    Description: {data.get('description')}")
                    
                    # Find owner if exists
                    for s, t, d in graph.edges(data=True):
                        if t == node and d.get('relationship') == 'owns':
                            owner = graph.nodes[s].get('name')
                            output.append(f"    Owner: {owner}")
            
            output.append("\nSOLUTIONS:")
            for node, data in graph.nodes(data=True):
                if data.get('type') == 'solution':
                    output.append(f"  - {data.get('name')}")
                    
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
            
            output.append("\nTRANSACTIONS:")
            for node, data in graph.nodes(data=True):
                if data.get('type') == 'transaction':
                    output.append(f"  - {data.get('transaction_type')}")
                    output.append(f"    Status: {data.get('status')}")
                    
                    # Find sender and receiver
                    sender = None
                    receiver = None
                    for s, t, d in graph.edges(data=True):
                        if t == node and d.get('relationship') == 'sends':
                            sender = graph.nodes[s].get('name')
                        if s == node and d.get('relationship') == 'receives':
                            receiver = graph.nodes[t].get('name')
                    
                    if sender and receiver:
                        output.append(f"    From {sender} to {receiver}")
            
            return "\n".join(output)
            
        elif format == "json":
            # Return a simplified JSON representation
            nodes = []
            for node, data in graph.nodes(data=True):
                nodes.append({
                    "id": node,
                    "type": data.get("type"),
                    "name": data.get("name", "Unknown"),
                    "data": {k: v for k, v in data.items() if k not in ["type", "name"]}
                })
                
            edges = []
            for s, t, data in graph.edges(data=True):
                edges.append({
                    "source": s,
                    "target": t,
                    "relationship": data.get("relationship", "unknown")
                })
                
            return json.dumps({
                "deal_name": deal.name,
                "nodes": nodes,
                "edges": edges
            }, indent=2)
            
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
                
                lines.append(f'  "{node}" [label="{name}", fillcolor="{color}"];')
            
            # Add edges with labels
            for s, t, data in graph.edges(data=True):
                relationship = data.get('relationship', '')
                lines.append(f'  "{s}" -> "{t}" [label="{relationship}"];')
            
            lines.append('}')
            return '\n'.join(lines)
            
        else:
            return f"Unsupported visualization format: {format}"

    @register_tool(
        name="finalize_deal",
        description="Finalize a deal after all requirements are met",
        domains=["agent_collaboration", "deal_making"],
        standard="DealFramework"
    )
    def finalize_deal(
        deal_dict: Dict[str, Any],
        finalized_by: str,
        require_human_review: bool = True
    ) -> Dict[str, Any]:
        """
        Finalize a deal after all requirements are met.

        Args:
            deal_dict: Dictionary representation of a Deal
            finalized_by: Name of the player finalizing the deal
            require_human_review: Whether human review is required before finalization

        Returns:
            Updated Deal dictionary with finalization status
        """
        validator = StandardsValidator()
        
        # Reconstruct the Deal object from dict
        deal = Deal.from_dict(deal_dict)
        
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
        
        # Check if human review is needed and required
        if require_human_review:
            deal_dict["status"] = "pending_human_review"
            deal_dict["finalized_by"] = finalized_by
            deal_dict["requires_human_approval"] = True
            return deal_dict
        else:
            # Finalize the deal
            deal.status = "finalized"
            deal.finalized_by = finalized_by
            deal.finalized_at = "current_timestamp"  # In a real implementation, use actual timestamp
            
            return deal.to_dict()