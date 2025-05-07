#!/usr/bin/env python3
"""
Economic Formal Translator

This module provides utilities for translating between economic concepts and formal languages,
particularly focusing on integration with the Lean 4 theorem prover for formal verification.
It supports both direction translation:
1. Economic concepts to formal representations
2. Formal representations to economic interpretations

Key components:
- LeanTranslator: Translates between economic concepts and Lean 4 code
- FormalStructureGenerator: Generates formal structure templates for economic models
- ProofGenerator: Generates proof templates and proof steps
- EconomicInterpreter: Interprets formal results in economic terms
"""

import re
import json
import tempfile
import subprocess
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from pathlib import Path

from economic_domain_model import (
    ConceptType, DomainAxiom, DomainModelManager, DomainTheorem, 
    EconomicConcept, FormalDefinition, FormalizationLanguage,
    Proof, ProofStep, TheoremStatus
)


@dataclass
class TranslationTemplate:
    """Template for translating economic concepts to formal language."""
    name: str
    template: str
    parameters: List[str]
    description: str
    concept_type: Optional[ConceptType] = None
    examples: List[Dict[str, str]] = field(default_factory=list)
    
    def fill(self, **kwargs) -> str:
        """Fill the template with parameters."""
        result = self.template
        for param in self.parameters:
            if param not in kwargs:
                raise ValueError(f"Missing parameter: {param}")
            result = result.replace(f"{{{param}}}", str(kwargs[param]))
        return result


class LeanTranslator:
    """Translates between economic concepts and Lean 4 code."""
    
    def __init__(self, domain_manager: DomainModelManager):
        """Initialize the translator.
        
        Args:
            domain_manager: The domain model manager containing economic concepts
        """
        self.domain_manager = domain_manager
        self.templates: Dict[str, TranslationTemplate] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load translation templates."""
        # Template for utility functions
        self.templates["utility_function"] = TranslationTemplate(
            name="Utility Function",
            template="""
/-- {name} is a utility function representing {description} -/
def {identifier} {type_params} : Utility {goods_dim} :=
  fun bundle => {formula}
""",
            parameters=["name", "description", "identifier", "type_params", "goods_dim", "formula"],
            description="Template for defining utility functions",
            concept_type=ConceptType.PREFERENCE,
            examples=[{
                "name": "CobbDouglas",
                "description": "Cobb-Douglas utility with equal weights",
                "identifier": "cobbDouglas",
                "type_params": "(n : Nat)",
                "goods_dim": "n",
                "formula": "∏ i, bundle i"
            }]
        )
        
        # Template for preference relations
        self.templates["preference_relation"] = TranslationTemplate(
            name="Preference Relation",
            template="""
/-- {name} is a preference relation representing {description} -/
def {identifier} {type_params} : PreferenceRelation {goods_dim} :=
  fun bundle1 bundle2 => {formula}
""",
            parameters=["name", "description", "identifier", "type_params", "goods_dim", "formula"],
            description="Template for defining preference relations",
            concept_type=ConceptType.PREFERENCE,
            examples=[{
                "name": "LexicographicPreference",
                "description": "lexicographic preferences over goods",
                "identifier": "lexicographic",
                "type_params": "",
                "goods_dim": "2",
                "formula": "bundle1 0 > bundle2 0 ∨ (bundle1 0 = bundle2 0 ∧ bundle1 1 > bundle2 1)"
            }]
        )
        
        # Template for market equilibrium
        self.templates["market_equilibrium"] = TranslationTemplate(
            name="Market Equilibrium",
            template="""
/-- {name} represents {description} -/
def {identifier} {type_params} : Prop :=
  ∀ i, {supply_condition} = {demand_condition}
""",
            parameters=["name", "description", "identifier", "type_params", "supply_condition", "demand_condition"],
            description="Template for defining market equilibrium conditions",
            concept_type=ConceptType.EQUILIBRIUM,
            examples=[{
                "name": "CompetitiveEquilibrium",
                "description": "a competitive market equilibrium where supply equals demand",
                "identifier": "competitiveEq",
                "type_params": "(n : Nat) (supply demand : Fin n → ℝ → ℝ) (p : Fin n → ℝ)",
                "supply_condition": "supply i (p i)",
                "demand_condition": "demand i (p i)"
            }]
        )
        
        # Template for production functions
        self.templates["production_function"] = TranslationTemplate(
            name="Production Function",
            template="""
/-- {name} is a production function representing {description} -/
def {identifier} {type_params} : ProductionFunction {input_dim} {output_dim} :=
  fun inputs => {formula}
