"""
Economic Theorem Repository

This module provides a repository for storing, retrieving, and managing
economic theorems, proofs, and their relationships.
"""

from typing import Dict, List, Tuple, Any, Optional, Set, Union, Callable
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx
import pickle


class TheoremStatus(Enum):
    """Status of a theorem in the repository."""
    UNPROVEN = "unproven"  # No proof attempts
    IN_PROGRESS = "in_progress"  # Proof attempts, but no successful proof
    PROVEN = "proven"  # Successfully proven
    DISPROVEN = "disproven"  # Counterexample found
    AXIOM = "axiom"  # Accepted without proof


class ProofStatus(Enum):
    """Status of a proof in the repository."""
    VALID = "valid"  # Valid proof
    INVALID = "invalid"  # Invalid proof
    UNCERTAIN = "uncertain"  # Proof not fully verified
    PARTIAL = "partial"  # Partially complete proof


@dataclass
class TheoremMetadata:
    """Metadata about a theorem."""
    created_at: float
    created_by: str
    domain: str
    tags: List[str]
    priority: int  # 1-5, where 1 is highest priority
    difficulty: int  # 1-5, where 5 is most difficult
    importance: int  # 1-5, where 5 is most important
    verification_level: int  # 0-3, where 3 is fully verified by multiple methods


