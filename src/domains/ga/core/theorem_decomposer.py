"""
Theorem Decomposition System

This module provides functionality for breaking down complex economic theorems
into smaller, more manageable lemmas that can be proved independently.
"""

from typing import Dict, List, Tuple, Any, Optional, Set, Union
import json
import re
import networkx as nx
from dataclasses import dataclass, field
import uuid

from ..agents.specialized_agents import DecompositionAgent
from ..repository.theorem_repository import Theorem, TheoremMetadata, TheoremStatus
from ..core.base_agent import GeneticTraits


@dataclass
class TheoremComponent:
    """A component of a theorem identified for decomposition."""
    component_id: str
    description: str
    expression: str
    component_type: str  # "assumption", "conclusion", "definition", "constraint", etc.
    dependencies: List[str] = field(default_factory=list)  # IDs of components this component depends on


@dataclass
class DecompositionResult:
    """The result of decomposing a theorem."""
    original_theorem_id: str
    components: List[TheoremComponent]
    lemmas: List[Dict[str, Any]]  # Specifications for generated lemmas
    decomposition_graph: nx.DiGraph
    decomposer_id: str  # ID of the agent that performed the decomposition


class TheoremDecomposer:
    """
    System for decomposing complex economic theorems into smaller lemmas.
    
    The decomposition process identifies logical components of a theorem,
    determines their dependencies, and creates a set of smaller lemmas that
    can be proved independently.
    """
    
    def __init__(self, decomposer_agents: Optional[List[DecompositionAgent]] = None):
        """
        Initialize a theorem decomposer.
        
        Args:
            decomposer_agents: Optional list of decomposition agents to use
        """
        self.decomposer_agents = decomposer_agents or []
        
        # If no agents provided, create a default one
        if not self.decomposer_agents:
            self.decomposer_agents = [DecompositionAgent()]
    
    def decompose_theorem(self, theorem: Dict[str, Any]) -> DecompositionResult:
        """
        Decompose a complex theorem into smaller lemmas.
        
        Args:
            theorem: The theorem specification to decompose
            
        Returns:
            Decomposition result with components and lemmas
        """
        # Choose the agent with the highest decomposition depth trait
        agent = max(self.decomposer_agents, 
                    key=lambda a: a.genotype.get_trait_value(GeneticTraits.DECOMPOSITION_DEPTH))
        
        # Create a decomposition graph
        decomposition_graph = nx.DiGraph()
        
        # Extract components from the theorem
        components = self._extract_components(theorem)
        
        # Analyze dependencies between components
        components = self._analyze_dependencies(components)
        
        # Add components to the graph
        for component in components:
            decomposition_graph.add_node(component.component_id, 
                                         type=component.component_type,
                                         description=component.description,
                                         expression=component.expression)
            
            # Add dependencies as graph edges
            for dep_id in component.dependencies:
                decomposition_graph.add_edge(dep_id, component.component_id, type="depends_on")
        
        # Generate lemmas from components
        lemmas = self._generate_lemmas(theorem, components, decomposition_graph, agent)
        
        # Create result
        return DecompositionResult(
            original_theorem_id=theorem["theorem_id"],
            components=components,
            lemmas=lemmas,
            decomposition_graph=decomposition_graph,
            decomposer_id=agent.agent_id
        )
    
    def _extract_components(self, theorem: Dict[str, Any]) -> List[TheoremComponent]:
        """
        Extract logical components from a theorem.
        
        Args:
            theorem: The theorem specification
            
        Returns:
            List of theorem components
        """
        components = []
        
        # Extract assumptions first
        if "assumptions" in theorem and theorem["assumptions"]:
            for i, assumption in enumerate(theorem["assumptions"]):
                component_id = f"{theorem['theorem_id']}_A{i+1}"
                component = TheoremComponent(
                    component_id=component_id,
                    description=f"Assumption {i+1}",
                    expression=assumption,
                    component_type="assumption"
                )
                components.append(component)
        
        # In a real implementation, this would parse the formal_expression
        # and extract logical components using syntax trees or pattern recognition
        
        # Extract from formal expression using simple patterns (placeholder)
        if "formal_expression" in theorem:
            expression = theorem["formal_expression"]
            
            # Check for implications (if-then statements)
            if "->" in expression or "⟹" in expression or "implies" in expression.lower():
                # Split into antecedent and consequent
                parts = re.split(r'->|⟹|implies', expression, flags=re.IGNORECASE, maxsplit=1)
                
                if len(parts) == 2:
                    # Antecedent
                    antecedent_id = f"{theorem['theorem_id']}_ANT"
                    antecedent = TheoremComponent(
                        component_id=antecedent_id,
                        description="Antecedent (if part)",
                        expression=parts[0].strip(),
                        component_type="antecedent"
                    )
                    components.append(antecedent)
                    
                    # Consequent
                    consequent_id = f"{theorem['theorem_id']}_CON"
                    consequent = TheoremComponent(
                        component_id=consequent_id,
                        description="Consequent (then part)",
                        expression=parts[1].strip(),
                        component_type="consequent",
                        dependencies=[antecedent_id]  # Consequent depends on antecedent
                    )
                    components.append(consequent)
            
            # Check for conjunctions (and statements)
            elif "∧" in expression or " and " in expression.lower():
                # Split into conjuncts
                parts = re.split(r'∧|\band\b', expression, flags=re.IGNORECASE)
                
                for i, part in enumerate(parts):
                    conjunct_id = f"{theorem['theorem_id']}_CONJ{i+1}"
                    conjunct = TheoremComponent(
                        component_id=conjunct_id,
                        description=f"Conjunct {i+1}",
                        expression=part.strip(),
                        component_type="conjunct"
                    )
                    components.append(conjunct)
            
            # Check for equivalence (if and only if)
            elif "↔" in expression or "⟺" in expression or "if and only if" in expression.lower():
                # Split into both directions
                parts = re.split(r'↔|⟺|\bif and only if\b', expression, flags=re.IGNORECASE, maxsplit=1)
                
                if len(parts) == 2:
                    # First direction
                    forward_id = f"{theorem['theorem_id']}_FWD"
                    forward = TheoremComponent(
                        component_id=forward_id,
                        description="Forward direction",
                        expression=f"{parts[0].strip()} → {parts[1].strip()}",
                        component_type="forward_implication"
                    )
                    components.append(forward)
                    
                    # Reverse direction
                    reverse_id = f"{theorem['theorem_id']}_REV"
                    reverse = TheoremComponent(
                        component_id=reverse_id,
                        description="Reverse direction",
                        expression=f"{parts[1].strip()} → {parts[0].strip()}",
                        component_type="reverse_implication"
                    )
                    components.append(reverse)
        
        # If no components were extracted, treat the entire theorem as one component
        if not any(c.component_type in ["antecedent", "consequent", "conjunct", 
                                        "forward_implication", "reverse_implication"] 
                   for c in components):
            main_id = f"{theorem['theorem_id']}_MAIN"
            main = TheoremComponent(
                component_id=main_id,
                description="Main theorem statement",
                expression=theorem.get("formal_expression", theorem.get("natural_language", "")),
                component_type="statement"
            )
            components.append(main)
        
        return components
    
    def _analyze_dependencies(self, components: List[TheoremComponent]) -> List[TheoremComponent]:
        """
        Analyze dependencies between theorem components.
        
        Args:
            components: List of theorem components
            
        Returns:
            Updated components with dependencies
        """
        # In a real implementation, this would use logical analysis to determine
        # which components depend on others
        
        # For illustration, we'll use a simple heuristic:
        # Assumptions are independent
        # Other components may depend on assumptions
        # Consequents depend on antecedents
        
        assumption_ids = [c.component_id for c in components if c.component_type == "assumption"]
        
        for component in components:
            # Skip assumptions
            if component.component_type == "assumption":
                continue
            
            # Consequents depend on antecedents
            if component.component_type == "consequent":
                # Dependencies already set in extract_components
                continue
            
            # For other components, check if they refer to assumptions
            for assumption_id in assumption_ids:
                # In a real implementation, this would be a more sophisticated analysis
                # For now, we'll assume non-assumption components depend on all assumptions
                if assumption_id not in component.dependencies:
                    component.dependencies.append(assumption_id)
        
        return components
    
    def _generate_lemmas(self, theorem: Dict[str, Any], 
                         components: List[TheoremComponent],
                         decomposition_graph: nx.DiGraph,
                         agent: DecompositionAgent) -> List[Dict[str, Any]]:
        """
        Generate lemmas from theorem components.
        
        Args:
            theorem: The original theorem specification
            components: Extracted theorem components
            decomposition_graph: Dependency graph of components
            agent: The decomposition agent
            
        Returns:
            List of lemma specifications
        """
        lemmas = []
        
        # Determine decomposition strategy based on agent traits
        decomposition_depth = agent.genotype.get_trait_value(GeneticTraits.DECOMPOSITION_DEPTH)
        
        # Different strategies for different theorem types
        
        # Strategy 1: For implications, create lemmas for the antecedent and consequent
        if any(c.component_type == "antecedent" for c in components) and any(c.component_type == "consequent" for c in components):
            antecedent = next(c for c in components if c.component_type == "antecedent")
            consequent = next(c for c in components if c.component_type == "consequent")
            
            # Lemma 1: Prove the antecedent
            lemma1 = self._create_lemma(
                theorem=theorem,
                parent_id=theorem["theorem_id"],
                suffix="L1_antecedent",
                natural_language=f"Antecedent of {theorem.get('natural_language', theorem['theorem_id'])}",
                formal_expression=antecedent.expression,
                assumptions=theorem.get("assumptions", []),
                variables=theorem.get("variables", {})
            )
            lemmas.append(lemma1)
            
            # Lemma 2: Prove the consequent given the antecedent
            lemma2 = self._create_lemma(
                theorem=theorem,
                parent_id=theorem["theorem_id"],
                suffix="L2_consequent",
                natural_language=f"Consequent of {theorem.get('natural_language', theorem['theorem_id'])} given antecedent",
                formal_expression=consequent.expression,
                assumptions=theorem.get("assumptions", []) + [antecedent.expression],
                variables=theorem.get("variables", {})
            )
            lemmas.append(lemma2)
        
        # Strategy 2: For equivalences, create lemmas for each direction
        elif any(c.component_type == "forward_implication" for c in components) and any(c.component_type == "reverse_implication" for c in components):
            forward = next(c for c in components if c.component_type == "forward_implication")
            reverse = next(c for c in components if c.component_type == "reverse_implication")
            
            # Lemma 1: Prove forward direction
            lemma1 = self._create_lemma(
                theorem=theorem,
                parent_id=theorem["theorem_id"],
                suffix="L1_forward",
                natural_language=f"Forward direction of {theorem.get('natural_language', theorem['theorem_id'])}",
                formal_expression=forward.expression,
                assumptions=theorem.get("assumptions", []),
                variables=theorem.get("variables", {})
            )
            lemmas.append(lemma1)
            
            # Lemma 2: Prove reverse direction
            lemma2 = self._create_lemma(
                theorem=theorem,
                parent_id=theorem["theorem_id"],
                suffix="L2_reverse",
                natural_language=f"Reverse direction of {theorem.get('natural_language', theorem['theorem_id'])}",
                formal_expression=reverse.expression,
                assumptions=theorem.get("assumptions", []),
                variables=theorem.get("variables", {})
            )
            lemmas.append(lemma2)
        
        # Strategy 3: For conjunctions, create a lemma for each conjunct
        elif any(c.component_type == "conjunct" for c in components):
            conjuncts = [c for c in components if c.component_type == "conjunct"]
            
            for i, conjunct in enumerate(conjuncts):
                lemma = self._create_lemma(
                    theorem=theorem,
                    parent_id=theorem["theorem_id"],
                    suffix=f"L{i+1}_conjunct",
                    natural_language=f"Conjunct {i+1} of {theorem.get('natural_language', theorem['theorem_id'])}",
                    formal_expression=conjunct.expression,
                    assumptions=theorem.get("assumptions", []),
                    variables=theorem.get("variables", {})
                )
                lemmas.append(lemma)
        
        # Strategy 4: For complex statements, create lemmas based on component types
        else:
            # For complex theorems, create lemmas based on decomposition depth
            # More depth means more lemmas
            
            # Calculate max lemmas based on decomposition depth
            max_lemmas = 1 + int(5 * decomposition_depth)
            
            # Group components by type
            component_groups = {}
            for component in components:
                if component.component_type not in component_groups:
                    component_groups[component.component_type] = []
                component_groups[component.component_type].append(component)
            
            # Create lemmas for each component group
            lemma_count = 0
            for component_type, group in component_groups.items():
                for i, component in enumerate(group):
                    if lemma_count >= max_lemmas:
                        break
                    
                    # Skip assumption components (they're already assumptions)
                    if component.component_type == "assumption":
                        continue
                    
                    lemma = self._create_lemma(
                        theorem=theorem,
                        parent_id=theorem["theorem_id"],
                        suffix=f"L{lemma_count+1}_{component_type}",
                        natural_language=f"{component.description} in {theorem.get('natural_language', theorem['theorem_id'])}",
                        formal_expression=component.expression,
                        assumptions=theorem.get("assumptions", []),
                        variables=theorem.get("variables", {})
                    )
                    lemmas.append(lemma)
                    lemma_count += 1
        
        return lemmas
    
    def _create_lemma(self, theorem: Dict[str, Any], parent_id: str, suffix: str,
                     natural_language: str, formal_expression: str, 
                     assumptions: List[str], variables: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a lemma specification.
        
        Args:
            theorem: The parent theorem
            parent_id: ID of the parent theorem
            suffix: Suffix for the lemma ID
            natural_language: Natural language statement of the lemma
            formal_expression: Formal expression of the lemma
            assumptions: Assumptions for the lemma
            variables: Variables used in the lemma
            
        Returns:
            Lemma specification
        """
        # Create lemma ID
        lemma_id = f"{parent_id}_{suffix}"
        
        # Copy relevant metadata from parent theorem
        metadata = {}
        if "metadata" in theorem:
            metadata = {
                "domain": theorem["metadata"].get("domain", ""),
                "tags": theorem["metadata"].get("tags", []),
                "priority": theorem["metadata"].get("priority", 3),
                "difficulty": max(1, theorem["metadata"].get("difficulty", 3) - 1),  # Lemmas are generally easier
                "importance": theorem["metadata"].get("importance", 3),
                "verification_level": 0  # Lemmas start unverified
            }
        
        # Create lemma specification
        lemma = {
            "theorem_id": lemma_id,
            "natural_language": natural_language,
            "formal_expression": formal_expression,
            "status": "unproven",
            "metadata": metadata,
            "assumptions": assumptions,
            "variables": variables,
            "parent_theorem": parent_id
        }
        
        return lemma


# Function to convert a DecompositionResult to Theorem objects
def decomposition_to_theorems(decomposition: DecompositionResult, 
                             parent_theorem: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert a decomposition result to a list of theorem objects.
    
    Args:
        decomposition: The decomposition result
        parent_theorem: The parent theorem specification
        
    Returns:
        List of theorem specifications for the lemmas
    """
    # Copy parent theorem metadata as a template
    metadata_template = {}
    if "metadata" in parent_theorem:
        metadata_template = {
            "domain": parent_theorem["metadata"].get("domain", ""),
            "tags": parent_theorem["metadata"].get("tags", []) + ["lemma"],
            "priority": parent_theorem["metadata"].get("priority", 3),
            "difficulty": parent_theorem["metadata"].get("difficulty", 3),
            "importance": parent_theorem["metadata"].get("importance", 3),
            "verification_level": 0
        }
    
    # Convert lemmas to theorem objects
    theorems = []
    for lemma in decomposition.lemmas:
        # Update the metadata with lemma-specific info
        metadata = metadata_template.copy()
        if "metadata" in lemma:
            metadata.update(lemma["metadata"])
        
        # Create theorem specification
        theorem = {
            "theorem_id": lemma["theorem_id"],
            "natural_language": lemma["natural_language"],
            "formal_expression": lemma["formal_expression"],
            "status": TheoremStatus.UNPROVEN.value,
            "metadata": metadata,
            "assumptions": lemma.get("assumptions", []),
            "variables": lemma.get("variables", {}),
            "parent_theorem": decomposition.original_theorem_id,
            "decomposer_id": decomposition.decomposer_id
        }
        theorems.append(theorem)
    
    return theorems