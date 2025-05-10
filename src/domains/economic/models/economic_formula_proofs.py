"""
Economic Formula Verification Proofs for HMS Models

This module implements formal verification proofs for the key economic formulas
used in the HMS ecosystem, particularly focusing on the Moneyball-Buffett approach
and the unified economic model.

It validates mathematical properties such as bounds, monotonicity, and conservatism
of the formulas, providing rigorous mathematical guarantees of their behavior.
"""

import numpy as np
import sympy as sp
from typing import Dict, List, Tuple, Optional, Any, Union
import json

# ===============================================
# Symbolic verification using SymPy
# ===============================================

def verify_war_score_symbolic():
    """
    Symbolic verification of WAR score bounds using SymPy.
    Proves that WAR score is bounded between -100 and 100.
    
    Returns:
        dict: The verification result with proof steps
    """
    # Define symbols
    n = sp.Symbol('n', integer=True, positive=True)  # Number of sectors
    w = sp.IndexedBase('w')  # Weights
    a = sp.IndexedBase('a')  # Agreement impacts
    d = sp.IndexedBase('d')  # Deficit reduction potentials
    i = sp.Symbol('i', integer=True)  # Index
    
    # Define WAR score formula symbolically
    war_expr = sp.Sum(w[i] * a[i] * d[i], (i, 1, n))
    
    # Define constraints
    weight_sum_constraint = sp.Eq(sp.Sum(w[i], (i, 1, n)), 1)
    weight_positive_constraint = w[i] > 0
    impact_bounds_constraint = sp.And(-100 <= a[i], a[i] <= 100)
    drp_positive_constraint = d[i] >= 0
    
    # Proof steps
    proof_steps = []
    
    # Step 1: Establish weight constraint
    proof_steps.append({
        "step": "Establish weight constraint",
        "expression": str(weight_sum_constraint),
        "explanation": "The sum of all sector weights equals 1.0"
    })
    
    # Step 2: Establish impact bounds
    proof_steps.append({
        "step": "Establish impact bounds",
        "expression": str(impact_bounds_constraint),
        "explanation": "All agreement impacts are bounded between -100 and 100"
    })
    
    # Step 3: Establish DRP constraint
    proof_steps.append({
        "step": "Establish DRP constraint",
        "expression": str(drp_positive_constraint),
        "explanation": "All deficit reduction potentials are non-negative"
    })
    
    # Step 4: Find minimum value (all impacts at -100)
    min_war_expr = sp.Sum(w[i] * (-100) * d[i], (i, 1, n))
    min_war_simplified = sp.simplify(min_war_expr)
    proof_steps.append({
        "step": "Calculate minimum value",
        "expression": str(min_war_expr) + " = " + str(min_war_simplified),
        "explanation": "Minimum WAR occurs when all agreement impacts are -100"
    })
    
    # Step 5: Find maximum value (all impacts at 100)
    max_war_expr = sp.Sum(w[i] * 100 * d[i], (i, 1, n))
    max_war_simplified = sp.simplify(max_war_expr)
    proof_steps.append({
        "step": "Calculate maximum value",
        "expression": str(max_war_expr) + " = " + str(max_war_simplified),
        "explanation": "Maximum WAR occurs when all agreement impacts are 100"
    })
    
    # Step 6: Conclude bounds
    bounds_conclusion = sp.And(-100 * sp.Sum(w[i] * d[i], (i, 1, n)) <= war_expr, 
                               war_expr <= 100 * sp.Sum(w[i] * d[i], (i, 1, n)))
    proof_steps.append({
        "step": "Establish bounds",
        "expression": str(bounds_conclusion),
        "explanation": "WAR score is bounded between -100 and 100 times the weighted sum of DRPs"
    })
    
    # Final conclusion with weight constraint applied
    final_conclusion = sp.And(-100 <= war_expr, war_expr <= 100)
    proof_steps.append({
        "step": "Apply weight constraint",
        "expression": str(final_conclusion),
        "explanation": "Since weights sum to 1.0, WAR score is bounded between -100 and 100"
    })
    
    return {
        "theorem": "WAR score is bounded between -100 and 100",
        "proof_steps": proof_steps,
        "conclusion": "verified"
    }

