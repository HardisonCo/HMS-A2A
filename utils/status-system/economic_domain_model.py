#!/usr/bin/env python3
"""
Economic Domain Model for Theorem Proving

This module provides formal representations of economic concepts, axioms, and theorems
in a format compatible with formal verification systems like Lean. It serves as the
foundation for economic theorem proving by genetic agents.

Key Components:
- EconomicConcept: Base class for all economic domain entities
- DomainAxiom: Represents fundamental economic axioms
- DomainTheorem: Represents economic theorems to be proved
- DomainRelation: Captures relationships between economic concepts
- DomainModelManager: Manages the economic domain knowledge base
"""

import json
import os
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field


class ConceptType(Enum):
    """Types of economic concepts in the domain model."""
    AGENT = "agent"  # Economic agents (consumers, firms, etc.)
    GOOD = "good"  # Economic goods and services
    MARKET = "market"  # Market structures and mechanisms
    PREFERENCE = "preference"  # Preference relations and utility
    PRODUCTION = "production"  # Production technologies and functions
    EQUILIBRIUM = "equilibrium"  # Equilibrium concepts
    WELFARE = "welfare"  # Welfare concepts and social choice
    INFORMATION = "information"  # Information structures
    UNCERTAINTY = "uncertainty"  # Risk and uncertainty
    GAME = "game"  # Game theoretic concepts
    META = "meta"  # Meta-concepts across domains


class FormalizationLanguage(Enum):
    """Supported formalization languages for economic concepts."""
    LEAN4 = "lean4"  # Lean 4 theorem prover
    COQ = "coq"  # Coq theorem prover
    ISABELLE = "isabelle"  # Isabelle/HOL theorem prover
    METAMATH = "metamath"  # Metamath proof language
    INTERNAL = "internal"  # Internal representation for the system


@dataclass
class FormalDefinition:
    """Formal definition of an economic concept in a specific language."""
    language: FormalizationLanguage
    code: str
    imports: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class EconomicConcept:
    """Base class for all economic domain entities."""
    id: str
    name: str
    description: str
    concept_type: ConceptType
    formal_definitions: Dict[FormalizationLanguage, FormalDefinition] = field(default_factory=dict)
    related_concepts: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def add_formal_definition(self, definition: FormalDefinition) -> None:
        """Add a formal definition in a specific language."""
        self.formal_definitions[definition.language] = definition
    
    def get_formal_definition(self, language: FormalizationLanguage) -> Optional[FormalDefinition]:
        """Get the formal definition in the specified language."""
        return self.formal_definitions.get(language)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "concept_type": self.concept_type.value,
            "formal_definitions": {
                lang.value: {
                    "code": defn.code,
                    "imports": defn.imports,
                    "dependencies": defn.dependencies
                } for lang, defn in self.formal_definitions.items()
            },
            "related_concepts": self.related_concepts,
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EconomicConcept':
        """Create an EconomicConcept from a dictionary."""
        concept = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            concept_type=ConceptType(data["concept_type"]),
            related_concepts=data.get("related_concepts", []),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )
        
        for lang_str, defn_data in data.get("formal_definitions", {}).items():
            language = FormalizationLanguage(lang_str)
            concept.add_formal_definition(FormalDefinition(
                language=language,
                code=defn_data["code"],
                imports=defn_data.get("imports", []),
                dependencies=defn_data.get("dependencies", [])
            ))
        
        return concept


@dataclass
class DomainAxiom(EconomicConcept):
    """Represents a fundamental economic axiom."""
    is_primitive: bool = True
    justification: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "is_primitive": self.is_primitive,
            "justification": self.justification
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DomainAxiom':
        """Create a DomainAxiom from a dictionary."""
        concept = super().from_dict(data)
        axiom = cls(
            id=concept.id,
            name=concept.name,
            description=concept.description,
            concept_type=concept.concept_type,
            formal_definitions=concept.formal_definitions,
            related_concepts=concept.related_concepts,
            tags=concept.tags,
            metadata=concept.metadata,
            is_primitive=data.get("is_primitive", True),
            justification=data.get("justification", "")
        )
        return axiom


