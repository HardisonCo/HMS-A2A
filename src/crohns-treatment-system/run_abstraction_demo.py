"""
Demo script for the abstraction analysis system.

This script runs a demonstration of the enhanced analysis system for
Crohn's disease clinical trials.
"""
import os
import json
import logging
import argparse
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_banner(text):
    """Print a banner with the given text."""
    width = len(text) + 6
    print("\n" + "=" * width)
    print(f"   {text}")
    print("=" * width + "\n")

def run_demo(data_file="tests/data/sample_trial_data.json", output_dir="output/demo"):
    """
    Run the abstraction analysis demo.
    
    Args:
        data_file: Path to the sample data file
        output_dir: Directory for output files
    """
    print_banner("Crohn's Disease Treatment System - Abstraction Analysis Demo")
    
    logger.info(f"Starting demo with data from {data_file}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load sample data
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    clinical_trials = data.get('clinical_trials', [])
    patient_data = data.get('patient_data', [])
    biomarker_data = data.get('biomarker_data', [])
    
    print(f"\nLoaded data for analysis:")
    print(f"- {len(clinical_trials)} clinical trials")
    print(f"- {len(patient_data)} patients")
    print(f"- {len(biomarker_data)} biomarkers\n")
    
    # Stage 1: Run abstraction analysis
    print_banner("Stage 1: Abstraction Analysis")
    
    print("Analyzing clinical trial data to identify key abstractions...\n")
    time.sleep(1)  # For demonstration pacing
    
    # Import the modules
    from src.analysis.abstraction_analysis import TrialAbstractionAnalysis
    
    # Initialize analyzer
    analyzer = TrialAbstractionAnalysis(max_abstractions=10, language="english", use_cache=True)
    
    # Run analysis
    analysis_results = analyzer.run_analysis(clinical_trials, patient_data, biomarker_data)
    
    # Print results
    print("\nAbstraction Analysis Results:")
    print(f"- Identified {len(analysis_results.get('abstractions', []))} abstractions")
    print(f"- Found {len(analysis_results.get('relationships', {}).get('details', []))} relationships")
    
    # Save analysis results
    output_file = os.path.join(output_dir, "abstraction_analysis_results.json")
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    print(f"\nSaved analysis results to {output_file}")
    
    # Stage 2: Generate visualizations
    print_banner("Stage 2: Visualization Generation")
    
    print("Generating visualizations for the abstraction analysis...\n")
    time.sleep(1)  # For demonstration pacing
    
    # Import visualizer
    from src.visualization.abstraction_visualizer import AbstractionVisualizer
    
    # Initialize visualizer
    visualizer = AbstractionVisualizer(output_dir=os.path.join(output_dir, "visualizations"))
    
    # Generate visualizations
    visualization_paths = visualizer.visualize_abstractions(analysis_results)
    
    # Generate HTML report
    html_report_path = os.path.join(output_dir, "visualizations", "report.html")
    visualizer.generate_html_report(analysis_results, html_report_path)
    
    # Print results
    print("\nGenerated Visualizations:")
    for name, path in visualization_paths.items():
        print(f"- {name}: {path}")
    print(f"- HTML Report: {html_report_path}")
    
    # Generate biomarker efficacy visualization
    biomarker_viz_path = os.path.join(output_dir, "visualizations", "biomarker_efficacy.png")
    visualizer.visualize_biomarker_efficacy(analysis_results, clinical_trials, biomarker_viz_path)
    print(f"- Biomarker Efficacy: {biomarker_viz_path}")
    
    # Stage 3: Enhanced Genetic Optimization
    print_banner("Stage 3: Enhanced Genetic Optimization")
    
    print("Optimizing treatment for patient using abstraction insights...\n")
    time.sleep(1)  # For demonstration pacing
    
    # Import enhanced genetic engine
    from src.coordination.genetic_engine.enhanced_genetic_engine import EnhancedGeneticEngine
    
    # Use first patient for demo
    patient = patient_data[0]
    
    print(f"Patient: {patient.get('patient_id')}")
    print(f"- Crohn's Type: {patient.get('clinical_data', {}).get('crohns_type')}")
    print(f"- CDAI: {patient.get('clinical_data', {}).get('disease_activity', {}).get('CDAI')}")
    
    print("\nGenetic Markers:")
    for marker in patient.get('biomarkers', {}).get('genetic_markers', []):
        print(f"- {marker.get('gene')}: {marker.get('variant')} ({marker.get('zygosity')})")
    
    print("\nTreatment History:")
    for med in patient.get('medication_history', []):
        print(f"- {med.get('name')}: {med.get('response')}")
    
    # Initialize enhanced genetic engine
    genetic_engine = EnhancedGeneticEngine(abstraction_analysis_results=analysis_results)
    
    # Optimize treatment with abstraction guidance
    print("\nRunning abstraction-guided optimization...")
    guided_treatment_plan = genetic_engine.optimize_treatment(patient, abstraction_guided=True)
    
    # Optimize treatment without abstraction guidance
    print("Running baseline optimization...")
    baseline_treatment_plan = genetic_engine.optimize_treatment(patient, abstraction_guided=False)
    
    # Print results
    print("\nTreatment Plans:")
    print("- Abstraction-guided treatment:")
    for med in guided_treatment_plan.get('treatment_plan', []):
        print(f"  - {med.get('medication')} {med.get('dosage')}{med.get('unit')} {med.get('frequency')} for {med.get('duration')} days")
    print(f"  - Fitness score: {guided_treatment_plan.get('fitness', 0):.2f}")
    
    print("\n- Baseline treatment:")
    for med in baseline_treatment_plan.get('treatment_plan', []):
        print(f"  - {med.get('medication')} {med.get('dosage')}{med.get('unit')} {med.get('frequency')} for {med.get('duration')} days")
    print(f"  - Fitness score: {baseline_treatment_plan.get('fitness', 0):.2f}")
    
    # Save results
    genetic_results = {
        "patient_id": patient.get('patient_id'),
        "guided_treatment_plan": guided_treatment_plan,
        "baseline_treatment_plan": baseline_treatment_plan
    }
    
    genetic_output_file = os.path.join(output_dir, "genetic_engine_results.json")
    with open(genetic_output_file, 'w') as f:
        json.dump(genetic_results, f, indent=2)
    print(f"\nSaved genetic engine results to {genetic_output_file}")
    
    # Stage 4: Enhanced Adaptive Trial Design
    print_banner("Stage 4: Enhanced Adaptive Trial Design")
    
    print("Designing an adaptive trial using abstraction insights...\n")
    time.sleep(1)  # For demonstration pacing
    
    # Import enhanced adaptive trial framework
    from src.coordination.a2a_integration.enhanced_adaptive_trial import EnhancedAdaptiveTrialFramework
    
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
    
    print("Protocol Template:")
    print(f"- Trial ID: {protocol_template.get('trial_id')}")
    print(f"- Title: {protocol_template.get('title')}")
    print(f"- Arms: {', '.join([arm.get('name') for arm in protocol_template.get('arms', [])])}")
    
    # Initialize enhanced adaptive trial framework
    adaptive_trial_framework = EnhancedAdaptiveTrialFramework(abstraction_analysis_results=analysis_results)
    
    # Design trial with abstraction guidance
    print("\nDesigning trial with abstraction guidance...")
    guided_trial_protocol = adaptive_trial_framework.design_trial(
        protocol_template, 
        patient_data, 
        abstraction_guided=True
    )
    
    # Design trial without abstraction guidance
    print("Designing trial without abstraction guidance...")
    baseline_trial_protocol = adaptive_trial_framework.design_trial(
        protocol_template, 
        patient_data, 
        abstraction_guided=False
    )
    
    # Print results
    print("\nAbstraction-guided trial design:")
    print("Biomarker stratification:")
    for arm in guided_trial_protocol.get('arms', []):
        biomarkers = [f"{b.get('biomarker')}:{b.get('criteria')}" for b in arm.get('biomarkerStratification', [])]
        print(f"- {arm.get('name')}: {', '.join(biomarkers) if biomarkers else 'none'}")
    
    print("\nAdaptive rules:")
    for rule in guided_trial_protocol.get('adaptiveRules', []):
        print(f"- {rule.get('triggerCondition')}: {rule.get('action')}")
    
    # Save results
    trial_results = {
        "guided_trial_protocol": guided_trial_protocol,
        "baseline_trial_protocol": baseline_trial_protocol
    }
    
    trial_output_file = os.path.join(output_dir, "adaptive_trial_results.json")
    with open(trial_output_file, 'w') as f:
        json.dump(trial_results, f, indent=2)
    print(f"\nSaved adaptive trial results to {trial_output_file}")
    
    # Final summary
    print_banner("Demo Complete")
    
    print("The Crohn's Disease Treatment System with enhanced abstraction analysis has successfully:")
    print("1. Identified key abstractions and relationships in clinical trial data")
    print("2. Generated informative visualizations of the abstractions")
    print("3. Enhanced treatment optimization with abstraction insights")
    print("4. Improved adaptive trial design using relationship analysis")
    
    print(f"\nAll output files are available in: {output_dir}")
    print(f"To view the HTML report, open: {html_report_path}")
    
    return {
        "analysis_results": analysis_results,
        "visualization_paths": visualization_paths,
        "html_report_path": html_report_path,
        "genetic_results": genetic_results,
        "trial_results": trial_results
    }

def main():
    """Main function to run the demo."""
    parser = argparse.ArgumentParser(description="Run the abstraction analysis demo")
    parser.add_argument("--data", default="tests/data/sample_trial_data.json", help="Path to sample data file")
    parser.add_argument("--output", default="output/demo", help="Directory for output files")
    args = parser.parse_args()
    
    # Run the demo
    run_demo(args.data, args.output)

if __name__ == "__main__":
    main()