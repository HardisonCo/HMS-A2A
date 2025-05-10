"""
CoRT (Chain of Recursive Thoughts) Integration for Genetic Theorem Proving

This module provides integration with HMS-A2A's Chain of Recursive Thoughts (CoRT) capabilities,
enabling genetic theorem proving agents to utilize recursive self-critique and
alternative generation for enhanced reasoning during theorem proving.
"""

from typing import Dict, List, Tuple, Any, Optional, Set, Union, Callable
import json
import os
import time
import logging
import uuid
from dataclasses import dataclass, field
import random
import asyncio
import subprocess
import sys
import inspect
import importlib.util

from ..core.base_agent import (
    GeneticTheoremProverAgent,
    GeneticTraits,
    ProofAttempt
)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class CoRTThinkingStep:
    """Represents a step in the Chain of Recursive Thoughts process."""
    step_id: str
    round: int
    description: str
    thinking: str
    critique: Optional[str] = None
    confidence: float = 0.0


@dataclass
class CoRTProofAttempt(ProofAttempt):
    """
    Extends ProofAttempt with Chain of Recursive Thoughts capabilities.
    """
    thinking_trace: List[CoRTThinkingStep] = field(default_factory=list)
    alternatives_considered: List[Dict[str, Any]] = field(default_factory=list)
    thinking_rounds: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        base_dict = {
            "theorem_id": self.theorem_id,
            "steps": self.steps,
            "success": self.success,
            "resources_used": self.resources_used,
            "time_taken": self.time_taken,
            "verification_result": self.verification_result,
            "thinking_trace": [
                {
                    "step_id": step.step_id,
                    "round": step.round,
                    "description": step.description,
                    "thinking": step.thinking,
                    "critique": step.critique,
                    "confidence": step.confidence
                }
                for step in self.thinking_trace
            ],
            "alternatives_considered": self.alternatives_considered,
            "thinking_rounds": self.thinking_rounds
        }
        return base_dict


