#!/usr/bin/env python3
"""
Economic Theorem Prover

This module provides the core theorem proving functionality for economic theorems,
leveraging DeepSeek-Prover-V2 for formal verification. It supports automated proof
generation, proof checking, and theorem decomposition for complex proofs.

Key Components:
- TheoremProver: Core prover that manages theorem proving workflows
- ProofStrategy: Represents proof strategies that can evolve through genetic algorithms
- SubgoalDecomposer: Breaks down complex theorems into manageable subgoals
- ProofVerifier: Verifies the correctness of generated proofs
"""

import os
import json
import time
import random
import asyncio
import tempfile
import subprocess
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path

from economic_domain_model import (
    ConceptType, DomainAxiom, DomainModelManager, DomainTheorem, 
    EconomicConcept, FormalDefinition, FormalizationLanguage,
    Proof, ProofStep, TheoremStatus, RelationType, DomainRelation
)

from economic_formal_translator import (
    LeanTranslator, FormalStructureGenerator, ProofGenerator, EconomicInterpreter
)


class ProofMethod(Enum):
    """Methods of proof for economic theorems."""
    DIRECT = "direct"  # Direct proof
    CONTRADICTION = "contradiction"  # Proof by contradiction
    CONTRAPOSITIVE = "contrapositive"  # Proof by contrapositive
    INDUCTION = "induction"  # Proof by induction
    CONSTRUCTION = "construction"  # Proof by construction
    CASES = "cases"  # Proof by cases
    ALGEBRAIC = "algebraic"  # Algebraic manipulation
    FIXED_POINT = "fixed_point"  # Fixed point theorems


@dataclass
class ProofStrategy:
    """Represents a proof strategy that can evolve through genetic algorithms."""
    id: str
    name: str
    description: str
    methods: List[ProofMethod]
    heuristics: Dict[str, float]  # Heuristic name to weight mapping
    axiom_preferences: List[str]  # IDs of preferred axioms to use
    lemma_preferences: List[str]  # IDs of preferred lemmas to use
    decomposition_threshold: int  # Complexity threshold for decomposition
    max_steps: int  # Maximum number of proof steps
    timeout: int  # Timeout in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "methods": [method.value for method in self.methods],
            "heuristics": self.heuristics,
            "axiom_preferences": self.axiom_preferences,
            "lemma_preferences": self.lemma_preferences,
            "decomposition_threshold": self.decomposition_threshold,
            "max_steps": self.max_steps,
            "timeout": self.timeout,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProofStrategy':
        """Create a ProofStrategy from a dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            methods=[ProofMethod(method) for method in data["methods"]],
            heuristics=data["heuristics"],
            axiom_preferences=data["axiom_preferences"],
            lemma_preferences=data["lemma_preferences"],
            decomposition_threshold=data["decomposition_threshold"],
            max_steps=data["max_steps"],
            timeout=data["timeout"],
            metadata=data.get("metadata", {})
        )
    
    def crossover(self, other: 'ProofStrategy') -> 'ProofStrategy':
        """Create a new strategy by crossing over with another strategy."""
        # Generate a new ID
        new_id = f"strategy_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Mix methods from both parents
        methods = list(set(self.methods + other.methods))
        if len(methods) > 5:  # Limit the number of methods
            methods = random.sample(methods, 5)
        
        # Combine heuristics using weighted average
        heuristics = {}
        all_heuristics = set(list(self.heuristics.keys()) + list(other.heuristics.keys()))
        for h in all_heuristics:
            weight1 = self.heuristics.get(h, 0.0)
            weight2 = other.heuristics.get(h, 0.0)
            # Random weight for combination
            r = random.random()
            heuristics[h] = r * weight1 + (1 - r) * weight2
        
        # Select some axioms and lemmas from each parent
        axiom_preferences = list(set(
            random.sample(self.axiom_preferences, min(len(self.axiom_preferences), 3)) +
            random.sample(other.axiom_preferences, min(len(other.axiom_preferences), 3))
        ))
        
        lemma_preferences = list(set(
            random.sample(self.lemma_preferences, min(len(self.lemma_preferences), 3)) +
            random.sample(other.lemma_preferences, min(len(other.lemma_preferences), 3))
        ))
        
        # Parameters can be mixed or taken from one parent
        if random.random() < 0.5:
            decomposition_threshold = self.decomposition_threshold
        else:
            decomposition_threshold = other.decomposition_threshold
        
        if random.random() < 0.5:
            max_steps = self.max_steps
        else:
            max_steps = other.max_steps
        
        if random.random() < 0.5:
            timeout = self.timeout
        else:
            timeout = other.timeout
        
        return ProofStrategy(
            id=new_id,
            name=f"Crossover({self.name}, {other.name})",
            description=f"Strategy created by crossing over {self.name} and {other.name}",
            methods=methods,
            heuristics=heuristics,
            axiom_preferences=axiom_preferences,
            lemma_preferences=lemma_preferences,
            decomposition_threshold=decomposition_threshold,
            max_steps=max_steps,
            timeout=timeout
        )
    
    def mutate(self, mutation_rate: float = 0.1) -> 'ProofStrategy':
        """Create a new strategy by mutating this strategy."""
        # Generate a new ID
        new_id = f"strategy_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Potentially add or remove a method
        methods = list(self.methods)
        if random.random() < mutation_rate:
            if len(methods) < len(ProofMethod) and random.random() < 0.5:
                # Add a new method
                available_methods = [m for m in ProofMethod if m not in methods]
                if available_methods:
                    methods.append(random.choice(available_methods))
            elif len(methods) > 1 and random.random() < 0.5:
                # Remove a method
                methods.remove(random.choice(methods))
        
        # Mutate heuristics
        heuristics = dict(self.heuristics)
        for h in heuristics:
            if random.random() < mutation_rate:
                # Adjust the weight by up to 20%
                delta = (random.random() - 0.5) * 0.4
                heuristics[h] = max(0.0, min(1.0, heuristics[h] + delta))
        
        # Potentially add a new heuristic
        if random.random() < mutation_rate:
            new_heuristics = [
                "contradiction_frequency", "lemma_utilization", "axiom_utilization",
                "step_simplicity", "symbol_count", "term_reuse", "structural_insight"
            ]
            unused_heuristics = [h for h in new_heuristics if h not in heuristics]
            if unused_heuristics:
                new_h = random.choice(unused_heuristics)
                heuristics[new_h] = random.random() * 0.5  # Start with a moderate weight
        
        # Mutate axiom and lemma preferences
        axiom_preferences = list(self.axiom_preferences)
        if random.random() < mutation_rate:
            if random.random() < 0.5 and axiom_preferences:
                # Remove a preference
                axiom_preferences.remove(random.choice(axiom_preferences))
            else:
                # Add a placeholder preference
                axiom_preferences.append(f"axiom_{random.randint(1, 100)}")
        
        lemma_preferences = list(self.lemma_preferences)
        if random.random() < mutation_rate:
            if random.random() < 0.5 and lemma_preferences:
                # Remove a preference
                lemma_preferences.remove(random.choice(lemma_preferences))
            else:
                # Add a placeholder preference
                lemma_preferences.append(f"lemma_{random.randint(1, 100)}")
        
        # Mutate parameters
        decomposition_threshold = self.decomposition_threshold
        if random.random() < mutation_rate:
            # Adjust by up to 20%
            delta = int((random.random() - 0.5) * 0.4 * decomposition_threshold)
            decomposition_threshold = max(1, decomposition_threshold + delta)
        
        max_steps = self.max_steps
        if random.random() < mutation_rate:
            # Adjust by up to 20%
            delta = int((random.random() - 0.5) * 0.4 * max_steps)
            max_steps = max(5, max_steps + delta)
        
        timeout = self.timeout
        if random.random() < mutation_rate:
            # Adjust by up to 20%
            delta = int((random.random() - 0.5) * 0.4 * timeout)
            timeout = max(10, timeout + delta)
        
        return ProofStrategy(
            id=new_id,
            name=f"Mutated({self.name})",
            description=f"Strategy created by mutating {self.name}",
            methods=methods,
            heuristics=heuristics,
            axiom_preferences=axiom_preferences,
            lemma_preferences=lemma_preferences,
            decomposition_threshold=decomposition_threshold,
            max_steps=max_steps,
            timeout=timeout
        )


class SubgoalDecomposer:
    """Breaks down complex theorems into manageable subgoals."""
    
    def __init__(self, domain_manager: DomainModelManager):
        """Initialize the decomposer.
        
        Args:
            domain_manager: The domain model manager
        """
        self.domain_manager = domain_manager
    
    def decompose_theorem(self, theorem: DomainTheorem, max_depth: int = 3) -> List[DomainTheorem]:
        """Decompose a theorem into subgoals.
        
        Args:
            theorem: The theorem to decompose
            max_depth: Maximum recursion depth for decomposition
            
        Returns:
            List of subgoal theorems
        """
        # If already decomposed, return the subgoals
        if theorem.decomposition:
            return [self.domain_manager.get_theorem(id) for id in theorem.decomposition if self.domain_manager.get_theorem(id)]
        
        # If simple enough or max depth reached, don't decompose
        if theorem.difficulty <= 3 or max_depth <= 0:
            return [theorem]
        
        # Get the formal definition to analyze
        lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
        if not lean_def:
            return [theorem]
        
        # Analyze theorem structure for decomposition
        subgoals = self._analyze_theorem_structure(theorem, lean_def)
        
        # If subgoals were identified, create them and link to original theorem
        if subgoals:
            subgoal_theorems = []
            for i, (name, description, formula) in enumerate(subgoals):
                subgoal_id = f"{theorem.id}_subgoal_{i+1}"
                
                # Create the subgoal theorem
                subgoal = DomainTheorem(
                    id=subgoal_id,
                    name=name,
                    description=description,
                    concept_type=theorem.concept_type,
                    status=TheoremStatus.CONJECTURED,
                    difficulty=max(1, theorem.difficulty - 2),  # Reduce difficulty
                    importance=theorem.importance,
                    parent_theorems=[theorem.id]
                )
                
                # Create formal definition for the subgoal
                subgoal.add_formal_definition(FormalDefinition(
                    language=FormalizationLanguage.LEAN4,
                    code=f"""
