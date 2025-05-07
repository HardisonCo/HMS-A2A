"""
Deals Framework for Agent Collaboration

This module implements the Deals framework for structured collaboration between
specialized agents, migrated from HMS-SME.
"""

import uuid
from typing import Dict, Any, List, Optional, Set, Union
from datetime import datetime
from enum import Enum
import networkx as nx
import logging

logger = logging.getLogger(__name__)


class DealStatus(str, Enum):
    """Status of a deal."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Deal:
    """
    A Deal represents a structured collaboration between multiple specialized agents.
    
    It contains problems, solutions, players, and transactions that form a graph of
    relationships and dependencies for complex agent collaboration.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        participants: List[str],
        deal_type: str = "standard",
        id: Optional[str] = None,
        domains: Optional[List[str]] = None,
        standards: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a new Deal.
        
        Args:
            name: Name of the deal
            description: Description of the deal
            participants: List of participant agent domains
            deal_type: Type of deal (standard, collaboration, etc.)
            id: Optional deal ID (generated if not provided)
            domains: Optional list of business domains this deal covers
            standards: Optional list of standards this deal should comply with
            metadata: Optional additional metadata
        """
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.participants = participants.copy()
        self.deal_type = deal_type
        self.domains = domains or []
        self.standards = standards or []
        self.status = DealStatus.DRAFT
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.finalized_by = None
        self.finalized_at = None
        self.metadata = metadata or {}
        
        # Initialize collections
        self.problems: Dict[str, Problem] = {}
        self.solutions: Dict[str, Solution] = {}
        self.players: Dict[str, Player] = {}
        self.transactions: List[Transaction] = []
        
        # Context objects for deal navigation
        self.context = {
            "deal_phase": "initialization",
            "current_focus": None,
            "history": [],
            "validation_errors": []
        }
        
        # Initialize graph
        self.graph = nx.DiGraph()
        self.graph.add_node(self.id, type="deal", name=self.name, description=self.description)
        
        # Initialize players for all participants
        for participant in participants:
            player = Player(
                agent_id=participant,
                name=f"{participant.capitalize()} Agent",
                role="participant"
            )
            self.add_player(player)
    
    def add_problem(self, problem: 'Problem') -> None:
        """Add a problem to the deal.
        
        Args:
            problem: The problem to add
        """
        self.problems[problem.id] = problem
        self.updated_at = datetime.now().isoformat()
        
        # Update graph
        self.graph.add_node(problem.id, type="problem", name=problem.name)
        self.graph.add_edge(self.id, problem.id, type="has_problem")
    
    def add_solution(self, solution: 'Solution') -> None:
        """Add a solution to the deal.
        
        Args:
            solution: The solution to add
        """
        self.solutions[solution.id] = solution
        self.updated_at = datetime.now().isoformat()
        
        # Update graph
        self.graph.add_node(solution.id, type="solution", name=solution.name)
        
        # If this solution addresses a problem, add that edge
        if solution.problem_id and solution.problem_id in self.problems:
            self.graph.add_edge(solution.id, solution.problem_id, type="addresses")
    
    def add_player(self, player: 'Player') -> None:
        """Add a player to the deal.
        
        Args:
            player: The player to add
        """
        self.players[player.id] = player
        self.updated_at = datetime.now().isoformat()
        
        # Update graph
        self.graph.add_node(player.id, type="player", name=player.name)
        self.graph.add_edge(self.id, player.id, type="has_player")
    
    def add_transaction(self, transaction: 'Transaction') -> None:
        """Add a transaction to the deal.
        
        Args:
            transaction: The transaction to add
        """
        self.transactions.append(transaction)
        self.updated_at = datetime.now().isoformat()
        
        # Update graph
        self.graph.add_node(transaction.id, type="transaction", name=transaction.name)
        
        # Add edges for from/to players
        if transaction.from_player in self.players:
            self.graph.add_edge(
                transaction.from_player, 
                transaction.id,
                type="initiates"
            )
        
        if transaction.to_player in self.players:
            self.graph.add_edge(
                transaction.id,
                transaction.to_player,
                type="receives"
            )
    
    def activate(self) -> None:
        """Activate the deal."""
        self.status = DealStatus.ACTIVE
        self.updated_at = datetime.now().isoformat()
    
    def complete(self) -> None:
        """Mark the deal as completed."""
        self.status = DealStatus.COMPLETED
        self.updated_at = datetime.now().isoformat()
    
    def cancel(self) -> None:
        """Cancel the deal."""
        self.status = DealStatus.CANCELLED
        self.updated_at = datetime.now().isoformat()
    
    def get_graph(self) -> nx.DiGraph:
        """Get the deal graph.
        
        Returns:
            Directed graph representing the deal
        """
        return self.graph
    
    def advance_phase(self, new_phase: str) -> None:
        """Advance the deal to a new phase.
        
        Args:
            new_phase: The new phase to advance to
        """
        valid_phases = [
            "initialization",
            "problem_definition",
            "solution_development",
            "negotiation",
            "execution",
            "evaluation",
            "finalization"
        ]
        
        if new_phase not in valid_phases:
            raise ValueError(f"Invalid phase: {new_phase}. Valid phases are: {', '.join(valid_phases)}")
        
        # Record history
        self.context["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "phase_change",
            "from": self.context["deal_phase"],
            "to": new_phase
        })
        
        # Update phase
        self.context["deal_phase"] = new_phase
        self.updated_at = datetime.now().isoformat()
        
        # Update graph
        self.graph.nodes[self.id]["phase"] = new_phase
    
    def set_focus(self, focus_id: str, focus_type: str) -> None:
        """Set the current focus of the deal.
        
        Args:
            focus_id: ID of the node to focus on
            focus_type: Type of focus (problem, solution, player, transaction)
        """
        # Record history
        self.context["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "focus_change",
            "from": self.context["current_focus"],
            "to": {"id": focus_id, "type": focus_type}
        })
        
        # Update focus
        self.context["current_focus"] = {"id": focus_id, "type": focus_type}
        self.updated_at = datetime.now().isoformat()
    
    def validate_standards_compliance(self) -> bool:
        """Validate that the deal complies with all applicable standards.
        
        Returns:
            True if compliant, False otherwise
        """
        # Clear previous validation errors
        self.context["validation_errors"] = []
        
        # Import validator here to avoid circular imports
        from specialized_agents.standards_validation import StandardsValidator
        validator = StandardsValidator()
        
        # Validate against each standard
        for standard in self.standards:
            # Validate deal structure
            validation_result = validator.validate_structure(self, standard)
            if not validation_result.valid:
                self.context["validation_errors"].extend(validation_result.violations)
        
        # Return True if no validation errors
        return len(self.context["validation_errors"]) == 0
    
    def assign_problem_owner(self, problem_id: str, player_id: str) -> None:
        """Assign a player as the owner of a problem.
        
        Args:
            problem_id: ID of the problem
            player_id: ID of the player
        """
        if problem_id not in self.problems:
            raise ValueError(f"Problem {problem_id} not found in deal")
        
        if player_id not in self.players:
            raise ValueError(f"Player {player_id} not found in deal")
        
        # Check if problem already has an owner
        for s, t, d in self.graph.edges(data=True):
            if t == problem_id and d.get("relationship") == "owns":
                # Remove existing ownership edge
                self.graph.remove_edge(s, t)
                break
        
        # Add ownership edge
        self.graph.add_edge(player_id, problem_id, relationship="owns")
        self.updated_at = datetime.now().isoformat()
    
    def assign_solution_owner(self, solution_id: str, player_id: str) -> None:
        """Assign a player as the owner of a solution.
        
        Args:
            solution_id: ID of the solution
            player_id: ID of the player
        """
        if solution_id not in self.solutions:
            raise ValueError(f"Solution {solution_id} not found in deal")
        
        if player_id not in self.players:
            raise ValueError(f"Player {player_id} not found in deal")
        
        # Check if solution already has an owner
        for s, t, d in self.graph.edges(data=True):
            if t == solution_id and d.get("relationship") == "owns":
                # Remove existing ownership edge
                self.graph.remove_edge(s, t)
                break
        
        # Add ownership edge
        self.graph.add_edge(player_id, solution_id, relationship="owns")
        self.updated_at = datetime.now().isoformat()
    
    def link_solution_to_problem(self, solution_id: str, problem_id: str) -> None:
        """Link a solution to a problem.
        
        Args:
            solution_id: ID of the solution
            problem_id: ID of the problem
        """
        if solution_id not in self.solutions:
            raise ValueError(f"Solution {solution_id} not found in deal")
        
        if problem_id not in self.problems:
            raise ValueError(f"Problem {problem_id} not found in deal")
        
        # Add solves edge
        self.graph.add_edge(solution_id, problem_id, relationship="solves")
        self.updated_at = datetime.now().isoformat()
    
    def evaluate_solution(
        self,
        solution_id: str,
        evaluator: str,
        meets_criteria: bool,
        evaluation_notes: str,
        suggested_improvements: Optional[List[str]] = None
    ) -> None:
        """Evaluate a solution.
        
        Args:
            solution_id: ID of the solution to evaluate
            evaluator: ID of the player evaluating the solution
            meets_criteria: Whether the solution meets the success criteria
            evaluation_notes: Notes on the evaluation
            suggested_improvements: Optional list of suggested improvements
        """
        if solution_id not in self.solutions:
            raise ValueError(f"Solution {solution_id} not found in deal")
        
        if evaluator not in self.players:
            raise ValueError(f"Player {evaluator} not found in deal")
        
        # Add evaluation to solution metadata
        solution = self.solutions[solution_id]
        
        if "evaluations" not in solution.metadata:
            solution.metadata["evaluations"] = []
        
        solution.metadata["evaluations"].append({
            "evaluator": evaluator,
            "timestamp": datetime.now().isoformat(),
            "meets_criteria": meets_criteria,
            "notes": evaluation_notes,
            "suggested_improvements": suggested_improvements or []
        })
        
        # Add evaluation edge to graph
        self.graph.add_edge(
            evaluator,
            solution_id,
            relationship="evaluated",
            meets_criteria=meets_criteria,
            timestamp=datetime.now().isoformat()
        )
        
        # Update solution in graph
        if "evaluations" not in self.graph.nodes[solution_id]:
            self.graph.nodes[solution_id]["evaluations"] = []
        
        self.graph.nodes[solution_id]["evaluations"].append({
            "evaluator": evaluator,
            "meets_criteria": meets_criteria,
            "timestamp": datetime.now().isoformat()
        })
        
        self.updated_at = datetime.now().isoformat()
    
    def export_graph(self, format: str = "networkx") -> Any:
        """Export the deal graph in various formats.
        
        Args:
            format: Format to export the graph in ("networkx", "json", "dot")
            
        Returns:
            Graph representation in the specified format
        """
        if format == "networkx":
            return self.graph
        
        elif format == "json":
            # Convert to JSON-serializable format
            nodes = []
            for node, data in self.graph.nodes(data=True):
                nodes.append({
                    "id": node,
                    "type": data.get("type", "unknown"),
                    "name": data.get("name", "unnamed"),
                    **{k: v for k, v in data.items() if k not in ["type", "name"]}
                })
            
            edges = []
            for s, t, data in self.graph.edges(data=True):
                edges.append({
                    "source": s,
                    "target": t,
                    "relationship": data.get("relationship", "related"),
                    **{k: v for k, v in data.items() if k != "relationship"}
                })
            
            return {"nodes": nodes, "edges": edges}
        
        elif format == "dot":
            # Generate DOT format for visualization
            lines = ['digraph DealGraph {']
            lines.append('  rankdir=LR;')
            lines.append('  node [shape=box, style=filled];')
            
            # Add nodes with colors by type
            for node, data in self.graph.nodes(data=True):
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
            for s, t, data in self.graph.edges(data=True):
                relationship = data.get('relationship', '')
                lines.append(f'  "{s}" -> "{t}" [label="{relationship}"];')
            
            lines.append('}')
            return '\n'.join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
    def finalize(self, finalized_by: str) -> bool:
        """Finalize the deal.
        
        Args:
            finalized_by: ID of the player finalizing the deal
            
        Returns:
            True if finalization was successful, False otherwise
        """
        if finalized_by not in self.players:
            raise ValueError(f"Player {finalized_by} not found in deal")
        
        # Validate standards compliance
        if not self.validate_standards_compliance():
            return False
        
        # Ensure all problems have solutions
        for problem_id in self.problems:
            has_solution = False
            for s, t, d in self.graph.edges(data=True):
                if t == problem_id and d.get("relationship") == "solves":
                    has_solution = True
                    break
            
            if not has_solution:
                self.context["validation_errors"].append({
                    "code": "NO_SOLUTION",
                    "message": f"Problem {self.problems[problem_id].name} has no solution",
                    "severity": "error"
                })
                return False
        
        # Update deal status and metadata
        self.status = DealStatus.COMPLETED
        self.finalized_by = finalized_by
        self.finalized_at = datetime.now().isoformat()
        self.updated_at = self.finalized_at
        
        # Update graph
        self.graph.nodes[self.id]["status"] = "completed"
        self.graph.nodes[self.id]["finalized_by"] = finalized_by
        self.graph.nodes[self.id]["finalized_at"] = self.finalized_at
        
        # Add finalization edge
        self.graph.add_edge(
            finalized_by,
            self.id,
            relationship="finalized",
            timestamp=self.finalized_at
        )
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the deal to a dictionary.
        
        Returns:
            Dictionary representation of the deal
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "participants": self.participants,
            "deal_type": self.deal_type,
            "domains": self.domains,
            "standards": self.standards,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "finalized_by": self.finalized_by,
            "finalized_at": self.finalized_at,
            "problems": [p.to_dict() for p in self.problems.values()],
            "solutions": [s.to_dict() for s in self.solutions.values()],
            "players": [p.to_dict() for p in self.players.values()],
            "transactions": [t.to_dict() for t in self.transactions],
            "context": self.context,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Deal':
        """Create a Deal from a dictionary.
        
        Args:
            data: Dictionary containing deal data
            
        Returns:
            Deal instance
        """
        # Create deal with basic attributes
        deal = cls(
            name=data["name"],
            description=data["description"],
            participants=data["participants"],
            deal_type=data.get("deal_type", "standard"),
            id=data["id"],
            domains=data.get("domains", []),
            standards=data.get("standards", []),
            metadata=data.get("metadata", {})
        )
        
        # Set status and timestamps
        deal.status = data["status"]
        deal.created_at = data["created_at"]
        deal.updated_at = data["updated_at"]
        deal.finalized_by = data.get("finalized_by")
        deal.finalized_at = data.get("finalized_at")
        
        # Set context
        if "context" in data:
            deal.context = data["context"]
        
        # Add problems
        for problem_data in data.get("problems", []):
            problem = Problem.from_dict(problem_data)
            deal.problems[problem.id] = problem
            deal.graph.add_node(
                problem.id, 
                type="problem", 
                name=problem.name,
                description=problem.description
            )
            deal.graph.add_edge(deal.id, problem.id, relationship="has_problem")
        
        # Add solutions
        for solution_data in data.get("solutions", []):
            solution = Solution.from_dict(solution_data)
            deal.solutions[solution.id] = solution
            deal.graph.add_node(
                solution.id, 
                type="solution", 
                name=solution.name,
                description=solution.description
            )
            
            # Link solution to problem if problem_id is set
            if solution.problem_id and solution.problem_id in deal.problems:
                deal.graph.add_edge(solution.id, solution.problem_id, relationship="solves")
        
        # Add players
        for player_data in data.get("players", []):
            player = Player.from_dict(player_data)
            deal.players[player.id] = player
            deal.graph.add_node(
                player.id, 
                type="player", 
                name=player.name,
                role=player.role
            )
            deal.graph.add_edge(deal.id, player.id, relationship="has_player")
        
        # Add transactions
        for transaction_data in data.get("transactions", []):
            transaction = Transaction.from_dict(transaction_data)
            deal.transactions.append(transaction)
            deal.graph.add_node(
                transaction.id, 
                type="transaction", 
                name=transaction.name,
                transaction_type=transaction.transaction_type,
                status=transaction.status
            )
            
            # Add edges for from/to players
            if transaction.from_player in deal.players:
                deal.graph.add_edge(
                    transaction.from_player, 
                    transaction.id,
                    relationship="initiates"
                )
            
            if transaction.to_player in deal.players:
                deal.graph.add_edge(
                    transaction.id,
                    transaction.to_player,
                    relationship="receives"
                )
        
        return deal


class Problem:
    """
    A Problem represents a business or domain problem to be solved within a deal.
    
    It contains context, events, domain-specific models, and a knowledge graph.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        problem_type: str = "general",
        domain: str = "general",
        id: Optional[str] = None,
        complexity: str = "moderate",
        urgency: str = "normal",
        impact_level: str = "medium",
        stakeholders: Optional[List[Dict[str, Any]]] = None,
        temporal_factors: Optional[Dict[str, Any]] = None,
        uncertainty_level: str = "medium",
        resources_required: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        success_criteria: Optional[List[str]] = None,
        standards: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a new Problem.
        
        Args:
            name: Name of the problem
            description: Description of the problem
            problem_type: Type of problem
            domain: Problem domain
            id: Optional problem ID (generated if not provided)
            complexity: Problem complexity
            urgency: Problem urgency
            impact_level: Problem impact level
            stakeholders: Optional list of stakeholders
            temporal_factors: Optional temporal factors
            uncertainty_level: Uncertainty level
            resources_required: Optional list of required resources
            constraints: Optional list of constraints
            success_criteria: Optional list of success criteria
            standards: Optional list of standards this problem should comply with
            metadata: Optional additional metadata
        """
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.problem_type = problem_type
        self.domain = domain
        self.complexity = complexity
        self.urgency = urgency
        self.impact_level = impact_level
        self.stakeholders = stakeholders or []
        self.temporal_factors = temporal_factors or {}
        self.uncertainty_level = uncertainty_level
        self.resources_required = resources_required or []
        self.constraints = constraints or []
        self.success_criteria = success_criteria or []
        self.standards = standards or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.owner_id = None
        self.status = "open"  # open, in_progress, solved, cancelled
        
        # Initialize context, events, and model as simple dicts
        self.context = {}
        self.events = []
        self.model = {}
        
        # Initialize graph
        self.graph = nx.DiGraph()
        self.graph.add_node(
            self.id, 
            type="problem", 
            name=self.name, 
            description=self.description,
            problem_type=self.problem_type,
            domain=self.domain,
            status=self.status
        )
    
    def add_context(self, context: Dict[str, Any]) -> None:
        """Add context to the problem.
        
        Args:
            context: The context to add
        """
        self.context.update(context)
        self.updated_at = datetime.now().isoformat()
    
    def add_event(self, event: Dict[str, Any]) -> None:
        """Add an event to the problem.
        
        Args:
            event: The event to add
        """
        event_with_timestamp = {
            "timestamp": datetime.now().isoformat(),
            **event
        }
        self.events.append(event_with_timestamp)
        self.updated_at = datetime.now().isoformat()
        
        # Add to graph
        event_id = str(uuid.uuid4())
        self.graph.add_node(
            event_id,
            type="event",
            name=event.get("name", "Event"),
            **event_with_timestamp
        )
        self.graph.add_edge(event_id, self.id, relationship="related_to")
    
    def update_model(self, model: Dict[str, Any]) -> None:
        """Update the problem model.
        
        Args:
            model: The model data to update
        """
        self.model.update(model)
        self.updated_at = datetime.now().isoformat()
    
    def set_owner(self, owner_id: str) -> None:
        """Set the owner of the problem.
        
        Args:
            owner_id: ID of the player who owns the problem
        """
        self.owner_id = owner_id
        self.updated_at = datetime.now().isoformat()
        
        # Update graph
        self.graph.nodes[self.id]["owner_id"] = owner_id
    
    def set_status(self, status: str) -> None:
        """Set the status of the problem.
        
        Args:
            status: New status (open, in_progress, solved, cancelled)
        """
        valid_statuses = ["open", "in_progress", "solved", "cancelled"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Valid statuses are: {', '.join(valid_statuses)}")
        
        self.status = status
        self.updated_at = datetime.now().isoformat()
        
        # Add event
        self.add_event({
            "type": "status_change",
            "from": self.status,
            "to": status
        })
        
        # Update graph
        self.graph.nodes[self.id]["status"] = status
    
    def add_success_criterion(self, criterion: str) -> None:
        """Add a success criterion to the problem.
        
        Args:
            criterion: The success criterion to add
        """
        if criterion not in self.success_criteria:
            self.success_criteria.append(criterion)
            self.updated_at = datetime.now().isoformat()
    
    def add_constraint(self, constraint: str) -> None:
        """Add a constraint to the problem.
        
        Args:
            constraint: The constraint to add
        """
        if constraint not in self.constraints:
            self.constraints.append(constraint)
            self.updated_at = datetime.now().isoformat()
    
    def add_resource_requirement(self, resource: str) -> None:
        """Add a resource requirement to the problem.
        
        Args:
            resource: The resource requirement to add
        """
        if resource not in self.resources_required:
            self.resources_required.append(resource)
            self.updated_at = datetime.now().isoformat()
    
    def add_stakeholder(self, stakeholder: Dict[str, Any]) -> None:
        """Add a stakeholder to the problem.
        
        Args:
            stakeholder: The stakeholder to add
        """
        self.stakeholders.append(stakeholder)
        self.updated_at = datetime.now().isoformat()
    
    def validate_standards_compliance(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate that the problem complies with all applicable standards.
        
        Returns:
            Tuple of (is_valid, violations)
        """
        # Import validator here to avoid circular imports
        from specialized_agents.standards_validation import StandardsValidator
        validator = StandardsValidator()
        
        violations = []
        
        # Validate against each standard
        for standard in self.standards:
            # Validate problem structure
            validation_result = validator.validate(self.to_dict(), standard)
            if not validation_result.valid:
                violations.extend(validation_result.violations)
        
        return len(violations) == 0, violations
    
    def export_graph(self, format: str = "networkx") -> Any:
        """Export the problem graph in various formats.
        
        Args:
            format: Format to export the graph in ("networkx", "json", "dot")
            
        Returns:
            Graph representation in the specified format
        """
        if format == "networkx":
            return self.graph
        
        elif format == "json":
            # Convert to JSON-serializable format
            nodes = []
            for node, data in self.graph.nodes(data=True):
                nodes.append({
                    "id": node,
                    "type": data.get("type", "unknown"),
                    "name": data.get("name", "unnamed"),
                    **{k: v for k, v in data.items() if k not in ["type", "name"]}
                })
            
            edges = []
            for s, t, data in self.graph.edges(data=True):
                edges.append({
                    "source": s,
                    "target": t,
                    "relationship": data.get("relationship", "related"),
                    **{k: v for k, v in data.items() if k != "relationship"}
                })
            
            return {"nodes": nodes, "edges": edges}
        
        elif format == "dot":
            # Generate DOT format for visualization
            lines = ['digraph ProblemGraph {']
            lines.append('  rankdir=LR;')
            lines.append('  node [shape=box, style=filled];')
            
            # Add nodes with colors by type
            for node, data in self.graph.nodes(data=True):
                node_type = data.get('type', 'unknown')
                name = data.get('name', node)
                
                if node_type == 'problem':
                    color = 'salmon'
                elif node_type == 'event':
                    color = 'lightblue'
                else:
                    color = 'white'
                
                lines.append(f'  "{node}" [label="{name}", fillcolor="{color}"];')
            
            # Add edges with labels
            for s, t, data in self.graph.edges(data=True):
                relationship = data.get('relationship', '')
                lines.append(f'  "{s}" -> "{t}" [label="{relationship}"];')
            
            lines.append('}')
            return '\n'.join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the problem to a dictionary.
        
        Returns:
            Dictionary representation of the problem
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "problem_type": self.problem_type,
            "domain": self.domain,
            "complexity": self.complexity,
            "urgency": self.urgency,
            "impact_level": self.impact_level,
            "stakeholders": self.stakeholders,
            "temporal_factors": self.temporal_factors,
            "uncertainty_level": self.uncertainty_level,
            "resources_required": self.resources_required,
            "constraints": self.constraints,
            "success_criteria": self.success_criteria,
            "standards": self.standards,
            "status": self.status,
            "owner_id": self.owner_id,
            "context": self.context,
            "events": self.events,
            "model": self.model,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Problem':
        """Create a Problem from a dictionary.
        
        Args:
            data: Dictionary containing problem data
            
        Returns:
            Problem instance
        """
        problem = cls(
            name=data["name"],
            description=data["description"],
            problem_type=data.get("problem_type", "general"),
            domain=data.get("domain", "general"),
            id=data["id"],
            complexity=data.get("complexity", "moderate"),
            urgency=data.get("urgency", "normal"),
            impact_level=data.get("impact_level", "medium"),
            stakeholders=data.get("stakeholders", []),
            temporal_factors=data.get("temporal_factors", {}),
            uncertainty_level=data.get("uncertainty_level", "medium"),
            resources_required=data.get("resources_required", []),
            constraints=data.get("constraints", []),
            success_criteria=data.get("success_criteria", []),
            standards=data.get("standards", []),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps
        problem.created_at = data["created_at"]
        problem.updated_at = data["updated_at"]
        
        # Set owner and status
        problem.owner_id = data.get("owner_id")
        problem.status = data.get("status", "open")
        
        # Set context, events, and model
        problem.context = data.get("context", {})
        problem.events = data.get("events", [])
        problem.model = data.get("model", {})
        
        return problem


class Solution:
    """
    A Solution represents a proposed answer to a Problem within a Deal.
    
    It contains implementation details, evaluations, and references to the problem it addresses.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        problem_id: Optional[str] = None,
        domain: str = "general",
        id: Optional[str] = None,
        solution_type: str = "standard",
        approach: Optional[str] = None,
        components: Optional[List[Dict[str, Any]]] = None,
        implementation_steps: Optional[List[Dict[str, Any]]] = None,
        resource_requirements: Optional[Dict[str, Any]] = None,
        estimated_effort: Optional[str] = None,
        expected_outcomes: Optional[List[str]] = None,
        risks: Optional[List[Dict[str, Any]]] = None,
        evaluation_criteria: Optional[List[Dict[str, Any]]] = None,
        standards: Optional[List[str]] = None,
        proposed_by: Optional[str] = None,
        status: str = "proposed",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a new Solution.
        
        Args:
            name: Name of the solution
            description: Description of the solution
            problem_id: Optional ID of the problem this solution addresses
            domain: Solution domain
            id: Optional solution ID (generated if not provided)
            solution_type: Type of solution
            approach: Optional approach description
            components: Optional list of solution components
            implementation_steps: Optional implementation steps
            resource_requirements: Optional resource requirements
            estimated_effort: Optional estimated effort
            expected_outcomes: Optional list of expected outcomes
            risks: Optional list of risks
            evaluation_criteria: Optional evaluation criteria
            standards: Optional list of standards this solution should comply with
            proposed_by: Optional ID of the player who proposed the solution
            status: Status of the solution (proposed, in_progress, implemented, rejected)
            metadata: Optional additional metadata
        """
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.problem_id = problem_id
        self.domain = domain
        self.solution_type = solution_type
        self.approach = approach or ""
        self.components = components or []
        self.implementation_steps = implementation_steps or []
        self.resource_requirements = resource_requirements or {}
        self.estimated_effort = estimated_effort or "Unknown"
        self.expected_outcomes = expected_outcomes or []
        self.risks = risks or []
        self.evaluation_criteria = evaluation_criteria or []
        self.standards = standards or []
        self.proposed_by = proposed_by
        self.status = status
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.owner_id = proposed_by  # Owner is initially the proposer
        self.evaluations = []
        
        # Initialize graph
        self.graph = nx.DiGraph()
        self.graph.add_node(
            self.id, 
            type="solution", 
            name=self.name,
            description=self.description,
            solution_type=self.solution_type,
            domain=self.domain,
            status=self.status
        )
        
        if problem_id:
            self.graph.add_node(problem_id, type="problem")
            self.graph.add_edge(self.id, problem_id, relationship="solves")
        
        if proposed_by:
            self.graph.add_node(proposed_by, type="player")
            self.graph.add_edge(proposed_by, self.id, relationship="proposed")
    
    def add_component(self, component: Dict[str, Any]) -> None:
        """Add a component to the solution.
        
        Args:
            component: The component to add
        """
        # Add ID if not provided
        if "id" not in component:
            component["id"] = str(uuid.uuid4())
        
        self.components.append(component)
        self.updated_at = datetime.now().isoformat()
        
        # Add to graph
        component_id = component["id"]
        self.graph.add_node(
            component_id,
            type="component",
            name=component.get("name", "Component"),
            **{k: v for k, v in component.items() if k not in ["name"]}
        )
        self.graph.add_edge(component_id, self.id, relationship="part_of")
    
    def add_implementation_step(self, step: Dict[str, Any]) -> None:
        """Add an implementation step to the solution.
        
        Args:
            step: The implementation step to add
        """
        # Add ID if not provided
        if "id" not in step:
            step["id"] = str(uuid.uuid4())
        
        # Add order if not provided
        if "order" not in step:
            step["order"] = len(self.implementation_steps) + 1
        
        self.implementation_steps.append(step)
        self.updated_at = datetime.now().isoformat()
        
        # Add to graph
        step_id = step["id"]
        self.graph.add_node(
            step_id,
            type="implementation_step",
            name=step.get("name", f"Step {step.get('order', 0)}"),
            **{k: v for k, v in step.items() if k not in ["name"]}
        )
        self.graph.add_edge(step_id, self.id, relationship="implements")
    
    def add_expected_outcome(self, outcome: str) -> None:
        """Add an expected outcome to the solution.
        
        Args:
            outcome: The expected outcome to add
        """
        if outcome not in self.expected_outcomes:
            self.expected_outcomes.append(outcome)
            self.updated_at = datetime.now().isoformat()
    
    def add_risk(self, risk: Dict[str, Any]) -> None:
        """Add a risk to the solution.
        
        Args:
            risk: The risk to add
        """
        # Add ID if not provided
        if "id" not in risk:
            risk["id"] = str(uuid.uuid4())
        
        self.risks.append(risk)
        self.updated_at = datetime.now().isoformat()
        
        # Add to graph
        risk_id = risk["id"]
        self.graph.add_node(
            risk_id,
            type="risk",
            name=risk.get("name", "Risk"),
            **{k: v for k, v in risk.items() if k not in ["name"]}
        )
        self.graph.add_edge(risk_id, self.id, relationship="threatens")
    
    def add_evaluation_criterion(self, criterion: Dict[str, Any]) -> None:
        """Add an evaluation criterion to the solution.
        
        Args:
            criterion: The evaluation criterion to add
        """
        # Add ID if not provided
        if "id" not in criterion:
            criterion["id"] = str(uuid.uuid4())
        
        self.evaluation_criteria.append(criterion)
        self.updated_at = datetime.now().isoformat()
    
    def set_status(self, status: str) -> None:
        """Set the status of the solution.
        
        Args:
            status: New status (proposed, in_progress, implemented, rejected)
        """
        valid_statuses = ["proposed", "in_progress", "implemented", "rejected"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Valid statuses are: {', '.join(valid_statuses)}")
        
        # Record old status
        old_status = self.status
        
        # Update status
        self.status = status
        self.updated_at = datetime.now().isoformat()
        
        # Add status change to metadata
        if "status_history" not in self.metadata:
            self.metadata["status_history"] = []
        
        self.metadata["status_history"].append({
            "from": old_status,
            "to": status,
            "timestamp": self.updated_at
        })
        
        # Update graph
        self.graph.nodes[self.id]["status"] = status
    
    def add_evaluation(
        self,
        evaluator: str,
        meets_criteria: bool,
        evaluation_notes: str,
        suggested_improvements: Optional[List[str]] = None,
        evaluation_id: Optional[str] = None
    ) -> str:
        """Add an evaluation of the solution.
        
        Args:
            evaluator: ID of the player evaluating the solution
            meets_criteria: Whether the solution meets the success criteria
            evaluation_notes: Notes on the evaluation
            suggested_improvements: Optional list of suggested improvements
            evaluation_id: Optional ID for the evaluation (generated if not provided)
            
        Returns:
            ID of the evaluation
        """
        evaluation_id = evaluation_id or str(uuid.uuid4())
        
        evaluation = {
            "id": evaluation_id,
            "evaluator": evaluator,
            "timestamp": datetime.now().isoformat(),
            "meets_criteria": meets_criteria,
            "notes": evaluation_notes,
            "suggested_improvements": suggested_improvements or []
        }
        
        self.evaluations.append(evaluation)
        self.updated_at = datetime.now().isoformat()
        
        # Add to graph
        self.graph.add_node(
            evaluation_id,
            type="evaluation",
            name=f"Evaluation by {evaluator}",
            **evaluation
        )
        self.graph.add_edge(evaluator, evaluation_id, relationship="evaluated")
        self.graph.add_edge(evaluation_id, self.id, relationship="evaluates")
        
        return evaluation_id
    
    def set_owner(self, owner_id: str) -> None:
        """Set the owner of the solution.
        
        Args:
            owner_id: ID of the player who owns the solution
        """
        # Record old owner
        old_owner = self.owner_id
        
        # Update owner
        self.owner_id = owner_id
        self.updated_at = datetime.now().isoformat()
        
        # Add owner change to metadata
        if "owner_history" not in self.metadata:
            self.metadata["owner_history"] = []
        
        self.metadata["owner_history"].append({
            "from": old_owner,
            "to": owner_id,
            "timestamp": self.updated_at
        })
        
        # Update graph
        self.graph.nodes[self.id]["owner_id"] = owner_id
        
        # Add ownership edge
        for s, t, d in self.graph.edges(data=True):
            if t == self.id and d.get("relationship") == "owns":
                # Remove existing ownership edge
                self.graph.remove_edge(s, t)
                break
        
        self.graph.add_edge(owner_id, self.id, relationship="owns")
    
    def validate_standards_compliance(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate that the solution complies with all applicable standards.
        
        Returns:
            Tuple of (is_valid, violations)
        """
        # Import validator here to avoid circular imports
        from specialized_agents.standards_validation import StandardsValidator
        validator = StandardsValidator()
        
        violations = []
        
        # Validate against each standard
        for standard in self.standards:
            # Validate solution structure
            validation_result = validator.validate(self.to_dict(), standard)
            if not validation_result.valid:
                violations.extend(validation_result.violations)
        
        return len(violations) == 0, violations
    
    def export_graph(self, format: str = "networkx") -> Any:
        """Export the solution graph in various formats.
        
        Args:
            format: Format to export the graph in ("networkx", "json", "dot")
            
        Returns:
            Graph representation in the specified format
        """
        if format == "networkx":
            return self.graph
        
        elif format == "json":
            # Convert to JSON-serializable format
            nodes = []
            for node, data in self.graph.nodes(data=True):
                nodes.append({
                    "id": node,
                    "type": data.get("type", "unknown"),
                    "name": data.get("name", "unnamed"),
                    **{k: v for k, v in data.items() if k not in ["type", "name"]}
                })
            
            edges = []
            for s, t, data in self.graph.edges(data=True):
                edges.append({
                    "source": s,
                    "target": t,
                    "relationship": data.get("relationship", "related"),
                    **{k: v for k, v in data.items() if k != "relationship"}
                })
            
            return {"nodes": nodes, "edges": edges}
        
        elif format == "dot":
            # Generate DOT format for visualization
            lines = ['digraph SolutionGraph {']
            lines.append('  rankdir=LR;')
            lines.append('  node [shape=box, style=filled];')
            
            # Add nodes with colors by type
            for node, data in self.graph.nodes(data=True):
                node_type = data.get('type', 'unknown')
                name = data.get('name', node)
                
                if node_type == 'solution':
                    color = 'lightgreen'
                elif node_type == 'component':
                    color = 'lightblue'
                elif node_type == 'implementation_step':
                    color = 'lightyellow'
                elif node_type == 'risk':
                    color = 'salmon'
                elif node_type == 'evaluation':
                    color = 'lightpink'
                else:
                    color = 'white'
                
                lines.append(f'  "{node}" [label="{name}", fillcolor="{color}"];')
            
            # Add edges with labels
            for s, t, data in self.graph.edges(data=True):
                relationship = data.get('relationship', '')
                lines.append(f'  "{s}" -> "{t}" [label="{relationship}"];')
            
            lines.append('}')
            return '\n'.join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the solution to a dictionary.
        
        Returns:
            Dictionary representation of the solution
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "problem_id": self.problem_id,
            "domain": self.domain,
            "solution_type": self.solution_type,
            "approach": self.approach,
            "components": self.components,
            "implementation_steps": self.implementation_steps,
            "resource_requirements": self.resource_requirements,
            "estimated_effort": self.estimated_effort,
            "expected_outcomes": self.expected_outcomes,
            "risks": self.risks,
            "evaluation_criteria": self.evaluation_criteria,
            "standards": self.standards,
            "proposed_by": self.proposed_by,
            "owner_id": self.owner_id,
            "status": self.status,
            "evaluations": self.evaluations,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Solution':
        """Create a Solution from a dictionary.
        
        Args:
            data: Dictionary containing solution data
            
        Returns:
            Solution instance
        """
        solution = cls(
            name=data["name"],
            description=data["description"],
            problem_id=data.get("problem_id"),
            domain=data.get("domain", "general"),
            id=data["id"],
            solution_type=data.get("solution_type", "standard"),
            approach=data.get("approach", ""),
            components=data.get("components", []),
            implementation_steps=data.get("implementation_steps", []),
            resource_requirements=data.get("resource_requirements", {}),
            estimated_effort=data.get("estimated_effort", "Unknown"),
            expected_outcomes=data.get("expected_outcomes", []),
            risks=data.get("risks", []),
            evaluation_criteria=data.get("evaluation_criteria", []),
            standards=data.get("standards", []),
            proposed_by=data.get("proposed_by"),
            status=data.get("status", "proposed"),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps
        solution.created_at = data["created_at"]
        solution.updated_at = data["updated_at"]
        
        # Set owner and evaluations
        solution.owner_id = data.get("owner_id", data.get("proposed_by"))
        solution.evaluations = data.get("evaluations", [])
        
        return solution


class Player:
    """
    A Player represents a participant in a Deal.
    
    It can be an agent, a human expert, or another entity involved in the deal.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        id: Optional[str] = None,
        player_type: str = "agent",  # agent, human, or organization
        capabilities: Optional[List[str]] = None,
        domain_expertise: Optional[List[str]] = None,
        standards: Optional[List[str]] = None,
        status: str = "active",  # active or inactive
        contact_info: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a new Player.
        
        Args:
            agent_id: ID of the agent this player represents
            name: Name of the player
            role: Role of the player in the deal
            id: Optional player ID (generated if not provided)
            player_type: Type of player (agent, human, organization)
            capabilities: Optional list of capabilities
            domain_expertise: Optional list of domain expertise
            standards: Optional list of standards this player complies with
            status: Status of the player (active or inactive)
            contact_info: Optional contact information
            metadata: Optional additional metadata
        """
        self.id = id or str(uuid.uuid4())
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.player_type = player_type
        self.capabilities = capabilities or []
        self.domain_expertise = domain_expertise or []
        self.standards = standards or []
        self.status = status
        self.contact_info = contact_info or {}
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.problems_owned = []
        self.solutions_owned = []
        self.tasks = []
        
        # Initialize graph
        self.graph = nx.DiGraph()
        self.graph.add_node(
            self.id, 
            type="player", 
            name=self.name,
            role=self.role,
            player_type=self.player_type,
            status=self.status
        )
    
    def add_capability(self, capability: str) -> None:
        """Add a capability to the player.
        
        Args:
            capability: The capability to add
        """
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.updated_at = datetime.now().isoformat()
    
    def add_domain_expertise(self, domain: str) -> None:
        """Add domain expertise to the player.
        
        Args:
            domain: The domain expertise to add
        """
        if domain not in self.domain_expertise:
            self.domain_expertise.append(domain)
            self.updated_at = datetime.now().isoformat()
    
    def set_role(self, role: str) -> None:
        """Set the role of the player.
        
        Args:
            role: The new role
        """
        self.role = role
        self.updated_at = datetime.now().isoformat()
        
        # Update graph
        self.graph.nodes[self.id]["role"] = role
    
    def set_status(self, status: str) -> None:
        """Set the status of the player.
        
        Args:
            status: The new status (active or inactive)
        """
        if status not in ["active", "inactive"]:
            raise ValueError(f"Invalid status: {status}. Valid statuses are: active, inactive")
        
        self.status = status
        self.updated_at = datetime.now().isoformat()
        
        # Update graph
        self.graph.nodes[self.id]["status"] = status
    
    def add_owned_problem(self, problem_id: str) -> None:
        """Add a problem owned by this player.
        
        Args:
            problem_id: ID of the problem
        """
        if problem_id not in self.problems_owned:
            self.problems_owned.append(problem_id)
            self.updated_at = datetime.now().isoformat()
            
            # Add to graph
            self.graph.add_node(problem_id, type="problem")
            self.graph.add_edge(self.id, problem_id, relationship="owns")
    
    def add_owned_solution(self, solution_id: str) -> None:
        """Add a solution owned by this player.
        
        Args:
            solution_id: ID of the solution
        """
        if solution_id not in self.solutions_owned:
            self.solutions_owned.append(solution_id)
            self.updated_at = datetime.now().isoformat()
            
            # Add to graph
            self.graph.add_node(solution_id, type="solution")
            self.graph.add_edge(self.id, solution_id, relationship="owns")
    
    def add_task(self, task: Dict[str, Any]) -> None:
        """Add a task for this player.
        
        Args:
            task: The task to add
        """
        # Add ID if not provided
        if "id" not in task:
            task["id"] = str(uuid.uuid4())
        
        # Add timestamp if not provided
        if "created_at" not in task:
            task["created_at"] = datetime.now().isoformat()
        
        # Add status if not provided
        if "status" not in task:
            task["status"] = "pending"
        
        self.tasks.append(task)
        self.updated_at = datetime.now().isoformat()
        
        # Add to graph
        task_id = task["id"]
        self.graph.add_node(
            task_id,
            type="task",
            name=task.get("name", "Task"),
            **{k: v for k, v in task.items() if k not in ["name"]}
        )
        self.graph.add_edge(task_id, self.id, relationship="assigned_to")
    
    def validate_standards_compliance(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate that the player complies with all applicable standards.
        
        Returns:
            Tuple of (is_valid, violations)
        """
        # Import validator here to avoid circular imports
        from specialized_agents.standards_validation import StandardsValidator
        validator = StandardsValidator()
        
        violations = []
        
        # Validate against each standard
        for standard in self.standards:
            # Validate player structure
            validation_result = validator.validate(self.to_dict(), standard)
            if not validation_result.valid:
                violations.extend(validation_result.violations)
        
        return len(violations) == 0, violations
    
    def export_graph(self, format: str = "networkx") -> Any:
        """Export the player graph in various formats.
        
        Args:
            format: Format to export the graph in ("networkx", "json", "dot")
            
        Returns:
            Graph representation in the specified format
        """
        if format == "networkx":
            return self.graph
        
        elif format == "json":
            # Convert to JSON-serializable format
            nodes = []
            for node, data in self.graph.nodes(data=True):
                nodes.append({
                    "id": node,
                    "type": data.get("type", "unknown"),
                    "name": data.get("name", "unnamed"),
                    **{k: v for k, v in data.items() if k not in ["type", "name"]}
                })
            
            edges = []
            for s, t, data in self.graph.edges(data=True):
                edges.append({
                    "source": s,
                    "target": t,
                    "relationship": data.get("relationship", "related"),
                    **{k: v for k, v in data.items() if k != "relationship"}
                })
            
            return {"nodes": nodes, "edges": edges}
        
        elif format == "dot":
            # Generate DOT format for visualization
            lines = ['digraph PlayerGraph {']
            lines.append('  rankdir=LR;')
            lines.append('  node [shape=box, style=filled];')
            
            # Add nodes with colors by type
            for node, data in self.graph.nodes(data=True):
                node_type = data.get('type', 'unknown')
                name = data.get('name', node)
                
                if node_type == 'player':
                    color = 'lightblue'
                elif node_type == 'problem':
                    color = 'salmon'
                elif node_type == 'solution':
                    color = 'lightgreen'
                elif node_type == 'task':
                    color = 'lightyellow'
                else:
                    color = 'white'
                
                lines.append(f'  "{node}" [label="{name}", fillcolor="{color}"];')
            
            # Add edges with labels
            for s, t, data in self.graph.edges(data=True):
                relationship = data.get('relationship', '')
                lines.append(f'  "{s}" -> "{t}" [label="{relationship}"];')
            
            lines.append('}')
            return '\n'.join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the player to a dictionary.
        
        Returns:
            Dictionary representation of the player
        """
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "player_type": self.player_type,
            "capabilities": self.capabilities,
            "domain_expertise": self.domain_expertise,
            "standards": self.standards,
            "status": self.status,
            "contact_info": self.contact_info,
            "problems_owned": self.problems_owned,
            "solutions_owned": self.solutions_owned,
            "tasks": self.tasks,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create a Player from a dictionary.
        
        Args:
            data: Dictionary containing player data
            
        Returns:
            Player instance
        """
        player = cls(
            agent_id=data["agent_id"],
            name=data["name"],
            role=data["role"],
            id=data["id"],
            player_type=data.get("player_type", "agent"),
            capabilities=data.get("capabilities", []),
            domain_expertise=data.get("domain_expertise", []),
            standards=data.get("standards", []),
            status=data.get("status", "active"),
            contact_info=data.get("contact_info", {}),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps
        player.created_at = data["created_at"]
        player.updated_at = data["updated_at"]
        
        # Set owned items and tasks
        player.problems_owned = data.get("problems_owned", [])
        player.solutions_owned = data.get("solutions_owned", [])
        player.tasks = data.get("tasks", [])
        
        return player


class Transaction:
    """
    A Transaction represents an exchange between Players in a Deal.
    
    It can be a payment, a service, or any other type of exchange.
    """
    
    def __init__(
        self,
        name: str,
        transaction_type: str,
        amount: float,
        from_player: str,
        to_player: str,
        id: Optional[str] = None,
        currency: str = "USD",
        status: str = "pending",
        description: Optional[str] = None,
        transaction_date: Optional[str] = None,
        expiration_date: Optional[str] = None,
        terms: Optional[List[str]] = None,
        related_resources: Optional[List[Dict[str, Any]]] = None,
        approval_requirements: Optional[List[str]] = None,
        standards: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a new Transaction.
        
        Args:
            name: Name of the transaction
            transaction_type: Type of transaction (payment, service, etc.)
            amount: Transaction amount
            from_player: ID of the player initiating the transaction
            to_player: ID of the player receiving the transaction
            id: Optional transaction ID (generated if not provided)
            currency: Currency for the transaction
            status: Transaction status (pending, completed, cancelled)
            description: Optional detailed description of the transaction
            transaction_date: Optional date when transaction should occur
            expiration_date: Optional date when transaction expires
            terms: Optional list of transaction terms
            related_resources: Optional list of related resources
            approval_requirements: Optional list of approval requirements
            standards: Optional list of standards this transaction should comply with
            metadata: Optional additional metadata
        """
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.transaction_type = transaction_type
        self.amount = amount
        self.from_player = from_player
        self.to_player = to_player
        self.currency = currency
        self.status = status
        self.description = description or ""
        self.transaction_date = transaction_date or datetime.now().isoformat()
        self.expiration_date = expiration_date
        self.terms = terms or []
        self.related_resources = related_resources or []
        self.approval_requirements = approval_requirements or []
        self.standards = standards or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.approval_history = []
        self.rejection_reason = None
        
        # Initialize graph
        self.graph = nx.DiGraph()
        self.graph.add_node(
            self.id, 
            type="transaction", 
            name=self.name,
            transaction_type=self.transaction_type,
            amount=self.amount,
            currency=self.currency,
            status=self.status
        )
        
        # Add nodes for from and to players
        self.graph.add_node(from_player, type="player")
        self.graph.add_node(to_player, type="player")
        
        # Add edges for transaction flow
        self.graph.add_edge(from_player, self.id, relationship="initiates")
        self.graph.add_edge(self.id, to_player, relationship="receives")
    
    def add_term(self, term: str) -> None:
        """Add a term to the transaction.
        
        Args:
            term: The term to add
        """
        if term not in self.terms:
            self.terms.append(term)
            self.updated_at = datetime.now().isoformat()
    
    def add_related_resource(self, resource: Dict[str, Any]) -> None:
        """Add a related resource to the transaction.
        
        Args:
            resource: The related resource to add
        """
        # Add ID if not provided
        if "id" not in resource:
            resource["id"] = str(uuid.uuid4())
        
        # Add resource type if not provided
        if "type" not in resource:
            resource["type"] = "generic"
        
        self.related_resources.append(resource)
        self.updated_at = datetime.now().isoformat()
        
        # Add to graph
        resource_id = resource["id"]
        self.graph.add_node(
            resource_id,
            type="resource",
            name=resource.get("name", "Resource"),
            resource_type=resource.get("type"),
            **{k: v for k, v in resource.items() if k not in ["id", "name", "type"]}
        )
        self.graph.add_edge(resource_id, self.id, relationship="supports")
    
    def add_approval_requirement(self, requirement: str) -> None:
        """Add an approval requirement to the transaction.
        
        Args:
            requirement: The approval requirement to add
        """
        if requirement not in self.approval_requirements:
            self.approval_requirements.append(requirement)
            self.updated_at = datetime.now().isoformat()
    
    def approve(self, player_id: str, notes: Optional[str] = None) -> None:
        """Approve the transaction.
        
        Args:
            player_id: ID of the player approving the transaction
            notes: Optional approval notes
        """
        approval = {
            "player_id": player_id,
            "timestamp": datetime.now().isoformat(),
            "action": "approved",
            "notes": notes
        }
        
        self.approval_history.append(approval)
        self.updated_at = datetime.now().isoformat()
        
        # Add approval edge to graph
        self.graph.add_edge(
            player_id,
            self.id,
            relationship="approved",
            timestamp=approval["timestamp"]
        )
        
        # Check if all requirements are met
        if self._check_all_approvals_met():
            self.complete()
    
    def reject(self, player_id: str, reason: str) -> None:
        """Reject the transaction.
        
        Args:
            player_id: ID of the player rejecting the transaction
            reason: Reason for rejection
        """
        rejection = {
            "player_id": player_id,
            "timestamp": datetime.now().isoformat(),
            "action": "rejected",
            "reason": reason
        }
        
        self.approval_history.append(rejection)
        self.rejection_reason = reason
        self.updated_at = datetime.now().isoformat()
        
        # Add rejection edge to graph
        self.graph.add_edge(
            player_id,
            self.id,
            relationship="rejected",
            timestamp=rejection["timestamp"],
            reason=reason
        )
        
        # Cancel the transaction
        self.cancel()
    
    def _check_all_approvals_met(self) -> bool:
        """Check if all approval requirements are met.
        
        Returns:
            True if all requirements are met, False otherwise
        """
        if not self.approval_requirements:
            # No approval requirements, so all are met
            return True
        
        # Get all approvals
        approvals = [a["player_id"] for a in self.approval_history if a["action"] == "approved"]
        
        # Check if all required players have approved
        return all(req in approvals for req in self.approval_requirements)
    
    def complete(self) -> None:
        """Mark the transaction as completed."""
        self.status = "completed"
        self.updated_at = datetime.now().isoformat()
        
        # Update graph
        self.graph.nodes[self.id]["status"] = "completed"
        
        # Add completion to metadata
        self.metadata["completed_at"] = self.updated_at
    
    def cancel(self) -> None:
        """Mark the transaction as cancelled."""
        self.status = "cancelled"
        self.updated_at = datetime.now().isoformat()
        
        # Update graph
        self.graph.nodes[self.id]["status"] = "cancelled"
        
        # Add cancellation to metadata
        self.metadata["cancelled_at"] = self.updated_at
    
    def set_expiration_date(self, expiration_date: str) -> None:
        """Set the expiration date of the transaction.
        
        Args:
            expiration_date: The expiration date in ISO format
        """
        self.expiration_date = expiration_date
        self.updated_at = datetime.now().isoformat()
        
        # Update graph
        self.graph.nodes[self.id]["expiration_date"] = expiration_date
    
    def is_expired(self) -> bool:
        """Check if the transaction is expired.
        
        Returns:
            True if expired, False otherwise
        """
        if not self.expiration_date:
            return False
        
        now = datetime.now().isoformat()
        return now > self.expiration_date
    
    def validate_standards_compliance(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate that the transaction complies with all applicable standards.
        
        Returns:
            Tuple of (is_valid, violations)
        """
        # Import validator here to avoid circular imports
        from specialized_agents.standards_validation import StandardsValidator
        validator = StandardsValidator()
        
        violations = []
        
        # Validate against each standard
        for standard in self.standards:
            # Validate transaction structure
            validation_result = validator.validate(self.to_dict(), standard)
            if not validation_result.valid:
                violations.extend(validation_result.violations)
        
        return len(violations) == 0, violations
    
    def export_graph(self, format: str = "networkx") -> Any:
        """Export the transaction graph in various formats.
        
        Args:
            format: Format to export the graph in ("networkx", "json", "dot")
            
        Returns:
            Graph representation in the specified format
        """
        if format == "networkx":
            return self.graph
        
        elif format == "json":
            # Convert to JSON-serializable format
            nodes = []
            for node, data in self.graph.nodes(data=True):
                nodes.append({
                    "id": node,
                    "type": data.get("type", "unknown"),
                    "name": data.get("name", "unnamed"),
                    **{k: v for k, v in data.items() if k not in ["type", "name"]}
                })
            
            edges = []
            for s, t, data in self.graph.edges(data=True):
                edges.append({
                    "source": s,
                    "target": t,
                    "relationship": data.get("relationship", "related"),
                    **{k: v for k, v in data.items() if k != "relationship"}
                })
            
            return {"nodes": nodes, "edges": edges}
        
        elif format == "dot":
            # Generate DOT format for visualization
            lines = ['digraph TransactionGraph {']
            lines.append('  rankdir=LR;')
            lines.append('  node [shape=box, style=filled];')
            
            # Add nodes with colors by type
            for node, data in self.graph.nodes(data=True):
                node_type = data.get('type', 'unknown')
                name = data.get('name', node)
                
                if node_type == 'transaction':
                    color = 'lightyellow'
                elif node_type == 'player':
                    color = 'lightblue'
                elif node_type == 'resource':
                    color = 'lightgreen'
                else:
                    color = 'white'
                
                lines.append(f'  "{node}" [label="{name}", fillcolor="{color}"];')
            
            # Add edges with labels
            for s, t, data in self.graph.edges(data=True):
                relationship = data.get('relationship', '')
                lines.append(f'  "{s}" -> "{t}" [label="{relationship}"];')
            
            lines.append('}')
            return '\n'.join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the transaction to a dictionary.
        
        Returns:
            Dictionary representation of the transaction
        """
        return {
            "id": self.id,
            "name": self.name,
            "transaction_type": self.transaction_type,
            "amount": self.amount,
            "from_player": self.from_player,
            "to_player": self.to_player,
            "currency": self.currency,
            "status": self.status,
            "description": self.description,
            "transaction_date": self.transaction_date,
            "expiration_date": self.expiration_date,
            "terms": self.terms,
            "related_resources": self.related_resources,
            "approval_requirements": self.approval_requirements,
            "standards": self.standards,
            "approval_history": self.approval_history,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create a Transaction from a dictionary.
        
        Args:
            data: Dictionary containing transaction data
            
        Returns:
            Transaction instance
        """
        transaction = cls(
            name=data["name"],
            transaction_type=data["transaction_type"],
            amount=data["amount"],
            from_player=data["from_player"],
            to_player=data["to_player"],
            id=data["id"],
            currency=data.get("currency", "USD"),
            status=data.get("status", "pending"),
            description=data.get("description", ""),
            transaction_date=data.get("transaction_date"),
            expiration_date=data.get("expiration_date"),
            terms=data.get("terms", []),
            related_resources=data.get("related_resources", []),
            approval_requirements=data.get("approval_requirements", []),
            standards=data.get("standards", []),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps
        transaction.created_at = data["created_at"]
        transaction.updated_at = data["updated_at"]
        
        # Set approval history and rejection reason
        transaction.approval_history = data.get("approval_history", [])
        transaction.rejection_reason = data.get("rejection_reason")
        
        # Rebuild graph with related resources
        for resource in data.get("related_resources", []):
            resource_id = resource.get("id")
            if resource_id:
                transaction.graph.add_node(
                    resource_id,
                    type="resource",
                    name=resource.get("name", "Resource"),
                    resource_type=resource.get("type"),
                    **{k: v for k, v in resource.items() if k not in ["id", "name", "type"]}
                )
                transaction.graph.add_edge(resource_id, transaction.id, relationship="supports")
        
        # Add approval edges
        for approval in data.get("approval_history", []):
            if approval.get("action") == "approved":
                transaction.graph.add_edge(
                    approval.get("player_id"),
                    transaction.id,
                    relationship="approved",
                    timestamp=approval.get("timestamp")
                )
            elif approval.get("action") == "rejected":
                transaction.graph.add_edge(
                    approval.get("player_id"),
                    transaction.id,
                    relationship="rejected",
                    timestamp=approval.get("timestamp"),
                    reason=approval.get("reason")
                )
        
        return transaction


class StandardsRegistry:
    """Registry for standards used in deals."""
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(StandardsRegistry, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize the registry."""
        self.standards = {}
        self.domain_standards = {}
        
        # Load standards from HMS-SME
        self._load_standards()
    
    def _load_standards(self):
        """Load standards from HMS-SME."""
        # Basic structure of standards by category
        base_standards = {
            "iso": [
                "ISO_9001", "ISO_14001", "ISO_17100", "ISO_13485", "ISO_27001"
            ],
            "financial": [
                "GAAP", "IFRS", "SOX", "FASB", "IAS"
            ],
            "healthcare": [
                "HIPAA", "HITECH", "HL7", "FHIR", "DICOM"
            ],
            "agriculture": [
                "USDA_ORGANIC", "GAP_CERTIFICATION", "GLOBALG.A.P"
            ],
            "legal": [
                "ABA_MODEL_RULES", "ETHICS_RULES", "CLIENT_CONFIDENTIALITY"
            ],
            "government": [
                "FOIA", "PRIVACY_ACT", "RECORDS_MANAGEMENT", "SECTION_508"
            ]
        }
        
        # Flatten the structure for easy lookup
        all_standards = []
        for category, standards in base_standards.items():
            all_standards.extend(standards)
            for standard in standards:
                self.domain_standards.setdefault(category, []).append(standard)
        
        # Store all standards
        self.standards = {standard: {"name": standard} for standard in all_standards}
    
    def get_standards_for_domain(self, domain: str) -> List[str]:
        """Get standards for a specific domain.
        
        Args:
            domain: The domain to get standards for
            
        Returns:
            List of standard identifiers
        """
        return self.domain_standards.get(domain, [])
    
    def get_standard(self, standard_id: str) -> Optional[Dict[str, Any]]:
        """Get a standard by ID.
        
        Args:
            standard_id: ID of the standard
            
        Returns:
            Standard information or None if not found
        """
        return self.standards.get(standard_id)
    
    def register_standard(
        self,
        standard_id: str,
        name: str,
        description: str,
        domains: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a new standard.
        
        Args:
            standard_id: ID of the standard
            name: Name of the standard
            description: Description of the standard
            domains: List of domains this standard applies to
            metadata: Optional additional metadata
        """
        self.standards[standard_id] = {
            "name": name,
            "description": description,
            "domains": domains,
            "metadata": metadata or {}
        }
        
        # Add to domain standards
        for domain in domains:
            self.domain_standards.setdefault(domain, []).append(standard_id)


# Create Deal MCP tools
from specialized_agents.tools_base import (
    StandardsCompliantTool,
    ContentPart,
    ToolMetadata,
    create_tool_input_model
)
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# Create the Create Deal Input Schema
CreateDealInputSchema = create_tool_input_model(
    "CreateDealInput",
    {
        "name": (str, Field(description="Name of the deal")),
        "description": (str, Field(description="Description of the deal")),
        "deal_type": (str, Field(description="Type of deal (standard, collaboration, etc.)")),
        "participants": (List[str], Field(description="List of participant agent domains"))
    },
    """Input schema for creating a deal."""
)

class CreateDealResult(BaseModel):
    """Result from creating a deal."""
    deal_id: str
    name: str
    status: str
    participants: List[str]
    created_at: str

class CreateDealTool(StandardsCompliantTool[CreateDealInputSchema, CreateDealResult]):
    """A standards-compliant tool for creating deals."""
    
    def __init__(self):
        """Initialize the create deal tool."""
        super().__init__(
            name="create_deal",
            description="Creates a new deal for collaboration between specialized agents",
            input_schema=CreateDealInputSchema,
            supported_standards=[
                "CROSS_DOMAIN_COLLABORATION",
                "AGENT_COOPERATION"
            ],
            domain="Collaboration",
            metadata=ToolMetadata(
                title="Create Deal Tool",
                read_only=False,
                destructive=False,
                idempotent=True,
                open_world=False,
                description="Standards-compliant deal creation tool"
            )
        )
    
    async def execute(self, args: CreateDealInputSchema, session_context: Optional[Dict[str, Any]] = None) -> CreateDealResult:
        """Execute the create deal operation.
        
        Args:
            args: Validated input arguments
            session_context: Optional session context
            
        Returns:
            Create deal result
        """
        # Create a new deal
        deal = Deal(
            name=args.name,
            description=args.description,
            participants=args.participants,
            deal_type=args.deal_type
        )
        
        # Store the deal in the session context
        if session_context:
            if "deals" not in session_context:
                session_context["deals"] = {}
            session_context["deals"][deal.id] = deal
        
        # Return the result
        return CreateDealResult(
            deal_id=deal.id,
            name=deal.name,
            status=deal.status,
            participants=deal.participants,
            created_at=deal.created_at
        )
    
    def format_result(self, result: CreateDealResult) -> List[ContentPart]:
        """Format the result for display.
        
        Args:
            result: Create deal result
            
        Returns:
            List of content parts
        """
        # Create a data part with the full result
        data_part = ContentPart(
            type=ContentPart.ContentType.DATA,
            content=result.model_dump()
        )
        
        # Format a text summary
        text_output = f"""
Deal created successfully:
- ID: {result.deal_id}
- Name: {result.name}
- Status: {result.status}
- Participants: {', '.join(result.participants)}
- Created: {result.created_at}
"""
        
        text_part = ContentPart(
            type=ContentPart.ContentType.TEXT,
            content=text_output.strip()
        )
        
        return [data_part, text_part]

# Create the Join Deal Input Schema
JoinDealInputSchema = create_tool_input_model(
    "JoinDealInput",
    {
        "deal_id": (str, Field(description="ID of the deal to join")),
        "role": (str, Field(description="Role in the deal"))
    },
    """Input schema for joining a deal."""
)

class JoinDealResult(BaseModel):
    """Result from joining a deal."""
    deal_id: str
    deal_name: str
    agent_role: str
    status: str

class JoinDealTool(StandardsCompliantTool[JoinDealInputSchema, JoinDealResult]):
    """A standards-compliant tool for joining deals."""
    
    def __init__(self):
        """Initialize the join deal tool."""
        super().__init__(
            name="join_deal",
            description="Joins an existing deal as a participant",
            input_schema=JoinDealInputSchema,
            supported_standards=[
                "CROSS_DOMAIN_COLLABORATION",
                "AGENT_COOPERATION"
            ],
            domain="Collaboration",
            metadata=ToolMetadata(
                title="Join Deal Tool",
                read_only=False,
                destructive=False,
                idempotent=True,
                open_world=False,
                description="Standards-compliant deal joining tool"
            )
        )
    
    async def execute(self, args: JoinDealInputSchema, session_context: Optional[Dict[str, Any]] = None) -> JoinDealResult:
        """Execute the join deal operation.
        
        Args:
            args: Validated input arguments
            session_context: Optional session context
            
        Returns:
            Join deal result
        """
        if not session_context or "deals" not in session_context:
            raise ValueError("No deals available in session context")
        
        # Get the deal
        deal_id = args.deal_id
        if deal_id not in session_context["deals"]:
            raise ValueError(f"Deal {deal_id} not found")
        
        deal = session_context["deals"][deal_id]
        
        # Get calling agent
        calling_agent = session_context.get("calling_agent")
        if not calling_agent:
            raise ValueError("No calling agent specified")
        
        # Add agent as participant if not already
        if calling_agent not in deal.participants:
            deal.participants.append(calling_agent)
            
            # Create a player for the agent
            player = Player(
                agent_id=calling_agent,
                name=f"{calling_agent.capitalize()} Agent",
                role=args.role
            )
            deal.add_player(player)
        
        # Return the result
        return JoinDealResult(
            deal_id=deal.id,
            deal_name=deal.name,
            agent_role=args.role,
            status="joined"
        )
    
    def format_result(self, result: JoinDealResult) -> List[ContentPart]:
        """Format the result for display.
        
        Args:
            result: Join deal result
            
        Returns:
            List of content parts
        """
        # Create a data part with the full result
        data_part = ContentPart(
            type=ContentPart.ContentType.DATA,
            content=result.model_dump()
        )
        
        # Format a text summary
        text_output = f"""
Successfully joined deal:
- Deal ID: {result.deal_id}
- Deal Name: {result.deal_name}
- Role: {result.agent_role}
- Status: {result.status}
"""
        
        text_part = ContentPart(
            type=ContentPart.ContentType.TEXT,
            content=text_output.strip()
        )
        
        return [data_part, text_part]


def register_deal_tools() -> List[str]:
    """Register all deal-related tools and return their names.
    
    Returns:
        List of registered tool names
    """
    from specialized_agents.collaboration.tool_registry import MCPToolRegistry
    
    # Create tools
    create_deal_tool = CreateDealTool()
    join_deal_tool = JoinDealTool()
    
    # Register tools
    registry = MCPToolRegistry()
    registry.register_tool(create_deal_tool, ["*"])
    registry.register_tool(join_deal_tool, ["*"])
    
    return [
        create_deal_tool.name,
        join_deal_tool.name
    ]