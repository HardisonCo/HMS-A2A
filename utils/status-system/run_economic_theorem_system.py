#!/usr/bin/env python3
"""
Economic Theorem System Runner

This script integrates all components of the economic theorem proving system
and provides a command-line interface to run the system with various configurations.
It serves as the main entry point for using the economic theorem proving system.

Usage:
  python run_economic_theorem_system.py --mode <mode> [--generations <n>] [--theorem-id <id>]

Modes:
  - setup: Initialize the system and create sample theorems
  - prove: Prove a specific theorem or all unproven theorems
  - analyze: Analyze the theorem repository
  - optimize: Optimize theorem statements and proofs
  - evolve: Run genetic evolution of the agent population
  - interactive: Run an interactive session for working with theorems
"""

import os
import sys
import json
import time
import logging
import argparse
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import all components
from economic_domain_model import (
    ConceptType, DomainAxiom, DomainModelManager, DomainTheorem, 
    EconomicConcept, FormalDefinition, FormalizationLanguage,
    Proof, ProofStep, TheoremStatus
)

from economic_formal_translator import (
    LeanTranslator, FormalStructureGenerator, ProofGenerator, EconomicInterpreter
)

from economic_theorem_prover import (
    TheoremProver, ProofStrategy, SubgoalDecomposer, ProofVerifier, DeepSeekProverInterface,
    ProofMethod
)

from economic_repository_integration import (
    TheoremRepository, TheoremRepositoryConfig, EconomicRepositoryAnalyzer,
    ProofStatusTracker, TheoremOptimizer, EconomicGeneticAgentSystem
)

from repository_analyzer import RepositoryAnalyzer
from genetic_agent_system import GeneticAgentSystem


def setup_logging(log_dir: str, log_level: str = "INFO") -> None:
    """Set up logging configuration.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (INFO, DEBUG, etc.)
    """
    os.makedirs(log_dir, exist_ok=True)
    
    # Determine log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure file handler
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"economic_theorem_system_{timestamp}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info(f"Logging initialized at level {log_level}")