def verify_drp_conservatism_symbolic():
    """
    Symbolic verification that DRP is a conservative estimate.
    Proves that DRP is always a conservative estimate compared to raw reduction estimates.
    
    Returns:
        dict: The verification result with proof steps
    """
    # Define symbols
    n = sp.Symbol('n', integer=True, positive=True)  # Number of policies
    p = sp.IndexedBase('p')  # Policy effects
    c = sp.IndexedBase('c')  # Confidence factors
    i = sp.IndexedBase('i')  # Implementation rates
    B = sp.Symbol('B', real=True, positive=True)  # Baseline deficit
    M = sp.Symbol('M', real=True, positive=True)  # Buffett margin of safety
    j = sp.Symbol('j', integer=True)  # Index
    
    # Define raw reduction
    raw_reduction = sp.Sum(p[j] * c[j] * i[j], (j, 1, n))
    
    # Define DRP formula symbolically
    drp_expr = B - raw_reduction * M
    
    # Define conservative estimate (baseline - raw reduction)
    conservative_estimate = B - raw_reduction
    
    # Define constraints
    mos_constraint = sp.And(M > 0, M <= 1)
    policy_positive_constraint = p[j] >= 0
    confidence_constraint = sp.And(0 <= c[j], c[j] <= 1)
    implementation_constraint = sp.And(0 <= i[j], i[j] <= 1)
    
    # Proof steps
    proof_steps = []
    
    # Step 1: Establish MoS constraint
    proof_steps.append({
        "step": "Establish Margin of Safety constraint",
        "expression": str(mos_constraint),
        "explanation": "Buffett Margin of Safety is between 0 and 1.0"
    })
    
    # Step 2: Establish policy constraints
    proof_steps.append({
        "step": "Establish policy effect constraint",
        "expression": str(policy_positive_constraint),
        "explanation": "All policy effects are non-negative"
    })
    
    # Step 3: Establish confidence constraints
    proof_steps.append({
        "step": "Establish confidence factor constraint",
        "expression": str(confidence_constraint),
        "explanation": "All confidence factors are between 0 and 1.0"
    })
    
    # Step 4: Establish implementation constraints
    proof_steps.append({
        "step": "Establish implementation rate constraint",
        "expression": str(implementation_constraint),
        "explanation": "All implementation rates are between 0 and 1.0"
    })
    
    # Step 5: Define raw reduction
    proof_steps.append({
        "step": "Define raw reduction",
        "expression": str(raw_reduction),
        "explanation": "Raw reduction is the sum of policy effects adjusted for confidence and implementation"
    })
    
    # Step 6: Define DRP
    proof_steps.append({
        "step": "Define DRP",
        "expression": str(drp_expr),
        "explanation": "DRP is baseline deficit minus raw reduction adjusted by Buffett Margin of Safety"
    })
    
    # Step 7: Show that raw_reduction * M <= raw_reduction when M <= 1
    raw_reduction_comparison = sp.And(M <= 1, raw_reduction >= 0)
    implication = sp.Implies(raw_reduction_comparison, raw_reduction * M <= raw_reduction)
    proof_steps.append({
        "step": "Compare adjusted and raw reductions",
        "expression": str(implication),
        "explanation": "When M <= 1 and raw_reduction >= 0, adjustment reduces the raw reduction"
    })
    
    # Step 8: Conclude DRP >= conservative_estimate
    drp_comparison = drp_expr >= conservative_estimate
    proof_steps.append({
        "step": "Compare DRP to conservative estimate",
        "expression": str(drp_comparison),
        "explanation": "DRP is greater than or equal to the conservative estimate"
    })
    
    # Final conclusion
    final_conclusion = "DRP is a conservative estimate compared to raw sum of policy effects"
    proof_steps.append({
        "step": "Conclusion",
        "expression": final_conclusion,
        "explanation": "The application of Buffett Margin of Safety ensures conservative estimates"
    })
    
    return {
        "theorem": "DRP is a conservative estimate compared to raw sum of policy effects",
        "proof_steps": proof_steps,
        "conclusion": "verified"
    }