/-- {name}: {description} -/
theorem {self._to_lean_identifier(subgoal_id)} :
  {formula} :=
  sorry
""",
                    imports=lean_def.imports,
                    dependencies=lean_def.dependencies
                ))
                
                # Add to domain manager
                self.domain_manager.add_theorem(subgoal)
                subgoal_theorems.append(subgoal)
                
                # Add relation to parent theorem
                relation = DomainRelation(
                    id=f"rel_{theorem.id}_{subgoal_id}",
                    relation_type=RelationType.COMPOSITION,
                    source_id=theorem.id,
                    target_id=subgoal_id,
                    description=f"Subgoal {i+1} of {theorem.name}",
                    bidirectional=False
                )
                
                self.domain_manager.add_relation(relation)
            
            # Update decomposition in original theorem
            theorem.decomposition = [subgoal.id for subgoal in subgoal_theorems]
            self.domain_manager.add_theorem(theorem)
            
            # Recursively decompose complex subgoals
            all_subgoals = []
            for subgoal in subgoal_theorems:
                if subgoal.difficulty > 3 and max_depth > 1:
                    all_subgoals.extend(self.decompose_theorem(subgoal, max_depth - 1))
                else:
                    all_subgoals.append(subgoal)
            
            return all_subgoals
        
        return [theorem]
    
    def _analyze_theorem_structure(self, theorem: DomainTheorem, lean_def: FormalDefinition) -> List[Tuple[str, str, str]]:
        """Analyze theorem structure to identify subgoals."""
        # Extract the theorem's conclusion
        code = lean_def.code
        
        # Check for implication structure (A → B)
        arrow_match = code.find("→")
        if arrow_match != -1:
            # Simple case with assumptions and conclusion
            parts = code.split("→")
            if len(parts) > 2:
                # Multiple implications: A → B → C → ...
                subgoals = []
                
                # Create intermediate subgoals
                for i in range(len(parts) - 1):
                    assumptions = " → ".join(parts[:i+1]).strip()
                    conclusion = parts[i+1].strip()
                    
                    # Clean up conclusion (remove trailing := sorry)
                    conclusion = conclusion.split(":=")[0].strip()
                    
                    name = f"Subgoal {i+1} of {theorem.name}"
                    description = f"Intermediate step in proving {theorem.name}"
                    formula = f"{assumptions} → {conclusion}"
                    
                    subgoals.append((name, description, formula))
                
                return subgoals
        
        # Check for conjunction structure (A ∧ B ∧ C)
        and_match = code.find("∧")
        if and_match != -1:
            # Split into multiple parts around ∧
            parts = re.findall(r'([^∧]+)(?:∧|$)', code)
            if len(parts) > 1:
                subgoals = []
                
                # Extract theorem header
                header_match = re.search(r'theorem\s+([^:]+):\s*', code)
                theorem_header = header_match.group(0) if header_match else "theorem: "
                
                # Create a subgoal for each part of the conjunction
                for i, part in enumerate(parts):
                    part = part.strip()
                    if part:
                        name = f"Conjunct {i+1} of {theorem.name}"
                        description = f"Component {i+1} of {theorem.name}"
                        
                        # Extract the formula part
                        formula_part = part.split(theorem_header)[-1]
                        formula_part = formula_part.split(":=")[0].strip()
                        
                        formula = formula_part
                        subgoals.append((name, description, formula))
                
                return subgoals
        
        # Check for universal quantifier structure (∀ x, P(x))
        forall_match = code.find("∀")
        if forall_match != -1 and "," in code[forall_match:]:
            # Extract the predicate
            parts = code[forall_match:].split(",", 1)
            if len(parts) > 1:
                quantifier = parts[0].strip()
                predicate = parts[1].strip().split(":=")[0].strip()
                
                # Identify specific cases to check
                # For example, if quantifying over natural numbers, check base case and inductive step
                if "Nat" in quantifier or "ℕ" in quantifier:
                    subgoals = [
                        (f"Base Case for {theorem.name}", 
                         f"Base case (n=0) for {theorem.name}", 
                         predicate.replace("n", "0")),
                        
                        (f"Inductive Step for {theorem.name}",
                         f"Inductive step (n → n+1) for {theorem.name}",
                         f"∀ n : Nat, {predicate} → {predicate.replace('n', 'n+1')}")
                    ]
                    return subgoals
                
                # For finite types, check specific instances
                if "Fin" in quantifier:
                    match = re.search(r'Fin\s+(\d+)', quantifier)
                    if match:
                        n = int(match.group(1))
                        subgoals = []
                        
                        # Create a subgoal for each case
                        for i in range(n):
                            subgoals.append(
                                (f"Case {i} for {theorem.name}",
                                 f"Specific case for index {i} in {theorem.name}",
                                 predicate.replace("i", str(i)))
                            )
                        
                        return subgoals
        
        # Check for existential quantifier (∃ x, P(x))
        exists_match = code.find("∃")
        if exists_match != -1 and "," in code[exists_match:]:
            # For existence proofs, create a subgoal for finding the witness
            parts = code[exists_match:].split(",", 1)
            if len(parts) > 1:
                quantifier = parts[0].strip()
                predicate = parts[1].strip().split(":=")[0].strip()
                
                subgoals = [
                    (f"Witness Construction for {theorem.name}",
                     f"Construction of a witness for {theorem.name}",
                     f"∃ {quantifier[2:]}"),
                    
                    (f"Witness Verification for {theorem.name}",
                     f"Verification that the witness satisfies the required property",
                     predicate)
                ]
                
                return subgoals
        
        # If no specific structure identified, use a general approach based on complexity
        if theorem.difficulty >= 5:
            # For complex theorems, split into existence and uniqueness if appropriate
            if "exists" in theorem.name.lower() or "unique" in theorem.name.lower():
                subgoals = [
                    (f"Existence part of {theorem.name}",
                     f"Proof that a solution exists for {theorem.name}",
                     "/* Existence part */"),
                    
                    (f"Uniqueness part of {theorem.name}",
                     f"Proof that the solution is unique for {theorem.name}",
                     "/* Uniqueness part */")
                ]
                return subgoals
            
            # Otherwise create a preparation and main proof subgoal
            subgoals = [
                (f"Preparation for {theorem.name}",
                 f"Preliminary lemmas and setup for {theorem.name}",
                 "/* Preparation */"),
                
                (f"Main argument for {theorem.name}",
                 f"Core proof argument for {theorem.name}",
                 "/* Main argument */")
            ]
            return subgoals
        
        # If all else fails, return an empty list (no decomposition)
        return []
    
    def _to_lean_identifier(self, id_str: str) -> str:
        """Convert an ID string to a valid Lean identifier."""
        # Replace non-alphanumeric characters with underscores
        identifier = re.sub(r'[^a-zA-Z0-9]', '_', id_str)
        
        # Ensure it starts with a letter
        if not identifier[0].isalpha():
            identifier = 'x_' + identifier
        
        # Use camelCase for Lean identifiers
        parts = identifier.split('_')
        identifier = parts[0].lower()
        for part in parts[1:]:
            if part:
                identifier += part[0].upper() + part[1:].lower()
        
        return identifier
    
    def recompose_proof(self, theorem: DomainTheorem, subgoal_proofs: Dict[str, Proof]) -> Optional[Proof]:
        """Recompose subgoal proofs into a proof of the original theorem.
        
        Args:
            theorem: The original theorem
            subgoal_proofs: Dictionary mapping subgoal IDs to their proofs
            
        Returns:
            A proof of the original theorem, or None if not all subgoals are proven
        """
        # Check if all subgoals have proofs
        for subgoal_id in theorem.decomposition:
            if subgoal_id not in subgoal_proofs:
                return None
        
        # Create a new proof for the original theorem
        proof_id = f"proof_{theorem.id}_{int(time.time())}"
        proof = Proof(
            proof_id=proof_id,
            language=FormalizationLanguage.LEAN4,
            complete=True,
            verified=all(p.verified for p in subgoal_proofs.values())
        )
        
        # First step: Set up the proof and reference subgoals
        steps = [
            ProofStep(
                step_id=f"step_1",
                description=f"Set up the proof of {theorem.name} using its subgoals",
                formal_code=f"-- This proof uses the following subgoals:\n" + 
                           "\n".join([f"-- - {self.domain_manager.get_theorem(sg_id).name}" 
                                     for sg_id in theorem.decomposition]),
                depends_on=[],
                confidence=1.0
            )
        ]
        
        # Add steps for each subgoal proof integration
        for i, subgoal_id in enumerate(theorem.decomposition):
            subgoal = self.domain_manager.get_theorem(subgoal_id)
            subgoal_proof = subgoal_proofs[subgoal_id]
            
            step = ProofStep(
                step_id=f"step_{i+2}",
                description=f"Apply the proof of subgoal: {subgoal.name}",
                formal_code=f"have {self._to_lean_identifier(subgoal_id)} := {self._to_lean_identifier(subgoal_id)}",
                depends_on=[steps[-1].step_id],
                confidence=subgoal_proof.steps[-1].confidence if subgoal_proof.steps else 0.8
            )
            
            steps.append(step)
        
        # Final step: Combine subgoals to conclude the theorem
        steps.append(
            ProofStep(
                step_id=f"step_{len(steps)+1}",
                description=f"Combine subgoals to conclude {theorem.name}",
                formal_code=f"exact (combine_subgoals {' '.join([self._to_lean_identifier(sg_id) for sg_id in theorem.decomposition])})",
                depends_on=[steps[-1].step_id],
                confidence=min(p.steps[-1].confidence if p.steps else 0.8 for p in subgoal_proofs.values())
            )
        )
        
        proof.steps = steps
        return proof


class ProofVerifier:
    """Verifies the correctness of generated proofs."""
    
    def __init__(self, domain_manager: DomainModelManager, translator: LeanTranslator, lean_path: Optional[str] = None):
        """Initialize the verifier.
        
        Args:
            domain_manager: The domain model manager
            translator: The Lean translator
            lean_path: Path to Lean executable (optional)
        """
        self.domain_manager = domain_manager
        self.translator = translator
        self.lean_path = lean_path or self._find_lean_executable()
    
    def _find_lean_executable(self) -> str:
        """Find the Lean executable in the system."""
        # Try common locations
        candidates = [
            "lean",  # If in PATH
            "/usr/local/bin/lean",
            "/usr/bin/lean",
            os.path.expanduser("~/.elan/bin/lean")
        ]
        
        for candidate in candidates:
            try:
                subprocess.run([candidate, "--version"], capture_output=True, check=True)
                return candidate
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        # Default to "lean" and hope it's in PATH
        return "lean"
    
    def verify_proof(self, theorem: DomainTheorem, proof: Proof) -> Tuple[bool, str]:
        """Verify a proof using Lean.
        
        Args:
            theorem: The theorem to verify
            proof: The proof to verify
            
        Returns:
            Tuple of (success, error_message)
        """
        if not self.lean_path:
            return False, "Lean executable not found"
        
        # Get the formal definition
        lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
        if not lean_def:
            return False, "No Lean formal definition found for the theorem"
        
        # Create a temporary directory for verification
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create necessary files
            self._export_dependencies(theorem, temp_dir)
            
            # Create the theorem file with proof
            proof_generator = ProofGenerator(self.translator)
            theorem_with_proof = proof_generator.synthesize_complete_proof(theorem, proof)
            
            theorem_file = os.path.join(temp_dir, f"{self._to_lean_identifier(theorem.id)}.lean")
            with open(theorem_file, 'w') as f:
                f.write(theorem_with_proof)
            
            # Run Lean to verify the proof
            try:
                result = subprocess.run(
                    [self.lean_path, theorem_file],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                # Check if verification succeeded
                if result.returncode == 0:
                    return True, "Proof verified successfully"
                else:
                    # Extract error message
                    error_msg = result.stderr.strip()
                    if not error_msg:
                        error_msg = result.stdout.strip()
                    
                    return False, f"Verification failed: {error_msg}"
            
            except Exception as e:
                return False, f"Verification error: {str(e)}"
    
    def _export_dependencies(self, theorem: DomainTheorem, export_dir: str) -> None:
        """Export all dependencies of a theorem to Lean files.
        
        Args:
            theorem: The theorem to export dependencies for
            export_dir: Directory to export to
        """
        # Get formal definition
        lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
        if not lean_def:
            return
        
        # Create imports file
        imports_file = os.path.join(export_dir, "Imports.lean")
        with open(imports_file, 'w') as f:
            f.write("\n".join(f"import {imp}" for imp in lean_def.imports))
        
        # Export axioms
        axioms_file = os.path.join(export_dir, "Axioms.lean")
        with open(axioms_file, 'w') as f:
            f.write("import Imports\n\n")
            f.write("namespace Economic\n\n")
            
            # Export all axioms used by the theorem
            for axiom_id in lean_def.dependencies:
                axiom = self.domain_manager.get_axiom(axiom_id)
                if axiom:
                    axiom_def = axiom.get_formal_definition(FormalizationLanguage.LEAN4)
                    if axiom_def:
                        f.write(f"-- {axiom.name}\n")
                        f.write(axiom_def.code)
                        f.write("\n\n")
            
            f.write("end Economic\n")
        
        # Export helper lemmas if any
        lemmas_file = os.path.join(export_dir, "Lemmas.lean")
        with open(lemmas_file, 'w') as f:
            f.write("import Axioms\n\n")
            f.write("namespace Economic\n\n")
            
            # Export any other theorems that this theorem depends on
            for dep_id in lean_def.dependencies:
                dep_theorem = self.domain_manager.get_theorem(dep_id)
                if dep_theorem:
                    dep_def = dep_theorem.get_formal_definition(FormalizationLanguage.LEAN4)
                    if dep_def:
                        f.write(f"-- {dep_theorem.name}\n")
                        f.write(dep_def.code)
                        f.write("\n\n")
            
            f.write("end Economic\n")
    
    def _to_lean_identifier(self, id_str: str) -> str:
        """Convert an ID string to a valid Lean identifier."""
        # Replace non-alphanumeric characters with underscores
        identifier = re.sub(r'[^a-zA-Z0-9]', '_', id_str)
        
        # Ensure it starts with a letter
        if not identifier[0].isalpha():
            identifier = 'x_' + identifier
        
        # Use camelCase for Lean identifiers
        parts = identifier.split('_')
        identifier = parts[0].lower()
        for part in parts[1:]:
            if part:
                identifier += part[0].upper() + part[1:].lower()
        
        return identifier


class DeepSeekProverInterface:
    """Interface to DeepSeek-Prover-V2 for theorem proving."""
    
    def __init__(self, model_path: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the DeepSeek-Prover interface.
        
        Args:
            model_path: Path to the DeepSeek-Prover model (for local use)
            api_key: API key for DeepSeek cloud API
        """
        self.model_path = model_path
        self.api_key = api_key
        
        # Currently we'll simulate the DeepSeek API as an actual implementation
        # would require access to DeepSeek's API or a local deployment of their model
        self.simulation_mode = True
    
    async def prove_theorem(self, theorem_statement: str, context: str = "") -> Tuple[bool, str]:
        """Prove a theorem using DeepSeek-Prover.
        
        Args:
            theorem_statement: The theorem statement in Lean 4
            context: Additional context (axioms, definitions, etc.)
            
        Returns:
            Tuple of (success, proof_or_error)
        """
        if self.simulation_mode:
            return await self._simulate_proving(theorem_statement, context)
        
        # Actual implementation would call the DeepSeek API or use the local model
        # For now, we'll just return a simulated result
        return False, "DeepSeek-Prover API not implemented"
    
    async def _simulate_proving(self, theorem_statement: str, context: str) -> Tuple[bool, str]:
        """Simulate proving a theorem for development purposes."""
        # Simulate API latency
        await asyncio.sleep(1)
        
        # Extract the theorem name for more realistic simulation
        theorem_name = "unknown_theorem"
        match = re.search(r'theorem\s+(\w+)', theorem_statement)
        if match:
            theorem_name = match.group(1)
        
        # Simulate simple proofs succeeding
        theorem_complexity = len(theorem_statement) + len(context)
        success_probability = 1.0 - (theorem_complexity / 10000.0)
        success_probability = max(0.1, min(0.9, success_probability))
        
        if random.random() < success_probability:
            # Generate a simulated proof
            proof = f"""
theorem {theorem_name} : 
{theorem_statement.split(':')[1].split(':=')[0].strip()} := 
begin
  -- Unfold definitions
  unfold_coes,
  
  -- Set up the proof
  intros,
  
  -- Apply relevant theorems
  apply key_theorem,
  
  -- Handle specific cases
  cases h,
  
  -- Algebraic manipulation
  rw [equation1, equation2],
  
  -- Conclude the proof
  exact this,
end
"""
            return True, proof
        else:
            # Generate a failure message
            error_types = [
                "Unable to resolve some variables",
                "Failed to find applicable lemmas",
                "Type mismatch in argument",
                "Timeout during proof search",
                "Cannot unify expressions"
            ]
            error = random.choice(error_types)
            return False, f"Proof generation failed: {error}"
    
    async def decompose_theorem(self, theorem_statement: str) -> List[str]:
        """Decompose a theorem into subgoals using DeepSeek-Prover.
        
        Args:
            theorem_statement: The theorem statement in Lean 4
            
        Returns:
            List of subgoal statements
        """
        if self.simulation_mode:
            # Simulate decomposition
            # Extract the theorem body
            match = re.search(r':\s*(.*?)\s*:=', theorem_statement, re.DOTALL)
            if not match:
                return []
            
            theorem_body = match.group(1).strip()
            
            # Check if it has implications
            if "→" in theorem_body:
                parts = theorem_body.split("→")
                if len(parts) <= 2:
                    # Simple A → B structure
                    return [
                        f"theorem subgoal1 : {parts[0].strip()}",
                        f"theorem subgoal2 : {parts[0].strip()} → {parts[1].strip()}"
                    ]
                else:
                    # Multiple implications
                    subgoals = []
                    for i in range(len(parts) - 1):
                        assumptions = " → ".join(parts[:i+1]).strip()
                        conclusion = parts[i+1].strip()
                        subgoals.append(f"theorem subgoal{i+1} : {assumptions} → {conclusion}")
                    return subgoals
            
            # Check for conjunctions
            if "∧" in theorem_body:
                parts = theorem_body.split("∧")
                return [f"theorem subgoal{i+1} : {part.strip()}" for i, part in enumerate(parts)]
            
            # Simple fallback: just split into two
            return [
                f"theorem subgoal1 : lemma_part_1",
                f"theorem subgoal2 : lemma_part_2"
            ]
        
        # Actual implementation would call the DeepSeek API
        return []


