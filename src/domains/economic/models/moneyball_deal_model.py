"""
Moneyball Deal Model - Neural Network Value Optimization Framework

This module implements the core functionality of the Moneyball Deal Model,
a comprehensive framework for identifying, evaluating, and executing high-value
deals across multiple contexts in the HMS ecosystem.

The model uses a neural network-like approach to identify opportunities and optimize
value creation across all participants, ensuring win-win outcomes.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
import json
import datetime
import networkx as nx
from scipy.optimize import minimize
import re
import math # Import math for log function

# =============================================================================
# Core Data Structures (Representing the 5 Steps + Deal)
# =============================================================================

@dataclass
class Intent:
    """Step 1: Representation of a problem or opportunity intent."""
    id: str
    description: str
    intent_vector: np.ndarray # Multi-dimensional representation
    value_dimensions: List[str] # Key dimensions for value creation
    constraints: Dict[str, Any] # Budget, timeline, regulatory, etc.
    context: Dict[str, Any] # Domain, environment, etc.

    @property
    def dimension_count(self) -> int:
        """Return the number of value dimensions."""
        return len(self.value_dimensions)

@dataclass
class Solution:
    """Step 2: Representation of a potential solution to an intent."""
    id: str
    description: str
    solution_vector: np.ndarray # Multi-dimensional representation
    potential_value: float # Estimated base value
    intent_id: str
    implementation_difficulty: float # Scale 0-1
    time_horizon: int # Estimated time in months/periods

    def __lt__(self, other):
        """Enable sorting of solutions by potential value."""
        return self.potential_value < other.potential_value

@dataclass
class Stakeholder:
    """Step 3: Representation of a deal stakeholder/player."""
    id: str
    name: str
    type: str  # e.g., government, corporate, ngo, civilian, agency_sub_entity
    capabilities: Dict[str, float] # Key skills/resources offered (scale 0-1)
    value_preferences: Dict[str, float] # Weights for different value dimensions
    risk_tolerance: float # Scale 0-1
    participation_costs: Dict[str, float] # Estimated costs (e.g., financial, time)
    expected_returns: Dict[str, float] # Desired returns by dimension

@dataclass
class FinancingStructure:
    """Step 4: Representation of a deal financing structure."""
    cost_allocation: Dict[str, float] # Cost distribution by stakeholder ID
    returns_allocation: Dict[str, Dict[str, float]] # Returns by stakeholder ID and value dimension
    timeline: Dict[str, Dict[str, float]] # Phased funding/payouts (Stakeholder -> Period -> Amount)
    conditions: Dict[str, Any] # Contingencies, triggers
    risk_sharing: Dict[str, float] # Risk distribution by stakeholder ID

    @property
    def total_cost(self) -> float:
        """Calculate the total estimated cost of the deal."""
        return sum(self.cost_allocation.values())

    @property
    def total_returns(self) -> float:
        """Calculate the total estimated returns from the deal."""
        total = 0.0
        for stakeholder_returns in self.returns_allocation.values():
            total += sum(stakeholder_returns.values())
        return total

@dataclass
class ExecutionPlan:
    """Step 5: Representation of a deal execution plan (Expertise/Delivery)."""
    responsibility_matrix: Dict[str, Dict[str, float]] # RACI-like matrix (Stakeholder -> Task -> Responsibility Score)
    timeline: Dict[int, List[str]] # Task allocation by period (Period -> List of Tasks)
    milestones: Dict[str, Dict[str, Any]] # Key milestones with verification criteria
    expertise_allocation: Dict[str, Dict[str, float]] # Allocation of expertise (Task -> Stakeholder -> Expertise Score)

    @property
    def duration(self) -> int:
        """Calculate the total duration of the execution plan based on timeline keys."""
        return max(self.timeline.keys()) if self.timeline else 0

@dataclass
class Deal:
    """Comprehensive representation of a structured deal."""
    id: str
    name: str
    intent: Intent
    solution: Solution
    stakeholders: Dict[str, Stakeholder] # Dictionary mapping ID to Stakeholder object
    financing: FinancingStructure
    execution: ExecutionPlan
    status: str # e.g., draft, proposed, active, completed, failed
    creation_date: datetime.datetime
    update_date: datetime.datetime
    metrics: Dict[str, Any] # Calculated metrics like DVF, Win-Win status, etc.

    @property
    def dvf(self) -> float:
        """Calculate the Deal Value Function score."""
        # This is a simplified version - full implementation would be more complex
        if not self.metrics or 'dvf' not in self.metrics:
             # Attempt calculation if not pre-calculated
             try:
                 return calculate_dvf(self.intent, self.solution, self.stakeholders, self.financing, self.execution)
             except Exception:
                 return 0.0 # Default if calculation fails
        return self.metrics.get('dvf', 0.0)

# =============================================================================
# Neural Network Value Optimization Model (Conceptual Placeholder)
# =============================================================================

class DealNeuralNetwork:
    """Conceptual Neural network-like structure for deal value optimization."""

    def __init__(self, dimensions: int, hidden_layers: List[int] = None):
        """
        Initialize the conceptual deal neural network.
        Args:
            dimensions: Number of value dimensions.
            hidden_layers: List of hidden layer sizes.
        """
        self.dimensions = dimensions
        # Placeholder: In a real implementation, this would define network layers,
        # weights, activation functions, and training mechanisms.
        print(f"Initialized conceptual DealNeuralNetwork with {dimensions} dimensions.")

    def evaluate_deal_potential(self, deal_features: np.ndarray) -> float:
        """ Placeholder for evaluating deal potential using the network. """
        # Placeholder: Returns a dummy value. Real implementation needed.
        return np.random.rand() * 100 # Dummy value

    def optimize_structure(self, deal: Deal) -> Deal:
        """ Placeholder for optimizing deal structure (e.g., financing). """
        # Placeholder: Returns the deal unmodified. Real implementation needed.
        print(f"Conceptual optimization applied to Deal {deal.id}")
        return deal

# =============================================================================
# Deal Value Function (DVF) Implementation
# =============================================================================

def calculate_deal_value_function(
    intent: Intent,
    solution: Solution,
    stakeholders: Dict[str, Stakeholder],
    financing: FinancingStructure,
    execution: ExecutionPlan,
    # Add other relevant factors as needed
) -> float:
    """
    Calculate the overall Deal Value Function (DVF) score for a deal.
    DVF = Σᵢ (Vᵢ ⋅ Wᵢ ⋅ Pᵢ ⋅ Cᵢ ⋅ Mᵢ) - TC
    Where:
    V = Intrinsic Value of dimension i
    W = Weight of dimension i
    P = Probability of success for dimension i
    C = Confidence factor for dimension i
    M = Margin of safety for dimension i
    TC = Transaction Costs

    Args:
        intent: The deal's intent.
        solution: The proposed solution.
        stakeholders: The participating stakeholders.
        financing: The financing structure.
        execution: The execution plan.

    Returns:
        Calculated DVF score.
    """
    # --- Placeholder Logic ---
    # A real implementation needs sophisticated models to derive these values.
    # We'll use simplified estimates based on provided data for now.

    # 1. Estimate Intrinsic Values (Vi) per dimension - Highly simplified
    intrinsic_values: Dict[str, float] = {
        dim: solution.potential_value / intent.dimension_count # Distribute potential value
        for dim in intent.value_dimensions
    }

    # 2. Define Weights (Wi) - Assume equal weight for simplicity
    num_dims = intent.dimension_count
    weights: Dict[str, float] = {
        dim: 1.0 / num_dims if num_dims > 0 else 0
        for dim in intent.value_dimensions
    }

    # 3. Estimate Probabilities (Pi) - Simplified based on difficulty/risk
    base_prob = 1.0 - (solution.implementation_difficulty * 0.5) # Base success prob
    probabilities: Dict[str, float] = {
        dim: base_prob * np.random.uniform(0.8, 1.0) # Add some randomness
        for dim in intent.value_dimensions
    }

    # 4. Define Confidence Factors (Ci) - Assume moderate confidence
    confidence_factors: Dict[str, float] = {
        dim: 0.75 for dim in intent.value_dimensions
    }

    # 5. Define Margin of Safety (Mi) - Buffett factor (e.g., 70%)
    margin_factors: Dict[str, float] = {
        dim: 0.7 for dim in intent.value_dimensions
    }

    # 6. Estimate Transaction Costs (TC) - Simplified
    transaction_costs = financing.total_cost * 0.05 # Assume 5% of financing cost

    # --- DVF Calculation ---
    dvf = 0.0
    for dimension in intent.value_dimensions:
        if dimension in intrinsic_values and dimension in weights and \
           dimension in probabilities and dimension in confidence_factors and \
           dimension in margin_factors:
            dimension_value = (
                intrinsic_values[dimension] *
                weights[dimension] *
                probabilities[dimension] *
                confidence_factors[dimension] *
                margin_factors[dimension]
            )
            dvf += dimension_value

    dvf -= transaction_costs

    # Adjust for network effects (requires network analysis - simplified here)
    # dvf += calculate_network_value_contribution(deal) # Placeholder

    return dvf


# =============================================================================
# Win-Win Calculation
# =============================================================================

def calculate_stakeholder_dvf(
    stakeholder: Stakeholder,
    deal_intent: Intent,
    deal_solution: Solution,
    stakeholder_costs: float,
    stakeholder_returns: Dict[str, float]
    # Add other necessary factors like probabilities, confidence, etc.
) -> float:
    """
    Calculate the DVF for a specific stakeholder.
    This is analogous to the overall DVF but uses stakeholder-specific
    preferences as weights and considers their allocated costs and returns.
    Ensuring DVF(Stakeholder) > 0 for all participants is the 'win-win' check.

    Args:
        stakeholder: The stakeholder object.
        deal_intent: The intent of the deal.
        deal_solution: The solution being implemented.
        stakeholder_costs: The stakeholder's allocated costs.
        stakeholder_returns: The stakeholder's allocated returns by dimension.

    Returns:
        Stakeholder-specific DVF score.
    """
    # --- Placeholder Logic ---
    # Use stakeholder's preferences as weights (Wi_s)
    # Use stakeholder's allocated returns as intrinsic value (Vi_s)

    # 1. Intrinsic Values = Allocated Returns for this stakeholder
    intrinsic_values = stakeholder_returns

    # 2. Weights = Stakeholder Preferences (normalized)
    total_preference = sum(stakeholder.value_preferences.values())
    weights = {
        dim: (pref / total_preference if total_preference > 0 else 0)
        for dim, pref in stakeholder.value_preferences.items()
    }
    # Ensure weights cover all return dimensions
    for dim in intrinsic_values:
        if dim not in weights:
             weights[dim] = 1.0 / len(intrinsic_values) if intrinsic_values else 0


    # 3. Probabilities (Pi_s) - Assume same as overall deal for simplicity
    base_prob = 1.0 - (deal_solution.implementation_difficulty * 0.5)
    probabilities = {
        dim: base_prob * np.random.uniform(0.8, 1.0)
        for dim in intrinsic_values
    }

    # 4. Confidence Factors (Ci_s) - Assume moderate confidence
    confidence_factors = {
        dim: 0.75 for dim in intrinsic_values
    }

    # 5. Margin of Safety (Mi_s) - Buffett factor (e.g., 70%)
    margin_factors = {
        dim: 0.7 for dim in intrinsic_values
    }

    # 6. Transaction Costs = Stakeholder Costs
    transaction_costs = stakeholder_costs

    # --- DVF Calculation for Stakeholder ---
    dvf_s = 0.0
    for dimension in intrinsic_values:
         # Check if all necessary components exist for the dimension
        if all(d in map_dict for d in [dimension] for map_dict in [weights, probabilities, confidence_factors, margin_factors]):
            dimension_value = (
                intrinsic_values[dimension] *
                weights[dimension] *
                probabilities[dimension] *
                confidence_factors[dimension] *
                margin_factors[dimension]
            )
            dvf_s += dimension_value

    dvf_s -= transaction_costs

    # Apply specific adjustments based on stakeholder type if needed
    # Example: log_std_deviation_adjustment for civilians
    if stakeholder.type == 'civilian':
        # Placeholder: Needs proper implementation of the formula
        # log_std_dev_adj = calculate_log_std_deviation_adjustment(...)
        # dvf_s += log_std_dev_adj
        pass


    return dvf_s


def is_win_win_deal(deal: Deal) -> bool:
    """
    Check if a deal satisfies the win-win condition (DVF > 0) for all stakeholders.

    Args:
        deal: The deal object.

    Returns:
        True if the deal is win-win, False otherwise.
    """
    if not deal.stakeholders or not deal.financing:
        print("Warning: Cannot check win-win without stakeholders and financing.")
        return False

    for stakeholder_id, stakeholder in deal.stakeholders.items():
        costs = deal.financing.cost_allocation.get(stakeholder_id, 0.0)
        returns_by_dim = deal.financing.returns_allocation.get(stakeholder_id, {})

        # Calculate stakeholder-specific DVF
        stakeholder_dvf = calculate_stakeholder_dvf(
            stakeholder,
            deal.intent,
            deal.solution,
            costs,
            returns_by_dim
        )

        # If any stakeholder has non-positive DVF, it's not win-win
        if stakeholder_dvf <= 0:
            print(f"Deal not win-win: Stakeholder {stakeholder_id} has DVF <= 0 ({stakeholder_dvf:.2f})")
            return False

    print("Deal satisfies win-win condition for all stakeholders.")
    return True

def calculate_log_std_deviation_adjustment(
    value: float,
    weighted_recursive_avg: float,
    mean_deviation_superset: float
) -> float:
    """
    Calculates the log std deviation adjustment component for win-win checks,
    particularly for civilian benefit evaluation.

    win = set of conditions X applied as log std deviation from mean of
    weighted recursive avg based on mean of deviation from log of super set avg
    premium delimited over timeframe as weight

    Args:
        value: The current value being evaluated (e.g., civilian benefit).
        weighted_recursive_avg: Weighted average of prior period values.
        mean_deviation_superset: Mean deviation from the average of a larger reference set.

    Returns:
        The calculated adjustment value. Returns 0 if inputs are invalid.
    """
    if mean_deviation_superset <= 0:
        print("Warning: Mean deviation of superset is non-positive, cannot calculate log adjustment.")
        return 0.0

    # Deviation from weighted recursive average
    deviation = abs(value - weighted_recursive_avg)

    # Avoid log(0) issues
    if deviation <= 0:
        # If value matches the average exactly, deviation is 0. Log is undefined.
        # Return 0 adjustment or handle as per specific domain logic.
        return 0.0
    if mean_deviation_superset <= 1: # log(x) for x<=1 is <=0, might not be desired denominator
         # Handle cases where the mean deviation is small, potentially log adjusted
         pass # Keep it as is for now, might need domain specific logic

    try:
        # log(|value - weighted_recursive_avg|)
        log_deviation = math.log(deviation)

        # log(mean_of_deviation_from_superset_avg)
        log_mean_deviation_superset = math.log(mean_deviation_superset)

        # Avoid division by zero if log_mean_deviation_superset is 0 (i.e., mean_deviation_superset is 1)
        if abs(log_mean_deviation_superset) < 1e-9:
             print("Warning: Log of mean deviation is close to zero, potential division by zero.")
             # Handle this case - perhaps return 0 or a large value depending on context
             return 0.0


        log_std_value = log_deviation / log_mean_deviation_superset
        return log_std_value

    except ValueError as e:
        print(f"Error calculating log std deviation adjustment: {e}")
        return 0.0
    except ZeroDivisionError:
         print("Error calculating log std deviation adjustment: Division by zero.")
         return 0.0


# =============================================================================
# Step 1: Intent Analysis Functions
# =============================================================================

def extract_components(problem_statement: str) -> List[str]:
    """Extract key components/phrases from a problem statement."""
    # Improved splitting and basic cleanup
    separators = r'[.,;!?\n]+'
    components = [p.strip().lower() for p in re.split(separators, problem_statement) if p.strip()]
    # Placeholder: Add NLP for entity/keyword extraction if needed
    return components

def map_to_dimensions(components: List[str], context: Dict[str, Any]) -> np.ndarray:
    """Map components to a predefined N-dimensional vector space."""
    dimensions = context.get('dimensions', ['economic', 'social', 'environmental', 'political', 'technical', 'legal', 'security'])
    intent_vector = np.zeros(len(dimensions))
    # Placeholder: Use embeddings or more sophisticated mapping
    for i, dim in enumerate(dimensions):
        for comp in components:
            if dim in comp: # Simple keyword check
                intent_vector[i] += 1.0
    norm = np.linalg.norm(intent_vector)
    return intent_vector / norm if norm > 0 else intent_vector

def identify_value_dimensions(intent_vector: np.ndarray, context: Dict[str, Any]) -> List[str]:
    """Identify relevant value dimensions based on the intent vector."""
    dimensions = context.get('dimensions', ['economic', 'social', 'environmental', 'political', 'technical', 'legal', 'security'])
    return [dimensions[i] for i, val in enumerate(intent_vector) if val > 0.1] # Threshold

def extract_constraints(problem_statement: str, scope: Dict[str, Any]) -> Dict[str, Any]:
    """Extract constraints from problem statement and scope."""
    constraints = { # Defaults
        'budget': scope.get('budget', float('inf')),
        'timeline': scope.get('timeline', 12), # months
        'geographical': scope.get('geographical', []),
        'regulatory': scope.get('regulatory', []),
        'technological': scope.get('technological', [])
    }
    # Placeholder: Use NLP to find constraints like "must cost less than $X", "within Y months"
    return constraints

def define_intent(problem_statement: str, context: Dict[str, Any], scope: Dict[str, Any]) -> Intent:
    """Define an intent object from a problem statement."""
    components = extract_components(problem_statement)
    intent_vector = map_to_dimensions(components, context)
    value_dimensions = identify_value_dimensions(intent_vector, context)
    constraints = extract_constraints(problem_statement, scope)
    intent_id = f"INT-{hash(problem_statement) % 10000:04d}"
    return Intent(
        id=intent_id,
        description=problem_statement,
        intent_vector=intent_vector,
        value_dimensions=value_dimensions,
        constraints=constraints,
        context=context
    )

# =============================================================================
# Step 2: Solution Matching Functions
# =============================================================================

def generate_candidates(intent_vector: np.ndarray, solution_database: List[Dict] = None) -> List[Dict]:
    """Generate or retrieve candidate solutions based on the intent vector."""
    # Placeholder: Needs a real solution database/generation mechanism
    if solution_database is None:
        solution_database = [{
            'id': f'SOL-{i:04d}', 'vector': np.random.rand(len(intent_vector)),
            'description': f'Generated Solution {i}', 'difficulty': np.random.uniform(0.2, 0.8),
            'timeline': np.random.randint(3, 36)} for i in range(10)]

    candidates = []
    norm_intent = np.linalg.norm(intent_vector)
    if norm_intent == 0: return [] # Avoid division by zero

    for solution in solution_database:
        norm_sol = np.linalg.norm(solution['vector'])
        if norm_sol == 0: continue # Skip zero vectors
        similarity = np.dot(intent_vector, solution['vector']) / (norm_intent * norm_sol)
        if similarity > 0.3: # Lowered threshold for more candidates
            solution['similarity'] = similarity
            candidates.append(solution)
    return candidates

def apply_constraints_to_solutions(candidates: List[Dict], constraints: Dict[str, Any]) -> List[Dict]:
    """Filter candidate solutions based on constraints."""
    # Renamed for clarity
    filtered = []
    timeline_constraint = constraints.get('timeline', float('inf'))
    for cand in candidates:
        if cand.get('timeline', 0) > timeline_constraint:
            continue
        # Placeholder: Add budget, regulatory checks etc.
        filtered.append(cand)
    return filtered

def calculate_potential_value(candidate: Dict, value_dimensions: List[str]) -> float:
    """Calculate potential value of a solution candidate."""
    # Simplified value model - needs refinement
    base_value = candidate.get('similarity', 0.0) * 100
    difficulty_factor = (1 - candidate.get('difficulty', 0.5) * 0.5) # Higher difficulty reduces value
    # Dimension alignment (placeholder)
    dim_alignment_factor = np.random.uniform(0.7, 1.0) # Assume some alignment
    return base_value * difficulty_factor * dim_alignment_factor

def match_solutions(intent: Intent, solution_database: List[Dict] = None) -> List[Solution]:
    """Match solutions to an intent, rank them by potential value."""
    candidates = generate_candidates(intent.intent_vector, solution_database)
    filtered = apply_constraints_to_solutions(candidates, intent.constraints)
    solutions = []
    for cand in filtered:
         potential_value = calculate_potential_value(cand, intent.value_dimensions)
         solutions.append(Solution(
             id=cand['id'], description=cand['description'], solution_vector=cand['vector'],
             potential_value=potential_value, intent_id=intent.id,
             implementation_difficulty=cand.get('difficulty', 0.5),
             time_horizon=cand.get('timeline', 12)))
    solutions.sort(reverse=True) # Sort high to low potential value
    return solutions

# =============================================================================
# Step 3: Stakeholder Mapping Functions
# =============================================================================

def identify_required_capabilities(solution_vector: np.ndarray, context: Dict[str, Any]) -> Dict[str, float]:
    """Identify expertise required based on solution vector."""
    # Placeholder: Needs mapping from solution dimensions to expertise areas
    expertise_areas = context.get('expertise_list', ['technical', 'financial', 'legal', 'operational', 'domain_specific'])
    req_expertise = {exp: np.random.uniform(0, 1) for exp in expertise_areas} # Dummy importance
    # Normalize
    total = sum(req_expertise.values())
    if total > 0: req_expertise = {k: v / total for k, v in req_expertise.items()}
    return req_expertise


def map_expertise_to_stakeholders(
    required_expertise: Dict[str, float],
    stakeholder_matrix: Dict[str, Stakeholder]
) -> Dict[str, Dict[str, float]]: # Returns {sh_id: {expertise_area: score}}
    """Map required expertise to stakeholder capabilities (simplified)."""
    expertise_map = {}
    for sh_id, sh in stakeholder_matrix.items():
        expertise_scores = {}
        # Simplified: Assume capabilities loosely map to expertise
        for exp_area, importance in required_expertise.items():
             # Heuristic: Average related capabilities or use a dummy score
             related_cap_score = sh.capabilities.get(exp_area, np.random.uniform(0.1, 0.7)) # Fallback to random
             expertise_scores[exp_area] = related_cap_score
        expertise_map[sh_id] = expertise_scores
    return expertise_map

def identify_expertise_gaps(
    required_expertise: Dict[str, float],
    expertise_map: Dict[str, Dict[str, float]]
) -> Dict[str, float]: # Returns {expertise_area: gap_score}
    """Identify gaps where required expertise is not sufficiently covered."""
    gaps = {}
    for exp_area, req_score in required_expertise.items():
        max_coverage = 0.0
        for sh_scores in expertise_map.values():
             max_coverage = max(max_coverage, sh_scores.get(exp_area, 0.0))
        # If requirement is high but coverage is low, identify gap
        if req_score > 0.5 and max_coverage < 0.6: # Example thresholds
             gaps[exp_area] = req_score - max_coverage
    print(f"Identified Expertise Gaps: {gaps}")
    return gaps

def find_additional_stakeholders_for_gaps( # Renamed for clarity
    expertise_gaps: Dict[str, float],
    external_stakeholder_db: List[Stakeholder] # Assume access to a larger DB
) -> Dict[str, Stakeholder]:
    """Find external stakeholders to fill expertise gaps."""
    # Placeholder: Needs search/matching logic against external DB
    additional_stakeholders = {}
    needed_expertise = list(expertise_gaps.keys())
    if not needed_expertise: return {}

    # Simple strategy: find best match for the biggest gap
    biggest_gap_area = max(expertise_gaps, key=expertise_gaps.get)
    best_match = None
    max_score = -1

    for sh in external_stakeholder_db:
         score = sh.capabilities.get(biggest_gap_area, 0.0)
         if score > max_score:
             max_score = score
             best_match = sh

    if best_match and max_score > 0.6: # Threshold for competence
         additional_stakeholders[best_match.id] = best_match
         print(f"Found additional stakeholder {best_match.id} for gap: {biggest_gap_area}")


    return additional_stakeholders


def update_stakeholder_matrix_with_additional( # Renamed for clarity
    stakeholder_matrix: Dict[str, Stakeholder],
    additional_stakeholders: Dict[str, Stakeholder]
) -> Dict[str, Stakeholder]:
    """Update stakeholder matrix with additional experts/partners."""
    updated_matrix = stakeholder_matrix.copy()
    updated_matrix.update(additional_stakeholders)
    return updated_matrix

def create_responsibility_matrix(
    tasks: List[str], # Assume tasks derived from solution/execution plan
    expertise_map: Dict[str, Dict[str, float]], # Stakeholder expertise scores
    stakeholder_matrix: Dict[str, Stakeholder]
) -> Dict[str, Dict[str, float]]: # Returns {sh_id: {task: responsibility_score}}
    """Create a responsibility matrix (simplified)."""
    # Placeholder: Assigns responsibility based on max expertise for the task's *implied* area
    responsibility_matrix = {sh_id: {} for sh_id in stakeholder_matrix}
    if not tasks: return responsibility_matrix
    expertise_areas = list(list(expertise_map.values())[0].keys()) if expertise_map else []
    if not expertise_areas: return responsibility_matrix # Need expertise areas defined

    for task in tasks:
         # Implied expertise area for task (simplified mapping)
         implied_area = expertise_areas[hash(task) % len(expertise_areas)]
         best_stakeholder = None
         max_expertise = -1
         # Find stakeholder with highest expertise in the implied area
         for sh_id, expertise_scores in expertise_map.items():
             score = expertise_scores.get(implied_area, 0.0)
             if score > max_expertise:
                 max_expertise = score
                 best_stakeholder = sh_id
         # Assign responsibility score (e.g., 1.0 for primary, 0.2 for support)
         if best_stakeholder:
             for sh_id in stakeholder_matrix:
                 if sh_id == best_stakeholder:
                      responsibility_matrix[sh_id][task] = 1.0 # Primary
                 else:
                      # Assign lower score if they have *some* relevant expertise
                      responsibility_matrix[sh_id][task] = 0.2 if expertise_map[sh_id].get(implied_area, 0) > 0.3 else 0.0


    return responsibility_matrix


def develop_timeline_and_milestones(
    solution: Solution,
    tasks: List[str] # Assume tasks derived from solution
) -> Tuple[Dict[int, List[str]], Dict[str, Dict[str, Any]]]: # Timeline, Milestones
    """Develop execution timeline and key milestones."""
    # Placeholder: Simple linear timeline and milestones per task
    timeline = {}
    milestones = {}
    duration = solution.time_horizon
    if not tasks or duration <= 0: return timeline, milestones

    tasks_per_period = math.ceil(len(tasks) / duration)

    for i, task in enumerate(tasks):
         period = i // tasks_per_period
         if period not in timeline: timeline[period] = []
         timeline[period].append(task)
         # Create a milestone for each task completion (simplified)
         milestones[f"Milestone_{i+1}_{task}"] = {
             "task": task,
             "period": period,
             "description": f"Complete task: {task}",
             "verification": "TBD"
         }

    # Ensure timeline covers the full duration
    final_period = (len(tasks) -1) // tasks_per_period
    for p in range(final_period + 1, duration):
        if p not in timeline: timeline[p] = []


    return timeline, milestones


def plan_delivery(
    solution: Solution,
    stakeholder_matrix: Dict[str, Stakeholder],
    intent: Intent, # Pass intent for context
    external_stakeholder_db: List[Stakeholder] = None # Optional external DB
) -> Tuple[ExecutionPlan, Dict[str, Stakeholder]]: # Return plan and potentially updated stakeholder matrix
    """Plan the delivery, including finding experts if needed."""
    print("Planning Delivery...")
    if external_stakeholder_db is None: external_stakeholder_db = []

    req_expertise = identify_required_expertise(solution.solution_vector, intent.context)
    expertise_map = map_expertise_to_stakeholders(req_expertise, stakeholder_matrix)
    gaps = identify_expertise_gaps(req_expertise, expertise_map)

    current_stakeholders = stakeholder_matrix.copy()
    if gaps:
        print("Attempting to find additional stakeholders for expertise gaps...")
        additional_sh = find_additional_stakeholders_for_gaps(gaps, external_stakeholder_db)
        if additional_sh:
            current_stakeholders = update_stakeholder_matrix_with_additional(current_stakeholders, additional_sh)
            # Remap expertise with the new stakeholder set
            expertise_map = map_expertise_to_stakeholders(req_expertise, current_stakeholders)
        else:
            print("Warning: Could not find additional stakeholders to fill all expertise gaps.")

    # Define tasks (placeholder based on solution description)
    tasks = [f"Task_{i+1}_{word}" for i, word in enumerate(solution.description.split()[:5])] # Simple task derivation
    if not tasks: tasks = ["Execute Solution"]


    resp_matrix = create_responsibility_matrix(tasks, expertise_map, current_stakeholders)
    exec_timeline, exec_milestones = develop_timeline_and_milestones(solution, tasks)

    exec_plan = ExecutionPlan(
        responsibility_matrix=resp_matrix,
        timeline=exec_timeline,
        milestones=exec_milestones,
        expertise_allocation=expertise_map # Expertise scores for the final stakeholder set
    )
    return exec_plan, current_stakeholders


# =============================================================================
# Deal Creation and Evaluation
# =============================================================================

def create_deal(
    intent: Intent,
    solution: Solution,
    stakeholders: Dict[str, Stakeholder],
    financing: FinancingStructure,
    execution: ExecutionPlan
) -> Deal:
    """Create a final Deal object from all components."""
    deal_id = f"DEAL-{hash(intent.id + solution.id) % 10000:04d}"
    deal_name = f"Deal for: {intent.description[:40]}"
    deal_name = deal_name + "..." if len(intent.description) > 40 else deal_name

    # Calculate final metrics for the deal object
    metrics = {}
    try:
        metrics['dvf'] = calculate_deal_value_function(intent, solution, stakeholders, financing, execution)
        metrics['win_win_status'] = is_win_win_deal(Deal( # Temporarily create Deal for check
             id="", name="", intent=intent, solution=solution, stakeholders=stakeholders,
             financing=financing, execution=execution, status="", creation_date=datetime.datetime.now(),
             update_date=datetime.datetime.now(), metrics={})) # Pass empty metrics
    except Exception as e:
        print(f"Error calculating metrics during deal creation: {e}")
        metrics['dvf'] = 0.0
        metrics['win_win_status'] = False

    metrics['implementation_complexity'] = solution.implementation_difficulty
    metrics['execution_duration'] = execution.duration

    return Deal(
        id=deal_id, name=deal_name, intent=intent, solution=solution,
        stakeholders=stakeholders, financing=financing, execution=execution,
        status="draft", creation_date=datetime.datetime.now(),
        update_date=datetime.datetime.now(), metrics=metrics
    )


# =============================================================================
# Monitoring and Network Analysis (Placeholders - require more context)
# =============================================================================

def monitor_deal_performance(deal: Deal, actual_data: Dict, time_period: int) -> Dict:
    """Monitor deal performance against projections."""
    # Placeholder: Needs detailed implementation based on available data
    print(f"Monitoring performance for Deal {deal.id} at period {time_period}")
    # Compare deal.execution.milestones, deal.financing.timeline vs actual_data
    return {
        "performance_metrics": {"overall": 0.85, "timeline": 0.9}, # Dummy data
        "variance_analysis": {"cost_variance": -500, "return_variance": 1000}, # Dummy data
        "recommended_adjustments": ["Increase resource allocation to Task 3"] # Dummy data
    }

def build_deal_network(deals: List[Deal]) -> nx.DiGraph:
    """Build a network graph of deals and stakeholders."""
    G = nx.DiGraph()
    # Add nodes for deals and stakeholders
    # Add edges representing relationships (participation, value flow)
    # Placeholder: Needs implementation
    print(f"Building deal network for {len(deals)} deals...")
    return G

def analyze_network_effects(G: nx.DiGraph, degree: int = 2) -> Dict:
    """Analyze N-degree network effects."""
    # Placeholder: Calculate direct and indirect value flows
    print(f"Analyzing network effects up to degree {degree}...")
    return {"node1": {"direct": 100, "indirect": 50}} # Dummy data

def calculate_network_value(network_effects: Dict) -> Dict:
     """Calculate total network value for each node."""
     # Placeholder: Sum direct and indirect effects
     print("Calculating total network value...")
     return {"node1": 150} # Dummy data

# =============================================================================
# Main Orchestration Function
# =============================================================================

def create_moneyball_deal(
    problem_statement: str,
    context: Dict[str, Any],
    scope: Dict[str, Any],
    stakeholder_database: List[Stakeholder],
    solution_database: List[Dict] = None,
    external_stakeholder_db: List[Stakeholder] = None # Add external DB
) -> Optional[Deal]:
    """
    Orchestrates the creation of a Moneyball deal following the 5 steps.

    Args:
        problem_statement: Problem or opportunity description.
        context: Contextual information (e.g., domain, dimensions).
        scope: Scope parameters (e.g., budget, timeline).
        stakeholder_database: List of potential primary stakeholders.
        solution_database: Optional database of predefined solutions.
        external_stakeholder_db: Optional larger database for finding experts.

    Returns:
        A Deal object if successful, None otherwise.
    """
    print("\n===== Starting Moneyball Deal Creation Process =====")
    try:
        # Step 1: Define Intent
        print("\n--- Step 1: Defining Intent ---")
        intent = define_intent(problem_statement, context, scope)
        print(f"Intent defined: {intent.id} - Value Dimensions: {intent.value_dimensions}")

        # Step 2: Match Solutions
        print("\n--- Step 2: Matching Solutions ---")
        solutions = match_solutions(intent, solution_database)
        if not solutions:
            print("Error: No matching solutions found.")
            return None
        solution = solutions[0] # Select best solution
        print(f"Best Solution selected: {solution.id} (Potential Value: {solution.potential_value:.2f})")

        # Step 3: Map Stakeholders
        print("\n--- Step 3: Mapping Stakeholders ---")
        stakeholders = map_stakeholders(solution, intent, stakeholder_database)
        if not stakeholders:
            print("Error: No suitable stakeholders identified.")
            return None
        print(f"Mapped {len(stakeholders)} stakeholders.")

        # Step 4: Optimize Financing
        print("\n--- Step 4: Optimizing Financing ---")
        # Recalculate value map for the final stakeholder set before optimizing financing
        stakeholder_cap_map = map_capabilities_to_stakeholders(
             identify_required_capabilities(solution.solution_vector, intent.context),
             list(stakeholders.values()) # Use the final list
        )
        stakeholder_value_map = calculate_stakeholder_value_contribution(
             stakeholder_cap_map, solution, intent
        )
        financing = optimize_financing(solution, stakeholders, intent, stakeholder_value_map)
        print(f"Financing optimized. Total Cost: {financing.total_cost:.2f}, Total Returns: {financing.total_returns:.2f}")

        # Step 5: Plan Delivery
        print("\n--- Step 5: Planning Delivery ---")
        execution_plan, final_stakeholders = plan_delivery(solution, stakeholders, intent, external_stakeholder_db)
        # If plan_delivery added stakeholders, financing might need recalculation - Skipped for now for simplicity
        if len(final_stakeholders) != len(stakeholders):
             print(f"Note: Stakeholder matrix updated during delivery planning to {len(final_stakeholders)} stakeholders.")
             # Ideally, re-run financing optimization here if stakeholders changed significantly
             stakeholders = final_stakeholders # Use the potentially updated list

        print(f"Execution Plan created. Duration: {execution_plan.duration} periods.")

        # Create Final Deal Object
        print("\n--- Creating Final Deal Object ---")
        deal = create_deal(intent, solution, stakeholders, financing, execution_plan)
        print(f"Deal {deal.id} created successfully.")
        print(f"  Deal DVF: {deal.dvf:.2f}")
        print(f"  Win-Win Status: {deal.metrics.get('win_win_status', 'N/A')}")

        return deal

    except Exception as e:
        print(f"Error during Moneyball deal creation: {e}")
        import traceback
        traceback.print_exc()
        return None


def evaluate_deal(deal: Deal) -> Optional[Dict[str, Any]]:
    """
    Evaluate a deal's characteristics and potential using updated logic.

    Args:
        deal: The Deal object.

    Returns:
        Dictionary of evaluation results or None if deal is invalid.
    """
    if not deal: return None
    print(f"\n===== Evaluating Deal: {deal.id} =====")

    # Recalculate metrics to ensure consistency
    dvf = calculate_deal_value_function(deal.intent, deal.solution, deal.stakeholders, deal.financing, deal.execution)
    win_win = is_win_win_deal(deal)

    evaluation = {
        "deal_id": deal.id,
        "deal_name": deal.name,
        "dvf": dvf,
        "win_win_status": win_win,
        "stakeholder_analysis": {},
        "network_potential": 0.0, # Placeholder
        "risk_assessment": {
            "implementation_risk": deal.solution.implementation_difficulty,
            "timeline_risk": min(1.0, deal.execution.duration / 24.0) if deal.execution.duration > 0 else 0,
            "stakeholder_risk": 0.0, # Calculated below
            "financial_risk": 0.0 # Calculated below
        }
    }

    # Stakeholder Analysis
    total_net_value = 0
    stakeholder_net_values = []
    for sh_id, stakeholder in deal.stakeholders.items():
        costs = deal.financing.cost_allocation.get(sh_id, 0.0)
        returns_by_dim = deal.financing.returns_allocation.get(sh_id, {})
        returns = sum(returns_by_dim.values())
        net_value = returns - costs
        roi = (net_value / costs) if costs > 0 else float('inf') if net_value > 0 else 0
        stakeholder_dvf = calculate_stakeholder_dvf(stakeholder, deal.intent, deal.solution, costs, returns_by_dim)

        evaluation["stakeholder_analysis"][sh_id] = {
            "name": stakeholder.name,
            "type": stakeholder.type,
            "costs": costs,
            "returns": returns,
            "net_value": net_value,
            "roi": roi,
            "calculated_dvf": stakeholder_dvf
        }
        total_net_value += net_value
        stakeholder_net_values.append(net_value)


    # Stakeholder Risk (Gini coefficient of net value distribution)
    if len(stakeholder_net_values) > 1:
        stakeholder_net_values.sort()
        n = len(stakeholder_net_values)
        index_sum = sum((2 * i + 1 - n) * val for i, val in enumerate(stakeholder_net_values))
        total_sum = sum(stakeholder_net_values)
        gini = index_sum / (n * total_sum) if total_sum != 0 else 0
        evaluation["risk_assessment"]["stakeholder_risk"] = abs(gini)


    # Financial Risk (e.g., Cost vs Potential Value ratio)
    financial_risk = deal.financing.total_cost / (deal.solution.potential_value + 1e-6) # Add epsilon
    evaluation["risk_assessment"]["financial_risk"] = min(1.0, financial_risk) # Cap at 1

    # Overall Risk
    weights = {"implementation": 0.4, "timeline": 0.2, "stakeholder": 0.2, "financial": 0.2}
    overall_risk = (evaluation["risk_assessment"]["implementation_risk"] * weights["implementation"] +
                    evaluation["risk_assessment"]["timeline_risk"] * weights["timeline"] +
                    evaluation["risk_assessment"]["stakeholder_risk"] * weights["stakeholder"] +
                    evaluation["risk_assessment"]["financial_risk"] * weights["financial"])
    evaluation["risk_assessment"]["overall_risk"] = overall_risk

    print(f"Evaluation Complete. DVF: {dvf:.2f}, Win-Win: {win_win}, Overall Risk: {overall_risk:.2f}")
    return evaluation


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("===== Moneyball Deal Model Example =====")

    # --- Dummy Data Setup ---
    stakeholder_db = [
        Stakeholder(id="GOV-001", name="Dept of Energy", type="government",
                    capabilities={"technical": 0.7, "financial": 0.9, "regulatory": 0.9},
                    value_preferences={"economic": 0.3, "environmental": 0.5, "security": 0.2},
                    risk_tolerance=0.6, participation_costs={"financial": 1000}, expected_returns={"economic": 500, "security": 500}),
        Stakeholder(id="CORP-001", name="Energy Corp", type="corporate",
                    capabilities={"technical": 0.9, "financial": 0.8, "operational": 0.7},
                    value_preferences={"economic": 0.8, "environmental": 0.2},
                    risk_tolerance=0.7, participation_costs={"financial": 2000}, expected_returns={"economic": 3000}),
        Stakeholder(id="NGO-001", name="Green Future", type="ngo",
                    capabilities={"network": 0.9, "social": 0.8, "environmental_advocacy": 0.9},
                    value_preferences={"social": 0.4, "environmental": 0.6},
                    risk_tolerance=0.4, participation_costs={"time": 500}, expected_returns={"social": 200, "environmental": 300}),
         Stakeholder(id="CIV-001", name="Local Community Group", type="civilian",
                    capabilities={"social": 0.7, "network": 0.6},
                    value_preferences={"social": 0.7, "economic": 0.3},
                    risk_tolerance=0.3, participation_costs={"time": 100}, expected_returns={"social": 100, "economic": 50})
    ]
    external_db = [ # For filling gaps
         Stakeholder(id="EXPERT-001", name="Legal Experts Inc", type="service_provider",
                    capabilities={"legal": 0.95, "regulatory": 0.8}, value_preferences={"economic": 1.0},
                    risk_tolerance=0.8, participation_costs={"financial": 500}, expected_returns={"economic": 750})
    ]

    # --- Deal Creation ---
    prob_statement = "Develop regional solar power infrastructure to boost local economy and meet environmental targets."
    context_info = {
        "dimensions": ["economic", "social", "environmental", "technical", "political", "legal"],
        "capabilities_list": ["technical", "financial", "regulatory", "operational", "network", "social", "legal", "political"],
        "expertise_list": ['technical', 'financial', 'legal', 'operational', 'domain_specific', 'social_impact']
    }
    scope_info = {"budget": 10000, "timeline": 18} # 18 months

    deal = create_moneyball_deal(
        problem_statement=prob_statement,
        context=context_info,
        scope=scope_info,
        stakeholder_database=stakeholder_db,
        external_stakeholder_db=external_db
        # solution_database could be provided here if available
    )

    # --- Deal Evaluation ---
    if deal:
        evaluation_results = evaluate_deal(deal)
        if evaluation_results:
             print("\n--- Deal Evaluation Results ---")
             print(json.dumps(evaluation_results, indent=2, default=str)) # Use default=str for datetime

             # --- Example: Monitoring ---
             print("\n--- Example Monitoring ---")
             # Dummy actual data for period 6
             actual_performance_data = {
                 "GOV-001": {"costs": 300, "returns": 200},
                 "CORP-001": {"costs": 1000, "returns": 1800},
                 "NGO-001": {"costs": 50, "returns": 100},
                 "CIV-001": {"costs": 10, "returns": 60},
                 "completed_milestones": ["Milestone_1_Task_1_Develop", "Milestone_2_Task_2_regional"]
             }
             monitoring_results = monitor_deal_performance(deal, actual_performance_data, time_period=6)
             print(json.dumps(monitoring_results, indent=2))
        else:
             print("Failed to evaluate the created deal.")

    else:
        print("Deal creation failed.")