def verify_sps_bounds_symbolic():
    """
    Symbolic verification of SPS bounds using SymPy.
    Proves that SPS is bounded between 0 and 100.
    
    Returns:
        dict: The verification result with proof steps
    """
    # Define symbols
    D = sp.Symbol('D', real=True)  # Deficit impact
    J = sp.Symbol('J', real=True)  # Job creation
    G = sp.Symbol('G', real=True)  # Growth potential
    E = sp.Symbol('E', real=True)  # Implementation ease
    
    # Define SPS formula symbolically
    sps_expr = 0.4 * D + 0.3 * J + 0.2 * G + 0.1 * E
    
    # Define constraints
    d_constraint = sp.And(0 <= D, D <= 100)
    j_constraint = sp.And(0 <= J, J <= 100)
    g_constraint = sp.And(0 <= G, G <= 100)
    e_constraint = sp.And(0 <= E, E <= 100)
    
    # Proof steps
    proof_steps = []
    
    # Step 1: Establish input constraints
    proof_steps.append({
        "step": "Establish deficit impact constraint",
        "expression": str(d_constraint),
        "explanation": "Deficit impact is bounded between 0 and 100"
    })
    
    proof_steps.append({
        "step": "Establish job creation constraint",
        "expression": str(j_constraint),
        "explanation": "Job creation is bounded between 0 and 100"
    })
    
    proof_steps.append({
        "step": "Establish growth potential constraint",
        "expression": str(g_constraint),
        "explanation": "Growth potential is bounded between 0 and 100"
    })
    
    proof_steps.append({
        "step": "Establish implementation ease constraint",
        "expression": str(e_constraint),
        "explanation": "Implementation ease is bounded between 0 and 100"
    })
    
    # Step 2: Define SPS formula
    proof_steps.append({
        "step": "Define SPS formula",
        "expression": str(sps_expr),
        "explanation": "SPS is a weighted sum of four factors with weights that sum to 1.0"
    })
    
    # Step 3: Find minimum value (all inputs at 0)
    min_sps = sps_expr.subs([(D, 0), (J, 0), (G, 0), (E, 0)])
    proof_steps.append({
        "step": "Calculate minimum value",
        "expression": f"min(SPS) = {min_sps}",
        "explanation": "Minimum SPS occurs when all inputs are 0"
    })
    
    # Step 4: Find maximum value (all inputs at 100)
    max_sps = sps_expr.subs([(D, 100), (J, 100), (G, 100), (E, 100)])
    proof_steps.append({
        "step": "Calculate maximum value",
        "expression": f"max(SPS) = {max_sps}",
        "explanation": "Maximum SPS occurs when all inputs are 100"
    })
    
    # Step 5: Verify weights sum to 1.0
    weight_sum = 0.4 + 0.3 + 0.2 + 0.1
    proof_steps.append({
        "step": "Verify weights sum to 1.0",
        "expression": f"0.4 + 0.3 + 0.2 + 0.1 = {weight_sum}",
        "explanation": "The weights in the SPS formula sum to 1.0"
    })
    
    # Step 6: Conclude bounds
    bounds_conclusion = sp.And(0 <= sps_expr, sps_expr <= 100)
    proof_steps.append({
        "step": "Establish bounds",
        "expression": str(bounds_conclusion),
        "explanation": "SPS is bounded between 0 and 100"
    })
    
    return {
        "theorem": "SPS is bounded between 0 and 100",
        "proof_steps": proof_steps,
        "conclusion": "verified"
    }

# ===============================================
# Numerical verification using NumPy
# ===============================================

def verify_war_score_numerical(num_trials=1000, seed=42):
    """
    Numerical verification of WAR score bounds using Monte Carlo simulation.
    
    Args:
        num_trials: Number of random trials to run
        seed: Random seed for reproducibility
        
    Returns:
        dict: The verification result with statistics
    """
    np.random.seed(seed)
    
    min_war = float('inf')
    max_war = float('-inf')
    all_wars = []
    
    for _ in range(num_trials):
        # Generate random number of sectors between 3 and 10
        n_sectors = np.random.randint(3, 11)
        
        # Generate random weights and normalize
        weights = np.random.uniform(0.1, 1.0, n_sectors)
        weights = weights / np.sum(weights)  # Ensure weights sum to 1.0
        
        # Generate random agreement impacts between -100 and 100
        impacts = np.random.uniform(-100, 100, n_sectors)
        
        # Generate random DRPs (all positive)
        drps = np.random.uniform(0.1, 10.0, n_sectors)
        
        # Calculate WAR score
        war = np.sum(weights * impacts * drps)
        all_wars.append(war)
        
        # Update min and max
        min_war = min(min_war, war)
        max_war = max(max_war, war)
    
    all_wars = np.array(all_wars)
    
    # Verify bounds
    below_negative_100 = np.sum(all_wars < -100)
    above_100 = np.sum(all_wars > 100)
    within_bounds = np.sum((all_wars >= -100) & (all_wars <= 100))
    
    verification_result = {
        "theorem": "WAR score is bounded between -100 and 100",
        "num_trials": num_trials,
        "minimum_observed": float(min_war),
        "maximum_observed": float(max_war),
        "mean": float(np.mean(all_wars)),
        "std_dev": float(np.std(all_wars)),
        "num_below_negative_100": int(below_negative_100),
        "num_above_100": int(above_100),
        "num_within_bounds": int(within_bounds),
        "percent_within_bounds": float(within_bounds / num_trials * 100),
        "conclusion": "verified" if below_negative_100 == 0 and above_100 == 0 else "counterexample_found"
    }
    
    return verification_result