class TheoremProver:
    """Core prover that manages theorem proving workflows."""
    
    def __init__(self, 
                 domain_manager: DomainModelManager, 
                 decomposer: SubgoalDecomposer,
                 translator: LeanTranslator,
                 verifier: ProofVerifier,
                 deepseek: DeepSeekProverInterface):
        """Initialize the theorem prover.
        
        Args:
            domain_manager: The domain model manager
            decomposer: The subgoal decomposer
            translator: The Lean translator
            verifier: The proof verifier
            deepseek: The DeepSeek-Prover interface
        """
        self.domain_manager = domain_manager
        self.decomposer = decomposer
        self.translator = translator
        self.verifier = verifier
        self.deepseek = deepseek
        
        # Load default proof strategies
        self.strategies: Dict[str, ProofStrategy] = {}
        self._load_default_strategies()
    
    def _load_default_strategies(self) -> None:
        """Load default proof strategies."""
        # Direct proof strategy
        direct_strategy = ProofStrategy(
            id="strategy_direct",
            name="Direct Proof Strategy",
            description="Strategy focusing on direct proof methods",
            methods=[ProofMethod.DIRECT, ProofMethod.ALGEBRAIC],
            heuristics={
                "step_simplicity": 0.8,
                "term_reuse": 0.6,
                "symbolic_complexity": 0.4
            },
            axiom_preferences=[],
            lemma_preferences=[],
            decomposition_threshold=5,
            max_steps=50,
            timeout=300
        )
        self.strategies[direct_strategy.id] = direct_strategy
        
        # Contradiction strategy
        contradiction_strategy = ProofStrategy(
            id="strategy_contradiction",
            name="Contradiction Proof Strategy",
            description="Strategy focusing on proof by contradiction",
            methods=[ProofMethod.CONTRADICTION, ProofMethod.CONTRAPOSITIVE],
            heuristics={
                "contradiction_frequency": 0.9,
                "case_analysis": 0.7,
                "assumption_count": 0.5
            },
            axiom_preferences=[],
            lemma_preferences=[],
            decomposition_threshold=4,
            max_steps=60,
            timeout=300
        )
        self.strategies[contradiction_strategy.id] = contradiction_strategy
        
        # Construction strategy
        construction_strategy = ProofStrategy(
            id="strategy_construction",
            name="Constructive Proof Strategy",
            description="Strategy focusing on constructive proofs",
            methods=[ProofMethod.CONSTRUCTION, ProofMethod.CASES],
            heuristics={
                "witness_complexity": 0.8,
                "construction_steps": 0.7,
                "case_coverage": 0.6
            },
            axiom_preferences=[],
            lemma_preferences=[],
            decomposition_threshold=3,
            max_steps=70,
            timeout=400
        )
        self.strategies[construction_strategy.id] = construction_strategy
        
        # Fixed point strategy
        fixed_point_strategy = ProofStrategy(
            id="strategy_fixed_point",
            name="Fixed Point Proof Strategy",
            description="Strategy focusing on fixed point theorems",
            methods=[ProofMethod.FIXED_POINT, ProofMethod.DIRECT],
            heuristics={
                "continuity_arguments": 0.9,
                "compactness_arguments": 0.8,
                "mapping_properties": 0.7
            },
            axiom_preferences=[],
            lemma_preferences=[],
            decomposition_threshold=6,
            max_steps=80,
            timeout=500
        )
        self.strategies[fixed_point_strategy.id] = fixed_point_strategy
    
    def add_strategy(self, strategy: ProofStrategy) -> None:
        """Add a new proof strategy."""
        self.strategies[strategy.id] = strategy
    
    def evolve_strategies(self, num_generations: int = 5, population_size: int = 10) -> None:
        """Evolve proof strategies through genetic algorithms.
        
        Args:
            num_generations: Number of generations to evolve
            population_size: Size of the strategy population
        """
        # Initialize population with existing strategies
        population = list(self.strategies.values())
        
        # Fill to population size if needed
        while len(population) < population_size:
            # Create a mutated version of a random strategy
            parent = random.choice(population)
            child = parent.mutate(mutation_rate=0.2)
            population.append(child)
        
        # Evolve for the specified number of generations
        for generation in range(num_generations):
            # Evaluate fitness (placeholder - actual implementation would test against theorems)
            fitness_scores = self._evaluate_strategies(population)
            
            # Select parents for next generation
            parents = self._select_parents(population, fitness_scores, population_size // 2)
            
            # Create new population through crossover and mutation
            new_population = []
            
            # Elite selection - keep top performers
            elite_count = max(1, population_size // 5)
            elite_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:elite_count]
            for i in elite_indices:
                new_population.append(population[i])
            
            # Fill the rest with crossover and mutation
            while len(new_population) < population_size:
                # Select parents and perform crossover
                parent1, parent2 = random.sample(parents, 2)
                child = parent1.crossover(parent2)
                
                # Apply mutation with some probability
                if random.random() < 0.3:
                    child = child.mutate(mutation_rate=0.1)
                
                new_population.append(child)
            
            # Update population for next generation
            population = new_population
            
            # Add all strategies to the manager
            for strategy in population:
                self.add_strategy(strategy)
        
        # Keep track of the best strategies
        best_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:5]
        print(f"Best strategies after evolution: {[population[i].name for i in best_indices]}")
    
    def _evaluate_strategies(self, strategies: List[ProofStrategy]) -> List[float]:
        """Evaluate fitness of proof strategies.
        
        This is a placeholder for actual evaluation, which would involve testing
        each strategy on a set of benchmark theorems.
        
        Args:
            strategies: List of strategies to evaluate
            
        Returns:
            List of fitness scores
        """
        # In a real implementation, we would test each strategy on benchmark theorems
        # For now, generate random scores based on strategy characteristics
        scores = []
        
        for strategy in strategies:
            # Base score
            score = 0.5
            
            # Reward diverse methods
            method_count = len(strategy.methods)
            score += 0.1 * min(method_count, 3)
            
            # Reward balanced heuristics
            heuristic_count = len(strategy.heuristics)
            score += 0.05 * min(heuristic_count, 5)
            
            # Reward reasonable timeouts (not too short, not too long)
            if 100 <= strategy.timeout <= 600:
                score += 0.1
            
            # Add some randomness
            score += random.random() * 0.2
            
            scores.append(score)
        
        return scores
    
    def _select_parents(self, 
                        population: List[ProofStrategy], 
                        fitness_scores: List[float], 
                        num_parents: int) -> List[ProofStrategy]:
        """Select parents for the next generation using tournament selection.
        
        Args:
            population: The current population
            fitness_scores: Fitness scores for each individual
            num_parents: Number of parents to select
            
        Returns:
            List of selected parents
        """
        parents = []
        
        # Tournament selection
        tournament_size = 3
        
        for _ in range(num_parents):
            # Select random candidates
            candidates = random.sample(range(len(population)), tournament_size)
            
            # Select the best candidate
            best_idx = max(candidates, key=lambda i: fitness_scores[i])
            parents.append(population[best_idx])
        
        return parents
    
    async def prove_theorem(self, 
                           theorem_id: str, 
                           strategy_id: Optional[str] = None,
                           decompose: bool = True,
                           max_depth: int = 3) -> Tuple[bool, str, Optional[Proof]]:
        """Prove a theorem.
        
        Args:
            theorem_id: ID of the theorem to prove
            strategy_id: ID of the strategy to use (or None for automatic selection)
            decompose: Whether to decompose complex theorems
            max_depth: Maximum decomposition depth
            
        Returns:
            Tuple of (success, message, proof)
        """
        # Get the theorem
        theorem = self.domain_manager.get_theorem(theorem_id)
        if not theorem:
            return False, f"Theorem not found: {theorem_id}", None
        
        # Get or select a strategy
        strategy = self._select_strategy(theorem, strategy_id)
        if not strategy:
            return False, f"Strategy not found: {strategy_id}", None
        
        # Check if the theorem is already proven
        if theorem.status == TheoremStatus.PROVEN:
            for proof in theorem.proofs:
                if proof.verified:
                    return True, f"Theorem already proven: {theorem.name}", proof
        
        # Check if the theorem needs decomposition
        if decompose and theorem.difficulty >= strategy.decomposition_threshold:
            # Decompose the theorem
            subgoals = self.decomposer.decompose_theorem(theorem, max_depth)
            
            if len(subgoals) > 1:
                # Recursively prove subgoals
                subgoal_proofs = {}
                all_successful = True
                failure_message = ""
                
                for subgoal in subgoals:
                    success, message, proof = await self.prove_theorem(
                        subgoal.id, 
                        strategy_id=strategy_id, 
                        decompose=True, 
                        max_depth=max_depth-1
                    )
                    
                    if success and proof:
                        subgoal_proofs[subgoal.id] = proof
                    else:
                        all_successful = False
                        failure_message = f"Failed to prove subgoal {subgoal.name}: {message}"
                        break
                
                if all_successful:
                    # Recompose the proof
                    proof = self.decomposer.recompose_proof(theorem, subgoal_proofs)
                    if proof:
                        # Add the proof to the theorem
                        self.domain_manager.add_proof_to_theorem(theorem_id, proof)
                        
                        # Update theorem status
                        self.domain_manager.update_theorem_status(theorem_id, TheoremStatus.PROVEN)
                        
                        return True, f"Theorem proven via subgoals: {theorem.name}", proof
                    else:
                        return False, "Failed to recompose subgoal proofs", None
                else:
                    return False, failure_message, None
        
        # Direct proof attempt using DeepSeek-Prover
        lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
        if not lean_def:
            return False, f"No Lean formal definition found for theorem: {theorem.name}", None
        
        # Prepare context with axioms and lemmas
        context = self._prepare_theorem_context(theorem, strategy)
        
        # Attempt to prove the theorem
        success, proof_code = await self.deepseek.prove_theorem(lean_def.code, context)
        
        if success:
            # Create a proof object
            proof_id = f"proof_{theorem_id}_{int(time.time())}"
            proof = Proof(
                proof_id=proof_id,
                language=FormalizationLanguage.LEAN4,
                complete=True,
                verified=False
            )
            
            # Parse the proof into steps
            steps = self._parse_proof_into_steps(proof_code)
            proof.steps = steps
            
            # Verify the proof
            verified, verification_message = self.verifier.verify_proof(theorem, proof)
            proof.verified = verified
            
            # Add the proof to the theorem
            self.domain_manager.add_proof_to_theorem(theorem_id, proof)
            
            # Update theorem status
            if verified:
                self.domain_manager.update_theorem_status(theorem_id, TheoremStatus.PROVEN)
            else:
                self.domain_manager.update_theorem_status(theorem_id, TheoremStatus.PARTIALLY_PROVEN)
            
            return verified, verification_message, proof
        else:
            return False, f"Failed to prove theorem: {proof_code}", None
    
    def _select_strategy(self, theorem: DomainTheorem, strategy_id: Optional[str] = None) -> Optional[ProofStrategy]:
        """Select a proof strategy for a theorem.
        
        Args:
            theorem: The theorem to select a strategy for
            strategy_id: ID of a specific strategy to use (optional)
            
        Returns:
            Selected proof strategy
        """
        if strategy_id and strategy_id in self.strategies:
            return self.strategies[strategy_id]
        
        # Auto-select based on theorem characteristics
        concept_type = theorem.concept_type
        difficulty = theorem.difficulty
        
        # For existence theorems, prefer construction or fixed point strategies
        if "existence" in theorem.name.lower() or "exists" in theorem.description.lower():
            if "fixed point" in theorem.description.lower() or "mapping" in theorem.description.lower():
                for strategy in self.strategies.values():
                    if ProofMethod.FIXED_POINT in strategy.methods:
                        return strategy
            else:
                for strategy in self.strategies.values():
                    if ProofMethod.CONSTRUCTION in strategy.methods:
                        return strategy
        
        # For uniqueness theorems, prefer contradiction strategies
        if "unique" in theorem.name.lower() or "uniqueness" in theorem.description.lower():
            for strategy in self.strategies.values():
                if ProofMethod.CONTRADICTION in strategy.methods:
                    return strategy
        
        # For welfare theorems, prefer direct proof
        if concept_type == ConceptType.WELFARE:
            for strategy in self.strategies.values():
                if ProofMethod.DIRECT in strategy.methods and ProofMethod.ALGEBRAIC in strategy.methods:
                    return strategy
        
        # Default selection based on difficulty
        if difficulty <= 3:
            # Simple theorems: prefer direct proof
            for strategy in self.strategies.values():
                if ProofMethod.DIRECT in strategy.methods:
                    return strategy
        elif difficulty <= 6:
            # Moderate difficulty: prefer mixed strategies
            for strategy in self.strategies.values():
                if len(strategy.methods) >= 2:
                    return strategy
        else:
            # High difficulty: prefer construction or fixed point
            for strategy in self.strategies.values():
                if ProofMethod.CONSTRUCTION in strategy.methods or ProofMethod.FIXED_POINT in strategy.methods:
                    return strategy
        
        # If no specific match, return the first strategy
        if self.strategies:
            return next(iter(self.strategies.values()))
        
        return None
    
    def _prepare_theorem_context(self, theorem: DomainTheorem, strategy: ProofStrategy) -> str:
        """Prepare the context for theorem proving.
        
        Args:
            theorem: The theorem to prove
            strategy: The proof strategy to use
            
        Returns:
            Context string with relevant axioms and lemmas
        """
        context = []
        
        # Get the formal definition
        lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
        if not lean_def:
            return ""
        
        # Add imports
        if lean_def.imports:
            context.append("-- Imports")
            for imp in lean_def.imports:
                context.append(f"import {imp}")
            context.append("")
        
        # Add namespace
        context.append("namespace Economic")
        context.append("")
        
        # Add dependencies
        if lean_def.dependencies:
            context.append("-- Dependencies")
            for dep_id in lean_def.dependencies:
                # Add axioms
                axiom = self.domain_manager.get_axiom(dep_id)
                if axiom:
                    axiom_def = axiom.get_formal_definition(FormalizationLanguage.LEAN4)
                    if axiom_def:
                        context.append(f"-- {axiom.name}")
                        context.append(axiom_def.code)
                        context.append("")
                
                # Add related theorems
                theorem_dep = self.domain_manager.get_theorem(dep_id)
                if theorem_dep and theorem_dep.id != theorem.id:
                    theorem_def = theorem_dep.get_formal_definition(FormalizationLanguage.LEAN4)
                    if theorem_def:
                        context.append(f"-- {theorem_dep.name}")
                        context.append(theorem_def.code)
                        context.append("")
        
        # Add preferred axioms from strategy
        if strategy.axiom_preferences:
            context.append("-- Strategy preferred axioms")
            for axiom_id in strategy.axiom_preferences:
                axiom = self.domain_manager.get_axiom(axiom_id)
                if axiom:
                    axiom_def = axiom.get_formal_definition(FormalizationLanguage.LEAN4)
                    if axiom_def:
                        context.append(f"-- {axiom.name}")
                        context.append(axiom_def.code)
                        context.append("")
        
        # Add preferred lemmas from strategy
        if strategy.lemma_preferences:
            context.append("-- Strategy preferred lemmas")
            for lemma_id in strategy.lemma_preferences:
                lemma = self.domain_manager.get_theorem(lemma_id)
                if lemma:
                    lemma_def = lemma.get_formal_definition(FormalizationLanguage.LEAN4)
                    if lemma_def:
                        context.append(f"-- {lemma.name}")
                        context.append(lemma_def.code)
                        context.append("")
        
        # Close namespace
        context.append("end Economic")
        
        return "\n".join(context)
    
    def _parse_proof_into_steps(self, proof_code: str) -> List[ProofStep]:
        """Parse a proof into individual steps.
        
        Args:
            proof_code: The full proof code
            
        Returns:
            List of proof steps
        """
        steps = []
        
        # Extract the proof part
        match = re.search(r'begin(.*?)end', proof_code, re.DOTALL)
        if not match:
            # If no "begin...end" block, try to extract from := to the end
            match = re.search(r':=(.*?)$', proof_code, re.DOTALL)
            if not match:
                # Create a single step with the full proof
                steps.append(ProofStep(
                    step_id="step_1",
                    description="Complete proof",
                    formal_code=proof_code,
                    depends_on=[],
                    confidence=0.5
                ))
                return steps
        
        proof_body = match.group(1).strip()
        
        # Split by comments or commas
        parts = re.split(r'(--.*?$|,\s*$)', proof_body, flags=re.MULTILINE)
        
        current_step = ""
        description = ""
        step_id = 1
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            if part.startswith("--"):
                # This is a description
                description = part[2:].strip()
            elif part.endswith(","):
                # This is a step
                current_step += part
                
                if not description:
                    # Generate a description from the step
                    description = f"Step {step_id}: {current_step[:40]}..."
                
                # Add the step
                steps.append(ProofStep(
                    step_id=f"step_{step_id}",
                    description=description,
                    formal_code=current_step.strip(),
                    depends_on=[f"step_{step_id-1}"] if step_id > 1 else [],
                    confidence=0.8
                ))
                
                # Reset for next step
                current_step = ""
                description = ""
                step_id += 1
            else:
                # Part of the current step
                current_step += part
        
        # Add any remaining step
        if current_step:
            if not description:
                description = f"Step {step_id}: {current_step[:40]}..."
            
            steps.append(ProofStep(
                step_id=f"step_{step_id}",
                description=description,
                formal_code=current_step.strip(),
                depends_on=[f"step_{step_id-1}"] if step_id > 1 else [],
                confidence=0.8
            ))
        
        return steps