""",
            parameters=["name", "description", "identifier", "type_params", "input_dim", "output_dim", "formula"],
            description="Template for defining production functions",
            concept_type=ConceptType.PRODUCTION,
            examples=[{
                "name": "LinearProduction",
                "description": "linear production technology",
                "identifier": "linearProd",
                "type_params": "(a : ℝ) (b : ℝ)",
                "input_dim": "1",
                "output_dim": "1",
                "formula": "λ x => a * x + b"
            }]
        )
        
        # Template for axioms
        self.templates["axiom"] = TranslationTemplate(
            name="Economic Axiom",
            template="""
/-- {name}: {description} -/
axiom {identifier} {type_params} : {formula}
""",
            parameters=["name", "description", "identifier", "type_params", "formula"],
            description="Template for defining economic axioms",
            examples=[{
                "name": "Transitivity",
                "description": "preferences are transitive",
                "identifier": "transitivity",
                "type_params": "{α : Type} (pref : α → α → Prop)",
                "formula": "∀ a b c, pref a b → pref b c → pref a c"
            }]
        )
        
        # Template for theorems
        self.templates["theorem"] = TranslationTemplate(
            name="Economic Theorem",
            template="""
/-- {name}: {description} -/
theorem {identifier} {type_params} :
  {assumptions} →
  {conclusion} :=
{proof}
""",
            parameters=["name", "description", "identifier", "type_params", "assumptions", "conclusion", "proof"],
            description="Template for defining economic theorems",
            examples=[{
                "name": "FirstWelfareTheorem",
                "description": "competitive equilibria are Pareto efficient",
                "identifier": "firstWelfareTheorem",
                "type_params": "(n : Nat) (agents : Fin m → Agent n) (p : Fin n → ℝ)",
                "assumptions": "CompetitiveEquilibrium n agents p",
                "conclusion": "ParetoEfficient n agents",
                "proof": "sorry"
            }]
        )
    
    def get_template(self, template_name: str) -> Optional[TranslationTemplate]:
        """Get a template by name."""
        return self.templates.get(template_name)
    
    def get_templates_for_concept_type(self, concept_type: ConceptType) -> List[TranslationTemplate]:
        """Get all templates suitable for a concept type."""
        return [
            template for template in self.templates.values()
            if template.concept_type is None or template.concept_type == concept_type
        ]
    
    def concept_to_lean(self, concept: EconomicConcept) -> str:
        """Translate an economic concept to Lean 4 code."""
        # Check if concept already has a Lean definition
        lean_def = concept.get_formal_definition(FormalizationLanguage.LEAN4)
        if lean_def:
            return lean_def.code
        
        # Otherwise, try to generate a definition based on concept type
        templates = self.get_templates_for_concept_type(concept.concept_type)
        if not templates:
            raise ValueError(f"No templates available for concept type: {concept.concept_type}")
        
        # Use the first template as a default
        template = templates[0]
        
        # Generate parameter values based on concept
        params = {}
        if "name" in template.parameters:
            params["name"] = concept.name
        if "description" in template.parameters:
            params["description"] = concept.description
        if "identifier" in template.parameters:
            params["identifier"] = self._to_lean_identifier(concept.id)
        
        # For other parameters, use placeholders
        for param in template.parameters:
            if param not in params:
                params[param] = f"<{param}>"
        
        return template.fill(**params)
    
    def theorem_to_lean(self, theorem: DomainTheorem) -> str:
        """Translate an economic theorem to Lean 4 code."""
        # Check if theorem already has a Lean definition
        lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
        if lean_def:
            return lean_def.code
        
        # Get the theorem template
        template = self.get_template("theorem")
        if not template:
            raise ValueError("Theorem template not found")
        
        # Generate parameter values
        params = {
            "name": theorem.name,
            "description": theorem.description,
            "identifier": self._to_lean_identifier(theorem.id),
            "type_params": "<type_params>",
            "assumptions": "<assumptions>",
            "conclusion": "<conclusion>",
            "proof": "sorry"
        }
        
        return template.fill(**params)
    
    def axiom_to_lean(self, axiom: DomainAxiom) -> str:
        """Translate an economic axiom to Lean 4 code."""
        # Check if axiom already has a Lean definition
        lean_def = axiom.get_formal_definition(FormalizationLanguage.LEAN4)
        if lean_def:
            return lean_def.code
        
        # Get the axiom template
        template = self.get_template("axiom")
        if not template:
            raise ValueError("Axiom template not found")
        
        # Generate parameter values
        params = {
            "name": axiom.name,
            "description": axiom.description,
            "identifier": self._to_lean_identifier(axiom.id),
            "type_params": "<type_params>",
            "formula": "<formula>"
        }
        
        return template.fill(**params)
    
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
    
    def lean_to_concept(self, lean_code: str) -> Dict[str, Any]:
        """Extract concept information from Lean code.
        
        Args:
            lean_code: Lean 4 code to analyze
            
        Returns:
            Dictionary with extracted concept information
        """
        info = {
            "name": None,
            "description": None,
            "type": None,
            "identifier": None,
            "formula": None,
            "is_axiom": False,
            "is_theorem": False,
            "assumptions": [],
            "conclusion": None
        }
        
        # Extract doc comments
        doc_match = re.search(r'/--\s*(.*?)\s*-/', lean_code, re.DOTALL)
        if doc_match:
            doc = doc_match.group(1).strip()
            
            # Try to extract name and description
            name_match = re.search(r'^(.*?)(?::|is|represents)(.*?)$', doc, re.MULTILINE)
            if name_match:
                info["name"] = name_match.group(1).strip()
                info["description"] = name_match.group(2).strip()
            else:
                # Just use the first line as name
                lines = doc.split('\n')
                info["name"] = lines[0].strip()
                if len(lines) > 1:
                    info["description"] = '\n'.join(lines[1:]).strip()
        
        # Determine if it's an axiom
        if "axiom " in lean_code:
            info["is_axiom"] = True
            info["type"] = "axiom"
            
            # Extract axiom identifier
            axiom_match = re.search(r'axiom\s+([a-zA-Z0-9_]+)', lean_code)
            if axiom_match:
                info["identifier"] = axiom_match.group(1)
            
            # Extract formula
            formula_match = re.search(r'axiom\s+[^:]+:\s*(.*?)(?:$|:=)', lean_code, re.DOTALL)
            if formula_match:
                info["formula"] = formula_match.group(1).strip()
        
        # Determine if it's a theorem
        elif "theorem " in lean_code:
            info["is_theorem"] = True
            info["type"] = "theorem"
            
            # Extract theorem identifier
            theorem_match = re.search(r'theorem\s+([a-zA-Z0-9_]+)', lean_code)
            if theorem_match:
                info["identifier"] = theorem_match.group(1)
            
            # Extract assumptions and conclusion
            arrow_match = re.search(r'theorem\s+[^:]+:\s*(.*?)\s*→\s*(.*?)(?:$|:=)', lean_code, re.DOTALL)
            if arrow_match:
                assumptions = arrow_match.group(1).strip()
                info["assumptions"] = [a.strip() for a in assumptions.split('→')]
                info["conclusion"] = arrow_match.group(2).strip()
            else:
                # No assumptions, just conclusion
                conclusion_match = re.search(r'theorem\s+[^:]+:\s*(.*?)(?:$|:=)', lean_code, re.DOTALL)
                if conclusion_match:
                    info["conclusion"] = conclusion_match.group(1).strip()
        
        # Determine if it's a definition
        elif "def " in lean_code:
            info["type"] = "definition"
            
            # Extract definition identifier
            def_match = re.search(r'def\s+([a-zA-Z0-9_]+)', lean_code)
            if def_match:
                info["identifier"] = def_match.group(1)
            
            # Try to determine concept type based on return type
            if "Utility" in lean_code:
                info["concept_type"] = "preference"
            elif "Production" in lean_code:
                info["concept_type"] = "production"
            elif "Market" in lean_code or "Equilibrium" in lean_code:
                info["concept_type"] = "market"
            elif "Welfare" in lean_code:
                info["concept_type"] = "welfare"
            
            # Extract formula
            formula_match = re.search(r'def\s+[^:=]+:=\s*(.*?)(?:$|where)', lean_code, re.DOTALL)
            if formula_match:
                info["formula"] = formula_match.group(1).strip()
        
        return info


class FormalStructureGenerator:
    """Generates formal structure templates for economic models."""
    
    def __init__(self, translator: LeanTranslator):
        """Initialize the generator.
        
        Args:
            translator: The Lean translator to use
        """
        self.translator = translator
    
    def generate_utility_structure(self, name: str, description: str, n_goods: int = 2) -> str:
        """Generate a utility function structure.
        
        Args:
            name: Name of the utility function
            description: Description of the utility function
            n_goods: Number of goods
            
        Returns:
            Lean code for the utility structure
        """
        template = self.translator.get_template("utility_function")
        if not template:
            raise ValueError("Utility function template not found")
        
        identifier = self.translator._to_lean_identifier(name)
        return template.fill(
            name=name,
            description=description,
            identifier=identifier,
            type_params="",
            goods_dim=str(n_goods),
            formula=f"/* Define {name} utility formula here */"
        )
    
    def generate_market_structure(self, name: str, description: str, n_goods: int = 2, n_agents: int = 2) -> str:
        """Generate a market structure.
        
        Args:
            name: Name of the market structure
            description: Description of the market structure
            n_goods: Number of goods
            n_agents: Number of agents
            
        Returns:
            Lean code for the market structure
        """
        code = f"""