def create_system_components(base_dir: str) -> Dict[str, Any]:
    """Create all system components.
    
    Args:
        base_dir: Base directory for system storage
        
    Returns:
        Dictionary containing all system components
    """
    # Create component directories
    domain_model_dir = os.path.join(base_dir, "domain_model")
    theorem_repo_dir = os.path.join(base_dir, "theorem_repository")
    lean_export_dir = os.path.join(base_dir, "lean_export")
    reports_dir = os.path.join(base_dir, "reports")
    
    os.makedirs(domain_model_dir, exist_ok=True)
    os.makedirs(theorem_repo_dir, exist_ok=True)
    os.makedirs(lean_export_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    # Create domain manager
    domain_manager = DomainModelManager(domain_model_dir)
    
    # Create theorem repository
    repo_config = TheoremRepositoryConfig(
        root_path=theorem_repo_dir,
        lean_export_path=lean_export_dir
    )
    theorem_repo = TheoremRepository(domain_manager, repo_config)
    
    # Create translator and prover components
    translator = LeanTranslator(domain_manager)
    structure_generator = FormalStructureGenerator(translator)
    proof_generator = ProofGenerator(translator)
    economic_interpreter = EconomicInterpreter(domain_manager)
    
    # Create prover components
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
    
    # Create repository analyzer
    repo_analyzer = RepositoryAnalyzer()
    
    # Create economic repository analyzer
    econ_repo_analyzer = EconomicRepositoryAnalyzer(
        domain_manager=domain_manager,
        theorem_repository=theorem_repo,
        repo_analyzer=repo_analyzer
    )
    
    # Create proof status tracker
    status_tracker = ProofStatusTracker(
        domain_manager=domain_manager,
        theorem_repository=theorem_repo,
        prover=prover
    )
    
    # Create theorem optimizer
    optimizer = TheoremOptimizer(
        domain_manager=domain_manager,
        translator=translator,
        prover=prover
    )
    
    # Create economic genetic agent system
    genetic_system = EconomicGeneticAgentSystem(
        domain_manager=domain_manager,
        theorem_repository=theorem_repo,
        repo_analyzer=econ_repo_analyzer,
        prover=prover,
        optimizer=optimizer
    )
    
    return {
        "domain_manager": domain_manager,
        "theorem_repository": theorem_repo,
        "translator": translator,
        "structure_generator": structure_generator,
        "proof_generator": proof_generator,
        "economic_interpreter": economic_interpreter,
        "decomposer": decomposer,
        "verifier": verifier,
        "deepseek": deepseek,
        "prover": prover,
        "repo_analyzer": repo_analyzer,
        "econ_repo_analyzer": econ_repo_analyzer,
        "status_tracker": status_tracker,
        "optimizer": optimizer,
        "genetic_system": genetic_system,
        "directories": {
            "base_dir": base_dir,
            "domain_model_dir": domain_model_dir,
            "theorem_repo_dir": theorem_repo_dir,
            "lean_export_dir": lean_export_dir,
            "reports_dir": reports_dir
        }
    }


def create_sample_theorems(components: Dict[str, Any]) -> None:
    """Create sample economic theorems for testing.
    
    Args:
        components: System components dictionary
    """
    domain_manager = components["domain_manager"]
    translator = components["translator"]
    
    # Create basic utility axioms
    utility_monotonicity = DomainAxiom(
        id="utility_monotonicity",
        name="Utility Monotonicity",
        description="Utility functions are monotonically increasing in all goods",
        concept_type=ConceptType.PREFERENCE,
        is_primitive=True,
        justification="Basic axiom of consumer theory"
    )
    
    utility_monotonicity.add_formal_definition(FormalDefinition(
        language=FormalizationLanguage.LEAN4,
        code="""
/-- Utility Monotonicity: Utility functions are monotonically increasing in all goods -/
axiom utilityMonotonicity {n : Nat} (u : Utility n) : Monotonic u
""",
        imports=["Mathlib.Data.Real.Basic"],
        dependencies=[]
    ))
    
    domain_manager.add_axiom(utility_monotonicity)
    
    # Create transitivity axiom
    preference_transitivity = DomainAxiom(
        id="preference_transitivity",
        name="Preference Transitivity",
        description="Preference relations are transitive",
        concept_type=ConceptType.PREFERENCE,
        is_primitive=True,
        justification="Basic axiom of rational choice"
    )
    
    preference_transitivity.add_formal_definition(FormalDefinition(
        language=FormalizationLanguage.LEAN4,
        code="""
/-- Preference Transitivity: Preference relations are transitive -/
axiom preferenceTransitivity {n : Nat} (≿ : PreferenceRelation n) :
  ∀ (x y z : Bundle n), x ≿ y → y ≿ z → x ≿ z
""",
        imports=["Mathlib.Data.Real.Basic"],
        dependencies=[]
    ))
    
    domain_manager.add_axiom(preference_transitivity)
    
    # Create market clearing axiom
    market_clearing = DomainAxiom(
        id="market_clearing",
        name="Market Clearing",
        description="In equilibrium, markets clear: supply equals demand for each good",
        concept_type=ConceptType.EQUILIBRIUM,
        is_primitive=True,
        justification="Basic axiom of general equilibrium theory"
    )
    
    market_clearing.add_formal_definition(FormalDefinition(
        language=FormalizationLanguage.LEAN4,
        code="""
/-- Market Clearing: In equilibrium, markets clear -/
axiom marketClearing {n m : Nat} (agents : Fin m → Agent n) (p : Fin n → ℝ) :
  CompetitiveEquilibrium n agents p →
  ∀ (g : Fin n), (∑ a : Fin m, demand agents a g p) = (∑ a : Fin m, supply agents a g p)
""",
        imports=["Mathlib.Data.Real.Basic", "Mathlib.Algebra.BigOperators.Basic"],
        dependencies=[]
    ))
    
    domain_manager.add_axiom(market_clearing)
    
    # Create utility maximization theorem
    utility_maximization = DomainTheorem(
        id="utility_maximization",
        name="Utility Maximization under Budget Constraint",
        description="Consumers maximize utility subject to their budget constraints",
        concept_type=ConceptType.PREFERENCE,
        status=TheoremStatus.CONJECTURED,
        difficulty=4,
        importance=9
    )
    
    utility_maximization.add_formal_definition(FormalDefinition(
        language=FormalizationLanguage.LEAN4,
        code="""
/-- Utility Maximization under Budget Constraint: Consumers maximize utility subject to their budget constraints -/
theorem utilityMaximization {n : Nat} (u : Utility n) (p : Fin n → ℝ) (w : ℝ) (x : Fin n → ℝ) :
  (∀ i, p i > 0) →
  utilityMonotonicity u →
  BudgetConstraint p w x →
  UtilityMaximizing u p w x →
  (∑ i, p i * x i) = w
""",
        imports=["Mathlib.Data.Real.Basic", "Mathlib.Algebra.BigOperators.Basic"],
        dependencies=["utility_monotonicity"]
    ))
    
    domain_manager.add_theorem(utility_maximization)
    
    # Create first welfare theorem
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
  (∀ i, p i > 0) →
  CompetitiveEquilibrium n agents p →
  ParetoEfficient n agents
""",
        imports=["Mathlib.Data.Real.Basic", "Mathlib.Algebra.BigOperators.Basic"],
        dependencies=["market_clearing", "utility_maximization"]
    ))
    
    domain_manager.add_theorem(first_welfare_theorem)
    
    # Create second welfare theorem
    second_welfare_theorem = DomainTheorem(
        id="second_welfare_theorem",
        name="Second Welfare Theorem",
        description="Any Pareto efficient allocation can be supported as a competitive equilibrium with appropriate lump-sum transfers",
        concept_type=ConceptType.WELFARE,
        status=TheoremStatus.CONJECTURED,
        difficulty=8,
        importance=9
    )
    
    second_welfare_theorem.add_formal_definition(FormalDefinition(
        language=FormalizationLanguage.LEAN4,
        code="""
/-- Second Welfare Theorem: Any Pareto efficient allocation can be supported as a competitive equilibrium with appropriate lump-sum transfers -/
theorem secondWelfareTheorem {n m : Nat} (agents : Fin m → Agent n) (alloc : Fin m → Fin n → ℝ) :
  ConvexPreferences n agents →
  ContinuousPreferences n agents →
  ParetoEfficient n agents alloc →
  ∃ (p : Fin n → ℝ) (w : Fin m → ℝ), 
    (∀ i, p i > 0) ∧
    (∀ a, BudgetConstraint p (w a) (alloc a)) ∧
    (∀ a, UtilityMaximizing (agents a).utility p (w a) (alloc a))
""",
        imports=["Mathlib.Data.Real.Basic", "Mathlib.Algebra.BigOperators.Basic"],
        dependencies=["utility_maximization", "preference_transitivity"]
    ))
    
    domain_manager.add_theorem(second_welfare_theorem)
    
    # Create equilibrium existence theorem
    equilibrium_existence = DomainTheorem(
        id="equilibrium_existence",
        name="Existence of Competitive Equilibrium",
        description="Under certain conditions, a competitive equilibrium exists",
        concept_type=ConceptType.EQUILIBRIUM,
        status=TheoremStatus.CONJECTURED,
        difficulty=9,
        importance=10
    )
    
    equilibrium_existence.add_formal_definition(FormalDefinition(
        language=FormalizationLanguage.LEAN4,
        code="""
/-- Existence of Competitive Equilibrium: Under certain conditions, a competitive equilibrium exists -/
theorem equilibriumExistence {n m : Nat} (agents : Fin m → Agent n) :
  (∀ a, ConvexPreferences n (agents a)) →
  (∀ a, ContinuousPreferences n (agents a)) →
  (∀ a g, (agents a).endowment g > 0) →
  ∃ (p : Fin n → ℝ), (∀ g, p g > 0) ∧ CompetitiveEquilibrium n agents p
""",
        imports=["Mathlib.Data.Real.Basic", "Mathlib.Algebra.BigOperators.Basic"],
        dependencies=["market_clearing"]
    ))
    
    domain_manager.add_theorem(equilibrium_existence)
    
    # Create law of demand theorem
    law_of_demand = DomainTheorem(
        id="law_of_demand",
        name="Law of Demand",
        description="Demand for a normal good decreases as its price increases",
        concept_type=ConceptType.PREFERENCE,
        status=TheoremStatus.CONJECTURED,
        difficulty=5,
        importance=8
    )
    
    law_of_demand.add_formal_definition(FormalDefinition(
        language=FormalizationLanguage.LEAN4,
        code="""
/-- Law of Demand: Demand for a normal good decreases as its price increases -/
theorem lawOfDemand {n : Nat} (u : Utility n) (i : Fin n) (p₁ p₂ : Fin n → ℝ) (w : ℝ) :
  (∀ j, p₁ j > 0) →
  (∀ j, p₂ j > 0) →
  (p₁ i > p₂ i) →
  (∀ j, j ≠ i → p₁ j = p₂ j) →
  utilityMonotonicity u →
  let x₁ := optimalDemand u p₁ w in
  let x₂ := optimalDemand u p₂ w in
  x₁ i < x₂ i
""",
        imports=["Mathlib.Data.Real.Basic"],
        dependencies=["utility_monotonicity", "utility_maximization"]
    ))
    
    domain_manager.add_theorem(law_of_demand)
    
    logging.info(f"Created {len(domain_manager.theorems)} sample theorems")


async def run_setup_mode(components: Dict[str, Any], args: argparse.Namespace) -> None:
    """Run system setup mode."""
    logging.info("Running setup mode")
    
    # Create sample theorems
    create_sample_theorems(components)
    
    # Export theorems to repository
    components["theorem_repository"].export_all_theorems()
    
    logging.info("Setup completed successfully")


async def run_prove_mode(components: Dict[str, Any], args: argparse.Namespace) -> None:
    """Run theorem proving mode."""
    theorem_id = args.theorem_id
    prover = components["prover"]
    domain_manager = components["domain_manager"]
    
    if theorem_id:
        # Prove a specific theorem
        logging.info(f"Attempting to prove theorem: {theorem_id}")
        theorem = domain_manager.get_theorem(theorem_id)
        
        if not theorem:
            logging.error(f"Theorem not found: {theorem_id}")
            return
        
        logging.info(f"Theorem: {theorem.name}")
        logging.info(f"Description: {theorem.description}")
        
        success, message, proof = await prover.prove_theorem(
            theorem_id=theorem_id,
            decompose=True
        )
        
        logging.info(f"Proof result: {success}")
        logging.info(f"Message: {message}")
        
        if proof:
            logging.info(f"Proof has {len(proof.steps)} steps")
            
            # Display proof steps
            for i, step in enumerate(proof.steps):
                logging.info(f"Step {i+1}: {step.description}")
    else:
        # Prove all unproven theorems
        unproven_theorems = [
            t for t in domain_manager.theorems.values()
            if t.status == TheoremStatus.CONJECTURED
        ]
        
        if not unproven_theorems:
            logging.info("No unproven theorems found")
            return
        
        logging.info(f"Attempting to prove {len(unproven_theorems)} theorems")
        
        for theorem in unproven_theorems:
            logging.info(f"Attempting to prove: {theorem.name}")
            
            success, message, proof = await prover.prove_theorem(
                theorem_id=theorem.id,
                decompose=True
            )
            
            logging.info(f"Result for {theorem.name}: {success}")
            logging.info(f"Message: {message}")
    
    # Export updated theorems to repository
    components["theorem_repository"].export_all_theorems()


async def run_analyze_mode(components: Dict[str, Any], args: argparse.Namespace) -> None:
    """Run repository analysis mode."""
    econ_repo_analyzer = components["econ_repo_analyzer"]
    reports_dir = components["directories"]["reports_dir"]
    
    logging.info("Analyzing theorem repository")
    
    # Analyze the repository
    issues = econ_repo_analyzer.analyze_repository()
    
    # Log issues
    logging.info(f"Found {len(issues)} issues")
    for i, issue in enumerate(issues):
        logging.info(f"Issue {i+1}: {issue.title}")
        logging.info(f"  Description: {issue.description}")
        logging.info(f"  Severity: {issue.severity.value}")
        logging.info(f"  Location: {issue.location}")
    
    # Create reports
    reports = econ_repo_analyzer.create_reports(reports_dir)
    
    logging.info("Generated analysis reports:")
    for report_name, report_path in reports.items():
        logging.info(f"  {report_name}: {report_path}")


async def run_optimize_mode(components: Dict[str, Any], args: argparse.Namespace) -> None:
    """Run theorem optimization mode."""
    theorem_id = args.theorem_id
    optimizer = components["optimizer"]
    domain_manager = components["domain_manager"]
    
    if theorem_id:
        # Optimize a specific theorem
        logging.info(f"Optimizing theorem: {theorem_id}")
        
        theorem = domain_manager.get_theorem(theorem_id)
        if not theorem:
            logging.error(f"Theorem not found: {theorem_id}")
            return
        
        # Optimize theorem statement
        success, message = optimizer.optimize_theorem_statement(theorem_id)
        logging.info(f"Statement optimization: {success}")
        logging.info(f"Message: {message}")
        
        # Optimize proofs if any
        for proof in theorem.proofs:
            success, message = optimizer.optimize_proof(theorem_id, proof.proof_id)
            logging.info(f"Optimization of proof {proof.proof_id}: {success}")
            logging.info(f"Message: {message}")
    else:
        # Optimize all theorems
        theorems = list(domain_manager.theorems.values())
        
        if not theorems:
            logging.info("No theorems found to optimize")
            return
        
        logging.info(f"Optimizing {len(theorems)} theorems")
        
        # First optimize statements
        for theorem in theorems:
            success, message = optimizer.optimize_theorem_statement(theorem.id)
            if success:
                logging.info(f"Optimized statement of {theorem.name}: {message}")
        
        # Then optimize proofs
        for theorem in theorems:
            for proof in theorem.proofs:
                success, message = optimizer.optimize_proof(theorem.id, proof.proof_id)
                if success:
                    logging.info(f"Optimized proof {proof.proof_id} of {theorem.name}: {message}")
    
    # Export updated theorems to repository
    components["theorem_repository"].export_all_theorems()


async def run_evolve_mode(components: Dict[str, Any], args: argparse.Namespace) -> None:
    """Run genetic evolution mode."""
    genetic_system = components["genetic_system"]
    reports_dir = components["directories"]["reports_dir"]
    
    generations = args.generations or 5
    
    logging.info(f"Running genetic evolution for {generations} generations")
    
    # Run genetic evolution
    stats = await genetic_system.run_genetic_evolution(
        generations=generations,
        tasks_per_generation=5
    )
    
    # Log evolution results
    for gen_stats in stats:
        logging.info(f"Generation {gen_stats['generation']}:")
        logging.info(f"  Agents: {gen_stats['agents']}")
        logging.info(f"  Tasks: {gen_stats['tasks']}")
        logging.info(f"  Successful tasks: {gen_stats['successful_tasks']}")
        logging.info(f"  Average fitness: {sum(gen_stats['fitness_scores'].values()) / len(gen_stats['fitness_scores']):.4f}")
    
    # Export evolution stats
    stats_path = os.path.join(reports_dir, f"evolution_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    logging.info(f"Evolution stats exported to {stats_path}")


async def run_interactive_mode(components: Dict[str, Any], args: argparse.Namespace) -> None:
    """Run interactive mode for working with theorems."""
    domain_manager = components["domain_manager"]
    theorem_repository = components["theorem_repository"]
    prover = components["prover"]
    optimizer = components["optimizer"]
    
    logging.info("Starting interactive mode")
    print("\nEconomic Theorem Proving System - Interactive Mode")
    print("=================================================")
    
    while True:
        print("\nAvailable commands:")
        print("1. List theorems")
        print("2. View theorem details")
        print("3. Create new theorem")
        print("4. Prove theorem")
        print("5. Optimize theorem")
        print("6. Analyze repository")
        print("7. Export theorems")
        print("8. Import theorems")
        print("9. Exit")
        
        choice = input("\nEnter command number: ")
        
        if choice == "1":
            # List theorems
            theorems = list(domain_manager.theorems.values())
            if not theorems:
                print("No theorems found")
                continue
            
            print(f"\nFound {len(theorems)} theorems:")
            for i, theorem in enumerate(theorems):
                print(f"{i+1}. {theorem.name} - Status: {theorem.status.value}")
        
        elif choice == "2":
            # View theorem details
            theorem_id = input("Enter theorem ID (or number from list): ")
            
            # Handle numeric input
            if theorem_id.isdigit():
                theorems = list(domain_manager.theorems.values())
                idx = int(theorem_id) - 1
                if 0 <= idx < len(theorems):
                    theorem = theorems[idx]
                    theorem_id = theorem.id
                else:
                    print("Invalid theorem number")
                    continue
            
            theorem = domain_manager.get_theorem(theorem_id)
            if not theorem:
                print(f"Theorem not found: {theorem_id}")
                continue
            
            print(f"\nTheorem: {theorem.name}")
            print(f"ID: {theorem.id}")
            print(f"Description: {theorem.description}")
            print(f"Concept type: {theorem.concept_type.value}")
            print(f"Status: {theorem.status.value}")
            print(f"Difficulty: {theorem.difficulty}/10")
            print(f"Importance: {theorem.importance}/10")
            
            # Show formal definition
            lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
            if lean_def:
                print("\nFormal definition:")
                print(lean_def.code)
            
            # Show proofs
            if theorem.proofs:
                print(f"\nProofs ({len(theorem.proofs)}):")
                for i, proof in enumerate(theorem.proofs):
                    print(f"Proof {i+1}: {proof.proof_id}")
                    print(f"  Complete: {proof.complete}")
                    print(f"  Verified: {proof.verified}")
                    print(f"  Steps: {len(proof.steps)}")
                
                # Option to view a specific proof
                proof_num = input("\nEnter proof number to view details (or press Enter to skip): ")
                if proof_num.isdigit() and 0 < int(proof_num) <= len(theorem.proofs):
                    proof = theorem.proofs[int(proof_num) - 1]
                    print(f"\nProof: {proof.proof_id}")
                    print(f"Complete: {proof.complete}")
                    print(f"Verified: {proof.verified}")
                    
                    if proof.steps:
                        print("\nSteps:")
                        for i, step in enumerate(proof.steps):
                            print(f"Step {i+1}: {step.description}")
                            print(f"  Code: {step.formal_code}")
                            print(f"  Confidence: {step.confidence:.2f}")
            else:
                print("\nNo proofs found")
        
        elif choice == "3":
            # Create new theorem
            print("\nCreating a new theorem:")
            
            name = input("Theorem name: ")
            description = input("Description: ")
            
            # Select concept type
            print("\nConcept types:")
            for i, concept_type in enumerate(ConceptType):
                print(f"{i+1}. {concept_type.value}")
            
            type_choice = input("Select concept type (number): ")
            if not type_choice.isdigit() or int(type_choice) < 1 or int(type_choice) > len(ConceptType):
                print("Invalid choice")
                continue
            
            concept_type = list(ConceptType)[int(type_choice) - 1]
            
            difficulty = input("Difficulty (1-10): ")
            importance = input("Importance (1-10): ")
            
            if not difficulty.isdigit() or not importance.isdigit():
                print("Invalid difficulty or importance")
                continue
            
            # Create the theorem
            theorem_id = name.lower().replace(" ", "_")
            theorem = DomainTheorem(
                id=theorem_id,
                name=name,
                description=description,
                concept_type=concept_type,
                status=TheoremStatus.CONJECTURED,
                difficulty=int(difficulty),
                importance=int(importance)
            )
            
            # Add formal definition
            print("\nEnter formal definition in Lean 4 (end with an empty line):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            
            formal_def = "\n".join(lines)
            
            if formal_def:
                theorem.add_formal_definition(FormalDefinition(
                    language=FormalizationLanguage.LEAN4,
                    code=formal_def,
                    imports=["Mathlib.Data.Real.Basic"],
                    dependencies=[]
                ))
            
            # Add to domain manager
            domain_manager.add_theorem(theorem)
            print(f"\nTheorem {theorem.name} created successfully")
            
            # Export to repository
            theorem_repository.export_all_theorems()
        
        elif choice == "4":
            # Prove theorem
            theorem_id = input("Enter theorem ID to prove (or number from list): ")
            
            # Handle numeric input
            if theorem_id.isdigit():
                theorems = list(domain_manager.theorems.values())
                idx = int(theorem_id) - 1
                if 0 <= idx < len(theorems):
                    theorem = theorems[idx]
                    theorem_id = theorem.id
                else:
                    print("Invalid theorem number")
                    continue
            
            theorem = domain_manager.get_theorem(theorem_id)
            if not theorem:
                print(f"Theorem not found: {theorem_id}")
                continue
            
            print(f"\nAttempting to prove: {theorem.name}")
            
            # Ask for decomposition preference
            decompose = input("Use theorem decomposition? (y/n): ").lower() == 'y'
            
            # Prove the theorem
            success, message, proof = await prover.prove_theorem(
                theorem_id=theorem_id,
                decompose=decompose
            )
            
            print(f"\nProof result: {success}")
            print(f"Message: {message}")
            
            if proof:
                print(f"Proof has {len(proof.steps)} steps")
                
                # Display proof steps
                for i, step in enumerate(proof.steps):
                    print(f"Step {i+1}: {step.description}")
            
            # Export to repository
            theorem_repository.export_all_theorems()
        
        elif choice == "5":
            # Optimize theorem
            theorem_id = input("Enter theorem ID to optimize (or number from list): ")
            
            # Handle numeric input
            if theorem_id.isdigit():
                theorems = list(domain_manager.theorems.values())
                idx = int(theorem_id) - 1
                if 0 <= idx < len(theorems):
                    theorem = theorems[idx]
                    theorem_id = theorem.id
                else:
                    print("Invalid theorem number")
                    continue
            
            theorem = domain_manager.get_theorem(theorem_id)
            if not theorem:
                print(f"Theorem not found: {theorem_id}")
                continue
            
            print(f"\nOptimizing theorem: {theorem.name}")
            
            # Optimize theorem statement
            success, message = optimizer.optimize_theorem_statement(theorem_id)
            print(f"Statement optimization: {success}")
            print(f"Message: {message}")
            
            # Optimize proofs if any
            if theorem.proofs:
                for i, proof in enumerate(theorem.proofs):
                    optimize_proof = input(f"Optimize proof {i+1}? (y/n): ").lower() == 'y'
                    if optimize_proof:
                        success, message = optimizer.optimize_proof(theorem_id, proof.proof_id)
                        print(f"Optimization of proof {proof.proof_id}: {success}")
                        print(f"Message: {message}")
            
            # Export to repository
            theorem_repository.export_all_theorems()
        
        elif choice == "6":
            # Analyze repository
            print("\nAnalyzing theorem repository...")
            
            # Get repository analyzer
            econ_repo_analyzer = components["econ_repo_analyzer"]
            reports_dir = components["directories"]["reports_dir"]
            
            # Analyze the repository
            issues = econ_repo_analyzer.analyze_repository()
            
            # Show issues
            print(f"\nFound {len(issues)} issues:")
            for i, issue in enumerate(issues):
                print(f"{i+1}. {issue.title}")
                print(f"   Description: {issue.description}")
                print(f"   Severity: {issue.severity.value}")
                print(f"   Location: {issue.location}")
            
            # Create reports
            reports = econ_repo_analyzer.create_reports(reports_dir)
            
            print("\nGenerated analysis reports:")
            for report_name, report_path in reports.items():
                print(f"  {report_name}: {report_path}")
        
        elif choice == "7":
            # Export theorems
            print("\nExporting theorems to repository...")
            theorem_repository.export_all_theorems()
            print("Export completed successfully")
        
        elif choice == "8":
            # Import theorems
            print("\nImporting theorems from repository...")
            theorem_repository.import_from_repository()
            print("Import completed successfully")
            
            # Show imported theorems
            theorems = list(domain_manager.theorems.values())
            print(f"\nRepository contains {len(theorems)} theorems:")
            for i, theorem in enumerate(theorems[:10]):  # Show first 10
                print(f"{i+1}. {theorem.name} - Status: {theorem.status.value}")
            
            if len(theorems) > 10:
                print(f"... and {len(theorems) - 10} more")
        
        elif choice == "9":
            # Exit
            print("\nExiting interactive mode")
            break
        
        else:
            print("Invalid command")


async def main() -> None:
    """Main entry point for the economic theorem system."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Economic Theorem Proving System")
    parser.add_argument("--mode", choices=["setup", "prove", "analyze", "optimize", "evolve", "interactive"],
                        default="interactive", help="Mode to run the system in")
    parser.add_argument("--base-dir", default="./economic_theorem_system",
                        help="Base directory for system storage")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level")
    parser.add_argument("--theorem-id", help="ID of the theorem to operate on")
    parser.add_argument("--generations", type=int, help="Number of generations for genetic evolution")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(os.path.join(args.base_dir, "logs"), args.log_level)
    
    try:
        # Create system components
        components = create_system_components(args.base_dir)
        
        # Run the selected mode
        if args.mode == "setup":
            await run_setup_mode(components, args)
        elif args.mode == "prove":
            await run_prove_mode(components, args)
        elif args.mode == "analyze":
            await run_analyze_mode(components, args)
        elif args.mode == "optimize":
            await run_optimize_mode(components, args)
        elif args.mode == "evolve":
            await run_evolve_mode(components, args)
        elif args.mode == "interactive":
            await run_interactive_mode(components, args)
    
    except Exception as e:
        logging.error(f"Error running the system: {str(e)}")
        logging.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())