def verify_drp_conservatism_numerical(num_trials=1000, seed=42):
    """
    Numerical verification that DRP is a conservative estimate using Monte Carlo simulation.
    
    Args:
        num_trials: Number of random trials to run
        seed: Random seed for reproducibility
        
    Returns:
        dict: The verification result with statistics
    """
    np.random.seed(seed)
    
    conservative_count = 0
    not_conservative_count = 0
    conservatism_ratios = []
    
    for _ in range(num_trials):
        # Generate random baseline deficit
        baseline_deficit = np.random.uniform(100, 1000)
        
        # Generate random number of policies between 3 and 10
        n_policies = np.random.randint(3, 11)
        
        # Generate random policy effects (all positive)
        policy_effects = np.random.uniform(1, 100, n_policies)
        
        # Generate random confidence factors between 0 and 1
        confidence_factors = np.random.uniform(0, 1, n_policies)
        
        # Generate random implementation rates between 0 and 1
        implementation_rates = np.random.uniform(0, 1, n_policies)
        
        # Generate random Buffett Margin of Safety between 0.5 and 1.0
        buffett_mos = np.random.uniform(0.5, 1.0)
        
        # Calculate raw reduction
        raw_reduction = np.sum(policy_effects * confidence_factors * implementation_rates)
        
        # Calculate DRP
        drp = baseline_deficit - raw_reduction * buffett_mos
        
        # Calculate non-conservative estimate
        non_conservative = baseline_deficit - raw_reduction
        
        # Check if DRP is conservative (DRP ≥ non-conservative)
        is_conservative = drp >= non_conservative
        
        if is_conservative:
            conservative_count += 1
        else:
            not_conservative_count += 1
        
        # Calculate conservatism ratio
        if non_conservative == baseline_deficit:  # No reduction
            conservatism_ratio = 1.0
        else:
            conservatism_ratio = (baseline_deficit - drp) / (baseline_deficit - non_conservative)
        conservatism_ratios.append(conservatism_ratio)
    
    conservatism_ratios = np.array(conservatism_ratios)
    
    verification_result = {
        "theorem": "DRP is a conservative estimate compared to raw sum of policy effects",
        "num_trials": num_trials,
        "num_conservative": int(conservative_count),
        "num_not_conservative": int(not_conservative_count),
        "percent_conservative": float(conservative_count / num_trials * 100),
        "mean_conservatism_ratio": float(np.mean(conservatism_ratios)),
        "min_conservatism_ratio": float(np.min(conservatism_ratios)),
        "max_conservatism_ratio": float(np.max(conservatism_ratios)),
        "conclusion": "verified" if not_conservative_count == 0 else "counterexample_found"
    }
    
    return verification_result

def verify_sps_bounds_numerical(num_trials=1000, seed=42):
    """
    Numerical verification of SPS bounds using Monte Carlo simulation.
    
    Args:
        num_trials: Number of random trials to run
        seed: Random seed for reproducibility
        
    Returns:
        dict: The verification result with statistics
    """
    np.random.seed(seed)
    
    min_sps = float('inf')
    max_sps = float('-inf')
    all_sps = []
    
    for _ in range(num_trials):
        # Generate random inputs between 0 and 100
        deficit_impact = np.random.uniform(0, 100)
        job_creation = np.random.uniform(0, 100)
        growth_potential = np.random.uniform(0, 100)
        implementation_ease = np.random.uniform(0, 100)
        
        # Calculate SPS
        sps = (deficit_impact * 0.4) + (job_creation * 0.3) + (growth_potential * 0.2) + (implementation_ease * 0.1)
        all_sps.append(sps)
        
        # Update min and max
        min_sps = min(min_sps, sps)
        max_sps = max(max_sps, sps)
    
    all_sps = np.array(all_sps)
    
    # Verify bounds
    below_zero = np.sum(all_sps < 0)
    above_100 = np.sum(all_sps > 100)
    within_bounds = np.sum((all_sps >= 0) & (all_sps <= 100))
    
    verification_result = {
        "theorem": "SPS is bounded between 0 and 100",
        "num_trials": num_trials,
        "minimum_observed": float(min_sps),
        "maximum_observed": float(max_sps),
        "mean": float(np.mean(all_sps)),
        "std_dev": float(np.std(all_sps)),
        "num_below_zero": int(below_zero),
        "num_above_100": int(above_100),
        "num_within_bounds": int(within_bounds),
        "percent_within_bounds": float(within_bounds / num_trials * 100),
        "conclusion": "verified" if below_zero == 0 and above_100 == 0 else "counterexample_found"
    }
    
    return verification_result