/-- {name}: {description} -/
structure {self.translator._to_lean_identifier(name)} where
  /-- Number of goods in the market -/
  n_goods : Nat := {n_goods}
  
  /-- Number of agents in the market -/
  n_agents : Nat := {n_agents}
  
  /-- Initial endowments for each agent -/
  endowments : Fin n_agents → Fin n_goods → ℝ
  
  /-- Utility function for each agent -/
  utilities : Fin n_agents → Utility n_goods
  
  /-- Prices of goods -/
  prices : Fin n_goods → ℝ
  
  /-- Price positivity -/
  prices_pos : ∀ i, prices i > 0
"""
        return code
    
    def generate_equilibrium_conditions(self, market_name: str) -> str:
        """Generate equilibrium conditions for a market.
        
        Args:
            market_name: Name of the market structure
            
        Returns:
            Lean code for equilibrium conditions
        """
        market_id = self.translator._to_lean_identifier(market_name)
        code = f"""
/-- Market clearing condition: supply equals demand for every good -/
def MarketClearing (market : {market_id}) : Prop :=
  ∀ g : Fin market.n_goods,
    (∑ a : Fin market.n_agents, market.optimal_demands a g) = 
    (∑ a : Fin market.n_agents, market.endowments a g)

/-- Budget feasibility: each agent's expenditure doesn't exceed their income -/
def BudgetFeasible (market : {market_id}) (a : Fin market.n_agents) : Prop :=
  (∑ g : Fin market.n_goods, market.prices g * market.optimal_demands a g) ≤
  (∑ g : Fin market.n_goods, market.prices g * market.endowments a g)