@dataclass
class Theorem:
    """Represents an economic theorem in the repository."""
    theorem_id: str
    natural_language: str
    formal_expression: str
    status: TheoremStatus
    metadata: TheoremMetadata
    assumptions: List[str] = field(default_factory=list)  # IDs of theorems/axioms used as assumptions
    variables: Dict[str, str] = field(default_factory=dict)  # Variable name -> type/description
    proofs: List[str] = field(default_factory=list)  # IDs of proofs for this theorem
    counterexamples: List[str] = field(default_factory=list)  # IDs of counterexamples
    generalizations: List[str] = field(default_factory=list)  # IDs of more general theorems
    specializations: List[str] = field(default_factory=list)  # IDs of more specific theorems
    related_theorems: List[str] = field(default_factory=list)  # IDs of related theorems
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert theorem to dictionary for serialization."""
        return {
            "theorem_id": self.theorem_id,
            "natural_language": self.natural_language,
            "formal_expression": self.formal_expression,
            "status": self.status.value,
            "metadata": {
                "created_at": self.metadata.created_at,
                "created_by": self.metadata.created_by,
                "domain": self.metadata.domain,
                "tags": self.metadata.tags,
                "priority": self.metadata.priority,
                "difficulty": self.metadata.difficulty,
                "importance": self.metadata.importance,
                "verification_level": self.metadata.verification_level
            },
            "assumptions": self.assumptions,
            "variables": self.variables,
            "proofs": self.proofs,
            "counterexamples": self.counterexamples,
            "generalizations": self.generalizations,
            "specializations": self.specializations,
            "related_theorems": self.related_theorems
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Theorem':
        """Create a theorem from a dictionary."""
        metadata = TheoremMetadata(
            created_at=data["metadata"]["created_at"],
            created_by=data["metadata"]["created_by"],
            domain=data["metadata"]["domain"],
            tags=data["metadata"]["tags"],
            priority=data["metadata"]["priority"],
            difficulty=data["metadata"]["difficulty"],
            importance=data["metadata"]["importance"],
            verification_level=data["metadata"]["verification_level"]
        )
        
        return cls(
            theorem_id=data["theorem_id"],
            natural_language=data["natural_language"],
            formal_expression=data["formal_expression"],
            status=TheoremStatus(data["status"]),
            metadata=metadata,
            assumptions=data.get("assumptions", []),
            variables=data.get("variables", {}),
            proofs=data.get("proofs", []),
            counterexamples=data.get("counterexamples", []),
            generalizations=data.get("generalizations", []),
            specializations=data.get("specializations", []),
            related_theorems=data.get("related_theorems", [])
        )


@dataclass
class ProofStep:
    """A single step in a proof."""
    step_id: str
    description: str
    expression: str
    justification: str
    previous_steps: List[str] = field(default_factory=list)  # IDs of steps this step depends on


@dataclass
class Proof:
    """Represents a proof of a theorem."""
    proof_id: str
    theorem_id: str
    status: ProofStatus
    created_at: float
    created_by: str
    verification_level: int  # 0-3, where 3 is fully verified by multiple methods
    method: str  # e.g., "direct", "induction", "contradiction"
    steps: List[ProofStep] = field(default_factory=list)
    used_theorems: List[str] = field(default_factory=list)  # IDs of theorems used in the proof
    used_axioms: List[str] = field(default_factory=list)  # IDs of axioms used in the proof
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert proof to dictionary for serialization."""
        return {
            "proof_id": self.proof_id,
            "theorem_id": self.theorem_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "verification_level": self.verification_level,
            "method": self.method,
            "steps": [
                {
                    "step_id": step.step_id,
                    "description": step.description,
                    "expression": step.expression,
                    "justification": step.justification,
                    "previous_steps": step.previous_steps
                }
                for step in self.steps
            ],
            "used_theorems": self.used_theorems,
            "used_axioms": self.used_axioms
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Proof':
        """Create a proof from a dictionary."""
        steps = [
            ProofStep(
                step_id=step["step_id"],
                description=step["description"],
                expression=step["expression"],
                justification=step["justification"],
                previous_steps=step.get("previous_steps", [])
            )
            for step in data.get("steps", [])
        ]
        
        return cls(
            proof_id=data["proof_id"],
            theorem_id=data["theorem_id"],
            status=ProofStatus(data["status"]),
            created_at=data["created_at"],
            created_by=data["created_by"],
            verification_level=data["verification_level"],
            method=data["method"],
            steps=steps,
            used_theorems=data.get("used_theorems", []),
            used_axioms=data.get("used_axioms", [])
        )


@dataclass
class Counterexample:
    """Represents a counterexample to a theorem."""
    counterexample_id: str
    theorem_id: str
    description: str
    parameters: Dict[str, Any]
    created_at: float
    created_by: str
    verification_level: int  # 0-3, where 3 is fully verified by multiple methods
    explanation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert counterexample to dictionary for serialization."""
        return {
            "counterexample_id": self.counterexample_id,
            "theorem_id": self.theorem_id,
            "description": self.description,
            "parameters": self.parameters,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "verification_level": self.verification_level,
            "explanation": self.explanation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Counterexample':
        """Create a counterexample from a dictionary."""
        return cls(
            counterexample_id=data["counterexample_id"],
            theorem_id=data["theorem_id"],
            description=data["description"],
            parameters=data["parameters"],
            created_at=data["created_at"],
            created_by=data["created_by"],
            verification_level=data["verification_level"],
            explanation=data["explanation"]
        )


class TheoremRepository:
    """Repository for storing, retrieving, and managing economic theorems and proofs."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize a theorem repository.
        
        Args:
            data_dir: Directory to store repository data. If not provided, data is kept in memory only.
        """
        self.data_dir = data_dir
        
        # Create data directory if specified
        if data_dir:
            os.makedirs(os.path.join(data_dir, "theorems"), exist_ok=True)
            os.makedirs(os.path.join(data_dir, "proofs"), exist_ok=True)
            os.makedirs(os.path.join(data_dir, "counterexamples"), exist_ok=True)
        
        # Initialize data structures
        self.theorems: Dict[str, Theorem] = {}
        self.proofs: Dict[str, Proof] = {}
        self.counterexamples: Dict[str, Counterexample] = {}
        
        # Initialize graph for theorem relationships
        self.graph = nx.DiGraph()
        
        # Load data if directory exists
        if data_dir and os.path.exists(data_dir):
            self.load()
    
    def add_theorem(self, theorem: Theorem) -> str:
        """
        Add a theorem to the repository.
        
        Args:
            theorem: The theorem to add
            
        Returns:
            The theorem ID
        """
        # Add to in-memory storage
        self.theorems[theorem.theorem_id] = theorem
        
        # Add to graph
        self.graph.add_node(theorem.theorem_id, type="theorem", status=theorem.status.value)
        
        # Add edges for relationships
        for assumption_id in theorem.assumptions:
            if assumption_id in self.theorems or assumption_id in self.graph:
                self.graph.add_edge(assumption_id, theorem.theorem_id, type="assumption")
        
        for related_id in theorem.related_theorems:
            if related_id in self.theorems or related_id in self.graph:
                self.graph.add_edge(theorem.theorem_id, related_id, type="related")
                self.graph.add_edge(related_id, theorem.theorem_id, type="related")
        
        for generalization_id in theorem.generalizations:
            if generalization_id in self.theorems or generalization_id in self.graph:
                self.graph.add_edge(theorem.theorem_id, generalization_id, type="generalization")
                self.graph.add_edge(generalization_id, theorem.theorem_id, type="specialization")
        
        for specialization_id in theorem.specializations:
            if specialization_id in self.theorems or specialization_id in self.graph:
                self.graph.add_edge(theorem.theorem_id, specialization_id, type="specialization")
                self.graph.add_edge(specialization_id, theorem.theorem_id, type="generalization")
        
        # Save to disk if data directory is specified
        if self.data_dir:
            theorem_path = os.path.join(self.data_dir, "theorems", f"{theorem.theorem_id}.json")
            with open(theorem_path, 'w') as f:
                json.dump(theorem.to_dict(), f, indent=2)
        
        return theorem.theorem_id
    
    def add_proof(self, proof: Proof) -> str:
        """
        Add a proof to the repository.
        
        Args:
            proof: The proof to add
            
        Returns:
            The proof ID
        """
        # Add to in-memory storage
        self.proofs[proof.proof_id] = proof
        
        # Update theorem status if valid proof
        if proof.status == ProofStatus.VALID and proof.theorem_id in self.theorems:
            theorem = self.theorems[proof.theorem_id]
            theorem.status = TheoremStatus.PROVEN
            theorem.proofs.append(proof.proof_id)
            
            # Update graph
            self.graph.nodes[theorem.theorem_id]['status'] = TheoremStatus.PROVEN.value
        
        # Add graph edges for theorems and axioms used in the proof
        if proof.theorem_id in self.graph:
            self.graph.add_node(proof.proof_id, type="proof", status=proof.status.value)
            self.graph.add_edge(proof.proof_id, proof.theorem_id, type="proves")
            
            for theorem_id in proof.used_theorems:
                if theorem_id in self.theorems or theorem_id in self.graph:
                    self.graph.add_edge(proof.proof_id, theorem_id, type="uses_theorem")
            
            for axiom_id in proof.used_axioms:
                if axiom_id in self.theorems or axiom_id in self.graph:
                    self.graph.add_edge(proof.proof_id, axiom_id, type="uses_axiom")
        
        # Save to disk if data directory is specified
        if self.data_dir:
            proof_path = os.path.join(self.data_dir, "proofs", f"{proof.proof_id}.json")
            with open(proof_path, 'w') as f:
                json.dump(proof.to_dict(), f, indent=2)
        
        return proof.proof_id
    
    def add_counterexample(self, counterexample: Counterexample) -> str:
        """
        Add a counterexample to the repository.
        
        Args:
            counterexample: The counterexample to add
            
        Returns:
            The counterexample ID
        """
        # Add to in-memory storage
        self.counterexamples[counterexample.counterexample_id] = counterexample
        
        # Update theorem status
        if counterexample.theorem_id in self.theorems:
            theorem = self.theorems[counterexample.theorem_id]
            theorem.status = TheoremStatus.DISPROVEN
            theorem.counterexamples.append(counterexample.counterexample_id)
            
            # Update graph
            self.graph.nodes[theorem.theorem_id]['status'] = TheoremStatus.DISPROVEN.value
        
        # Add to graph
        if counterexample.theorem_id in self.graph:
            self.graph.add_node(counterexample.counterexample_id, type="counterexample")
            self.graph.add_edge(counterexample.counterexample_id, counterexample.theorem_id, type="disproves")
        
        # Save to disk if data directory is specified
        if self.data_dir:
            ce_path = os.path.join(self.data_dir, "counterexamples", f"{counterexample.counterexample_id}.json")
            with open(ce_path, 'w') as f:
                json.dump(counterexample.to_dict(), f, indent=2)
        
        return counterexample.counterexample_id
    
    def get_theorem(self, theorem_id: str) -> Optional[Theorem]:
        """
        Get a theorem by ID.
        
        Args:
            theorem_id: The ID of the theorem to retrieve
            
        Returns:
            The theorem, or None if not found
        """
        return self.theorems.get(theorem_id)
    
    def get_proof(self, proof_id: str) -> Optional[Proof]:
        """
        Get a proof by ID.
        
        Args:
            proof_id: The ID of the proof to retrieve
            
        Returns:
            The proof, or None if not found
        """
        return self.proofs.get(proof_id)
    
    def get_counterexample(self, counterexample_id: str) -> Optional[Counterexample]:
        """
        Get a counterexample by ID.
        
        Args:
            counterexample_id: The ID of the counterexample to retrieve
            
        Returns:
            The counterexample, or None if not found
        """
        return self.counterexamples.get(counterexample_id)
    
    def get_related_theorems(self, theorem_id: str) -> List[Theorem]:
        """
        Get theorems related to a given theorem.
        
        Args:
            theorem_id: The ID of the theorem to get related theorems for
            
        Returns:
            List of related theorems
        """
        if theorem_id not in self.graph:
            return []
        
        related_theorems = []
        for _, related_id, data in self.graph.out_edges(theorem_id, data=True):
            if data.get('type') in {'related', 'generalization', 'specialization'}:
                if related_id in self.theorems:
                    related_theorems.append(self.theorems[related_id])
        
        return related_theorems
    
    def get_proofs_for_theorem(self, theorem_id: str) -> List[Proof]:
        """
        Get all proofs for a given theorem.
        
        Args:
            theorem_id: The ID of the theorem to get proofs for
            
        Returns:
            List of proofs for the theorem
        """
        if theorem_id not in self.theorems:
            return []
        
        theorem = self.theorems[theorem_id]
        return [self.proofs[proof_id] for proof_id in theorem.proofs if proof_id in self.proofs]
    
    def get_counterexamples_for_theorem(self, theorem_id: str) -> List[Counterexample]:
        """
        Get all counterexamples for a given theorem.
        
        Args:
            theorem_id: The ID of the theorem to get counterexamples for
            
        Returns:
            List of counterexamples for the theorem
        """
        if theorem_id not in self.theorems:
            return []
        
        theorem = self.theorems[theorem_id]
        return [self.counterexamples[ce_id] for ce_id in theorem.counterexamples if ce_id in self.counterexamples]
    
    def search_theorems(self, query: str, domain: Optional[str] = None, 
                        tags: Optional[List[str]] = None, 
                        status: Optional[TheoremStatus] = None) -> List[Theorem]:
        """
        Search for theorems matching criteria.
        
        Args:
            query: Text to search for in theorem statements
            domain: Optional domain to filter by
            tags: Optional list of tags to filter by
            status: Optional status to filter by
            
        Returns:
            List of matching theorems
        """
        query = query.lower()
        matches = []
        
        for theorem in self.theorems.values():
            # Check text match
            if query in theorem.natural_language.lower() or query in theorem.formal_expression.lower():
                # Check domain filter
                if domain and theorem.metadata.domain != domain:
                    continue
                
                # Check tags filter
                if tags and not any(tag in theorem.metadata.tags for tag in tags):
                    continue
                
                # Check status filter
                if status and theorem.status != status:
                    continue
                
                matches.append(theorem)
        
        return matches
    
    def get_theorems_by_status(self, status: TheoremStatus) -> List[Theorem]:
        """
        Get all theorems with a given status.
        
        Args:
            status: The status to filter by
            
        Returns:
            List of matching theorems
        """
        return [theorem for theorem in self.theorems.values() if theorem.status == status]
    
    def get_theorem_dependency_graph(self, theorem_id: str) -> nx.DiGraph:
        """
        Get a dependency graph for a theorem.
        
        Args:
            theorem_id: The ID of the theorem to get dependencies for
            
        Returns:
            Directed graph of theorem dependencies
        """
        if theorem_id not in self.graph:
            return nx.DiGraph()
        
        # Get all predecessors (theorems this theorem depends on)
        dependencies = nx.ancestors(self.graph, theorem_id)
        dependencies.add(theorem_id)
        
        # Create subgraph
        return self.graph.subgraph(dependencies)
    
    def get_theorem_dependents_graph(self, theorem_id: str) -> nx.DiGraph:
        """
        Get a graph of theorems that depend on a given theorem.
        
        Args:
            theorem_id: The ID of the theorem to get dependents for
            
        Returns:
            Directed graph of theorem dependents
        """
        if theorem_id not in self.graph:
            return nx.DiGraph()
        
        # Get all successors (theorems that depend on this theorem)
        dependents = nx.descendants(self.graph, theorem_id)
        dependents.add(theorem_id)
        
        # Create subgraph
        return self.graph.subgraph(dependents)
    
    def get_theorems_by_domain(self, domain: str) -> List[Theorem]:
        """
        Get all theorems in a given domain.
        
        Args:
            domain: The domain to filter by
            
        Returns:
            List of matching theorems
        """
        return [theorem for theorem in self.theorems.values() if theorem.metadata.domain == domain]
    
    def get_theorems_by_tag(self, tag: str) -> List[Theorem]:
        """
        Get all theorems with a given tag.
        
        Args:
            tag: The tag to filter by
            
        Returns:
            List of matching theorems
        """
        return [theorem for theorem in self.theorems.values() if tag in theorem.metadata.tags]
    
    def get_next_theorems_to_prove(self, count: int = 10) -> List[Theorem]:
        """
        Get the next theorems to prove, based on priority and importance.
        
        Args:
            count: Number of theorems to return
            
        Returns:
            List of theorems to prove
        """
        unproven = [theorem for theorem in self.theorems.values() 
                   if theorem.status in [TheoremStatus.UNPROVEN, TheoremStatus.IN_PROGRESS]]
        
        # Sort by priority (lower is higher) and then by importance (higher is more important)
        sorted_theorems = sorted(unproven, key=lambda t: (t.metadata.priority, -t.metadata.importance))
        
        return sorted_theorems[:count]
    
    def save(self) -> None:
        """Save the repository to disk."""
        if not self.data_dir:
            raise ValueError("Cannot save repository: data directory not specified")
        
        # Save theorems
        for theorem_id, theorem in self.theorems.items():
            theorem_path = os.path.join(self.data_dir, "theorems", f"{theorem_id}.json")
            with open(theorem_path, 'w') as f:
                json.dump(theorem.to_dict(), f, indent=2)
        
        # Save proofs
        for proof_id, proof in self.proofs.items():
            proof_path = os.path.join(self.data_dir, "proofs", f"{proof_id}.json")
            with open(proof_path, 'w') as f:
                json.dump(proof.to_dict(), f, indent=2)
        
        # Save counterexamples
        for ce_id, ce in self.counterexamples.items():
            ce_path = os.path.join(self.data_dir, "counterexamples", f"{ce_id}.json")
            with open(ce_path, 'w') as f:
                json.dump(ce.to_dict(), f, indent=2)
        
        # Save graph
        graph_path = os.path.join(self.data_dir, "theorem_graph.pkl")
        with open(graph_path, 'wb') as f:
            pickle.dump(self.graph, f)
    
    def load(self) -> None:
        """Load the repository from disk."""
        if not self.data_dir or not os.path.exists(self.data_dir):
            return
        
        # Load theorems
        theorems_dir = os.path.join(self.data_dir, "theorems")
        if os.path.exists(theorems_dir):
            for filename in os.listdir(theorems_dir):
                if filename.endswith(".json"):
                    theorem_path = os.path.join(theorems_dir, filename)
                    with open(theorem_path, 'r') as f:
                        theorem_data = json.load(f)
                        theorem = Theorem.from_dict(theorem_data)
                        self.theorems[theorem.theorem_id] = theorem
        
        # Load proofs
        proofs_dir = os.path.join(self.data_dir, "proofs")
        if os.path.exists(proofs_dir):
            for filename in os.listdir(proofs_dir):
                if filename.endswith(".json"):
                    proof_path = os.path.join(proofs_dir, filename)
                    with open(proof_path, 'r') as f:
                        proof_data = json.load(f)
                        proof = Proof.from_dict(proof_data)
                        self.proofs[proof.proof_id] = proof
        
        # Load counterexamples
        ce_dir = os.path.join(self.data_dir, "counterexamples")
        if os.path.exists(ce_dir):
            for filename in os.listdir(ce_dir):
                if filename.endswith(".json"):
                    ce_path = os.path.join(ce_dir, filename)
                    with open(ce_path, 'r') as f:
                        ce_data = json.load(f)
                        ce = Counterexample.from_dict(ce_data)
                        self.counterexamples[ce.counterexample_id] = ce
        
        # Load graph
        graph_path = os.path.join(self.data_dir, "theorem_graph.pkl")
        if os.path.exists(graph_path):
            with open(graph_path, 'rb') as f:
                self.graph = pickle.load(f)
        else:
            # Rebuild graph from theorems and proofs
            self._rebuild_graph()
    
    def _rebuild_graph(self) -> None:
        """Rebuild the theorem relationship graph from scratch."""
        self.graph = nx.DiGraph()
        
        # Add theorems
        for theorem_id, theorem in self.theorems.items():
            self.graph.add_node(theorem_id, type="theorem", status=theorem.status.value)
        
        # Add proofs
        for proof_id, proof in self.proofs.items():
            self.graph.add_node(proof_id, type="proof", status=proof.status.value)
            
            # Add proof -> theorem edge
            if proof.theorem_id in self.theorems:
                self.graph.add_edge(proof_id, proof.theorem_id, type="proves")
            
            # Add proof -> used theorem edges
            for theorem_id in proof.used_theorems:
                if theorem_id in self.theorems:
                    self.graph.add_edge(proof_id, theorem_id, type="uses_theorem")
            
            # Add proof -> used axiom edges
            for axiom_id in proof.used_axioms:
                if axiom_id in self.theorems:
                    self.graph.add_edge(proof_id, axiom_id, type="uses_axiom")
        
        # Add counterexamples
        for ce_id, ce in self.counterexamples.items():
            self.graph.add_node(ce_id, type="counterexample")
            
            # Add counterexample -> theorem edge
            if ce.theorem_id in self.theorems:
                self.graph.add_edge(ce_id, ce.theorem_id, type="disproves")
        
        # Add theorem relationships
        for theorem_id, theorem in self.theorems.items():
            # Add assumption edges
            for assumption_id in theorem.assumptions:
                if assumption_id in self.theorems:
                    self.graph.add_edge(assumption_id, theorem_id, type="assumption")
            
            # Add related theorem edges
            for related_id in theorem.related_theorems:
                if related_id in self.theorems:
                    self.graph.add_edge(theorem_id, related_id, type="related")
                    self.graph.add_edge(related_id, theorem_id, type="related")
            
            # Add generalization edges
            for generalization_id in theorem.generalizations:
                if generalization_id in self.theorems:
                    self.graph.add_edge(theorem_id, generalization_id, type="generalization")
                    self.graph.add_edge(generalization_id, theorem_id, type="specialization")
            
            # Add specialization edges
            for specialization_id in theorem.specializations:
                if specialization_id in self.theorems:
                    self.graph.add_edge(theorem_id, specialization_id, type="specialization")
                    self.graph.add_edge(specialization_id, theorem_id, type="generalization")
    
    def get_repository_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the repository.
        
        Returns:
            Dictionary of repository statistics
        """
        # Count theorems by status
        status_counts = {status.value: 0 for status in TheoremStatus}
        for theorem in self.theorems.values():
            status_counts[theorem.status.value] += 1
        
        # Count theorems by domain
        domain_counts = {}
        for theorem in self.theorems.values():
            domain = theorem.metadata.domain
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Calculate proof success rate
        valid_proofs = sum(1 for proof in self.proofs.values() if proof.status == ProofStatus.VALID)
        proof_success_rate = valid_proofs / len(self.proofs) if self.proofs else 0.0
        
        # Get average verification level
        avg_verification = sum(theorem.metadata.verification_level for theorem in self.theorems.values()) / len(self.theorems) if self.theorems else 0.0
        
        return {
            "total_theorems": len(self.theorems),
            "total_proofs": len(self.proofs),
            "total_counterexamples": len(self.counterexamples),
            "theorem_status_counts": status_counts,
            "domain_counts": domain_counts,
            "proof_success_rate": proof_success_rate,
            "average_verification_level": avg_verification,
            "graph_node_count": self.graph.number_of_nodes(),
            "graph_edge_count": self.graph.number_of_edges()
        }