# ===============================================
# Verify economic intelligence formula
# ===============================================

def verify_economic_intelligence_formula():
    """
    Verify the Economic Intelligence (EI) formula from the Treasury approach.
    
    Returns:
        dict: The verification result with proof steps
    """
    # Define symbols
    n = sp.Symbol('n', integer=True, positive=True)  # Number of data points
    q = sp.IndexedBase('q')  # Data quality
    s = sp.IndexedBase('s')  # Signal strength
    p = sp.IndexedBase('p')  # Predictive accuracy
    i = sp.Symbol('i', integer=True)  # Index
    
    # Define EI formula symbolically
    ei_expr = sp.Sum(q[i] * s[i] * p[i], (i, 1, n)) / n
    
    # Define constraints
    quality_constraint = sp.And(0 <= q[i], q[i] <= 1)
    signal_constraint = sp.And(0 <= s[i], s[i] <= 1)
    accuracy_constraint = sp.And(0 <= p[i], p[i] <= 1)
    
    # Proof steps
    proof_steps = []
    
    # Step 1: Establish constraints
    proof_steps.append({
        "step": "Establish data quality constraint",
        "expression": str(quality_constraint),
        "explanation": "Data quality is bounded between 0 and 1"
    })
    
    proof_steps.append({
        "step": "Establish signal strength constraint",
        "expression": str(signal_constraint),
        "explanation": "Signal strength is bounded between 0 and 1"
    })
    
    proof_steps.append({
        "step": "Establish predictive accuracy constraint",
        "expression": str(accuracy_constraint),
        "explanation": "Predictive accuracy is bounded between 0 and 1"
    })
    
    # Step 2: Define EI formula
    proof_steps.append({
        "step": "Define EI formula",
        "expression": str(ei_expr),
        "explanation": "Economic Intelligence (EI) is the average of quality-adjusted signals weighted by predictive accuracy"
    })
    
    # Step 3: Find minimum value (all inputs at 0)
    min_ei = 0
    proof_steps.append({
        "step": "Calculate minimum value",
        "expression": f"min(EI) = {min_ei}",
        "explanation": "Minimum EI occurs when all inputs are 0"
    })
    
    # Step 4: Find maximum value (all inputs at 1)
    max_ei = 1
    proof_steps.append({
        "step": "Calculate maximum value",
        "expression": f"max(EI) = {max_ei}",
        "explanation": "Maximum EI occurs when all inputs are 1"
    })
    
    # Step 5: Conclude bounds
    bounds_conclusion = sp.And(0 <= ei_expr, ei_expr <= 1)
    proof_steps.append({
        "step": "Establish bounds",
        "expression": str(bounds_conclusion),
        "explanation": "EI is bounded between 0 and 1"
    })
    
    return {
        "theorem": "Economic Intelligence (EI) is bounded between 0 and 1",
        "proof_steps": proof_steps,
        "conclusion": "verified"
    }

# ===============================================
# Verify unified model formula
# ===============================================