/-- Utility maximization: each agent maximizes utility subject to budget constraint -/
def UtilityMaximizing (market : {market_id}) (a : Fin market.n_agents) : Prop :=
  BudgetFeasible market a ∧
  ∀ (bundle : Fin market.n_goods → ℝ),
    (∀ g, bundle g ≥ 0) →
    (∑ g, market.prices g * bundle g) ≤ (∑ g, market.prices g * market.endowments a g) →
    market.utilities a bundle ≤ market.utilities a (market.optimal_demands a)

/-- Competitive equilibrium: markets clear and agents maximize utility -/
def CompetitiveEquilibrium (market : {market_id}) : Prop :=
  MarketClearing market ∧ ∀ a, UtilityMaximizing market a
"""
        return code
    
    def generate_theorem_template(self, name: str, description: str, assumptions: List[str], conclusion: str) -> str:
        """Generate a theorem template.
        
        Args:
            name: Name of the theorem
            description: Description of the theorem
            assumptions: List of assumption formulas
            conclusion: Conclusion formula
            
        Returns:
            Lean code for the theorem
        """
        template = self.translator.get_template("theorem")
        if not template:
            raise ValueError("Theorem template not found")
        
        identifier = self.translator._to_lean_identifier(name)
        
        # Join assumptions with →
        assumptions_str = " →\n  ".join(assumptions)
        
        return template.fill(
            name=name,
            description=description,
            identifier=identifier,
            type_params="",
            assumptions=assumptions_str,
            conclusion=conclusion,
            proof="sorry"
        )
    
    def generate_axiom_template(self, name: str, description: str, formula: str) -> str:
        """Generate an axiom template.
        
        Args:
            name: Name of the axiom
            description: Description of the axiom
            formula: Axiom formula
            
        Returns:
            Lean code for the axiom
        """
        template = self.translator.get_template("axiom")
        if not template:
            raise ValueError("Axiom template not found")
        
        identifier = self.translator._to_lean_identifier(name)
        
        return template.fill(
            name=name,
            description=description,
            identifier=identifier,
            type_params="",
            formula=formula
        )
    
    def generate_domain_file_structure(self, module_name: str, imports: List[str], concepts: List[EconomicConcept]) -> str:
        """Generate a complete Lean file for a domain.
        
        Args:
            module_name: Name of the Lean module
            imports: List of modules to import
            concepts: List of economic concepts to include
            
        Returns:
            Complete Lean file content
        """
        # Generate imports
        imports_str = "\n".join(f"import {imp}" for imp in imports)
        
        # Generate module documentation
        doc = f"""/-!
# {module_name}

