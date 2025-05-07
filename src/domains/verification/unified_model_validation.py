"""
Unified Economic Model Validation

This module implements formal validation of the unified economic model that integrates
approaches from Treasury, FDIC, CFTC, and SBA. It validates key mathematical properties
and ensures the model behaves as expected across a range of inputs.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import io
import base64

# ===============================================
# Model definitions and core data structures
# ===============================================

@dataclass
class UnifiedModelParameters:
    """Parameters for the unified economic model."""
    # Treasury parameters (Economic Intelligence)
    data_quality: float = 0.8         # Quality of economic data (0-1)
    signal_strength: float = 0.7      # Strength of economic signals (0-1)
    predictive_accuracy: float = 0.75 # Accuracy of economic predictions (0-1)
    
    # FDIC parameters (Financial Stability)
    institutional_risk: float = 0.3   # Risk level of financial institutions (0-1)
    systemic_connection: float = 0.5  # Degree of systemic connections (0-1)
    vulnerability: float = 0.4        # System vulnerability (0-1)
    max_possible_risk: float = 1.0    # Maximum potential risk (normalization factor)
    
    # CFTC parameters (Market Health)
    liquidity_score: float = 0.8      # Market liquidity (0-1)
    transparency_score: float = 0.7   # Market transparency (0-1)
    participation_score: float = 0.6  # Market participation breadth (0-1)
    resilience_score: float = 0.75    # Market resilience to shocks (0-1)
    
    # SBA parameters (Business Support)
    access_to_capital: float = 0.65   # Capital access for businesses (0-1)
    technical_assistance: float = 0.7 # Technical support availability (0-1)
    market_access: float = 0.6        # Access to markets (0-1)
    regulatory_efficiency: float = 0.5# Regulatory environment efficiency (0-1)
    
    # Unified model weights
    ei_weight: float = 0.3            # Weight for Economic Intelligence
    fs_weight: float = 0.3            # Weight for Financial Stability
    mh_weight: float = 0.2            # Weight for Market Health
    bs_weight: float = 0.2            # Weight for Business Support

@dataclass
class ModelEvaluation:
    """Evaluation results for a model."""
    score: float
    component_scores: Dict[str, float]
    sensitivity: Dict[str, float]
    robustness: float
    validation_properties: Dict[str, bool]

# ===============================================
# Component model calculations
# ===============================================

def calculate_economic_intelligence(params: UnifiedModelParameters) -> float:
    """
    Calculate the Economic Intelligence (EI) score using Treasury's approach.
    
    Args:
        params: Model parameters
        
    Returns:
        float: Economic Intelligence score (0-1)
    """
    # Simple version for demonstration
    ei = (params.data_quality * params.signal_strength * params.predictive_accuracy)
    return ei

def calculate_financial_stability(params: UnifiedModelParameters) -> float:
    """
    Calculate the Financial Stability (FS) score using FDIC's approach.
    
    Args:
        params: Model parameters
        
    Returns:
        float: Financial Stability score (0-1)
    """
    # Higher score means more stability (less risk)
    risk_factor = params.institutional_risk * params.systemic_connection * params.vulnerability
    fs = 1.0 - (risk_factor / params.max_possible_risk)
    return fs

def calculate_market_health(params: UnifiedModelParameters) -> float:
    """
    Calculate the Market Health (MH) score using CFTC's approach.
    
    Args:
        params: Model parameters
        
    Returns:
        float: Market Health score (0-1)
    """
    mh = (params.liquidity_score * 0.3) + \
         (params.transparency_score * 0.3) + \
         (params.participation_score * 0.2) + \
         (params.resilience_score * 0.2)
    return mh

def calculate_business_support(params: UnifiedModelParameters) -> float:
    """
    Calculate the Business Support (BS) score using SBA's approach.
    
    Args:
        params: Model parameters
        
    Returns:
        float: Business Support score (0-1)
    """
    bs = (params.access_to_capital * 0.35) + \
         (params.technical_assistance * 0.25) + \
         (params.market_access * 0.25) + \
         (params.regulatory_efficiency * 0.15)
    return bs

# ===============================================
# Unified model calculation
# ===============================================

def calculate_unified_model(params: UnifiedModelParameters) -> Dict[str, float]:
    """
    Calculate the unified model score and component scores.
    
    Args:
        params: Model parameters
        
    Returns:
        dict: Unified model score and component scores
    """
    # Calculate component scores
    ei = calculate_economic_intelligence(params)
    fs = calculate_financial_stability(params)
    mh = calculate_market_health(params)
    bs = calculate_business_support(params)
    
    # Calculate unified score
    unified_score = (ei * params.ei_weight) + \
                    (fs * params.fs_weight) + \
                    (mh * params.mh_weight) + \
                    (bs * params.bs_weight)
    
    return {
        "unified_score": unified_score,
        "economic_intelligence": ei,
        "financial_stability": fs,
        "market_health": mh,
        "business_support": bs
    }

# ===============================================
# Model evaluation and validation
# ===============================================

def calculate_sensitivity(params: UnifiedModelParameters, param_name: str, num_points: int = 10) -> Dict[str, List[float]]:
    """
    Calculate the sensitivity of the unified model to a specific parameter.
    
    Args:
        params: Base model parameters
        param_name: Name of the parameter to vary
        num_points: Number of points to calculate
        
    Returns:
        dict: Parameter values and corresponding model scores
    """
    # Copy the parameters
    base_params = params
    
    # Get the parameter range (0 to 1 for most parameters)
    param_values = np.linspace(0, 1, num_points)
    unified_scores = []
    component_scores = {
        "economic_intelligence": [],
        "financial_stability": [],
        "market_health": [],
        "business_support": []
    }
    
    # Calculate scores for each parameter value
    for value in param_values:
        # Create a new parameters object with the modified value
        new_params = UnifiedModelParameters(**vars(base_params))
        setattr(new_params, param_name, value)
        
        # Calculate the scores
        scores = calculate_unified_model(new_params)
        
        # Store the scores
        unified_scores.append(scores["unified_score"])
        component_scores["economic_intelligence"].append(scores["economic_intelligence"])
        component_scores["financial_stability"].append(scores["financial_stability"])
        component_scores["market_health"].append(scores["market_health"])
        component_scores["business_support"].append(scores["business_support"])
    
    return {
        "param_values": param_values.tolist(),
        "unified_scores": unified_scores,
        "component_scores": component_scores
    }

def calculate_parameter_sensitivities(params: UnifiedModelParameters) -> Dict[str, float]:
    """
    Calculate the sensitivity of the unified model to each parameter.
    
    Args:
        params: Model parameters
        
    Returns:
        dict: Sensitivity of each parameter
    """
    sensitivities = {}
    base_score = calculate_unified_model(params)["unified_score"]
    
    # List of parameters to test
    param_names = [
        "data_quality", "signal_strength", "predictive_accuracy",
        "institutional_risk", "systemic_connection", "vulnerability",
        "liquidity_score", "transparency_score", "participation_score", "resilience_score",
        "access_to_capital", "technical_assistance", "market_access", "regulatory_efficiency"
    ]
    
    # Calculate sensitivity for each parameter
    for param_name in param_names:
        current_value = getattr(params, param_name)
        
        # Calculate score with parameter +10%
        new_params = UnifiedModelParameters(**vars(params))
        setattr(new_params, param_name, min(current_value * 1.1, 1.0))
        high_score = calculate_unified_model(new_params)["unified_score"]
        
        # Calculate score with parameter -10%
        new_params = UnifiedModelParameters(**vars(params))
        setattr(new_params, param_name, max(current_value * 0.9, 0.0))
        low_score = calculate_unified_model(new_params)["unified_score"]
        
        # Calculate sensitivity as (normalized) percent change in score
        if base_score == 0:
            sensitivity = 0
        else:
            avg_delta = (abs(high_score - base_score) + abs(low_score - base_score)) / 2
            sensitivity = avg_delta / base_score
        
        sensitivities[param_name] = float(sensitivity)
    
    return sensitivities

def validate_model_properties(params: UnifiedModelParameters) -> Dict[str, bool]:
    """
    Validate key properties of the unified model.
    
    Args:
        params: Model parameters
        
    Returns:
        dict: Validation results for each property
    """
    validation_results = {}
    
    # 1. Verify that unified score is bounded between 0 and 1
    scores = calculate_unified_model(params)
    validation_results["unified_score_bounded"] = 0 <= scores["unified_score"] <= 1
    
    # 2. Verify that component scores are bounded between 0 and 1
    validation_results["ei_bounded"] = 0 <= scores["economic_intelligence"] <= 1
    validation_results["fs_bounded"] = 0 <= scores["financial_stability"] <= 1
    validation_results["mh_bounded"] = 0 <= scores["market_health"] <= 1
    validation_results["bs_bounded"] = 0 <= scores["business_support"] <= 1
    
    # 3. Verify that model is monotonic with respect to positive factors
    base_score = scores["unified_score"]
    
    # Test monotonicity for a representative positive factor
    new_params = UnifiedModelParameters(**vars(params))
    new_params.data_quality = min(params.data_quality + 0.1, 1.0)
    new_score = calculate_unified_model(new_params)["unified_score"]
    validation_results["monotonic_positive"] = new_score >= base_score
    
    # 4. Verify that model is monotonic with respect to negative factors
    new_params = UnifiedModelParameters(**vars(params))
    new_params.institutional_risk = max(params.institutional_risk - 0.1, 0.0)
    new_score = calculate_unified_model(new_params)["unified_score"]
    validation_results["monotonic_negative"] = new_score >= base_score
    
    # 5. Verify that weights sum to 1.0
    weight_sum = params.ei_weight + params.fs_weight + params.mh_weight + params.bs_weight
    validation_results["weights_sum_to_one"] = abs(weight_sum - 1.0) < 1e-6
    
    return validation_results

def calculate_model_robustness(params: UnifiedModelParameters, num_samples: int = 100) -> float:
    """
    Calculate the robustness of the unified model to parameter variations.
    
    Args:
        params: Base model parameters
        num_samples: Number of random parameter sets to test
        
    Returns:
        float: Robustness score (lower is better)
    """
    base_score = calculate_unified_model(params)["unified_score"]
    
    # Generate random parameter variations
    scores = []
    for _ in range(num_samples):
        # Create random parameter variations within ±10% of original
        new_params = UnifiedModelParameters(**vars(params))
        
        # Modify each parameter randomly
        for param_name, param_value in vars(params).items():
            # Skip weights to maintain sum = 1.0
            if param_name.endswith('_weight'):
                continue
                
            # Only modify numeric parameters
            if isinstance(param_value, (int, float)):
                # Random variation within ±10%
                variation = np.random.uniform(-0.1, 0.1) * param_value
                new_value = param_value + variation
                
                # Ensure value stays within bounds (most are 0-1)
                new_value = max(0.0, min(1.0, new_value))
                
                setattr(new_params, param_name, new_value)
        
        # Calculate score with new parameters
        score = calculate_unified_model(new_params)["unified_score"]
        scores.append(score)
    
    # Calculate standard deviation of scores as a measure of robustness
    robustness = float(np.std(scores))
    
    return robustness

def evaluate_model(params: UnifiedModelParameters) -> ModelEvaluation:
    """
    Perform a comprehensive evaluation of the unified model.
    
    Args:
        params: Model parameters
        
    Returns:
        ModelEvaluation: Evaluation results
    """
    # Calculate model scores
    scores = calculate_unified_model(params)
    
    # Calculate parameter sensitivities
    sensitivities = calculate_parameter_sensitivities(params)
    
    # Validate model properties
    validation_results = validate_model_properties(params)
    
    # Calculate model robustness
    robustness = calculate_model_robustness(params)
    
    return ModelEvaluation(
        score=scores["unified_score"],
        component_scores={
            "economic_intelligence": scores["economic_intelligence"],
            "financial_stability": scores["financial_stability"],
            "market_health": scores["market_health"],
            "business_support": scores["business_support"]
        },
        sensitivity=sensitivities,
        robustness=robustness,
        validation_properties=validation_results
    )

# ===============================================
# Visualization functions
# ===============================================

def plot_sensitivity_analysis(param_name: str, sensitivity_data: Dict[str, List[float]]) -> str:
    """
    Create a sensitivity analysis plot and return it as a base64 encoded string.
    
    Args:
        param_name: Name of the parameter being analyzed
        sensitivity_data: Sensitivity data from calculate_sensitivity
        
    Returns:
        str: Base64 encoded PNG image
    """
    plt.figure(figsize=(10, 6))
    
    # Plot unified score
    plt.plot(
        sensitivity_data["param_values"],
        sensitivity_data["unified_scores"],
        'k-',
        linewidth=2,
        label="Unified Score"
    )
    
    # Plot component scores
    plt.plot(
        sensitivity_data["param_values"],
        sensitivity_data["component_scores"]["economic_intelligence"],
        'b--',
        label="Economic Intelligence"
    )
    plt.plot(
        sensitivity_data["param_values"],
        sensitivity_data["component_scores"]["financial_stability"],
        'g--',
        label="Financial Stability"
    )
    plt.plot(
        sensitivity_data["param_values"],
        sensitivity_data["component_scores"]["market_health"],
        'r--',
        label="Market Health"
    )
    plt.plot(
        sensitivity_data["param_values"],
        sensitivity_data["component_scores"]["business_support"],
        'm--',
        label="Business Support"
    )
    
    plt.xlabel(f"{param_name.replace('_', ' ').title()} Value")
    plt.ylabel("Score")
    plt.title(f"Sensitivity Analysis for {param_name.replace('_', ' ').title()}")
    plt.legend()
    plt.grid(True)
    plt.ylim(0, 1)
    
    # Convert plot to base64 encoded string
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_str

def plot_parameter_sensitivities(sensitivities: Dict[str, float]) -> str:
    """
    Create a bar chart of parameter sensitivities and return it as a base64 encoded string.
    
    Args:
        sensitivities: Parameter sensitivities
        
    Returns:
        str: Base64 encoded PNG image
    """
    # Sort parameters by sensitivity
    sorted_params = sorted(sensitivities.items(), key=lambda x: x[1], reverse=True)
    param_names = [p[0].replace('_', ' ').title() for p in sorted_params]
    param_values = [p[1] for p in sorted_params]
    
    plt.figure(figsize=(12, 8))
    plt.barh(param_names, param_values)
    plt.xlabel("Sensitivity")
    plt.ylabel("Parameter")
    plt.title("Parameter Sensitivities")
    plt.grid(True, axis='x')
    
    # Convert plot to base64 encoded string
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_str

def plot_component_scores(scores: Dict[str, float]) -> str:
    """
    Create a radar chart of component scores and return it as a base64 encoded string.
    
    Args:
        scores: Component scores
        
    Returns:
        str: Base64 encoded PNG image
    """
    # Extract scores
    categories = ['Economic\nIntelligence', 'Financial\nStability', 'Market\nHealth', 'Business\nSupport']
    values = [
        scores["economic_intelligence"],
        scores["financial_stability"],
        scores["market_health"],
        scores["business_support"]
    ]
    
    # Close the plot for the radar chart
    values.append(values[0])
    
    # Calculate angles for the radar chart
    angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
    angles.append(angles[0])
    
    # Plot the radar chart
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, values, 'o-', linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), categories)
    ax.set_ylim(0, 1)
    ax.grid(True)
    plt.title("Component Scores", size=15)
    
    # Convert plot to base64 encoded string
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_str

# ===============================================
# Monte Carlo simulation
# ===============================================

def run_monte_carlo_simulation(num_samples: int = 1000) -> Dict[str, Any]:
    """
    Run a Monte Carlo simulation of the unified model with random parameters.
    
    Args:
        num_samples: Number of random parameter sets to test
        
    Returns:
        dict: Simulation results
    """
    unified_scores = []
    component_scores = {
        "economic_intelligence": [],
        "financial_stability": [],
        "market_health": [],
        "business_support": []
    }
    
    # Generate random parameters and calculate scores
    for _ in range(num_samples):
        # Generate random parameters
        params = UnifiedModelParameters(
            # Treasury parameters
            data_quality=np.random.uniform(0, 1),
            signal_strength=np.random.uniform(0, 1),
            predictive_accuracy=np.random.uniform(0, 1),
            
            # FDIC parameters
            institutional_risk=np.random.uniform(0, 1),
            systemic_connection=np.random.uniform(0, 1),
            vulnerability=np.random.uniform(0, 1),
            
            # CFTC parameters
            liquidity_score=np.random.uniform(0, 1),
            transparency_score=np.random.uniform(0, 1),
            participation_score=np.random.uniform(0, 1),
            resilience_score=np.random.uniform(0, 1),
            
            # SBA parameters
            access_to_capital=np.random.uniform(0, 1),
            technical_assistance=np.random.uniform(0, 1),
            market_access=np.random.uniform(0, 1),
            regulatory_efficiency=np.random.uniform(0, 1),
            
            # Keep the original weights
            ei_weight=0.3,
            fs_weight=0.3,
            mh_weight=0.2,
            bs_weight=0.2
        )
        
        # Calculate scores
        scores = calculate_unified_model(params)
        
        # Store the scores
        unified_scores.append(scores["unified_score"])
        component_scores["economic_intelligence"].append(scores["economic_intelligence"])
        component_scores["financial_stability"].append(scores["financial_stability"])
        component_scores["market_health"].append(scores["market_health"])
        component_scores["business_support"].append(scores["business_support"])
    
    # Calculate statistics
    unified_scores = np.array(unified_scores)
    ei_scores = np.array(component_scores["economic_intelligence"])
    fs_scores = np.array(component_scores["financial_stability"])
    mh_scores = np.array(component_scores["market_health"])
    bs_scores = np.array(component_scores["business_support"])
    
    stats = {
        "unified_score": {
            "mean": float(np.mean(unified_scores)),
            "median": float(np.median(unified_scores)),
            "min": float(np.min(unified_scores)),
            "max": float(np.max(unified_scores)),
            "std": float(np.std(unified_scores))
        },
        "economic_intelligence": {
            "mean": float(np.mean(ei_scores)),
            "median": float(np.median(ei_scores)),
            "min": float(np.min(ei_scores)),
            "max": float(np.max(ei_scores)),
            "std": float(np.std(ei_scores))
        },
        "financial_stability": {
            "mean": float(np.mean(fs_scores)),
            "median": float(np.median(fs_scores)),
            "min": float(np.min(fs_scores)),
            "max": float(np.max(fs_scores)),
            "std": float(np.std(fs_scores))
        },
        "market_health": {
            "mean": float(np.mean(mh_scores)),
            "median": float(np.median(mh_scores)),
            "min": float(np.min(mh_scores)),
            "max": float(np.max(mh_scores)),
            "std": float(np.std(mh_scores))
        },
        "business_support": {
            "mean": float(np.mean(bs_scores)),
            "median": float(np.median(bs_scores)),
            "min": float(np.min(bs_scores)),
            "max": float(np.max(bs_scores)),
            "std": float(np.std(bs_scores))
        }
    }
    
    # Check bounds (unified score should always be between 0 and 1)
    bounds_check = {
        "unified_score_below_0": int(np.sum(unified_scores < 0)),
        "unified_score_above_1": int(np.sum(unified_scores > 1)),
        "ei_below_0": int(np.sum(ei_scores < 0)),
        "ei_above_1": int(np.sum(ei_scores > 1)),
        "fs_below_0": int(np.sum(fs_scores < 0)),
        "fs_above_1": int(np.sum(fs_scores > 1)),
        "mh_below_0": int(np.sum(mh_scores < 0)),
        "mh_above_1": int(np.sum(mh_scores > 1)),
        "bs_below_0": int(np.sum(bs_scores < 0)),
        "bs_above_1": int(np.sum(bs_scores > 1))
    }
    
    # Calculate correlations between component scores and unified score
    correlations = {
        "ei_unified": float(np.corrcoef(ei_scores, unified_scores)[0, 1]),
        "fs_unified": float(np.corrcoef(fs_scores, unified_scores)[0, 1]),
        "mh_unified": float(np.corrcoef(mh_scores, unified_scores)[0, 1]),
        "bs_unified": float(np.corrcoef(bs_scores, unified_scores)[0, 1])
    }
    
    return {
        "num_samples": num_samples,
        "statistics": stats,
        "bounds_check": bounds_check,
        "correlations": correlations,
        "unified_scores": unified_scores.tolist(),
        "component_scores": {
            "economic_intelligence": ei_scores.tolist(),
            "financial_stability": fs_scores.tolist(),
            "market_health": mh_scores.tolist(),
            "business_support": bs_scores.tolist()
        }
    }

# ===============================================
# End-to-end validation
# ===============================================

def validate_unified_model(output_file='unified_model_validation_results.json'):
    """
    Perform a comprehensive validation of the unified economic model.
    
    Args:
        output_file: Path to the output JSON file
    
    Returns:
        dict: Validation results
    """
    print("Starting unified model validation...")
    
    # Create base parameters
    params = UnifiedModelParameters()
    
    # Evaluate the model
    print("Evaluating model with base parameters...")
    evaluation = evaluate_model(params)
    
    # Run Monte Carlo simulation
    print("Running Monte Carlo simulation...")
    monte_carlo = run_monte_carlo_simulation(num_samples=1000)
    
    # Run sensitivity analyses for key parameters
    print("Running sensitivity analyses...")
    sensitivity_analyses = {}
    key_params = [
        "data_quality", "institutional_risk", "liquidity_score", "access_to_capital"
    ]
    
    for param in key_params:
        print(f"  Analyzing sensitivity to {param}...")
        sensitivity_analyses[param] = calculate_sensitivity(params, param)
    
    # Generate evaluation report
    print("Generating plots...")
    plots = {}
    for param in key_params:
        plots[f"{param}_sensitivity"] = plot_sensitivity_analysis(param, sensitivity_analyses[param])
    
    plots["parameter_sensitivities"] = plot_parameter_sensitivities(evaluation.sensitivity)
    plots["component_scores"] = plot_component_scores(evaluation.component_scores)
    
    # Validate model properties
    print("Validating model properties...")
    property_validation = {}
    
    # Validate bounds
    property_validation["bounds"] = all([
        evaluation.validation_properties["unified_score_bounded"],
        evaluation.validation_properties["ei_bounded"],
        evaluation.validation_properties["fs_bounded"],
        evaluation.validation_properties["mh_bounded"],
        evaluation.validation_properties["bs_bounded"]
    ])
    
    # Validate monotonicity
    property_validation["monotonicity"] = all([
        evaluation.validation_properties["monotonic_positive"],
        evaluation.validation_properties["monotonic_negative"]
    ])
    
    # Validate weight normalization
    property_validation["weight_normalization"] = evaluation.validation_properties["weights_sum_to_one"]
    
    # Validate Monte Carlo bounds
    property_validation["monte_carlo_bounds"] = all([
        monte_carlo["bounds_check"]["unified_score_below_0"] == 0,
        monte_carlo["bounds_check"]["unified_score_above_1"] == 0,
        monte_carlo["bounds_check"]["ei_below_0"] == 0,
        monte_carlo["bounds_check"]["ei_above_1"] == 0,
        monte_carlo["bounds_check"]["fs_below_0"] == 0,
        monte_carlo["bounds_check"]["fs_above_1"] == 0,
        monte_carlo["bounds_check"]["mh_below_0"] == 0,
        monte_carlo["bounds_check"]["mh_above_1"] == 0,
        monte_carlo["bounds_check"]["bs_below_0"] == 0,
        monte_carlo["bounds_check"]["bs_above_1"] == 0
    ])
    
    # Overall validation result
    validation_result = all(property_validation.values())
    
    # Compile results
    results = {
        "validation_result": validation_result,
        "property_validation": property_validation,
        "model_evaluation": {
            "unified_score": evaluation.score,
            "component_scores": evaluation.component_scores,
            "sensitivities": evaluation.sensitivity,
            "robustness": evaluation.robustness
        },
        "monte_carlo": {
            "statistics": monte_carlo["statistics"],
            "correlations": monte_carlo["correlations"]
        },
        "sensitivity_analyses": {
            param: {
                "param_values": analysis["param_values"],
                "unified_scores": analysis["unified_scores"]
            } for param, analysis in sensitivity_analyses.items()
        },
        "plots": plots
    }
    
    # Save results to file
    print(f"Saving validation results to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Validation complete!")
    return results

if __name__ == "__main__":
    validate_unified_model()