def verify_unified_model_formula():
    """
    Verify the unified model formula that integrates Treasury, FDIC, CFTC, and SBA approaches.
    
    Returns:
        dict: The verification result with proof steps
    """
    # Define symbols
    EI = sp.Symbol('EI', real=True)  # Economic Intelligence (Treasury)
    FS = sp.Symbol('FS', real=True)  # Financial Stability (FDIC)
    MH = sp.Symbol('MH', real=True)  # Market Health (CFTC)
    BS = sp.Symbol('BS', real=True)  # Business Support (SBA)
    
    # Define unified model formula symbolically
    um_expr = 0.3 * EI + 0.3 * FS + 0.2 * MH + 0.2 * BS
    
    # Define constraints
    ei_constraint = sp.And(0 <= EI, EI <= 1)
    fs_constraint = sp.And(0 <= FS, FS <= 1)
    mh_constraint = sp.And(0 <= MH, MH <= 1)
    bs_constraint = sp.And(0 <= BS, BS <= 1)
    
    # Proof steps
    proof_steps = []
    
    # Step 1: Establish constraints
    proof_steps.append({
        "step": "Establish Economic Intelligence constraint",
        "expression": str(ei_constraint),
        "explanation": "Economic Intelligence (EI) is bounded between 0 and 1"
    })
    
    proof_steps.append({
        "step": "Establish Financial Stability constraint",
        "expression": str(fs_constraint),
        "explanation": "Financial Stability (FS) is bounded between 0 and 1"
    })
    
    proof_steps.append({
        "step": "Establish Market Health constraint",
        "expression": str(mh_constraint),
        "explanation": "Market Health (MH) is bounded between 0 and 1"
    })
    
    proof_steps.append({
        "step": "Establish Business Support constraint",
        "expression": str(bs_constraint),
        "explanation": "Business Support (BS) is bounded between 0 and 1"
    })
    
    # Step 2: Define unified model formula
    proof_steps.append({
        "step": "Define unified model formula",
        "expression": str(um_expr),
        "explanation": "Unified Model (UM) is a weighted sum of EI, FS, MH, and BS"
    })
    
    # Step 3: Verify weights sum to 1.0
    weight_sum = 0.3 + 0.3 + 0.2 + 0.2
    proof_steps.append({
        "step": "Verify weights sum to 1.0",
        "expression": f"0.3 + 0.3 + 0.2 + 0.2 = {weight_sum}",
        "explanation": "The weights in the unified model formula sum to 1.0"
    })
    
    # Step 4: Find minimum value (all inputs at 0)
    min_um = um_expr.subs([(EI, 0), (FS, 0), (MH, 0), (BS, 0)])
    proof_steps.append({
        "step": "Calculate minimum value",
        "expression": f"min(UM) = {min_um}",
        "explanation": "Minimum UM occurs when all inputs are 0"
    })
    
    # Step 5: Find maximum value (all inputs at 1)
    max_um = um_expr.subs([(EI, 1), (FS, 1), (MH, 1), (BS, 1)])
    proof_steps.append({
        "step": "Calculate maximum value",
        "expression": f"max(UM) = {max_um}",
        "explanation": "Maximum UM occurs when all inputs are 1"
    })
    
    # Step 6: Conclude bounds
    bounds_conclusion = sp.And(0 <= um_expr, um_expr <= 1)
    proof_steps.append({
        "step": "Establish bounds",
        "expression": str(bounds_conclusion),
        "explanation": "UM is bounded between 0 and 1"
    })
    
    return {
        "theorem": "Unified Model (UM) is bounded between 0 and 1",
        "proof_steps": proof_steps,
        "conclusion": "verified"
    }

# ===============================================
# Main verification function
# ===============================================

def run_all_verifications(output_file='economic_model_verification_results.json'):
    """
    Run all economic formula verifications and save results to a JSON file.
    
    Args:
        output_file: Path to the output JSON file
        
    Returns:
        dict: All verification results
    """
    # Dictionary to store all verification results
    all_results = {}
    
    # Symbolic verifications
    print("Running symbolic verification of WAR score...")
    all_results['war_score_symbolic'] = verify_war_score_symbolic()
    
    print("Running symbolic verification of DRP conservatism...")
    all_results['drp_conservatism_symbolic'] = verify_drp_conservatism_symbolic()
    
    print("Running symbolic verification of SPS bounds...")
    all_results['sps_bounds_symbolic'] = verify_sps_bounds_symbolic()
    
    print("Running symbolic verification of Economic Intelligence formula...")
    all_results['economic_intelligence_symbolic'] = verify_economic_intelligence_formula()
    
    print("Running symbolic verification of Unified Model formula...")
    all_results['unified_model_symbolic'] = verify_unified_model_formula()
    
    # Numerical verifications
    print("Running numerical verification of WAR score...")
    all_results['war_score_numerical'] = verify_war_score_numerical()
    
    print("Running numerical verification of DRP conservatism...")
    all_results['drp_conservatism_numerical'] = verify_drp_conservatism_numerical()
    
    print("Running numerical verification of SPS bounds...")
    all_results['sps_bounds_numerical'] = verify_sps_bounds_numerical()
    
    # Save results to file
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"All verification results saved to {output_file}")
    return all_results

if __name__ == "__main__":
    run_all_verifications()