class TheoremStatus(Enum):
    """Status of a theorem in the formalization process."""
    CONJECTURED = "conjectured"  # Proposed but not proven
    PARTIALLY_PROVEN = "partially_proven"  # Some proofs exist but incomplete
    PROVEN = "proven"  # Fully proven
    DISPROVEN = "disproven"  # Counter-example found
    UNDECIDABLE = "undecidable"  # Shown to be undecidable in the system


@dataclass
class ProofStep:
    """A single step in a proof."""
    step_id: str
    description: str
    formal_code: str
    depends_on: List[str] = field(default_factory=list)
    generated_by: Optional[str] = None  # Agent ID that generated this step
    confidence: float = 1.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "step_id": self.step_id,
            "description": self.description,
            "formal_code": self.formal_code,
            "depends_on": self.depends_on,
            "generated_by": self.generated_by,
            "confidence": self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProofStep':
        """Create a ProofStep from a dictionary."""
        return cls(
            step_id=data["step_id"],
            description=data["description"],
            formal_code=data["formal_code"],
            depends_on=data.get("depends_on", []),
            generated_by=data.get("generated_by"),
            confidence=data.get("confidence", 1.0)
        )


@dataclass
class Proof:
    """A formal proof of a theorem."""
    proof_id: str
    language: FormalizationLanguage
    steps: List[ProofStep] = field(default_factory=list)
    complete: bool = False
    verified: bool = False
    created_by: Optional[str] = None
    created_at: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "proof_id": self.proof_id,
            "language": self.language.value,
            "steps": [step.to_dict() for step in self.steps],
            "complete": self.complete,
            "verified": self.verified,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Proof':
        """Create a Proof from a dictionary."""
        proof = cls(
            proof_id=data["proof_id"],
            language=FormalizationLanguage(data["language"]),
            complete=data.get("complete", False),
            verified=data.get("verified", False),
            created_by=data.get("created_by"),
            created_at=data.get("created_at", ""),
            metadata=data.get("metadata", {})
        )
        proof.steps = [ProofStep.from_dict(step) for step in data.get("steps", [])]
        return proof


@dataclass
class DomainTheorem(EconomicConcept):
    """Represents an economic theorem to be proven."""
    status: TheoremStatus = TheoremStatus.CONJECTURED
    difficulty: int = 1  # 1-10 scale of proving difficulty
    importance: int = 1  # 1-10 scale of theorem importance
    proofs: List[Proof] = field(default_factory=list)
    decomposition: List[str] = field(default_factory=list)  # IDs of subgoal theorems
    parent_theorems: List[str] = field(default_factory=list)  # IDs of theorems this is a subgoal for
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "status": self.status.value,
            "difficulty": self.difficulty,
            "importance": self.importance,
            "proofs": [proof.to_dict() for proof in self.proofs],
            "decomposition": self.decomposition,
            "parent_theorems": self.parent_theorems
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DomainTheorem':
        """Create a DomainTheorem from a dictionary."""
        concept = super().from_dict(data)
        theorem = cls(
            id=concept.id,
            name=concept.name,
            description=concept.description,
            concept_type=concept.concept_type,
            formal_definitions=concept.formal_definitions,
            related_concepts=concept.related_concepts,
            tags=concept.tags,
            metadata=concept.metadata,
            status=TheoremStatus(data.get("status", "conjectured")),
            difficulty=data.get("difficulty", 1),
            importance=data.get("importance", 1),
            decomposition=data.get("decomposition", []),
            parent_theorems=data.get("parent_theorems", [])
        )
        
        theorem.proofs = [Proof.from_dict(proof) for proof in data.get("proofs", [])]
        return theorem


