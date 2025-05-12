"""
Test script for the abstraction analysis module.

This script tests the functionality of the abstraction analysis module
with sample trial data.
"""
import os
import json
import logging
import argparse
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the modules to test
from src.analysis.abstraction_analysis import TrialAbstractionAnalysis
from src.visualization.abstraction_visualizer import AbstractionVisualizer
from src.coordination.genetic_engine.enhanced_genetic_engine import EnhancedGeneticEngine
from src.coordination.a2a_integration.enhanced_adaptive_trial import EnhancedAdaptiveTrialFramework

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_abstraction_analysis(data_file, output_dir):
    """
    Test the abstraction analysis module.
    
    Args:
        data_file: Path to the sample data file
        output_dir: Directory for output files
    """
    logger.info(f"Testing abstraction analysis with data from {data_file}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load sample data
    with open(data_file, 'r') as f:
        data = json.load(f)
        
    clinical_trials = data.get('clinical_trials', [])
    patient_data = data.get('patient_data', [])
    biomarker_data = data.get('biomarker_data', [])
    
    logger.info(f"Loaded {len(clinical_trials)} trials, {len(patient_data)} patients, {len(biomarker_data)} biomarkers")
    
    # Initialize analyzer
    analyzer = TrialAbstractionAnalysis(max_abstractions=10, language="english", use_cache=True)
    
    # Run analysis
    logger.info("Running abstraction analysis...")
    analysis_results = analyzer.run_analysis(clinical_trials, patient_data, biomarker_data)
    
    # Save analysis results
    output_file = os.path.join(output_dir, "abstraction_analysis_results.json")
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    logger.info(f"Saved analysis results to {output_file}")
    
    # Generate visualizations
    logger.info("Generating visualizations...")
    visualizer = AbstractionVisualizer(output_dir=os.path.join(output_dir, "visualizations"))
    visualization_paths = visualizer.visualize_abstractions(analysis_results)
    
    # Generate HTML report
    html_report_path = os.path.join(output_dir, "visualizations", "report.html")
    visualizer.generate_html_report(analysis_results, html_report_path)
    logger.info(f"Generated HTML report at {html_report_path}")
    
    # Generate biomarker efficacy visualization
    biomarker_viz_path = os.path.join(output_dir, "visualizations", "biomarker_efficacy.png")
    visualizer.visualize_biomarker_efficacy(analysis_results, clinical_trials, biomarker_viz_path)
    
    return analysis_results

def test_enhanced_genetic_engine(analysis_results, data_file, output_dir):
    """
    Test the enhanced genetic engine.
    
    Args:
        analysis_results: Results from abstraction analysis
        data_file: Path to the sample data file
        output_dir: Directory for output files
    """
    logger.info("Testing enhanced genetic engine...")
    
    # Load sample data
    with open(data_file, 'r') as f:
        data = json.load(f)
        
    patient_data = data.get('patient_data', [])[0]  # Use first patient for testing
    
    # Initialize enhanced genetic engine
    genetic_engine = EnhancedGeneticEngine(abstraction_analysis_results=analysis_results)
    
    # Optimize treatment with abstraction guidance
    logger.info(f"Optimizing treatment for patient {patient_data.get('patient_id')} with abstraction guidance...")
    guided_treatment_plan = genetic_engine.optimize_treatment(patient_data, abstraction_guided=True)
    
    # Optimize treatment without abstraction guidance
    logger.info(f"Optimizing treatment for patient {patient_data.get('patient_id')} without abstraction guidance...")
    baseline_treatment_plan = genetic_engine.optimize_treatment(patient_data, abstraction_guided=False)
    
    # Save results
    results = {
        "patient_id": patient_data.get('patient_id'),
        "guided_treatment_plan": guided_treatment_plan,
        "baseline_treatment_plan": baseline_treatment_plan
    }
    
    output_file = os.path.join(output_dir, "genetic_engine_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved genetic engine results to {output_file}")
    
    return results

def test_enhanced_adaptive_trial(analysis_results, data_file, output_dir):
    """
    Test the enhanced adaptive trial framework.
    
    Args:
        analysis_results: Results from abstraction analysis
        data_file: Path to the sample data file
        output_dir: Directory for output files
    """
    logger.info("Testing enhanced adaptive trial framework...")
    
    # Load sample data
    with open(data_file, 'r') as f:
        data = json.load(f)
        
    # Create a protocol template
    protocol_template = {
        "trial_id": "CROHNS-003",
        "title": "Advanced Adaptive Trial for Crohn's Disease",
        "phase": 2,
        "arms": [
            {
                "armId": "ARM-001",
                "name": "Upadacitinib 15mg",
                "treatment": {
                    "medication": "Upadacitinib",
                    "dosage": "15",
                    "unit": "mg",
                    "frequency": "daily"
                },
                "biomarkerStratification": []
            },
            {
                "armId": "ARM-002",
                "name": "Ustekinumab",
                "treatment": {
                    "medication": "Ustekinumab",
                    "dosage": "90",
                    "unit": "mg",
                    "frequency": "every 8 weeks"
                },
                "biomarkerStratification": []
            },
            {
                "armId": "ARM-003",
                "name": "Placebo",
                "treatment": {
                    "medication": "Placebo",
                    "dosage": "0",
                    "unit": "mg",
                    "frequency": "daily"
                },
                "biomarkerStratification": []
            }
        ],
        "adaptiveRules": []
    }
    
    # Use patient data as population
    patient_population = data.get('patient_data', [])
    
    # Initialize enhanced adaptive trial framework
    adaptive_trial_framework = EnhancedAdaptiveTrialFramework(abstraction_analysis_results=analysis_results)
    
    # Design trial with abstraction guidance
    logger.info("Designing trial with abstraction guidance...")
    guided_trial_protocol = adaptive_trial_framework.design_trial(
        protocol_template, 
        patient_population, 
        abstraction_guided=True
    )
    
    # Design trial without abstraction guidance
    logger.info("Designing trial without abstraction guidance...")
    baseline_trial_protocol = adaptive_trial_framework.design_trial(
        protocol_template, 
        patient_population, 
        abstraction_guided=False
    )
    
    # Save results
    results = {
        "guided_trial_protocol": guided_trial_protocol,
        "baseline_trial_protocol": baseline_trial_protocol
    }
    
    output_file = os.path.join(output_dir, "adaptive_trial_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved adaptive trial results to {output_file}")
    
    return results

def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Test the abstraction analysis module")
    parser.add_argument("--data", default="tests/data/sample_trial_data.json", help="Path to sample data file")
    parser.add_argument("--output", default="output/tests", help="Directory for output files")
    args = parser.parse_args()
    
    # Run the tests
    analysis_results = test_abstraction_analysis(args.data, args.output)
    genetic_results = test_enhanced_genetic_engine(analysis_results, args.data, args.output)
    trial_results = test_enhanced_adaptive_trial(analysis_results, args.data, args.output)
    
    # Log completion
    logger.info("All tests completed successfully")
    logger.info(f"Output files are in {args.output}")

if __name__ == "__main__":
    main()