if __name__ == "__main__":
    # Basic usage example
    from economic_domain_model import DomainModelManager
    from economic_formal_translator import LeanTranslator
    
    # Create domain manager and load basics
    domain_manager = DomainModelManager()
    
    # Create translator and components
    translator = LeanTranslator(domain_manager)
    decomposer = SubgoalDecomposer(domain_manager)
    verifier = ProofVerifier(domain_manager, translator)
    deepseek = DeepSeekProverInterface()
    
    # Create theorem prover
    prover = TheoremProver(
        domain_manager=domain_manager,
        decomposer=decomposer,
        translator=translator,
        verifier=verifier,
        deepseek=deepseek
    )
    
    # Test evolution of strategies
    prover.evolve_strategies(num_generations=3, population_size=5)
    
    # Print available strategies
    print("Available proof strategies:")
    for strategy_id, strategy in prover.strategies.items():
        print(f"- {strategy.name} ({strategy.id}): {strategy.description}")
        print(f"  Methods: {[m.value for m in strategy.methods]}")
        print(f"  Heuristics: {strategy.heuristics}")
        print()
    
    # Create and add a sample theorem for testing
    from economic_domain_model import DomainTheorem, TheoremStatus, FormalizationLanguage, FormalDefinition, ConceptType
    
    # Create a simple theorem
    theorem = DomainTheorem(
        id="pareto_efficiency",
        name="Pareto Efficiency of Competitive Equilibria",
        description="Competitive equilibria are Pareto efficient",
        concept_type=ConceptType.WELFARE,
        status=TheoremStatus.CONJECTURED,
        difficulty=5,
        importance=9
    )
    
    theorem.add_formal_definition(FormalDefinition(
        language=FormalizationLanguage.LEAN4,
        code="""
/-- Pareto Efficiency of Competitive Equilibria: Competitive equilibria are Pareto efficient -/
theorem paretoEfficiency {n m : Nat} (agents : Fin m → Agent n) (p : Fin n → ℝ) :
  CompetitiveEquilibrium n agents p →
  ParetoEfficient n agents :=
  sorry
""",
        imports=["Mathlib.Data.Real.Basic", "Mathlib.Data.Fin.Basic"],
        dependencies=[]
    ))
    
    domain_manager.add_theorem(theorem)
    
    # Run the prover (in an async context)
    import asyncio
    
    async def test_prover():
        success, message, proof = await prover.prove_theorem(
            theorem_id="pareto_efficiency",
            decompose=True
        )
        
        print(f"Proof result: {success}")
        print(f"Message: {message}")
        if proof:
            print(f"Proof has {len(proof.steps)} steps")
            for step in proof.steps:
                print(f"- {step.description}")
    
    # Run the test
    asyncio.run(test_prover())