class RelationType(Enum):
    """Types of relationships between economic concepts."""
    GENERALIZATION = "generalization"  # Is-a relationship
    COMPOSITION = "composition"  # Has-a relationship
    DEPENDENCY = "dependency"  # Depends-on relationship
    EQUIVALENCE = "equivalence"  # Equivalent concepts
    CONTRADICTION = "contradiction"  # Contradictory concepts
    IMPLICATION = "implication"  # One concept implies another
    ASSOCIATION = "association"  # General association


@dataclass
class DomainRelation:
    """Captures a relationship between economic concepts."""
    id: str
    relation_type: RelationType
    source_id: str
    target_id: str
    description: str = ""
    formal_definition: Optional[str] = None
    bidirectional: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "relation_type": self.relation_type.value,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "description": self.description,
            "formal_definition": self.formal_definition,
            "bidirectional": self.bidirectional,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DomainRelation':
        """Create a DomainRelation from a dictionary."""
        return cls(
            id=data["id"],
            relation_type=RelationType(data["relation_type"]),
            source_id=data["source_id"],
            target_id=data["target_id"],
            description=data.get("description", ""),
            formal_definition=data.get("formal_definition"),
            bidirectional=data.get("bidirectional", False),
            metadata=data.get("metadata", {})
        )


class DomainModelManager:
    """Manages the economic domain knowledge base."""
    
    def __init__(self, storage_dir: str = "./domain_model"):
        """Initialize the domain model manager.
        
        Args:
            storage_dir: Directory to store domain model files
        """
        self.storage_dir = storage_dir
        self.concepts: Dict[str, EconomicConcept] = {}
        self.axioms: Dict[str, DomainAxiom] = {}
        self.theorems: Dict[str, DomainTheorem] = {}
        self.relations: Dict[str, DomainRelation] = {}
        
        os.makedirs(storage_dir, exist_ok=True)
        
        # Paths for storing different components
        self.concepts_path = os.path.join(storage_dir, "concepts.json")
        self.axioms_path = os.path.join(storage_dir, "axioms.json")
        self.theorems_path = os.path.join(storage_dir, "theorems.json")
        self.relations_path = os.path.join(storage_dir, "relations.json")
        
        # Load existing data if available
        self._load_data()
    
    def _load_data(self) -> None:
        """Load domain model data from storage."""
        if os.path.exists(self.concepts_path):
            with open(self.concepts_path, 'r') as f:
                concepts_data = json.load(f)
                self.concepts = {
                    id: EconomicConcept.from_dict(data) 
                    for id, data in concepts_data.items()
                }
        
        if os.path.exists(self.axioms_path):
            with open(self.axioms_path, 'r') as f:
                axioms_data = json.load(f)
                self.axioms = {
                    id: DomainAxiom.from_dict(data) 
                    for id, data in axioms_data.items()
                }
        
        if os.path.exists(self.theorems_path):
            with open(self.theorems_path, 'r') as f:
                theorems_data = json.load(f)
                self.theorems = {
                    id: DomainTheorem.from_dict(data) 
                    for id, data in theorems_data.items()
                }
        
        if os.path.exists(self.relations_path):
            with open(self.relations_path, 'r') as f:
                relations_data = json.load(f)
                self.relations = {
                    id: DomainRelation.from_dict(data) 
                    for id, data in relations_data.items()
                }
    
    def _save_data(self) -> None:
        """Save domain model data to storage."""
        # Save concepts
        with open(self.concepts_path, 'w') as f:
            json.dump({
                id: concept.to_dict() 
                for id, concept in self.concepts.items()
            }, f, indent=2)
        
        # Save axioms
        with open(self.axioms_path, 'w') as f:
            json.dump({
                id: axiom.to_dict() 
                for id, axiom in self.axioms.items()
            }, f, indent=2)
        
        # Save theorems
        with open(self.theorems_path, 'w') as f:
            json.dump({
                id: theorem.to_dict() 
                for id, theorem in self.theorems.items()
            }, f, indent=2)
        
        # Save relations
        with open(self.relations_path, 'w') as f:
            json.dump({
                id: relation.to_dict() 
                for id, relation in self.relations.items()
            }, f, indent=2)
    
    def add_concept(self, concept: EconomicConcept) -> None:
        """Add a concept to the domain model."""
        self.concepts[concept.id] = concept
        self._save_data()
    
    def add_axiom(self, axiom: DomainAxiom) -> None:
        """Add an axiom to the domain model."""
        self.axioms[axiom.id] = axiom
        self.concepts[axiom.id] = axiom  # Also store in concepts
        self._save_data()
    
    def add_theorem(self, theorem: DomainTheorem) -> None:
        """Add a theorem to the domain model."""
        self.theorems[theorem.id] = theorem
        self.concepts[theorem.id] = theorem  # Also store in concepts
        self._save_data()
    
    def add_relation(self, relation: DomainRelation) -> None:
        """Add a relation to the domain model."""
        self.relations[relation.id] = relation
        
        # Update related_concepts for source and target
        source = self.get_concept(relation.source_id)
        target = self.get_concept(relation.target_id)
        
        if source and target.id not in source.related_concepts:
            source.related_concepts.append(target.id)
        
        if target and source.id not in target.related_concepts:
            target.related_concepts.append(source.id)
        
        self._save_data()
    
    def get_concept(self, concept_id: str) -> Optional[EconomicConcept]:
        """Get a concept by its ID."""
        return self.concepts.get(concept_id)
    
    def get_axiom(self, axiom_id: str) -> Optional[DomainAxiom]:
        """Get an axiom by its ID."""
        return self.axioms.get(axiom_id)
    
    def get_theorem(self, theorem_id: str) -> Optional[DomainTheorem]:
        """Get a theorem by its ID."""
        return self.theorems.get(theorem_id)
    
    def get_relation(self, relation_id: str) -> Optional[DomainRelation]:
        """Get a relation by its ID."""
        return self.relations.get(relation_id)
    
    def get_relations_for_concept(self, concept_id: str) -> List[DomainRelation]:
        """Get all relations involving a concept."""
        return [
            relation for relation in self.relations.values()
            if relation.source_id == concept_id or relation.target_id == concept_id
        ]
    
    def get_concepts_by_type(self, concept_type: ConceptType) -> List[EconomicConcept]:
        """Get all concepts of a specific type."""
        return [
            concept for concept in self.concepts.values()
            if concept.concept_type == concept_type
        ]
    
    def get_theorems_by_status(self, status: TheoremStatus) -> List[DomainTheorem]:
        """Get all theorems with a specific status."""
        return [
            theorem for theorem in self.theorems.values()
            if theorem.status == status
        ]
    
    def update_theorem_status(self, theorem_id: str, status: TheoremStatus) -> bool:
        """Update the status of a theorem."""
        theorem = self.get_theorem(theorem_id)
        if not theorem:
            return False
        
        theorem.status = status
        self._save_data()
        return True
    
    def add_proof_to_theorem(self, theorem_id: str, proof: Proof) -> bool:
        """Add a proof to a theorem."""
        theorem = self.get_theorem(theorem_id)
        if not theorem:
            return False
        
        # Check if proof with this ID already exists
        existing_proof_ids = [p.proof_id for p in theorem.proofs]
        if proof.proof_id in existing_proof_ids:
            # Replace existing proof
            idx = existing_proof_ids.index(proof.proof_id)
            theorem.proofs[idx] = proof
        else:
            # Add new proof
            theorem.proofs.append(proof)
        
        # Update theorem status if proof is complete and verified
        if proof.complete and proof.verified and theorem.status != TheoremStatus.PROVEN:
            theorem.status = TheoremStatus.PROVEN
        
        self._save_data()
        return True
    
    def export_to_lean(self, output_dir: str) -> None:
        """Export the domain model to Lean 4 source files."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Export axioms
        axioms_file = os.path.join(output_dir, "EconomicAxioms.lean")
        with open(axioms_file, 'w') as f:
            f.write("import Mathlib.Data.Real.Basic\n\n")
            f.write("/-!\n# Economic Axioms\n\nThis file contains the basic axioms of economic theory.\n-/\n\n")
            f.write("namespace Economic\n\n")
            
            for axiom in self.axioms.values():
                lean_def = axiom.get_formal_definition(FormalizationLanguage.LEAN4)
                if lean_def:
                    f.write(f"/-\n{axiom.name}\n\n{axiom.description}\n-/\n")
                    f.write(lean_def.code)
                    f.write("\n\n")
            
            f.write("end Economic\n")
        
        # Export theorems
        theorems_file = os.path.join(output_dir, "EconomicTheorems.lean")
        with open(theorems_file, 'w') as f:
            f.write("import EconomicAxioms\n\n")
            f.write("/-!\n# Economic Theorems\n\nThis file contains the theorems of economic theory.\n-/\n\n")
            f.write("namespace Economic\n\n")
            
            for theorem in self.theorems.values():
                lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
                if lean_def:
                    f.write(f"/-\n{theorem.name}\n\n{theorem.description}\n-/\n")
                    f.write(lean_def.code)
                    f.write("\n\n")
            
            f.write("end Economic\n")
    
    def get_concept_neighborhood(self, concept_id: str, depth: int = 1) -> Set[str]:
        """Get IDs of concepts in the neighborhood of a concept.
        
        Args:
            concept_id: ID of the central concept
            depth: Depth of neighborhood traversal
            
        Returns:
            Set of concept IDs in the neighborhood
        """
        if depth <= 0:
            return {concept_id}
        
        neighborhood = {concept_id}
        concept = self.get_concept(concept_id)
        
        if not concept:
            return neighborhood
        
        # Add directly related concepts
        neighborhood.update(concept.related_concepts)
        
        # Recursively add neighbors of neighbors
        if depth > 1:
            for related_id in concept.related_concepts:
                sub_neighborhood = self.get_concept_neighborhood(related_id, depth - 1)
                neighborhood.update(sub_neighborhood)
        
        return neighborhood
    
    def find_path_between_concepts(self, 
                                  source_id: str, 
                                  target_id: str, 
                                  max_depth: int = 5) -> Optional[List[str]]:
        """Find a path between two concepts in the concept graph.
        
        Args:
            source_id: ID of the source concept
            target_id: ID of the target concept
            max_depth: Maximum path length to consider
            
        Returns:
            List of concept IDs forming a path, or None if no path exists
        """
        if source_id == target_id:
            return [source_id]
        
        # Breadth-first search
        queue = [(source_id, [source_id])]
        visited = {source_id}
        
        while queue:
            current_id, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            current_concept = self.get_concept(current_id)
            if not current_concept:
                continue
            
            for related_id in current_concept.related_concepts:
                if related_id == target_id:
                    return path + [target_id]
                
                if related_id not in visited:
                    visited.add(related_id)
                    queue.append((related_id, path + [related_id]))
        
        return None


if __name__ == "__main__":
    # Basic usage example
    manager = DomainModelManager()
    
    # Create and add a concept
    utility = EconomicConcept(
        id="utility",
        name="Utility",
        description="A measure of satisfaction or happiness derived from consumption.",
        concept_type=ConceptType.PREFERENCE
    )
    
    # Add a formal definition in Lean
    utility.add_formal_definition(FormalDefinition(
        language=FormalizationLanguage.LEAN4,
        code="""