class CoRTClient:
    """
    Client for interacting with HMS-A2A's Chain of Recursive Thoughts (CoRT) system.
    
    This client supports both local CoRT implementation and integration with 
    the HMS-A2A CoRT server.
    """
    
    def __init__(self, local_mode: bool = True, cort_server_url: Optional[str] = None,
                max_rounds: int = 3, generate_alternatives: int = 3):
        """
        Initialize a CoRT client.
        
        Args:
            local_mode: Whether to use local CoRT implementation (True) or HMS-A2A server (False)
            cort_server_url: URL for the CoRT server (required if local_mode is False)
            max_rounds: Maximum number of thinking rounds
            generate_alternatives: Number of alternative approaches to generate
        """
        self.local_mode = local_mode
        self.cort_server_url = cort_server_url
        self.max_rounds = max_rounds
        self.generate_alternatives = generate_alternatives
        
        # Validate configuration
        if not local_mode and not cort_server_url:
            raise ValueError("cort_server_url must be provided when local_mode is False")
        
        # Try to import CoRT modules from HMS-A2A if available
        self.cort_module = None
        if not local_mode:
            try:
                # Check if path to HMS-A2A is in sys.path
                hms_a2a_path = None
                for path in sys.path:
                    if os.path.basename(path) == "HMS-A2A":
                        hms_a2a_path = path
                        break
                
                if not hms_a2a_path:
                    # Look for HMS-A2A in parent directories
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    while os.path.basename(current_dir) != "HMS-A2A" and os.path.dirname(current_dir) != current_dir:
                        current_dir = os.path.dirname(current_dir)
                    
                    if os.path.basename(current_dir) == "HMS-A2A":
                        hms_a2a_path = current_dir
                
                if hms_a2a_path:
                    # Try to import CoRT modules
                    sys.path.append(hms_a2a_path)
                    self.cort_module = importlib.import_module("graph.cort_react_agent")
                    logger.info(f"Successfully imported HMS-A2A CoRT module from {hms_a2a_path}")
                else:
                    logger.warning("Could not find HMS-A2A in path, falling back to local mode")
                    self.local_mode = True
            except ImportError as e:
                logger.warning(f"Could not import HMS-A2A CoRT module: {e}, falling back to local mode")
                self.local_mode = True
    
    async def apply_cort(self, theorem_spec: Dict[str, Any], 
                         initial_approach: str,
                         instructions: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply Chain of Recursive Thoughts to a theorem proving approach.
        
        Args:
            theorem_spec: The theorem specification to prove
            initial_approach: Initial approach to proving the theorem
            instructions: Optional instructions for guiding the thought process
            
        Returns:
            CoRT result with thinking trace and refined approach
        """
        if not self.local_mode and self.cort_module:
            # Use HMS-A2A CoRT implementation if available
            return await self._apply_external_cort(theorem_spec, initial_approach, instructions)
        else:
            # Use local CoRT implementation
            return self._apply_local_cort(theorem_spec, initial_approach, instructions)
    
    async def _apply_external_cort(self, theorem_spec: Dict[str, Any],
                                  initial_approach: str,
                                  instructions: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply CoRT using the external HMS-A2A implementation.
        
        Args:
            theorem_spec: The theorem specification to prove
            initial_approach: Initial approach to proving the theorem
            instructions: Optional instructions for guiding the thought process
            
        Returns:
            CoRT result with thinking trace and refined approach
        """
        if not self.cort_module:
            raise ValueError("External CoRT module not available")
        
        try:
            # Create CoRT evaluator
            from graph.cort_react_agent import CoRTReactAgent
            
            # Initialize CoRT agent
            cort_agent = CoRTReactAgent(
                use_cort=True,
                max_rounds=self.max_rounds,
                generate_alternatives=self.generate_alternatives
            )
            
            # Prepare input for CoRT
            input_text = f"""
Theorem: {theorem_spec['natural_language']}
Formal Expression: {theorem_spec['formal_expression']}
Assumptions: {', '.join(theorem_spec.get('assumptions', []))}

Initial Approach:
{initial_approach}

{instructions if instructions else ""}
"""
            
            # Apply CoRT
            result = await cort_agent.process(input_text)
            
            # Parse CoRT result
            thinking_trace = []
            for i, round_data in enumerate(result.get("thinking_trace", [])):
                thinking_step = CoRTThinkingStep(
                    step_id=f"cort_round_{i+1}",
                    round=i+1,
                    description=f"Thinking round {i+1}",
                    thinking=round_data.get("thinking", ""),
                    critique=round_data.get("critique", ""),
                    confidence=round_data.get("confidence", 0.0)
                )
                thinking_trace.append(thinking_step)
            
            # Parse alternatives
            alternatives = result.get("alternatives", [])
            
            # Format CoRT result
            cort_result = {
                "final_approach": result.get("final_response", initial_approach),
                "thinking_trace": [
                    {
                        "step_id": step.step_id,
                        "round": step.round,
                        "description": step.description,
                        "thinking": step.thinking,
                        "critique": step.critique,
                        "confidence": step.confidence
                    }
                    for step in thinking_trace
                ],
                "alternatives": alternatives,
                "thinking_rounds": len(thinking_trace)
            }
            
            return cort_result
            
        except Exception as e:
            logger.error(f"Error applying external CoRT: {e}")
            # Fall back to local implementation
            return self._apply_local_cort(theorem_spec, initial_approach, instructions)
    
    def _apply_local_cort(self, theorem_spec: Dict[str, Any],
                         initial_approach: str,
                         instructions: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply CoRT using a local implementation.
        
        Args:
            theorem_spec: The theorem specification to prove
            initial_approach: Initial approach to proving the theorem
            instructions: Optional instructions for guiding the thought process
            
        Returns:
            CoRT result with thinking trace and refined approach
        """
        # This is a simulated CoRT implementation for demonstration
        # In a real implementation, this would use a more sophisticated recursive thinking process
        
        thinking_trace = []
        current_approach = initial_approach
        
        # Determine number of thinking rounds based on theorem complexity
        complexity = theorem_spec.get("metadata", {}).get("difficulty", 3)
        num_rounds = min(self.max_rounds, 1 + complexity // 2)
        
        for round_idx in range(num_rounds):
            # Simulate thinking step
            thinking = self._simulate_thinking(
                theorem_spec=theorem_spec,
                approach=current_approach,
                round_idx=round_idx,
                instructions=instructions
            )
            
            # Simulate critique
            critique = self._simulate_critique(thinking, theorem_spec)
            
            # Update current approach based on critique
            current_approach = self._refine_approach(current_approach, critique)
            
            # Calculate confidence (increasing with rounds)
            confidence = 0.5 + (0.5 * (round_idx + 1) / num_rounds)
            
            # Record thinking step
            thinking_step = CoRTThinkingStep(
                step_id=f"cort_round_{round_idx+1}",
                round=round_idx + 1,
                description=f"Thinking round {round_idx+1}",
                thinking=thinking,
                critique=critique,
                confidence=confidence
            )
            thinking_trace.append(thinking_step)
        
        # Generate alternative approaches
        alternatives = self._generate_alternatives(
            theorem_spec=theorem_spec,
            main_approach=current_approach,
            num_alternatives=self.generate_alternatives
        )
        
        # Format CoRT result
        cort_result = {
            "final_approach": current_approach,
            "thinking_trace": [
                {
                    "step_id": step.step_id,
                    "round": step.round,
                    "description": step.description,
                    "thinking": step.thinking,
                    "critique": step.critique,
                    "confidence": step.confidence
                }
                for step in thinking_trace
            ],
            "alternatives": alternatives,
            "thinking_rounds": num_rounds
        }
        
        return cort_result
    
    def _simulate_thinking(self, theorem_spec: Dict[str, Any], 
                          approach: str, 
                          round_idx: int, 
                          instructions: Optional[str] = None) -> str:
        """
        Simulate a CoRT thinking step.
        
        Args:
            theorem_spec: The theorem specification
            approach: Current approach to the proof
            round_idx: Index of the current thinking round
            instructions: Optional instructions
            
        Returns:
            Simulated thinking text
        """
        # This is a placeholder for a real thinking process
        # In a real implementation, this would use an LLM to generate recursive thoughts
        
        theorem_id = theorem_spec["theorem_id"]
        formal_expression = theorem_spec.get("formal_expression", "")
        natural_language = theorem_spec.get("natural_language", "")
        assumptions = theorem_spec.get("assumptions", [])
        
        thinking_templates = [
            f"For theorem {theorem_id}, I need to first understand the formal expression: {formal_expression}. "
            f"The theorem states that {natural_language}. Let me analyze the assumptions: {', '.join(assumptions)}. "
            f"Given these, my approach is to {approach}. However, I should consider potential issues...",
            
            f"In proving {theorem_id}, I need to carefully examine the steps. "
            f"My current approach is {approach}. "
            f"Let me think about whether this approach addresses all the conditions in the theorem...",
            
            f"For round {round_idx+1}, I'm revisiting theorem {theorem_id}. "
            f"The main challenge is properly formalizing {formal_expression}. "
            f"My current proof strategy is {approach}. "
            f"I should verify whether this approach is rigorous and accounts for edge cases..."
        ]
        
        # Select a template based on round
        template_idx = min(round_idx, len(thinking_templates) - 1)
        thinking = thinking_templates[template_idx]
        
        # Add some variety based on round
        if round_idx == 0:
            thinking += "\n\nI should start by identifying the key components of the theorem."
        elif round_idx == 1:
            thinking += "\n\nI need to check if my proof structure is sound and covers all cases."
        else:
            thinking += "\n\nAt this stage, I should focus on refining the formal aspects and addressing any weaknesses in the proof."
        
        return thinking
    
    def _simulate_critique(self, thinking: str, theorem_spec: Dict[str, Any]) -> str:
        """
        Simulate a CoRT critique step.
        
        Args:
            thinking: The thinking to critique
            theorem_spec: The theorem specification
            
        Returns:
            Simulated critique text
        """
        # This is a placeholder for a real critique process
        # In a real implementation, this would use an LLM to generate critiques
        
        critique_templates = [
            "This thinking is generally on the right track, but it lacks formal rigor in how it approaches the assumptions. "
            "The proof needs to explicitly connect each step to the formal axioms.",
            
            "The approach seems reasonable, but it doesn't adequately address potential edge cases or boundary conditions. "
            "Consider what happens at extreme values or special cases.",
            
            "The logical structure of this proof needs work. There are gaps in the reasoning that need to be filled "
            "with intermediate steps to maintain formal validity."
        ]
        
        # Select a random critique
        critique = random.choice(critique_templates)
        
        # Add some specificity based on theorem attributes
        difficulty = theorem_spec.get("metadata", {}).get("difficulty", 3)
        
        if difficulty <= 2:
            critique += "\n\nOverall, this is a straightforward theorem that should not require an overly complex proof approach."
        elif difficulty >= 4:
            critique += "\n\nThis is a challenging theorem that likely requires more sophisticated proof techniques than initially proposed."
        
        return critique
    
    def _refine_approach(self, approach: str, critique: str) -> str:
        """
        Refine an approach based on critique.
        
        Args:
            approach: Current approach to the proof
            critique: Critique of the current approach
            
        Returns:
            Refined approach
        """
        # This is a placeholder for a real refinement process
        # In a real implementation, this would use an LLM to generate refinements
        
        # Extract key suggestions from critique (simulated)
        suggestion = ""
        if "formal rigor" in critique:
            suggestion = "needs more formal rigor"
        elif "edge cases" in critique:
            suggestion = "address edge cases"
        elif "logical structure" in critique:
            suggestion = "improve logical structure"
        else:
            suggestion = "general improvements"
        
        # Refine the approach
        refined_approach = f"{approach}\n\nRefined based on critique ({suggestion}):\n"
        
        if "formal rigor" in critique:
            refined_approach += "1. Explicitly connect each step to formal axioms\n"
            refined_approach += "2. Use more precise mathematical notation\n"
            refined_approach += "3. Clearly state all assumptions at each step\n"
        elif "edge cases" in critique:
            refined_approach += "1. Consider boundary conditions at extreme values\n"
            refined_approach += "2. Handle special cases separately\n"
            refined_approach += "3. Verify the proof works for all possible inputs\n"
        elif "logical structure" in critique:
            refined_approach += "1. Add intermediate steps to fill reasoning gaps\n"
            refined_approach += "2. Reorganize the proof for better logical flow\n"
            refined_approach += "3. Make deductive steps more explicit\n"
        else:
            refined_approach += "1. Enhance clarity of presentation\n"
            refined_approach += "2. Verify all steps are mathematically sound\n"
            refined_approach += "3. Ensure the proof directly addresses the theorem statement\n"
        
        return refined_approach
    
    def _generate_alternatives(self, theorem_spec: Dict[str, Any],
                              main_approach: str,
                              num_alternatives: int) -> List[Dict[str, Any]]:
        """
        Generate alternative approaches to a theorem proof.
        
        Args:
            theorem_spec: The theorem specification
            main_approach: The main proof approach
            num_alternatives: Number of alternatives to generate
            
        Returns:
            List of alternative approaches
        """
        # This is a placeholder for a real alternative generation process
        # In a real implementation, this would use an LLM to generate alternatives
        
        alternative_templates = [
            {
                "name": "Contradiction approach",
                "description": "Prove by assuming the negation and deriving a contradiction",
                "approach": "I'll prove this theorem by contradiction:\n1. Assume the negation of the theorem\n2. Show this leads to a logical contradiction\n3. Conclude the theorem must be true"
            },
            {
                "name": "Induction approach",
                "description": "Prove using mathematical induction",
                "approach": "I'll use mathematical induction:\n1. Prove the base case\n2. Assume the inductive hypothesis\n3. Prove the inductive step"
            },
            {
                "name": "Constructive approach",
                "description": "Provide a direct construction that proves the theorem",
                "approach": "I'll use a constructive approach:\n1. Directly construct an object that satisfies the theorem\n2. Verify the construction meets all required properties\n3. Show the construction is valid in all cases"
            },
            {
                "name": "Contrapositive approach",
                "description": "Prove using the contrapositive form",
                "approach": "I'll prove the contrapositive:\n1. Convert the theorem to its contrapositive form\n2. Directly prove this equivalent statement\n3. Apply logical equivalence to conclude the original theorem"
            },
            {
                "name": "Case analysis approach",
                "description": "Break into cases and prove each separately",
                "approach": "I'll use case analysis:\n1. Partition the domain into exhaustive cases\n2. Prove the theorem for each case separately\n3. Combine the cases to show the theorem holds generally"
            }
        ]
        
        # Generate alternatives (avoiding the approach similar to main_approach)
        alternatives = []
        available_templates = alternative_templates.copy()
        random.shuffle(available_templates)
        
        # Filter out templates too similar to main approach
        filtered_templates = [
            template for template in available_templates
            if template["name"].lower() not in main_approach.lower()
        ]
        
        # Generate alternatives
        for i in range(min(num_alternatives, len(filtered_templates))):
            template = filtered_templates[i]
            
            # Add some specificity based on theorem attributes
            domain = theorem_spec.get("metadata", {}).get("domain", "economics")
            
            # Create alternative
            alternative = {
                "name": template["name"],
                "description": template["description"],
                "approach": template["approach"],
                "domain_adaptation": f"Adaptation for {domain} domain: "
                                     f"This approach is particularly suitable for economic theorems "
                                     f"because it handles the structural properties common in {domain}."
            }
            
            alternatives.append(alternative)
        
        return alternatives


class CoRTEnhancedAgent(GeneticTheoremProverAgent):
    """
    Extends the genetic theorem prover agent with Chain of Recursive Thoughts capabilities.
    
    This agent uses recursive self-critique and alternative generation to enhance
    its theorem proving abilities.
    """
    
    def __init__(self, agent_id: Optional[str] = None, genotype: Optional[Any] = None,
                specialization: Optional[str] = None, cort_client: Optional[CoRTClient] = None):
        """
        Initialize a CoRT-enhanced genetic theorem prover agent.
        
        Args:
            agent_id: Unique identifier for this agent
            genotype: The genetic makeup of the agent
            specialization: Optional specialization area for this agent
            cort_client: Optional CoRT client for recursive thinking
        """
        super().__init__(agent_id=agent_id, genotype=genotype, specialization=specialization)
        
        # Set up CoRT client
        self.cort_client = cort_client or CoRTClient(
            local_mode=True,
            max_rounds=3,
            generate_alternatives=3
        )
        
        # CoRT-specific metrics
        self.cort_stats = {
            "thinking_rounds_total": 0,
            "alternatives_generated": 0,
            "cort_improvement_rate": 0.0,
            "avg_confidence": 0.0
        }
    
    async def prove_theorem_with_cort(self, theorem_spec: Dict[str, Any]) -> CoRTProofAttempt:
        """
        Attempt to prove a theorem using Chain of Recursive Thoughts.
        
        Args:
            theorem_spec: The theorem specification to prove
            
        Returns:
            CoRT proof attempt result
        """
        start_time = time.time()
        
        # Generate initial approach based on agent's genetic traits
        initial_approach = self._generate_initial_approach(theorem_spec)
        
        # Apply CoRT to refine the approach
        cort_result = await self.cort_client.apply_cort(
            theorem_spec=theorem_spec,
            initial_approach=initial_approach,
            instructions=self._generate_cort_instructions(theorem_spec)
        )
        
        # Extract refined approach
        refined_approach = cort_result.get("final_approach", initial_approach)
        
        # Convert thinking trace
        thinking_trace = []
        for step_data in cort_result.get("thinking_trace", []):
            thinking_step = CoRTThinkingStep(
                step_id=step_data.get("step_id", str(uuid.uuid4())),
                round=step_data.get("round", 0),
                description=step_data.get("description", ""),
                thinking=step_data.get("thinking", ""),
                critique=step_data.get("critique", ""),
                confidence=step_data.get("confidence", 0.0)
            )
            thinking_trace.append(thinking_step)
        
        # Extract alternatives
        alternatives = cort_result.get("alternatives", [])
        
        # Simulate proof steps based on refined approach
        proof_steps = self._simulate_proof_steps_from_approach(refined_approach, theorem_spec)
        
        # Simulate success probability based on approach and agent traits
        exploration = self.genotype.get_trait_value(GeneticTraits.EXPLORATION_TENDENCY)
        formal_strictness = self.genotype.get_trait_value(GeneticTraits.FORMAL_STRICTNESS)
        method_preference = self.genotype.get_trait_value(GeneticTraits.PROOF_METHOD_PREFERENCE)
        
        # CoRT enhances success probability
        cort_boost = 0.2 * len(thinking_trace) / 3.0  # Up to 0.2 boost from CoRT
        cort_improvement_rate = 0.5  # Placeholder for measuring CoRT improvement
        
        # Calculate overall success probability
        success_probability = 0.3 + 0.2 * exploration + 0.3 * formal_strictness + 0.2 * method_preference + cort_boost
        success = random.random() < success_probability
        
        # Calculate resources used
        thinking_rounds = len(thinking_trace)
        resources_used = {
            "memory": 100 + 50 * thinking_rounds,  # MB
            "computation": 80 + 40 * thinking_rounds + 20 * len(alternatives)  # Arbitrary units
        }
        
        end_time = time.time()
        time_taken = end_time - start_time
        
        # Update CoRT stats
        self.cort_stats["thinking_rounds_total"] += thinking_rounds
        self.cort_stats["alternatives_generated"] += len(alternatives)
        self.cort_stats["cort_improvement_rate"] = 0.7 * self.cort_stats["cort_improvement_rate"] + 0.3 * cort_improvement_rate
        
        if thinking_trace:
            avg_confidence = sum(step.confidence for step in thinking_trace) / len(thinking_trace)
            self.cort_stats["avg_confidence"] = 0.7 * self.cort_stats["avg_confidence"] + 0.3 * avg_confidence
        
        # Create and return the proof attempt
        attempt = CoRTProofAttempt(
            theorem_id=theorem_spec["theorem_id"],
            steps=proof_steps,
            success=success,
            resources_used=resources_used,
            time_taken=time_taken,
            thinking_trace=thinking_trace,
            alternatives_considered=alternatives,
            thinking_rounds=thinking_rounds
        )
        
        self.proof_attempts.append(attempt)
        if success:
            self.proof_successes += 1
            
        return attempt
    
    def _generate_initial_approach(self, theorem_spec: Dict[str, Any]) -> str:
        """
        Generate an initial proof approach based on the agent's genetic traits.
        
        Args:
            theorem_spec: The theorem specification
            
        Returns:
            Initial proof approach
        """
        # Get relevant genetic traits
        method_preference = self.genotype.get_trait_value(GeneticTraits.PROOF_METHOD_PREFERENCE)
        formal_strictness = self.genotype.get_trait_value(GeneticTraits.FORMAL_STRICTNESS)
        decomposition_depth = self.genotype.get_trait_value(GeneticTraits.DECOMPOSITION_DEPTH)
        exploration = self.genotype.get_trait_value(GeneticTraits.EXPLORATION_TENDENCY)
        
        # Determine preferred proof method based on method_preference
        proof_methods = [
            "direct proof",
            "proof by contradiction",
            "proof by induction",
            "proof by contrapositive",
            "constructive proof"
        ]
        
        # Select method based on genetic preferences
        method_index = min(len(proof_methods) - 1, int(method_preference * len(proof_methods)))
        preferred_method = proof_methods[method_index]
        
        # Build approach
        approach = f"I'll approach this theorem using a {preferred_method}.\n\n"
        
        # Add details based on other traits
        if formal_strictness > 0.7:
            approach += "The proof will be highly formal and rigorous, carefully applying axioms and definitions at each step.\n"
        elif formal_strictness > 0.4:
            approach += "The proof will maintain a balance between formality and readability, with clear justification for each step.\n"
        else:
            approach += "The proof will focus on intuitive understanding, with formal details provided where necessary.\n"
        
        if decomposition_depth > 0.7:
            approach += "I'll break the theorem into several smaller components and prove each separately.\n"
        elif decomposition_depth > 0.4:
            approach += "I'll identify the main components of the theorem and structure the proof accordingly.\n"
        else:
            approach += "I'll approach the theorem as a whole, addressing the key claim directly.\n"
        
        if exploration > 0.7:
            approach += "I'll explore multiple potential approaches to find the most elegant solution.\n"
        elif exploration > 0.4:
            approach += "I'll consider alternative approaches if the main strategy encounters difficulties.\n"
        else:
            approach += "I'll focus on a single, direct approach to the proof.\n"
        
        # Add specialization-specific considerations
        if self.specialization:
            approach += f"\nAs a {self.specialization} specialist, I'll particularly focus on "
            
            if self.specialization == "axiom":
                approach += "careful selection of axioms and precise formal definitions."
            elif self.specialization == "decomposition":
                approach += "effective breaking down of the theorem into manageable lemmas."
            elif self.specialization == "proof_strategy":
                approach += "selecting the optimal proof strategy for this theorem type."
            elif self.specialization == "counterexample":
                approach += "testing boundary conditions to ensure the proof is robust."
            elif self.specialization == "verification":
                approach += "verifying each step with formal rigor."
            elif self.specialization == "generalization":
                approach += "identifying patterns that could lead to more general results."
            else:
                approach += f"applying my {self.specialization} expertise to the proof."
        
        return approach
    
    def _generate_cort_instructions(self, theorem_spec: Dict[str, Any]) -> str:
        """
        Generate instructions for the CoRT process based on theorem and agent traits.
        
        Args:
            theorem_spec: The theorem specification
            
        Returns:
            Instructions for CoRT
        """
        # Get relevant genetic traits
        verification_thoroughness = self.genotype.get_trait_value(GeneticTraits.VERIFICATION_THOROUGHNESS)
        formal_strictness = self.genotype.get_trait_value(GeneticTraits.FORMAL_STRICTNESS)
        
        # Basic instructions
        instructions = "Instructions for recursive thinking:\n"
        
        # Add trait-based instructions
        if verification_thoroughness > 0.7:
            instructions += "- Carefully verify each step of the proof for logical soundness\n"
            instructions += "- Check for potential counterexamples or edge cases\n"
        
        if formal_strictness > 0.7:
            instructions += "- Maintain strict formal rigor throughout the proof\n"
            instructions += "- Explicitly cite relevant axioms or theorems for each step\n"
        
        # Add theorem-specific instructions
        domain = theorem_spec.get("metadata", {}).get("domain", "economics")
        difficulty = theorem_spec.get("metadata", {}).get("difficulty", 3)
        
        instructions += f"\nThis is a theorem in the domain of {domain} with difficulty level {difficulty}.\n"
        
        if difficulty >= 4:
            instructions += "This is a challenging theorem that likely requires deep analysis and careful proof structuring.\n"
        
        # Add specialization-specific instructions
        if self.specialization:
            instructions += f"\nAs a {self.specialization} specialist, focus particularly on "
            
            if self.specialization == "axiom":
                instructions += "identifying and applying the most relevant axioms."
            elif self.specialization == "decomposition":
                instructions += "effective decomposition of complex parts into lemmas."
            elif self.specialization == "proof_strategy":
                instructions += "evaluating and selecting the optimal proof strategy."
            elif self.specialization == "counterexample":
                instructions += "identifying potential counterexamples or edge cases."
            elif self.specialization == "verification":
                instructions += "rigorous verification of each proof step."
            elif self.specialization == "generalization":
                instructions += "opportunities to generalize the approach or results."
            else:
                instructions += f"applying {self.specialization} expertise."
        
        return instructions
    
    def _simulate_proof_steps_from_approach(self, approach: str, 
                                           theorem_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Simulate proof steps based on a refined approach.
        
        Args:
            approach: The refined proof approach
            theorem_spec: The theorem specification
            
        Returns:
            List of proof steps
        """
        # This is a placeholder for a real proof step generation process
        # In a real implementation, this would use the approach to guide formal proof construction
        
        steps = []
        
        # Extract approach type from the approach text
        approach_type = "direct"  # Default
        if "contradiction" in approach.lower():
            approach_type = "contradiction"
        elif "induction" in approach.lower():
            approach_type = "induction"
        elif "contrapositive" in approach.lower():
            approach_type = "contrapositive"
        elif "constructive" in approach.lower():
            approach_type = "constructive"
        
        # Generate steps based on approach type
        if approach_type == "direct":
            steps = [
                {
                    "step": 1,
                    "description": "Formalize the theorem statement",
                    "expression": f"Theorem: {theorem_spec.get('formal_expression', '')}",
                    "justification": "Direct translation of the theorem statement"
                },
                {
                    "step": 2,
                    "description": "Apply relevant axioms and definitions",
                    "expression": "Apply axioms to initial expression",
                    "justification": f"Using assumptions: {', '.join(theorem_spec.get('assumptions', []))}"
                },
                {
                    "step": 3,
                    "description": "Derive intermediate result",
                    "expression": "Intermediate expression derived from axioms",
                    "justification": "Logical deduction from previous step"
                },
                {
                    "step": 4,
                    "description": "Complete the proof",
                    "expression": "Final expression equivalent to theorem statement",
                    "justification": "Logical transformation of intermediate result"
                }
            ]
        elif approach_type == "contradiction":
            steps = [
                {
                    "step": 1,
                    "description": "Assume the negation of the theorem",
                    "expression": f"Assume not({theorem_spec.get('formal_expression', '')})",
                    "justification": "Setup for proof by contradiction"
                },
                {
                    "step": 2,
                    "description": "Apply relevant axioms to the negation",
                    "expression": "Derived expression from negation",
                    "justification": f"Using assumptions: {', '.join(theorem_spec.get('assumptions', []))}"
                },
                {
                    "step": 3,
                    "description": "Derive a contradiction",
                    "expression": "Expression contradicting axioms or itself",
                    "justification": "Logical consequence of the negation"
                },
                {
                    "step": 4,
                    "description": "Conclude the theorem must be true",
                    "expression": theorem_spec.get('formal_expression', ''),
                    "justification": "Since the negation leads to a contradiction"
                }
            ]
        elif approach_type == "induction":
            steps = [
                {
                    "step": 1,
                    "description": "Establish the base case",
                    "expression": "Base case expression",
                    "justification": "Direct verification for the simplest case"
                },
                {
                    "step": 2,
                    "description": "State the inductive hypothesis",
                    "expression": "Assume theorem holds for arbitrary k",
                    "justification": "Setup for inductive step"
                },
                {
                    "step": 3,
                    "description": "Prove the inductive step",
                    "expression": "Show theorem holds for k+1",
                    "justification": "Using the inductive hypothesis and axioms"
                },
                {
                    "step": 4,
                    "description": "Conclude by induction",
                    "expression": theorem_spec.get('formal_expression', ''),
                    "justification": "By the principle of mathematical induction"
                }
            ]
        else:
            # Generic steps for other approach types
            steps = [
                {
                    "step": 1,
                    "description": f"Set up {approach_type} proof",
                    "expression": "Initial formulation",
                    "justification": f"Starting point for {approach_type} approach"
                },
                {
                    "step": 2,
                    "description": "Apply key transformation",
                    "expression": "Transformed expression",
                    "justification": "Using relevant theorems and axioms"
                },
                {
                    "step": 3,
                    "description": "Derive conclusion",
                    "expression": "Final expression",
                    "justification": "Logical consequence of previous steps"
                }
            ]
        
        # Adjust steps based on specific elements in the approach
        if "decomposition" in approach.lower() or "breaking down" in approach.lower():
            # Add decomposition steps
            decomposition_step = {
                "step": 2,  # Insert after initial step
                "description": "Decompose the theorem into components",
                "expression": "Split into multiple related lemmas",
                "justification": "Breaking down complex theorem for manageability"
            }
            
            # Insert decomposition step
            steps.insert(1, decomposition_step)
            
            # Adjust subsequent step numbers
            for i in range(2, len(steps)):
                steps[i]["step"] = i + 1
        
        return steps
    
    async def prove_theorem(self, theorem_spec: Dict[str, Any]) -> ProofAttempt:
        """
        Override the base prove_theorem method to use CoRT capabilities.
        
        Args:
            theorem_spec: The theorem specification to prove
            
        Returns:
            Proof attempt result
        """
        # Use CoRT enhanced proving
        return await self.prove_theorem_with_cort(theorem_spec)


# Factory function to create CoRT-enhanced agents
def create_cort_enhanced_agent(specialization: str, 
                              agent_id: Optional[str] = None,
                              genotype: Optional[Any] = None,
                              cort_client: Optional[CoRTClient] = None) -> CoRTEnhancedAgent:
    """
    Create a CoRT-enhanced agent with the specified specialization.
    
    Args:
        specialization: The type of specialized agent to create
        agent_id: Optional ID for the agent
        genotype: Optional genotype for the agent
        cort_client: Optional CoRT client for recursive thinking
        
    Returns:
        A CoRT-enhanced genetic theorem prover agent
    """
    # Create a plain specialized agent (this is needed to get the specialization-specific genotype)
    from ..agents.specialized_agents import create_specialized_agent
    base_agent = create_specialized_agent(specialization, agent_id, genotype)
    
    # Create a CoRT-enhanced agent with the same ID and genotype
    cort_agent = CoRTEnhancedAgent(
        agent_id=base_agent.agent_id,
        genotype=base_agent.genotype,
        specialization=specialization,
        cort_client=cort_client
    )
    
    return cort_agent