This file contains definitions and theorems for economic concepts related to {module_name.lower()}.
-/"""
        
        # Generate namespace
        namespace = f"namespace Economic.{module_name}"
        end_namespace = f"end Economic.{module_name}"
        
        # Generate content for each concept
        content = []
        for concept in concepts:
            if isinstance(concept, DomainAxiom):
                content.append(self.translator.axiom_to_lean(concept))
            elif isinstance(concept, DomainTheorem):
                content.append(self.translator.theorem_to_lean(concept))
            else:
                content.append(self.translator.concept_to_lean(concept))
        
        content_str = "\n\n".join(content)
        
        # Combine all parts
        file_content = f"{imports_str}\n\n{doc}\n\n{namespace}\n\n{content_str}\n\n{end_namespace}"
        return file_content


class ProofGenerator:
    """Generates proof templates and proof steps."""
    
    def __init__(self, translator: LeanTranslator):
        """Initialize the generator.
        
        Args:
            translator: The Lean translator to use
        """
        self.translator = translator
    
    def generate_proof_sketch(self, theorem: DomainTheorem) -> List[str]:
        """Generate a proof sketch for a theorem.
        
        Args:
            theorem: The theorem to generate a proof sketch for
            
        Returns:
            List of proof step descriptions
        """
        # Get the formal definition in Lean
        lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
        if not lean_def:
            raise ValueError(f"Theorem {theorem.id} doesn't have a Lean formal definition")
        
        # Extract theorem parts
        theorem_info = self.translator.lean_to_concept(lean_def.code)
        
        # Generate proof sketch based on theorem type
        if "equilibrium" in theorem.name.lower() or "equilibrium" in theorem.description.lower():
            return self._generate_equilibrium_proof_sketch(theorem, theorem_info)
        elif "welfare" in theorem.name.lower() or "welfare" in theorem.description.lower():
            return self._generate_welfare_proof_sketch(theorem, theorem_info)
        elif "existence" in theorem.name.lower() or "existence" in theorem.description.lower():
            return self._generate_existence_proof_sketch(theorem, theorem_info)
        elif "uniqueness" in theorem.name.lower() or "uniqueness" in theorem.description.lower():
            return self._generate_uniqueness_proof_sketch(theorem, theorem_info)
        else:
            # Default general proof approach
            return [
                f"Set up the proof by introducing the assumptions: {', '.join(theorem_info.get('assumptions', []))}",
                "Break down the definitions involved in the theorem",
                "Apply relevant axioms and lemmas",
                "Construct the main argument",
                "Verify that the conclusion follows from the previous steps"
            ]
    
    def _generate_equilibrium_proof_sketch(self, theorem: DomainTheorem, theorem_info: Dict[str, Any]) -> List[str]:
        """Generate a proof sketch for equilibrium-related theorems."""
        return [
            "Introduce all variables and assumptions",
            "Expand the definition of equilibrium",
            "Consider the market clearing conditions for each good",
            "Analyze utility maximization for each agent",
            "Connect market clearing and utility maximization",
            "Apply relevant economic axioms",
            "Derive the target conclusion using the equilibrium properties"
        ]
    
    def _generate_welfare_proof_sketch(self, theorem: DomainTheorem, theorem_info: Dict[str, Any]) -> List[str]:
        """Generate a proof sketch for welfare-related theorems."""
        return [
            "Introduce all variables and assumptions",
            "Expand the definition of welfare concepts",
            "Set up a proof by contradiction (assume the conclusion is false)",
            "Derive implications for agent utilities",
            "Apply equilibrium conditions and budget constraints",
            "Show contradiction with initial welfare assumptions",
            "Conclude the theorem holds"
        ]
    
    def _generate_existence_proof_sketch(self, theorem: DomainTheorem, theorem_info: Dict[str, Any]) -> List[str]:
        """Generate a proof sketch for existence-related theorems."""
        return [
            "Introduce the relevant structures and assumptions",
            "Set up a suitable fixed point theorem (e.g., Brouwer or Kakutani)",
            "Define an appropriate mapping",
            "Verify the conditions of the fixed point theorem",
            "Show that fixed points correspond to solutions",
            "Conclude existence from the fixed point theorem",
            "Verify that the solution satisfies all required properties"
        ]
    
    def _generate_uniqueness_proof_sketch(self, theorem: DomainTheorem, theorem_info: Dict[str, Any]) -> List[str]:
        """Generate a proof sketch for uniqueness-related theorems."""
        return [
            "Introduce the relevant structures and assumptions",
            "Assume there are two distinct solutions",
            "Derive properties of both solutions using the assumptions",
            "Show that these properties lead to a contradiction",
            "Conclude uniqueness from the contradiction"
        ]
    
    def generate_proof_step(self, theorem: DomainTheorem, step_description: str, previous_steps: List[ProofStep] = None) -> ProofStep:
        """Generate a proof step based on its description.
        
        Args:
            theorem: The theorem being proved
            step_description: Description of the proof step
            previous_steps: Previous proof steps
            
        Returns:
            A new proof step
        """
        # Generate a unique step ID
        step_id = f"step_{len(previous_steps) + 1 if previous_steps else 1}"
        
        # Generate dependencies on previous steps
        depends_on = []
        if previous_steps:
            # By default, depend on the immediately previous step
            depends_on = [previous_steps[-1].step_id]
        
        # Generate formal code based on step description
        lean_code = self._step_description_to_lean(step_description, theorem, previous_steps)
        
        return ProofStep(
            step_id=step_id,
            description=step_description,
            formal_code=lean_code,
            depends_on=depends_on,
            confidence=0.8  # Default confidence
        )
    
    def _step_description_to_lean(self, description: str, theorem: DomainTheorem, previous_steps: List[ProofStep] = None) -> str:
        """Convert a step description to Lean code.
        
        Args:
            description: Description of the proof step
            theorem: The theorem being proved
            previous_steps: Previous proof steps
            
        Returns:
            Lean code for the proof step
        """
        # Pattern match on common proof step descriptions
        if "introduce" in description.lower() or "set up" in description.lower():
            return "intros"
        elif "by contradiction" in description.lower():
            return "by_contradiction"
        elif "definition" in description.lower() or "expand" in description.lower():
            # Try to identify the definition to unfold
            for word in description.split():
                if len(word) > 3 and word[0].isupper():
                    return f"unfold {word}"
            return "unfold"
        elif "apply" in description.lower():
            # Try to identify the theorem or lemma to apply
            for word in description.split():
                if len(word) > 3 and not any(c.isdigit() for c in word):
                    if word.endswith(".") or word.endswith(","):
                        word = word[:-1]
                    return f"apply {word}"
            return "apply"
        elif "case" in description.lower():
            return "cases"
        elif "contradiction" in description.lower():
            return "contradiction"
        elif "conclude" in description.lower() or "therefore" in description.lower():
            return "exact"
        elif "rewrite" in description.lower() or "substitute" in description.lower():
            return "rw"
        elif "simplify" in description.lower():
            return "simp"
        elif "existence" in description.lower():
            return "exists"
        elif "uniqueness" in description.lower():
            return "subst"
        elif "assumption" in description.lower():
            return "assumption"
        else:
            # Default placeholder
            return "-- " + description
    
    def create_proof_from_sketch(self, theorem: DomainTheorem, sketch: List[str]) -> Proof:
        """Create a proof from a sketch.
        
        Args:
            theorem: The theorem to prove
            sketch: List of proof step descriptions
            
        Returns:
            A new proof
        """
        proof_id = f"proof_{theorem.id}_{len(theorem.proofs) + 1}"
        steps = []
        
        for i, description in enumerate(sketch):
            step = self.generate_proof_step(theorem, description, steps[:i])
            steps.append(step)
        
        return Proof(
            proof_id=proof_id,
            language=FormalizationLanguage.LEAN4,
            steps=steps,
            complete=False,
            verified=False
        )
    
    def synthesize_complete_proof(self, theorem: DomainTheorem, proof: Proof) -> str:
        """Synthesize a complete Lean proof from proof steps.
        
        Args:
            theorem: The theorem to prove
            proof: The proof with steps
            
        Returns:
            Complete Lean proof code
        """
        lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
        if not lean_def:
            raise ValueError(f"Theorem {theorem.id} doesn't have a Lean formal definition")
        
        # Extract the theorem statement without the proof
        theorem_stmt = re.sub(r':=.*$', '', lean_def.code, flags=re.DOTALL).strip()
        
        # Compose the proof from the steps
        proof_code = " := begin\n"
        for step in proof.steps:
            proof_code += f"  -- {step.description}\n"
            proof_code += f"  {step.formal_code},\n"
        proof_code += "end"
        
        return theorem_stmt + proof_code


class EconomicInterpreter:
    """Interprets formal results in economic terms."""
    
    def __init__(self, domain_manager: DomainModelManager):
        """Initialize the interpreter.
        
        Args:
            domain_manager: The domain model manager
        """
        self.domain_manager = domain_manager
    
    def interpret_proof_result(self, theorem: DomainTheorem, proof: Proof) -> str:
        """Interpret the economic meaning of a proof result.
        
        Args:
            theorem: The theorem proved
            proof: The proof of the theorem
            
        Returns:
            Economic interpretation of the proof
        """
        # Base interpretation on theorem type
        theorem_name = theorem.name.lower()
        
        if "welfare" in theorem_name:
            return self._interpret_welfare_theorem(theorem, proof)
        elif "existence" in theorem_name:
            return self._interpret_existence_theorem(theorem, proof)
        elif "equilibrium" in theorem_name:
            return self._interpret_equilibrium_theorem(theorem, proof)
        elif "efficiency" in theorem_name:
            return self._interpret_efficiency_theorem(theorem, proof)
        elif "pareto" in theorem_name:
            return self._interpret_pareto_theorem(theorem, proof)
        else:
            # Default interpretation
            return f"The theorem '{theorem.name}' has been {proof.verified and 'verified' or 'formalized'}. " \
                   f"This establishes that {theorem.description}"
    
    def _interpret_welfare_theorem(self, theorem: DomainTheorem, proof: Proof) -> str:
        """Interpret welfare theorems."""
        if "first" in theorem.name.lower():
            return (
                f"The First Welfare Theorem has been {proof.verified and 'verified' or 'formalized'}. "
                f"This establishes that competitive market equilibria lead to Pareto efficient allocations. "
                f"In economic terms, this means that perfect competition results in an allocation where "
                f"no individual can be made better off without making someone else worse off, "
                f"confirming the 'invisible hand' mechanism described by Adam Smith."
            )
        elif "second" in theorem.name.lower():
            return (
                f"The Second Welfare Theorem has been {proof.verified and 'verified' or 'formalized'}. "
                f"This establishes that any Pareto efficient allocation can be supported as a competitive "
                f"equilibrium with appropriate lump-sum transfers. In economic terms, this means that "
                f"issues of efficiency and equity can be separated: society can first achieve efficiency "
                f"through markets and then address distributional concerns through appropriate transfers."
            )
        else:
            return (
                f"This welfare theorem has been {proof.verified and 'verified' or 'formalized'}. "
                f"It establishes important connections between market outcomes and social welfare, "
                f"specifically that {theorem.description}"
            )
    
    def _interpret_existence_theorem(self, theorem: DomainTheorem, proof: Proof) -> str:
        """Interpret existence theorems."""
        return (
            f"The existence theorem for {theorem.name.split('Existence')[0].strip()} has been "
            f"{proof.verified and 'verified' or 'formalized'}. This formally establishes that "
            f"a solution to the economic problem exists under the specified conditions. "
            f"In practical terms, this guarantees that the economic system being modeled "
            f"can reach a stable state that satisfies all the specified constraints."
        )
    
    def _interpret_equilibrium_theorem(self, theorem: DomainTheorem, proof: Proof) -> str:
        """Interpret equilibrium theorems."""
        return (
            f"The equilibrium properties for {theorem.name.split('Equilibrium')[0].strip()} have been "
            f"{proof.verified and 'verified' or 'formalized'}. This theorem establishes conditions "
            f"under which market prices coordinate supply and demand efficiently. "
            f"In economic terms, this means that {theorem.description}, "
            f"which validates the theoretical basis for market-based resource allocation."
        )
    
    def _interpret_efficiency_theorem(self, theorem: DomainTheorem, proof: Proof) -> str:
        """Interpret efficiency theorems."""
        return (
            f"The efficiency properties for {theorem.name.split('Efficiency')[0].strip()} have been "
            f"{proof.verified and 'verified' or 'formalized'}. This theorem establishes that "
            f"the economic mechanism achieves an efficient allocation of resources, meaning "
            f"that no resources are wasted. In practical terms, this validation assures us "
            f"that the economic system we're analyzing makes optimal use of scarce resources."
        )
    
    def _interpret_pareto_theorem(self, theorem: DomainTheorem, proof: Proof) -> str:
        """Interpret Pareto-related theorems."""
        return (
            f"The Pareto properties for {theorem.name.split('Pareto')[0].strip()} have been "
            f"{proof.verified and 'verified' or 'formalized'}. This theorem establishes that "
            f"the economic outcome satisfies Pareto efficiency, meaning no individual can be made "
            f"better off without making someone else worse off. This is a fundamental welfare "
            f"criterion in economics, confirming that the mechanism achieves a form of optimality."
        )
    
    def extract_economic_insights(self, theorem: DomainTheorem, proof: Proof) -> List[str]:
        """Extract key economic insights from a proven theorem.
        
        Args:
            theorem: The theorem proved
            proof: The proof of the theorem
            
        Returns:
            List of economic insights
        """
        insights = []
        
        # Extract insights based on the theorem's tags and related concepts
        theorem_focus = theorem.name.lower()
        
        # Add insights based on theorem focus
        if "welfare" in theorem_focus:
            insights.append("This result provides formal validation for welfare economics principles.")
            insights.append("The theorem connects market outcomes with social welfare concepts.")
        
        if "equilibrium" in theorem_focus:
            insights.append("This result confirms the mathematical existence of market equilibrium.")
            insights.append("The theorem provides conditions under which markets can reach stable states.")
        
        if "efficiency" in theorem_focus or "pareto" in theorem_focus:
            insights.append("This result formally validates that the economic system achieves efficient outcomes.")
            insights.append("The theorem establishes optimality properties of resource allocation.")
        
        # Add insights based on theorem difficulty
        if theorem.difficulty >= 8:
            insights.append("This is a mathematically complex result that provides deep theoretical foundations.")
        elif theorem.difficulty >= 5:
            insights.append("This result bridges theoretical economic concepts with practical implications.")
        else:
            insights.append("This theorem provides a basic building block for economic theory.")
        
        # Add insights based on theorem importance
        if theorem.importance >= 8:
            insights.append("This is a cornerstone result in economic theory with far-reaching implications.")
        elif theorem.importance >= 5:
            insights.append("This theorem has significant implications for economic policy and analysis.")
        
        # Add generic insight
        insights.append(f"The formal verification of this theorem strengthens the mathematical foundations of {theorem.concept_type.value} theory in economics.")
        
        return insights
    
    def suggest_economic_applications(self, theorem: DomainTheorem) -> List[str]:
        """Suggest practical economic applications for a theorem.
        
        Args:
            theorem: The theorem to suggest applications for
            
        Returns:
            List of suggested applications
        """
        applications = []
        
        # Suggest applications based on theorem type
        concept_type = theorem.concept_type
        
        if concept_type == ConceptType.EQUILIBRIUM:
            applications.append("Market design for achieving efficient trading outcomes")
            applications.append("Regulatory policies that maintain market equilibrium")
            applications.append("Understanding price formation in complex markets")
        
        elif concept_type == ConceptType.WELFARE:
            applications.append("Social welfare evaluation of economic policies")
            applications.append("Redistribution mechanisms to achieve equity goals")
            applications.append("Cost-benefit analysis frameworks")
        
        elif concept_type == ConceptType.PREFERENCE:
            applications.append("Consumer behavior modeling and prediction")
            applications.append("Product design optimization based on preferences")
            applications.append("Marketing strategy development")
        
        elif concept_type == ConceptType.PRODUCTION:
            applications.append("Production process optimization")
            applications.append("Supply chain efficiency improvement")
            applications.append("Resource allocation decision-making")
        
        elif concept_type == ConceptType.MARKET:
            applications.append("Market structure analysis and competition policy")
            applications.append("Trading mechanism design")
            applications.append("Price discovery systems")
        
        # Add generic applications
        applications.append("Economic education and theoretical foundations")
        applications.append("Research frameworks for empirical validation of economic theories")
        
        return applications


if __name__ == "__main__":
    # Basic usage example
    from economic_domain_model import DomainModelManager
    
    # Create domain manager and load basics
    domain_manager = DomainModelManager()
    
    # Create translator and test it
    translator = LeanTranslator(domain_manager)
    
    # Test structure generator
    structure_generator = FormalStructureGenerator(translator)
    market_structure = structure_generator.generate_market_structure(
        "CompetitiveMarket", 
        "model of a perfectly competitive market with multiple goods and agents",
        n_goods=3,
        n_agents=2
    )
    print(market_structure)
    
    equilibrium_conditions = structure_generator.generate_equilibrium_conditions("CompetitiveMarket")
    print(equilibrium_conditions)
    
    # Test proof generator
    proof_generator = ProofGenerator(translator)
    
    # Create and add a simple theorem for testing
    from economic_domain_model import DomainTheorem, TheoremStatus, FormalizationLanguage, FormalDefinition
    
    first_welfare_theorem = DomainTheorem(
        id="first_welfare_theorem",
        name="First Welfare Theorem",
        description="Competitive equilibria are Pareto efficient",
        concept_type=ConceptType.WELFARE,
        status=TheoremStatus.CONJECTURED,
        difficulty=7,
        importance=10
    )
    
    first_welfare_theorem.add_formal_definition(FormalDefinition(
        language=FormalizationLanguage.LEAN4,
        code="""