/-- Utility is a function from bundles of goods to real numbers. -/
def Utility (n : Nat) := Fin n → ℝ → ℝ

/-- A utility function is monotonic if more goods always lead to higher utility. -/
def Monotonic {n : Nat} (u : Utility n) : Prop :=
  ∀ (bundle1 bundle2 : Fin n → ℝ), 
    (∀ i, bundle1 i ≤ bundle2 i) → (∃ j, bundle1 j < bundle2 j) → 
    u bundle1 < u bundle2
""",
        imports=["Mathlib.Data.Real.Basic", "Mathlib.Data.Fin.Basic"]
    ))
    
    manager.add_concept(utility)
    
    # Create and add an axiom
    nonsatiation = DomainAxiom(
        id="nonsatiation",
        name="Non-satiation",
        description="Consumers always prefer more goods to less.",
        concept_type=ConceptType.PREFERENCE,
        is_primitive=True,
        justification="Basic axiom of consumer theory, supported by empirical evidence."
    )
    
    nonsatiation.add_formal_definition(FormalDefinition(
        language=FormalizationLanguage.LEAN4,
        code="""
/-- The non-satiation axiom states that for any consumer, more is always preferred to less. -/
axiom nonsatiation {n : Nat} (u : Utility n) : Monotonic u
""",
        imports=["Mathlib.Data.Real.Basic"],
        dependencies=["utility"]
    ))
    
    manager.add_axiom(nonsatiation)
    
    # Create and add a theorem
    utility_maximization = DomainTheorem(
        id="utility_maximization",
        name="Utility Maximization under Budget Constraint",
        description="Consumers maximize utility subject to their budget constraints.",
        concept_type=ConceptType.PREFERENCE,
        status=TheoremStatus.CONJECTURED,
        difficulty=5,
        importance=8
    )
    
    utility_maximization.add_formal_definition(FormalDefinition(
        language=FormalizationLanguage.LEAN4,
        code="""
