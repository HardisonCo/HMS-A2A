# Crohn's Disease Treatment System: Usage Examples

This document provides practical examples demonstrating how to use the integrated Crohn's disease treatment system for various use cases. These examples show the integration between codex-rs, supervisors, and domains with the adaptive trial framework.

## Table of Contents

1. [Patient Treatment Optimization](#patient-treatment-optimization)
2. [Running an Adaptive Trial](#running-an-adaptive-trial)
3. [Biomarker Analysis](#biomarker-analysis)
4. [System Health Monitoring](#system-health-monitoring)
5. [Generating Visualization Reports](#generating-visualization-reports)
6. [Self-Healing Demonstration](#self-healing-demonstration)
7. [Command Line Interface](#command-line-interface)
8. [Integration with HMS-EHR](#integration-with-hms-ehr)

## Patient Treatment Optimization

### Example: Optimizing Treatment for a Single Patient

This example demonstrates how to optimize a treatment plan for a single patient based on their biomarkers, disease characteristics, and prior treatment history.

```python
#!/usr/bin/env python3
import asyncio
import json
import logging

from src.coordination.a2a_integration.codex_rs_integration import codex_integration
from src.data_layer.trial_data.trial_data_transformer import TrialDataTransformer

async def optimize_patient_treatment():
    # Initialize components
    await codex_integration.initialize()
    transformer = TrialDataTransformer()
    
    # Sample patient data
    patient_data = {
        "patient_id": "P12345",
        "demographics": {
            "age": 42,
            "sex": "female",
            "ethnicity": "Caucasian",
            "weight": 65.5,
            "height": 170.0
        },
        "clinical_data": {
            "crohns_type": "ileocolonic",
            "diagnosis_date": "2019-03-15",
            "disease_activity": {
                "CDAI": 220,
                "SES_CD": 12,
                "fecal_calprotectin": 280
            }
        },
        "biomarkers": {
            "genetic_markers": [
                {
                    "gene": "NOD2",
                    "variant": "variant",
                    "zygosity": "heterozygous"
                },
                {
                    "gene": "IL23R",
                    "variant": "variant",
                    "zygosity": "heterozygous"
                }
            ],
            "microbiome_profile": {
                "diversity_index": 0.65,
                "key_species": [
                    {
                        "name": "F. prausnitzii",
                        "abundance": 0.15
                    },
                    {
                        "name": "E. coli",
                        "abundance": 0.4
                    }
                ]
            },
            "serum_markers": {
                "CRP": 12.5,
                "ESR": 22
            }
        },
        "treatment_history": [
            {
                "medication": "Infliximab",
                "response": "partial",
                "start_date": "2019-05-01",
                "end_date": "2020-02-15",
                "adverse_events": ["infusion reaction"]
            },
            {
                "medication": "Azathioprine",
                "response": "none",
                "start_date": "2020-03-01",
                "end_date": "2020-09-15",
                "adverse_events": []
            }
        ]
    }
    
    try:
        # Transform to genetic engine format
        genetic_format = transformer.transform_patient_for_genetic_engine(patient_data)
        
        # Optimize treatment
        treatment_plan = await codex_integration.optimize_patient_treatment(genetic_format)
        
        # Display the result
        print("\nOptimized Treatment Plan:")
        print("=======================")
        for med in treatment_plan['treatment_plan']:
            print(f"• {med['medication']} {med['dosage']}{med['unit']} {med['frequency']} for {med['duration']} days")
        
        print(f"\nTreatment Fitness: {treatment_plan['fitness']:.2f}")
        
        if 'explanations' in treatment_plan:
            print("\nRationale:")
            for explanation in treatment_plan['explanations']:
                print(f"• {explanation}")
        
        # Save the result to a JSON file
        with open('output/patient_P12345_treatment.json', 'w') as f:
            json.dump(treatment_plan, f, indent=2)
        print("\nTreatment plan saved to output/patient_P12345_treatment.json")
        
    finally:
        # Shutdown
        await codex_integration.shutdown()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the example
    asyncio.run(optimize_patient_treatment())
```

### Expected Output

```
Optimized Treatment Plan:
=======================
• Upadacitinib 15.0mg daily for 30 days
• Methotrexate 15.0mg weekly for 30 days

Treatment Fitness: 0.85

Rationale:
• Treatment plan optimized with 0.85 fitness score.
• Upadacitinib selected based on patient's biomarker profile and disease characteristics.
• Methotrexate selected based on patient's biomarker profile and disease characteristics.
• NOD2 variant detected, which may predict increased response to certain biologics.
• IL23R variant detected, which may predict better response to IL-23 inhibitors.

Treatment plan saved to output/patient_P12345_treatment.json
```

## Running an Adaptive Trial

### Example: Conducting an Adaptive Clinical Trial

This example demonstrates how to run an adaptive clinical trial with multiple patients and treatment arms, with automatic adaptation based on interim results.

```python
#!/usr/bin/env python3
import asyncio
import os
import logging

from src.coordination.a2a_integration.codex_rs_integration import codex_integration
from src.data_layer.trial_data.trial_data_transformer import TrialDataTransformer
from src.visualization.trial_results_visualizer import TrialResultsVisualizer

async def run_adaptive_trial():
    # Initialize components
    await codex_integration.initialize()
    transformer = TrialDataTransformer()
    visualizer = TrialResultsVisualizer()
    
    try:
        # Load patient cohort from CSV
        patient_cohort = transformer.csv_to_patient_profiles('data/patient_cohort.csv')
        
        # Define trial protocol
        trial_protocol = {
            "trial_id": "CROHNS-001",
            "title": "Adaptive Trial of JAK Inhibitors in Crohn's Disease",
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
                    "biomarkerStratification": [
                        {
                            "biomarker": "NOD2",
                            "criteria": "variant"
                        }
                    ]
                },
                {
                    "armId": "ARM-002",
                    "name": "Upadacitinib 30mg",
                    "treatment": {
                        "medication": "Upadacitinib",
                        "dosage": "30",
                        "unit": "mg",
                        "frequency": "daily"
                    },
                    "biomarkerStratification": [
                        {
                            "biomarker": "NOD2",
                            "criteria": "variant"
                        }
                    ]
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
            "adaptiveRules": [
                {
                    "triggerCondition": "interim_analysis_1",
                    "action": "response_adaptive_randomization",
                    "parameters": {
                        "min_allocation": 0.1
                    }
                }
            ],
            "primaryEndpoints": [
                {
                    "name": "Clinical Remission",
                    "metric": "CDAI < 150",
                    "timepoint": "Week 16"
                }
            ],
            "secondaryEndpoints": [
                {
                    "name": "Endoscopic Improvement",
                    "metric": "SES-CD decrease ≥ 50%",
                    "timepoint": "Week 24"
                }
            ]
        }
        
        # Transform patient data for trial
        trial_patients = []
        for patient in patient_cohort:
            genetic_format = transformer.transform_patient_for_genetic_engine(patient)
            trial_patients.append(genetic_format)
        
        print(f"Starting adaptive trial with {len(trial_patients)} patients")
        
        # Run the trial
        trial_results = await codex_integration.run_adaptive_trial(trial_protocol, trial_patients)
        
        # Print summary of results
        print("\nTrial Results Summary:")
        print("=====================")
        print(f"Trial ID: {trial_results['trial_id']}")
        print(f"Status: {trial_results['status']}")
        print(f"Total patients: {len(trial_results['patient_outcomes'])}")
        
        # Print arm-specific results
        arm_results = {}
        for outcome in trial_results['patient_outcomes']:
            arm = outcome['arm']
            if arm not in arm_results:
                arm_results[arm] = {'count': 0, 'response_sum': 0, 'adverse_events': 0}
            
            arm_results[arm]['count'] += 1
            arm_results[arm]['response_sum'] += outcome['response']
            arm_results[arm]['adverse_events'] += len(outcome.get('adverse_events', []))
        
        print("\nResults by Treatment Arm:")
        for arm, results in arm_results.items():
            mean_response = results['response_sum'] / results['count'] if results['count'] > 0 else 0
            print(f"• {arm}: {results['count']} patients, mean response {mean_response:.2f}, {results['adverse_events']} adverse events")
        
        # Print adaptations
        if 'adaptations' in trial_results and trial_results['adaptations']:
            print("\nAdaptations:")
            for adaptation in trial_results['adaptations']:
                print(f"• {adaptation['type']} triggered by {adaptation.get('triggerCondition', 'unknown')}")
        
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        # Generate visualizations
        visualizations = visualizer.create_trial_summary_dashboard(trial_results)
        
        # Save visualizations
        visualizer.save_visualizations(visualizations, 'output/visualizations')
        
        # Generate HTML report
        visualizer.generate_html_report(trial_results, 'output/trial_report.html')
        
        print("\nTrial report generated at 'output/trial_report.html'")
        print("Individual visualizations saved in 'output/visualizations/'")
        
    finally:
        # Shutdown
        await codex_integration.shutdown()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the example
    asyncio.run(run_adaptive_trial())
```

## Biomarker Analysis

### Example: Analyzing Biomarker Influence on Treatment Response

This example demonstrates how to analyze the influence of biomarkers on treatment response using data from a completed trial.

```python
#!/usr/bin/env python3
import asyncio
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from src.data_layer.trial_data.trial_data_transformer import TrialDataTransformer

async def analyze_biomarker_influence():
    # Create transformer
    transformer = TrialDataTransformer()
    
    # Load trial results
    with open('data/completed_trial_results.json', 'r') as f:
        trial_results = json.load(f)
    
    # Load patient data
    with open('data/patient_biomarkers.json', 'r') as f:
        patient_biomarkers = json.load(f)
    
    # Combine patient outcomes with biomarker data
    combined_data = []
    
    for outcome in trial_results['patient_outcomes']:
        patient_id = outcome['patient_id']
        
        # Find biomarker data for this patient
        biomarker_data = next((b for b in patient_biomarkers if b['patient_id'] == patient_id), None)
        
        if biomarker_data:
            # Create combined record
            record = {
                'patient_id': patient_id,
                'arm': outcome['arm'],
                'response': outcome['response'],
                'adverse_events': len(outcome.get('adverse_events', [])),
            }
            
            # Add biomarker data
            for marker in biomarker_data.get('biomarkers', {}).get('genetic_markers', []):
                gene = marker.get('gene', '')
                variant = marker.get('variant', '')
                record[f'biomarker_{gene}'] = 1 if variant == 'variant' else 0
            
            # Add serum markers
            serum_markers = biomarker_data.get('biomarkers', {}).get('serum_markers', {})
            for marker, value in serum_markers.items():
                record[f'biomarker_{marker}'] = value
            
            combined_data.append(record)
    
    # Convert to DataFrame
    df = pd.DataFrame(combined_data)
    
    # Create output directory
    os.makedirs('output/biomarker_analysis', exist_ok=True)
    
    # Analyze biomarker correlation with response
    biomarker_cols = [col for col in df.columns if col.startswith('biomarker_')]
    
    print("Biomarker Correlation Analysis:")
    print("=============================")
    
    # Calculate correlations
    correlations = []
    for col in biomarker_cols:
        corr = df[['response', col]].corr().iloc[0, 1]
        if not pd.isna(corr):
            biomarker_name = col.replace('biomarker_', '')
            correlations.append({
                'biomarker': biomarker_name,
                'correlation': corr
            })
            print(f"• {biomarker_name}: correlation with response = {corr:.3f}")
    
    # Sort correlations
    correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
    
    # Create correlation plot
    plt.figure(figsize=(10, 6))
    corr_df = pd.DataFrame(correlations)
    colors = ['green' if x > 0 else 'red' for x in corr_df['correlation']]
    sns.barplot(x='biomarker', y='correlation', data=corr_df, palette=colors)
    plt.xlabel('Biomarker')
    plt.ylabel('Correlation with Response')
    plt.title('Biomarker Correlation with Treatment Response')
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('output/biomarker_analysis/correlation.png')
    
    print("\nCorrelation plot saved to 'output/biomarker_analysis/correlation.png'")
    
    # Analyze response by treatment arm and biomarker status
    top_biomarker = correlations[0]['biomarker'] if correlations else None
    
    if top_biomarker and f'biomarker_{top_biomarker}' in df.columns:
        # Create categorical variable for the top biomarker
        biomarker_col = f'biomarker_{top_biomarker}'
        if df[biomarker_col].nunique() <= 2:
            # Binary biomarker
            df['biomarker_status'] = df[biomarker_col].map({0: 'Normal', 1: 'Variant'})
        else:
            # Continuous biomarker - create bins
            df['biomarker_status'] = pd.qcut(df[biomarker_col], 2, labels=['Low', 'High'])
        
        # Create interaction plot
        plt.figure(figsize=(10, 6))
        sns.pointplot(x='arm', y='response', hue='biomarker_status', data=df, dodge=0.5)
        plt.xlabel('Treatment Arm')
        plt.ylabel('Mean Response')
        plt.title(f'Response by Treatment Arm and {top_biomarker} Status')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('output/biomarker_analysis/interaction.png')
        
        print(f"\nInteraction plot for {top_biomarker} saved to 'output/biomarker_analysis/interaction.png'")
        
        # Print statistical summary
        print(f"\nResponse by Treatment Arm and {top_biomarker} Status:")
        summary = df.groupby(['arm', 'biomarker_status'])['response'].agg(['mean', 'std', 'count']).reset_index()
        
        for _, row in summary.iterrows():
            print(f"• {row['arm']}, {row['biomarker_status']}: mean={row['mean']:.2f}, count={int(row['count'])}")
    
    # Save combined data
    df.to_csv('output/biomarker_analysis/combined_data.csv', index=False)
    print("\nCombined data saved to 'output/biomarker_analysis/combined_data.csv'")

if __name__ == "__main__":
    # Run the example
    asyncio.run(analyze_biomarker_influence())
```

## System Health Monitoring

### Example: Monitoring and Reporting System Health

This example demonstrates how to monitor the health of the integrated system components and generate a health report.

```python
#!/usr/bin/env python3
import asyncio
import json
import logging
from datetime import datetime
import os

from src.coordination.a2a_integration.codex_rs_integration import codex_integration

async def monitor_system_health():
    # Initialize components
    await codex_integration.initialize()
    
    try:
        # Monitor system health
        health = await codex_integration.monitor_system_health()
        
        # Print health summary
        print("\nSystem Health Summary:")
        print("=====================")
        print(f"Overall Status: {health['status']}")
        print(f"Timestamp: {health['timestamp']}")
        
        # Display component health
        print("\nComponent Status:")
        for component, data in health['components'].items():
            status = data['status']
            emoji = "✅" if status == 'healthy' else "❌"
            print(f"{emoji} {component}: {status}")
            
            # If there are details, show them
            if 'details' in data:
                if isinstance(data['details'], dict):
                    for key, value in data['details'].items():
                        print(f"  - {key}: {value}")
                else:
                    print(f"  - {data['details']}")
        
        # Create output directory
        os.makedirs('output/monitoring', exist_ok=True)
        
        # Save health report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f'output/monitoring/health_report_{timestamp}.json'
        
        with open(report_path, 'w') as f:
            json.dump(health, f, indent=2)
        
        print(f"\nHealth report saved to '{report_path}'")
        
        # Check if there are unhealthy components
        if health['status'] != 'healthy':
            print("\nUnhealthy Components Detected:")
            for component, data in health['components'].items():
                if data['status'] != 'healthy':
                    print(f"• {component}: {data['status']}")
                    if 'details' in data:
                        if isinstance(data['details'], dict) and 'error' in data['details']:
                            print(f"  - Error: {data['details']['error']}")
                        elif isinstance(data['details'], str):
                            print(f"  - Details: {data['details']}")
            
            print("\nRecommended Actions:")
            print("• Run the self-healing procedure")
            print("• Check logs for error details")
            print("• Restart components if necessary")
        
    finally:
        # Shutdown
        await codex_integration.shutdown()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the example
    asyncio.run(monitor_system_health())
```

## Generating Visualization Reports

### Example: Creating Visualizations from Trial Results

This example demonstrates how to generate comprehensive visualizations and reports from trial results.

```python
#!/usr/bin/env python3
import asyncio
import json
import os
import logging

from src.visualization.trial_results_visualizer import TrialResultsVisualizer

async def generate_visualizations():
    # Create visualizer
    visualizer = TrialResultsVisualizer(config={
        'figsize': (12, 8),
        'dpi': 150,
        'style': 'seaborn-whitegrid',
        'palette': 'viridis',
        'theme': 'light'  # or 'dark'
    })
    
    # Load trial results
    with open('data/completed_trial_results.json', 'r') as f:
        trial_results = json.load(f)
    
    # Create output directories
    os.makedirs('output/visualizations', exist_ok=True)
    os.makedirs('output/reports', exist_ok=True)
    
    print("Generating trial visualizations...")
    
    # Generate dashboard visualizations
    visualizations = visualizer.create_trial_summary_dashboard(trial_results)
    
    # Save individual visualizations
    visualizer.save_visualizations(visualizations, 'output/visualizations')
    
    # Generate HTML report
    visualizer.generate_html_report(trial_results, 'output/reports/trial_report.html')
    
    print(f"Generated {len(visualizations)} visualizations:")
    for name in visualizations.keys():
        print(f"• {name}.png")
    
    print("\nHTML report generated at 'output/reports/trial_report.html'")
    
    # Load patient data and treatment plan for patient-specific visualizations
    with open('data/patient_example.json', 'r') as f:
        patient_data = json.load(f)
    
    with open('data/treatment_plan_example.json', 'r') as f:
        treatment_plan = json.load(f)
    
    print("\nGenerating patient-specific visualizations...")
    
    # Generate patient-specific visualizations
    patient_visualizations = visualizer.visualize_patient_specific_results(
        patient_data, treatment_plan
    )
    
    # Save patient-specific visualizations
    patient_id = patient_data.get('patient_id', 'unknown')
    patient_dir = f'output/visualizations/patient_{patient_id}'
    os.makedirs(patient_dir, exist_ok=True)
    
    for name, img_data in patient_visualizations.items():
        import base64
        img_binary = base64.b64decode(img_data)
        
        with open(f'{patient_dir}/{name}.png', 'wb') as f:
            f.write(img_binary)
    
    print(f"Generated {len(patient_visualizations)} patient-specific visualizations for Patient {patient_id}:")
    for name in patient_visualizations.keys():
        print(f"• {name}.png")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the example
    asyncio.run(generate_visualizations())
```

## Self-Healing Demonstration

### Example: Demonstrating Self-Healing Capabilities

This example demonstrates the self-healing capabilities of the system by introducing a simulated failure and observing the recovery.

```python
#!/usr/bin/env python3
import asyncio
import json
import logging
import os
from datetime import datetime

from src.coordination.a2a_integration.codex_rs_integration import codex_integration

async def demonstrate_self_healing():
    # Initialize components
    await codex_integration.initialize()
    
    try:
        # Create output directory
        os.makedirs('output/self_healing', exist_ok=True)
        
        # Load trial protocol
        with open('data/trial_protocol.json', 'r') as f:
            trial_protocol = json.load(f)
        
        # Load patient cohort
        with open('data/patient_cohort.json', 'r') as f:
            patient_cohort = json.load(f)
        
        print("Demonstrating self-healing capabilities")
        print("=====================================")
        
        # Step 1: Run a healthy trial as baseline
        print("\nStep 1: Running healthy trial as baseline...")
        healthy_results = await codex_integration.run_adaptive_trial(
            trial_protocol, patient_cohort
        )
        
        # Save healthy results
        with open('output/self_healing/healthy_results.json', 'w') as f:
            json.dump(healthy_results, f, indent=2)
        
        print(f"Healthy trial completed with {len(healthy_results['patient_outcomes'])} patient outcomes")
        
        # Step 2: Create a corrupted version of the results
        print("\nStep 2: Simulating failure conditions...")
        corrupted_results = healthy_results.copy()
        corrupted_results['status'] = 'error'
        corrupted_results['patient_outcomes'] = []  # Remove all outcomes
        corrupted_results['error'] = 'Simulation failure'
        
        # Save corrupted results
        with open('output/self_healing/corrupted_results.json', 'w') as f:
            json.dump(corrupted_results, f, indent=2)
        
        # Step 3: Apply self-healing to the corrupted results
        print("\nStep 3: Applying self-healing...")
        healed_results = await codex_integration._apply_self_healing(
            corrupted_results, trial_protocol, patient_cohort
        )
        
        # Save healed results
        with open('output/self_healing/healed_results.json', 'w') as f:
            json.dump(healed_results, f, indent=2)
        
        # Step 4: Analyze and report on the healing
        print("\nStep 4: Analyzing healing results...")
        print("\nHealing Summary:")
        print(f"• Original status: {corrupted_results['status']}")
        print(f"• Healed status: {healed_results['status']}")
        print(f"• Healing applied: {healed_results.get('healing_applied', False)}")
        
        if 'healing_summary' in healed_results:
            print(f"• Healing summary: {healed_results['healing_summary']}")
        
        print(f"• Original patient outcomes: {len(corrupted_results['patient_outcomes'])}")
        print(f"• Healed patient outcomes: {len(healed_results['patient_outcomes'])}")
        
        if healed_results['patient_outcomes']:
            healed_count = sum(1 for o in healed_results['patient_outcomes'] if o.get('healed', False))
            print(f"• Patients with healing applied: {healed_count}")
        
        print("\nSelf-healing demonstration complete")
        print("Results saved to:")
        print("• output/self_healing/healthy_results.json")
        print("• output/self_healing/corrupted_results.json")
        print("• output/self_healing/healed_results.json")
        
    finally:
        # Shutdown
        await codex_integration.shutdown()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the example
    asyncio.run(demonstrate_self_healing())
```

## Command Line Interface

### Example: Command Line Interface for System Components

This example demonstrates how to create a simple command line interface for interacting with the system.

```python
#!/usr/bin/env python3
import asyncio
import argparse
import json
import os
import logging
from datetime import datetime

from src.coordination.a2a_integration.codex_rs_integration import codex_integration
from src.data_layer.trial_data.trial_data_transformer import TrialDataTransformer
from src.visualization.trial_results_visualizer import TrialResultsVisualizer

async def optimize_treatment(args):
    """Optimize treatment for a patient"""
    await codex_integration.initialize()
    transformer = TrialDataTransformer()
    
    try:
        # Load patient data
        with open(args.patient_file, 'r') as f:
            patient_data = json.load(f)
        
        # Transform to genetic engine format
        genetic_format = transformer.transform_patient_for_genetic_engine(patient_data)
        
        # Optimize treatment
        treatment_plan = await codex_integration.optimize_patient_treatment(genetic_format)
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        
        # Save the result
        with open(args.output, 'w') as f:
            json.dump(treatment_plan, f, indent=2)
        
        print(f"Treatment plan optimized with fitness {treatment_plan['fitness']:.2f}")
        print(f"Result saved to {args.output}")
        
    finally:
        await codex_integration.shutdown()

async def run_trial(args):
    """Run an adaptive trial"""
    await codex_integration.initialize()
    transformer = TrialDataTransformer()
    visualizer = TrialResultsVisualizer()
    
    try:
        # Load trial protocol
        with open(args.protocol_file, 'r') as f:
            trial_protocol = json.load(f)
        
        # Load or create patient cohort
        if args.patient_file.endswith('.csv'):
            patient_cohort = transformer.csv_to_patient_profiles(args.patient_file)
        else:
            with open(args.patient_file, 'r') as f:
                patient_cohort = json.load(f)
        
        # Transform patient data if needed
        trial_patients = []
        for patient in patient_cohort:
            if 'biomarker_values' not in patient:  # Check if already transformed
                genetic_format = transformer.transform_patient_for_genetic_engine(patient)
                trial_patients.append(genetic_format)
            else:
                trial_patients.append(patient)
        
        # Run the trial
        trial_results = await codex_integration.run_adaptive_trial(
            trial_protocol, trial_patients
        )
        
        # Create output directory
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        
        # Save the results
        with open(args.output, 'w') as f:
            json.dump(trial_results, f, indent=2)
        
        # Generate visualizations if requested
        if args.visualize:
            vis_dir = os.path.join(os.path.dirname(args.output), 'visualizations')
            os.makedirs(vis_dir, exist_ok=True)
            
            # Generate visualizations
            visualizations = visualizer.create_trial_summary_dashboard(trial_results)
            
            # Save visualizations
            visualizer.save_visualizations(visualizations, vis_dir)
            
            # Generate HTML report
            report_path = os.path.join(os.path.dirname(args.output), 'trial_report.html')
            visualizer.generate_html_report(trial_results, report_path)
            
            print(f"Visualizations saved to {vis_dir}")
            print(f"HTML report generated at {report_path}")
        
        print(f"Trial completed with {len(trial_results['patient_outcomes'])} patient outcomes")
        print(f"Results saved to {args.output}")
        
    finally:
        await codex_integration.shutdown()

async def monitor_health(args):
    """Monitor system health"""
    await codex_integration.initialize()
    
    try:
        # Monitor health
        health = await codex_integration.monitor_system_health()
        
        # Create output directory if it doesn't exist
        if args.output:
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            
            # Save the health report
            with open(args.output, 'w') as f:
                json.dump(health, f, indent=2)
            
            print(f"Health report saved to {args.output}")
        
        # Print health status
        print(f"System health: {health['status']}")
        
        for component, data in health['components'].items():
            status = data['status']
            emoji = "✅" if status == 'healthy' else "❌"
            print(f"{emoji} {component}: {status}")
        
    finally:
        await codex_integration.shutdown()

async def visualize_results(args):
    """Generate visualizations from trial results"""
    visualizer = TrialResultsVisualizer()
    
    # Load trial results
    with open(args.results_file, 'r') as f:
        trial_results = json.load(f)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate visualizations
    visualizations = visualizer.create_trial_summary_dashboard(trial_results)
    
    # Save visualizations
    visualizer.save_visualizations(visualizations, args.output_dir)
    
    # Generate HTML report
    report_path = os.path.join(args.output_dir, 'trial_report.html')
    visualizer.generate_html_report(trial_results, report_path)
    
    print(f"Generated {len(visualizations)} visualizations in {args.output_dir}")
    print(f"HTML report generated at {report_path}")

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description='Crohn\'s Disease Treatment System CLI')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Treatment optimization command
    optimize_parser = subparsers.add_parser('optimize', help='Optimize treatment for a patient')
    optimize_parser.add_argument('patient_file', help='Patient data JSON file')
    optimize_parser.add_argument('--output', '-o', default='output/treatment_plan.json',
                                help='Output file for the treatment plan')
    
    # Trial execution command
    trial_parser = subparsers.add_parser('trial', help='Run an adaptive trial')
    trial_parser.add_argument('protocol_file', help='Trial protocol JSON file')
    trial_parser.add_argument('patient_file', help='Patient cohort JSON or CSV file')
    trial_parser.add_argument('--output', '-o', default='output/trial_results.json',
                             help='Output file for the trial results')
    trial_parser.add_argument('--visualize', '-v', action='store_true',
                             help='Generate visualizations')
    
    # Health monitoring command
    health_parser = subparsers.add_parser('health', help='Monitor system health')
    health_parser.add_argument('--output', '-o', 
                              help='Output file for the health report (optional)')
    
    # Visualization command
    visualize_parser = subparsers.add_parser('visualize', help='Generate visualizations')
    visualize_parser.add_argument('results_file', help='Trial results JSON file')
    visualize_parser.add_argument('--output-dir', '-o', default='output/visualizations',
                                 help='Output directory for visualizations')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Execute the appropriate command
    if args.command == 'optimize':
        asyncio.run(optimize_treatment(args))
    elif args.command == 'trial':
        asyncio.run(run_trial(args))
    elif args.command == 'health':
        asyncio.run(monitor_health(args))
    elif args.command == 'visualize':
        asyncio.run(visualize_results(args))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

### CLI Usage Examples

```bash
# Optimize treatment for a patient
./cli.py optimize data/patient_example.json -o output/treatment_plan.json

# Run an adaptive trial
./cli.py trial data/trial_protocol.json data/patient_cohort.csv -o output/trial_results.json -v

# Monitor system health
./cli.py health -o output/health_report.json

# Generate visualizations from trial results
./cli.py visualize output/trial_results.json -o output/visualization_report
```

## Integration with HMS-EHR

### Example: Integrating with HMS-EHR System

This example demonstrates how to integrate with the HMS-EHR system to retrieve patient data and feed treatment recommendations back.

```python
#!/usr/bin/env python3
import asyncio
import json
import logging
import os
import requests
from datetime import datetime

from src.coordination.a2a_integration.codex_rs_integration import codex_integration
from src.data_layer.trial_data.trial_data_transformer import TrialDataTransformer
from src.data_layer.ehr_integration.fhir_client import FHIRClient

async def ehr_integration_workflow():
    # Initialize components
    await codex_integration.initialize()
    transformer = TrialDataTransformer()
    
    # Initialize FHIR client
    fhir_client = FHIRClient(
        base_url="https://ehr-server.example.com/fhir",
        auth_token="YOUR_AUTH_TOKEN"
    )
    
    try:
        # Step 1: Retrieve patient list with Crohn's disease
        print("Retrieving patients with Crohn's disease...")
        
        # In a real implementation, this would use the FHIR client
        # For this example, we'll load from a sample file
        with open('data/ehr_patient_list.json', 'r') as f:
            patient_list = json.load(f)
        
        # Create output directory
        os.makedirs('output/ehr_integration', exist_ok=True)
        
        # Process each patient
        for patient_id in patient_list['patient_ids']:
            print(f"\nProcessing patient {patient_id}...")
            
            # Step 2: Retrieve patient data from EHR
            print(f"Retrieving data for patient {patient_id} from EHR...")
            
            # In a real implementation, this would use the FHIR client
            # For this example, we'll load from a sample file
            try:
                with open(f'data/ehr_patients/{patient_id}.json', 'r') as f:
                    ehr_data = json.load(f)
            except FileNotFoundError:
                print(f"No EHR data found for patient {patient_id}, skipping")
                continue
            
            # Step 3: Transform EHR data to patient profile
            print("Transforming EHR data to patient profile...")
            patient_profile = transformer.hms_ehr_to_patient_profile(ehr_data)
            
            # Save patient profile
            with open(f'output/ehr_integration/{patient_id}_profile.json', 'w') as f:
                json.dump(patient_profile, f, indent=2)
            
            # Step 4: Transform to genetic engine format
            print("Preparing data for treatment optimization...")
            genetic_format = transformer.transform_patient_for_genetic_engine(patient_profile)
            
            # Step 5: Optimize treatment
            print("Optimizing treatment plan...")
            treatment_plan = await codex_integration.optimize_patient_treatment(genetic_format)
            
            # Save treatment plan
            with open(f'output/ehr_integration/{patient_id}_treatment.json', 'w') as f:
                json.dump(treatment_plan, f, indent=2)
            
            # Step 6: Format treatment plan for EHR
            print("Formatting treatment plan for EHR...")
            ehr_treatment_plan = {
                "resourceType": "CarePlan",
                "status": "active",
                "intent": "plan",
                "title": "Crohn's Disease Treatment Plan",
                "subject": {
                    "reference": f"Patient/{patient_id}"
                },
                "created": datetime.now().isoformat(),
                "activity": []
            }
            
            # Add medications to care plan
            for med in treatment_plan['treatment_plan']:
                activity = {
                    "detail": {
                        "status": "scheduled",
                        "description": f"{med['medication']} {med['dosage']}{med['unit']} {med['frequency']} for {med['duration']} days",
                        "category": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/care-plan-activity-category",
                                    "code": "medication",
                                    "display": "Medication"
                                }
                            ]
                        }
                    }
                }
                ehr_treatment_plan["activity"].append(activity)
            
            # Save EHR treatment plan
            with open(f'output/ehr_integration/{patient_id}_ehr_treatment.json', 'w') as f:
                json.dump(ehr_treatment_plan, f, indent=2)
            
            # Step 7: Submit treatment plan to EHR
            print("Submitting treatment plan to EHR...")
            
            # In a real implementation, this would use the FHIR client
            # fhir_client.create_resource('CarePlan', ehr_treatment_plan)
            
            print(f"Treatment plan for patient {patient_id} processed and submitted to EHR")
        
        print("\nEHR integration workflow completed")
        print(f"Results saved to output/ehr_integration/")
        
    finally:
        # Shutdown
        await codex_integration.shutdown()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the example
    asyncio.run(ehr_integration_workflow())
```

## Conclusion

These examples demonstrate how to use the Crohn's disease treatment system for various clinical and research applications. The examples can be adapted to specific use cases or extended with additional functionality as needed.

For more information on the integration architecture and implementation details, refer to the [Integration Guide](INTEGRATION-GUIDE.md).