/-- First Welfare Theorem: Competitive equilibria are Pareto efficient -/
theorem firstWelfareTheorem {n m : Nat} (agents : Fin m → Agent n) (p : Fin n → ℝ) :
  CompetitiveEquilibrium n agents p →
  ParetoEfficient n agents :=
  sorry
""",
        imports=["Mathlib.Data.Real.Basic", "Mathlib.Data.Fin.Basic"]
    ))
    
    domain_manager.add_theorem(first_welfare_theorem)
    
    # Generate a proof sketch
    proof_sketch = proof_generator.generate_proof_sketch(first_welfare_theorem)
    print("Proof sketch:")
    for step in proof_sketch:
        print(f"- {step}")
    
    # Create a proof from the sketch
    proof = proof_generator.create_proof_from_sketch(first_welfare_theorem, proof_sketch)
    
    # Test synthesizing complete proof
    complete_proof = proof_generator.synthesize_complete_proof(first_welfare_theorem, proof)
    print("\nComplete proof:")
    print(complete_proof)
    
    # Test economic interpreter
    interpreter = EconomicInterpreter(domain_manager)
    
    # Simulate a verified proof
    proof.verified = True
    
    interpretation = interpreter.interpret_proof_result(first_welfare_theorem, proof)
    print("\nEconomic interpretation:")
    print(interpretation)
    
    insights = interpreter.extract_economic_insights(first_welfare_theorem, proof)
    print("\nEconomic insights:")
    for insight in insights:
        print(f"- {insight}")
    
    applications = interpreter.suggest_economic_applications(first_welfare_theorem)
    print("\nSuggested applications:")
    for app in applications:
        print(f"- {app}")