/-- Budget constraint: the total expenditure on goods cannot exceed income. -/
def BudgetConstraint {n : Nat} (prices : Fin n → ℝ) (income : ℝ) (bundle : Fin n → ℝ) : Prop :=
  (∑ i, prices i * bundle i) ≤ income

/-- A bundle is utility-maximizing if no affordable bundle yields higher utility. -/
def UtilityMaximizing {n : Nat} (u : Utility n) (prices : Fin n → ℝ) (income : ℝ) (bundle : Fin n → ℝ) : Prop :=
  BudgetConstraint prices income bundle ∧ 
  ∀ (bundle' : Fin n → ℝ), BudgetConstraint prices income bundle' → u bundle' ≤ u bundle

/-- Under non-satiation, the budget constraint binds at a utility-maximizing bundle. -/
theorem utility_maximization_budget_binding {n : Nat} (u : Utility n) (prices : Fin n → ℝ) (income : ℝ) (bundle : Fin n → ℝ)
  (h_positive_prices : ∀ i, prices i > 0)
  (h_monotonic : Monotonic u)
  (h_maximizing : UtilityMaximizing u prices income bundle) :
  (∑ i, prices i * bundle i) = income :=
  sorry
""",
        imports=["Mathlib.Data.Real.Basic", "Mathlib.Algebra.BigOperators.Basic"],
        dependencies=["utility", "nonsatiation"]
    ))
    
    manager.add_theorem(utility_maximization)
    
    # Create and add a relation
    utility_nonsatiation_relation = DomainRelation(
        id="utility_nonsatiation_rel",
        relation_type=RelationType.IMPLICATION,
        source_id="nonsatiation",
        target_id="utility_maximization",
        description="Non-satiation implies that the budget constraint binds at an optimum.",
        formal_definition="∀ {n : Nat} (u : Utility n), Monotonic u → (∀ (prices : Fin n → ℝ) (income : ℝ) (bundle : Fin n → ℝ), UtilityMaximizing u prices income bundle → (∑ i, prices i * bundle i) = income)"
    )
    
    manager.add_relation(utility_nonsatiation_relation)
    
    # Export to Lean files
    manager.export_to_lean("./lean_export")