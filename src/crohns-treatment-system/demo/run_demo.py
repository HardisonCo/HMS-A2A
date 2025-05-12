#!/usr/bin/env python3
"""
Crohn's Disease Treatment System Demo

This script demonstrates the key capabilities of the Crohn's Disease Treatment System,
including treatment optimization, adaptive trials, visualization, and integration.
"""

import os
import json
import logging
import asyncio
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('crohns-treatment-demo')

# Import system modules
try:
    # Try to import the actual modules
    from src.coordination.a2a_integration.codex_rs_integration import codex_integration
    from src.coordination.a2a_integration.genetic_sequence_ffi import analyze_patient_sequences, get_crohns_variant_info
    from src.data_layer.trial_data.trial_data_transformer import TrialDataTransformer
    from src.visualization.trial_results_visualizer import TrialResultsVisualizer
    
    MOCK_MODE = False
    logger.info("Running with actual system components")
except ImportError:
    # If modules aren't available, run in mock mode
    MOCK_MODE = True
    logger.info("Running in mock mode - system components not available")


# Mock data for demonstration purposes
SAMPLE_PATIENT = {
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

# Sample genetic sequence data for Crohn's disease analysis
SAMPLE_GENETIC_DATA = {
    "patient_id": "P12345",
    "sequences": {
        "NOD2": "ATGGGCGAGAGGCTGGTCTTCAACCAGCTGCAGGCTGCCCGCAGGGCTCTGGCGGGCCGAGCAGCTGCTTGGCGGGACCCTGCTGCGCGGCAAGGACTGGGAGCAGTTGTTGGCGTTCACCTCAGACTTGGAGCCTGCTGTTGAAGTGGGACCAGATGGAGATCAGGGCCTGAAGGCTGATGGTGGGATGGGGCAGGAAGCAGCCAAGGCCAAGCCTGCCTCAATGTCCACCTCAACCGAAGAG",
        "IL23R": "ATGAAAAAATATATTCTTGTACGTGGTTATCTTCTTAGAGACATTGGTATTGCCATTCTTTATATTCTAAATAGTGTTCGGAATACTTCAGATATTTCAACCAAAAGGAAAGATTATTTCTGCATATATCAGTTCCTGACATTTATTATTGGGAAATTATTTTCAACGACGATTTCCTATCATGGTGTGTCCTGAAAAACTTGAAACAGAGCAACAG",
        "ATG16L1": "ATGGAGTTACAGATTAGAAACAGGTTCCTGTTCCCAGTGCCAGTGTCCTTTCTGCCGGGATCAGCCTCCCAGGAGTGGATAAAAATCACTGAGCTAAAGACGCACATTGCCTTTGCTGCCTCTTCAGATCAACAGATGTGTCTCTCCGGACTTTGAAACAAGACACCGTGTGACACACTATCTCAGATGCCAGGAAAAGGTCCAGGCTGAGAAGCTGAAGACGAGGCTGGAGGAGCGGGCAGCT"
    },
    "demographic": {
        "age": 42,
        "sex": "female",
        "ethnicity": "Caucasian",
        "family_history": True
    },
    "clinical": {
        "diagnosis_age": 40,
        "disease_location": "ileocolonic",
        "disease_behavior": "inflammatory",
        "extraintestinal_manifestations": ["arthritis", "uveitis"],
        "previous_treatments": ["Infliximab", "Azathioprine"],
        "treatment_responses": {
            "Infliximab": "partial",
            "Azathioprine": "none"
        }
    }
}

SAMPLE_GENETIC_ANALYSIS_RESULT = {
    "variants": [
        {
            "gene": "NOD2",
            "variant_id": "R702W",
            "nucleotide_change": "C2104T",
            "protein_change": "Arg702Trp",
            "zygosity": "heterozygous",
            "clinical_significance": "pathogenic",
            "impact_score": 0.85,
            "description": "Common NOD2 variant associated with Crohn's disease, particularly ileal disease."
        },
        {
            "gene": "IL23R",
            "variant_id": "R381Q",
            "nucleotide_change": "G1142A",
            "protein_change": "Arg381Gln",
            "zygosity": "heterozygous",
            "clinical_significance": "protective",
            "impact_score": 0.72,
            "description": "Protective variant that reduces risk of inflammatory bowel disease."
        },
        {
            "gene": "ATG16L1",
            "variant_id": "T300A",
            "nucleotide_change": "A898G",
            "protein_change": "Thr300Ala",
            "zygosity": "homozygous",
            "clinical_significance": "risk factor",
            "impact_score": 0.68,
            "description": "Associated with impaired autophagy and increased susceptibility to Crohn's disease."
        }
    ],
    "risk_assessment": {
        "overall_risk": "high",
        "risk_score": 0.78,
        "contributing_factors": [
            {
                "factor": "NOD2 R702W variant",
                "contribution": "major",
                "description": "Associated with 2-4x increased risk of Crohn's disease"
            },
            {
                "factor": "ATG16L1 T300A homozygosity",
                "contribution": "moderate",
                "description": "Associated with 1.5-2x increased risk"
            },
            {
                "factor": "IL23R R381Q variant",
                "contribution": "protective",
                "description": "Reduces risk by approximately 0.7x"
            }
        ],
        "confidence": 0.92
    },
    "treatment_recommendations": [
        {
            "treatment": "Ustekinumab",
            "expected_efficacy": 0.82,
            "genetic_basis": [
                {
                    "gene": "IL23R",
                    "variant": "R381Q",
                    "effect": "Variant suggests good response to IL-12/23 inhibition"
                }
            ],
            "confidence": 0.78,
            "contraindications": []
        },
        {
            "treatment": "Vedolizumab",
            "expected_efficacy": 0.75,
            "genetic_basis": [
                {
                    "gene": "NOD2",
                    "variant": "R702W",
                    "effect": "Patients with NOD2 variants often respond well to gut-selective therapies"
                }
            ],
            "confidence": 0.71,
            "contraindications": []
        },
        {
            "treatment": "Infliximab",
            "expected_efficacy": 0.62,
            "genetic_basis": [
                {
                    "gene": "ATG16L1",
                    "variant": "T300A",
                    "effect": "May have reduced response to anti-TNF therapy"
                }
            ],
            "confidence": 0.65,
            "contraindications": ["Previous infusion reaction"]
        }
    ],
    "analysis_id": "GEN-12345-ABC",
    "analysis_timestamp": "2023-05-15T14:30:00Z"
}

SAMPLE_VARIANT_INFO = {
    "gene": "NOD2",
    "variant": "R702W",
    "significance": "pathogenic",
    "description": "Missense variant in the NOD2 gene resulting in an arginine to tryptophan substitution at position 702.",
    "impact_on_disease": "Associated with 2-4 fold increased risk of Crohn's disease, particularly ileal Crohn's disease.",
    "frequency": {
        "general_population": 0.04,
        "crohns_patients": 0.15,
        "caucasian": 0.05,
        "asian": 0.01,
        "african": 0.02
    },
    "treatment_implications": [
        {
            "treatment": "Anti-TNF agents",
            "effect": "Reduced efficacy in patients with NOD2 variants",
            "evidence_level": "moderate"
        },
        {
            "treatment": "Vedolizumab",
            "effect": "May have increased efficacy in patients with NOD2 variants",
            "evidence_level": "limited"
        },
        {
            "treatment": "Surgery",
            "effect": "Higher risk of postoperative recurrence",
            "evidence_level": "strong"
        }
    ],
    "literature": [
        {
            "title": "A frameshift mutation in NOD2 associated with susceptibility to Crohn's disease",
            "authors": ["Ogura Y", "Bonen DK", "Inohara N", "et al."],
            "journal": "Nature",
            "year": 2001,
            "doi": "10.1038/35079114",
            "pubmed_id": "11385577",
            "key_findings": "Identification of NOD2 as a susceptibility gene for Crohn's disease."
        },
        {
            "title": "Association between the R702W mutation in the NOD2/CARD15 gene and Crohn's disease in Hungarian and German cohorts",
            "authors": ["Nagy Z", "Karadi O", "Rumi G", "et al."],
            "journal": "World J Gastroenterol",
            "year": 2005,
            "pubmed_id": "16437633",
            "key_findings": "Confirmed the association between R702W mutation and Crohn's disease in European populations."
        }
    ]
}

SAMPLE_TRIAL_PROTOCOL = {
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

SAMPLE_TRIAL_RESULTS = {
    "trial_id": "CROHNS-001",
    "status": "completed",
    "patient_outcomes": [
        {
            "patient_id": "P001",
            "arm": "Upadacitinib 15mg",
            "response": 0.75,
            "adverse_events": ["headache"]
        },
        {
            "patient_id": "P002",
            "arm": "Upadacitinib 30mg",
            "response": 0.82,
            "adverse_events": ["headache", "nausea"]
        },
        {
            "patient_id": "P003",
            "arm": "Placebo",
            "response": 0.35,
            "adverse_events": []
        },
        {
            "patient_id": "P004",
            "arm": "Upadacitinib 15mg",
            "response": 0.68,
            "adverse_events": []
        },
        {
            "patient_id": "P005",
            "arm": "Upadacitinib 30mg",
            "response": 0.79,
            "adverse_events": ["fatigue"]
        }
    ],
    "adaptations": [
        {
            "type": "response_adaptive_randomization",
            "triggerCondition": "interim_analysis_1",
            "timestamp": "2023-06-15T10:30:00Z",
            "parameters": {
                "arm_weights": {
                    "Upadacitinib 15mg": 0.35,
                    "Upadacitinib 30mg": 0.55,
                    "Placebo": 0.1
                }
            }
        },
        {
            "type": "drop_arm",
            "triggerCondition": "interim_analysis_2",
            "timestamp": "2023-07-15T14:45:00Z",
            "parameters": {
                "dropped_arms": ["Placebo"],
                "reason": "low_efficacy"
            }
        }
    ]
}

SAMPLE_TREATMENT_PLAN = {
    "treatment_plan": [
        {
            "medication": "Upadacitinib",
            "dosage": 15.0,
            "unit": "mg",
            "frequency": "daily",
            "duration": 30
        },
        {
            "medication": "Methotrexate",
            "dosage": 15.0,
            "unit": "mg",
            "frequency": "weekly",
            "duration": 30
        }
    ],
    "fitness": 0.85,
    "confidence": 0.78,
    "explanations": [
        "Treatment plan optimized with 0.85 fitness score.",
        "Upadacitinib selected based on patient's biomarker profile and disease characteristics.",
        "Methotrexate selected based on patient's biomarker profile and disease characteristics.",
        "NOD2 variant detected, which may predict increased response to certain biologics.",
        "IL23R variant detected, which may predict better response to IL-23 inhibitors."
    ],
    "biomarker_influences": {
        "NOD2": 0.8,
        "IL23R": 0.7,
        "microbiome_diversity": 0.5,
        "F_prausnitzii": 0.4
    }
}


# Mock implementations for running in mock mode
class MockCodexIntegration:
    """Mock implementation of the codex integration"""
    
    async def initialize(self):
        logger.info("Mock: Initializing codex integration")
        await asyncio.sleep(0.5)
        
    async def shutdown(self):
        logger.info("Mock: Shutting down codex integration")
        await asyncio.sleep(0.2)
        
    async def optimize_patient_treatment(self, patient_data):
        logger.info(f"Mock: Optimizing treatment for patient {patient_data.get('patient_id', 'unknown')}")
        await asyncio.sleep(1.0)
        return SAMPLE_TREATMENT_PLAN
        
    async def run_adaptive_trial(self, trial_protocol, patient_cohort):
        logger.info(f"Mock: Running adaptive trial for protocol {trial_protocol.get('trial_id', 'unknown')}")
        await asyncio.sleep(2.0)
        return SAMPLE_TRIAL_RESULTS
        
    async def monitor_system_health(self):
        logger.info("Mock: Monitoring system health")
        await asyncio.sleep(0.5)
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "components": {
                "genetic_engine": {
                    "status": "healthy",
                    "details": "Operational"
                },
                "clinical_trial_agent": {
                    "status": "healthy",
                    "details": "Operational"
                },
                "supervisor": {
                    "status": "healthy",
                    "details": "Operational"
                }
            }
        }
        
    async def _apply_self_healing(self, results, trial_protocol, patient_cohort):
        logger.info("Mock: Applying self-healing")
        await asyncio.sleep(1.0)
        
        healed_results = {
            "trial_id": results.get("trial_id", "unknown"),
            "status": "completed",
            "healing_applied": True,
            "original_status": results.get("status", "unknown"),
            "patient_outcomes": [],
            "healing_summary": "Self-healing applied to fix trial results anomalies"
        }
        
        # Generate placeholder outcomes
        for i, patient in enumerate(patient_cohort[:5]):
            healed_results["patient_outcomes"].append({
                "patient_id": patient.get("patient_id", f"unknown_{i}"),
                "arm": "placeholder",
                "response": 0.5,
                "adverse_events": [],
                "healed": True
            })
            
        return healed_results


# Mock implementation for genetic sequence analysis
async def mock_analyze_patient_sequences(patient_data):
    """Mock implementation of analyze_patient_sequences"""
    logger.info(f"Mock: Analyzing genetic sequences for patient {patient_data.get('patient_id', 'unknown')}")
    await asyncio.sleep(1.0)
    return SAMPLE_GENETIC_ANALYSIS_RESULT

async def mock_get_crohns_variant_info(gene, variant):
    """Mock implementation of get_crohns_variant_info"""
    logger.info(f"Mock: Getting variant info for {gene} {variant}")
    await asyncio.sleep(0.5)
    return SAMPLE_VARIANT_INFO


class MockTrialDataTransformer:
    """Mock implementation of the trial data transformer"""
    
    def __init__(self, config=None):
        self.config = config or {}
        logger.info("Mock: Initializing trial data transformer")
        
    def csv_to_patient_profiles(self, csv_path):
        logger.info(f"Mock: Transforming CSV data from {csv_path}")
        # Return a list of sample patients
        return [SAMPLE_PATIENT for _ in range(5)]
        
    def transform_patient_for_genetic_engine(self, patient):
        logger.info(f"Mock: Transforming patient {patient.get('patient_id', 'unknown')} for genetic engine")
        # Return a simplified version with just the essential fields
        return {
            "patient_id": patient.get("patient_id", "unknown"),
            "age": patient.get("demographics", {}).get("age", 0),
            "weight": patient.get("demographics", {}).get("weight", 0),
            "crohns_type": patient.get("clinical_data", {}).get("crohns_type", ""),
            "severity": "moderate",
            "genetic_markers": {marker.get("gene"): marker.get("variant") 
                              for marker in patient.get("biomarkers", {}).get("genetic_markers", [])},
            "biomarker_values": {
                "CRP": patient.get("biomarkers", {}).get("serum_markers", {}).get("CRP", 0),
                "ESR": patient.get("biomarkers", {}).get("serum_markers", {}).get("ESR", 0)
            }
        }
        
    def hms_ehr_to_patient_profile(self, ehr_data):
        logger.info("Mock: Transforming EHR data to patient profile")
        return SAMPLE_PATIENT


class MockTrialResultsVisualizer:
    """Mock implementation of the trial results visualizer"""
    
    def __init__(self, config=None):
        self.config = config or {}
        logger.info("Mock: Initializing trial results visualizer")
        
    def create_trial_summary_dashboard(self, trial_results):
        logger.info(f"Mock: Creating dashboard for trial {trial_results.get('trial_id', 'unknown')}")
        
        # Create simple visualizations
        visualizations = {}
        
        # Response by arm visualization
        plt.figure(figsize=(10, 6))
        df = pd.DataFrame(trial_results.get("patient_outcomes", []))
        sns.barplot(x="arm", y="response", data=df)
        plt.title("Patient Response by Treatment Arm")
        plt.ylim(0, 1)
        plt.tight_layout()
        
        # Save to buffer and convert to base64
        import io
        import base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        visualizations['response_by_arm'] = base64.b64encode(buf.read()).decode('utf-8')
        
        # Add more mock visualizations
        visualizations['response_distribution'] = visualizations['response_by_arm']
        visualizations['trial_summary'] = visualizations['response_by_arm']
        
        return visualizations
        
    def save_visualizations(self, visualizations, output_dir):
        logger.info(f"Mock: Saving {len(visualizations)} visualizations to {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Save each visualization (in mock mode, they're all the same image)
        for name, img_data in visualizations.items():
            import base64
            img_binary = base64.b64decode(img_data)
            
            with open(os.path.join(output_dir, f"{name}.png"), 'wb') as f:
                f.write(img_binary)
                
    def generate_html_report(self, trial_results, output_file):
        logger.info(f"Mock: Generating HTML report for trial {trial_results.get('trial_id', 'unknown')}")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Create a simple HTML report
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Trial Results: {trial_results.get('trial_id', 'unknown')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #4b6cb7; color: white; padding: 20px; }}
        .section {{ background-color: white; padding: 20px; margin: 20px 0; }}
        h1, h2, h3 {{ color: #4b6cb7; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Adaptive Clinical Trial Results</h1>
        <p>Trial ID: {trial_results.get('trial_id', 'unknown')}</p>
        <p>Status: {trial_results.get('status', 'unknown')}</p>
    </div>
    <div class="section">
        <h2>Mock Report</h2>
        <p>This is a mock HTML report for demonstration purposes.</p>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html)
            
    def visualize_patient_specific_results(self, patient_data, treatment_plan):
        logger.info(f"Mock: Creating visualizations for patient {patient_data.get('patient_id', 'unknown')}")
        
        # Create simple visualizations
        visualizations = {}
        
        # Treatment plan visualization
        plt.figure(figsize=(10, 6))
        medications = treatment_plan.get('treatment_plan', [])
        med_names = [med.get('medication', '') for med in medications]
        dosages = [med.get('dosage', 0) for med in medications]
        
        sns.barplot(x=med_names, y=dosages)
        plt.title("Treatment Plan Medications")
        plt.tight_layout()
        
        # Save to buffer and convert to base64
        import io
        import base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        visualizations['treatment_plan'] = base64.b64encode(buf.read()).decode('utf-8')
        
        # Add more mock visualizations
        visualizations['biomarker_influence'] = visualizations['treatment_plan']
        visualizations['confidence_breakdown'] = visualizations['treatment_plan']
        
        return visualizations
    
    def visualize_genetic_analysis(self, genetic_analysis):
        """Create visualizations for genetic analysis results"""
        logger.info(f"Creating visualizations for genetic analysis {genetic_analysis.get('analysis_id', 'unknown')}")
        
        visualizations = {}
        
        # Variant impact visualization
        plt.figure(figsize=(10, 6))
        variants = genetic_analysis.get('variants', [])
        gene_names = [var.get('gene', '') + ' ' + var.get('variant_id', '') for var in variants]
        impact_scores = [var.get('impact_score', 0) for var in variants]
        
        # Create color map based on clinical significance
        significance_colors = {
            'pathogenic': 'red',
            'likely_pathogenic': 'orange',
            'uncertain': 'gray',
            'likely_benign': 'lightblue',
            'benign': 'blue',
            'protective': 'green',
            'risk factor': 'orange'
        }
        
        colors = [significance_colors.get(var.get('clinical_significance', ''), 'gray') for var in variants]
        
        # Plot with custom colors
        plt.figure(figsize=(10, 6))
        bars = plt.bar(gene_names, impact_scores, color=colors)
        plt.title("Genetic Variant Impact Scores")
        plt.ylim(0, 1)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color, label=sig) 
                          for sig, color in significance_colors.items()
                          if sig in [var.get('clinical_significance', '') for var in variants]]
        plt.legend(handles=legend_elements, title="Clinical Significance")
        
        # Save to buffer and convert to base64
        import io
        import base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        visualizations['variant_impact'] = base64.b64encode(buf.read()).decode('utf-8')
        
        # Treatment recommendations visualization
        plt.figure(figsize=(10, 6))
        treatments = genetic_analysis.get('treatment_recommendations', [])
        treatment_names = [t.get('treatment', '') for t in treatments]
        efficacy_scores = [t.get('expected_efficacy', 0) for t in treatments]
        confidence_scores = [t.get('confidence', 0) for t in treatments]
        
        # Use DataFrame for grouped bar chart
        df = pd.DataFrame({
            'Treatment': treatment_names,
            'Expected Efficacy': efficacy_scores,
            'Confidence': confidence_scores
        })
        
        # Reshape for seaborn
        df_melted = pd.melt(df, id_vars=['Treatment'], var_name='Metric', value_name='Score')
        
        # Create grouped bar chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Treatment', y='Score', hue='Metric', data=df_melted)
        plt.title("Treatment Recommendations Based on Genetic Analysis")
        plt.ylim(0, 1)
        plt.tight_layout()
        
        # Save to buffer and convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        visualizations['treatment_recommendations'] = base64.b64encode(buf.read()).decode('utf-8')
        
        return visualizations


# If in mock mode, use mock implementations
if MOCK_MODE:
    codex_integration = MockCodexIntegration()
    TrialDataTransformer = MockTrialDataTransformer
    TrialResultsVisualizer = MockTrialResultsVisualizer
    analyze_patient_sequences = mock_analyze_patient_sequences
    get_crohns_variant_info = mock_get_crohns_variant_info


async def demo_treatment_optimization():
    """Demonstrate treatment optimization"""
    print("\n" + "="*80)
    print("TREATMENT OPTIMIZATION DEMO")
    print("="*80)
    
    # Initialize components
    await codex_integration.initialize()
    transformer = TrialDataTransformer()
    
    try:
        print("\nPatient Profile:")
        print("--------------")
        print(f"ID: {SAMPLE_PATIENT['patient_id']}")
        print(f"Age: {SAMPLE_PATIENT['demographics']['age']}")
        print(f"Sex: {SAMPLE_PATIENT['demographics']['sex']}")
        print(f"Crohn's Type: {SAMPLE_PATIENT['clinical_data']['crohns_type']}")
        print(f"CDAI: {SAMPLE_PATIENT['clinical_data']['disease_activity']['CDAI']}")
        print(f"Fecal Calprotectin: {SAMPLE_PATIENT['clinical_data']['disease_activity']['fecal_calprotectin']}")
        
        print("\nBiomarkers:")
        for marker in SAMPLE_PATIENT['biomarkers']['genetic_markers']:
            print(f"- {marker['gene']}: {marker['variant']} ({marker['zygosity']})")
        
        print("\nTransforming patient data for genetic engine...")
        genetic_format = transformer.transform_patient_for_genetic_engine(SAMPLE_PATIENT)
        
        print("\nOptimizing treatment...")
        treatment_plan = await codex_integration.optimize_patient_treatment(genetic_format)
        
        print("\nOptimized Treatment Plan:")
        print("=======================")
        for med in treatment_plan['treatment_plan']:
            print(f"• {med['medication']} {med['dosage']}{med['unit']} {med['frequency']} for {med['duration']} days")
        
        print(f"\nTreatment Fitness: {treatment_plan['fitness']:.2f}")
        
        if 'explanations' in treatment_plan:
            print("\nRationale:")
            for explanation in treatment_plan['explanations']:
                print(f"• {explanation}")
        
        # Create output directory
        os.makedirs('demo_output/treatment', exist_ok=True)
        
        # Save treatment plan to file
        with open('demo_output/treatment/treatment_plan.json', 'w') as f:
            json.dump(treatment_plan, f, indent=2)
        
        print("\nTreatment plan saved to demo_output/treatment/treatment_plan.json")
        
        # Create visualizations if available
        visualizer = TrialResultsVisualizer()
        patient_viz = visualizer.visualize_patient_specific_results(SAMPLE_PATIENT, treatment_plan)
        
        # Save visualizations
        os.makedirs('demo_output/treatment/visualizations', exist_ok=True)
        for name, img_data in patient_viz.items():
            import base64
            img_binary = base64.b64decode(img_data)
            
            with open(f'demo_output/treatment/visualizations/{name}.png', 'wb') as f:
                f.write(img_binary)
        
        print(f"\nVisualizations saved to demo_output/treatment/visualizations/")
        
    finally:
        # Shutdown
        await codex_integration.shutdown()


async def demo_genetic_sequence_analysis():
    """Demonstrate genetic sequence analysis capabilities"""
    print("\n" + "="*80)
    print("GENETIC SEQUENCE ANALYSIS DEMO")
    print("="*80)
    
    try:
        print("\nPatient Genetic Data:")
        print("--------------------")
        print(f"Patient ID: {SAMPLE_GENETIC_DATA['patient_id']}")
        print(f"Age: {SAMPLE_GENETIC_DATA['demographic']['age']}")
        print(f"Sex: {SAMPLE_GENETIC_DATA['demographic']['sex']}")
        print(f"Family History: {'Positive' if SAMPLE_GENETIC_DATA['demographic']['family_history'] else 'Negative'}")
        
        print("\nSequenced Genes:")
        for gene, sequence in SAMPLE_GENETIC_DATA['sequences'].items():
            print(f"• {gene}: {len(sequence)} base pairs")
        
        print("\nAnalyzing genetic sequences...")
        analysis_result = await analyze_patient_sequences(SAMPLE_GENETIC_DATA)
        
        print("\nGenetic Analysis Results:")
        print("=======================")
        print(f"Analysis ID: {analysis_result.get('analysis_id', 'unknown')}")
        print(f"Analysis Date: {analysis_result.get('analysis_timestamp', 'unknown')}")
        
        print("\nIdentified Variants:")
        for variant in analysis_result.get('variants', []):
            significance = variant.get('clinical_significance', '')
            significance_indicator = "⚠️" if significance in ["pathogenic", "likely_pathogenic", "risk factor"] else "✅" if significance == "protective" else "ℹ️"
            print(f"{significance_indicator} {variant.get('gene', '')}: {variant.get('variant_id', '')} ({variant.get('zygosity', '')})")
            print(f"   {variant.get('description', '')}")
        
        print("\nRisk Assessment:")
        risk = analysis_result.get('risk_assessment', {})
        print(f"Overall Risk: {risk.get('overall_risk', 'unknown').upper()} (Score: {risk.get('risk_score', 0):.2f})")
        print("Contributing Factors:")
        for factor in risk.get('contributing_factors', []):
            print(f"• {factor.get('factor', '')}: {factor.get('description', '')}")
        
        print("\nTreatment Recommendations:")
        for i, rec in enumerate(analysis_result.get('treatment_recommendations', []), 1):
            print(f"{i}. {rec.get('treatment', '')} - Expected Efficacy: {rec.get('expected_efficacy', 0):.2f}")
            print(f"   Genetic Basis: {', '.join([g.get('gene', '') + ' ' + g.get('variant', '') for g in rec.get('genetic_basis', [])])}")
            
            if rec.get('contraindications', []):
                print(f"   ⚠️ Contraindications: {', '.join(rec.get('contraindications', []))}")
        
        # Get detailed information about a specific variant
        print("\nRetrieving detailed information for NOD2 R702W variant...")
        variant_info = await get_crohns_variant_info("NOD2", "R702W")
        
        print("\nNOD2 R702W Variant Details:")
        print("=========================")
        print(f"Clinical Significance: {variant_info.get('significance', '')}")
        print(f"Description: {variant_info.get('description', '')}")
        print(f"Disease Impact: {variant_info.get('impact_on_disease', '')}")
        
        print("\nPopulation Frequency:")
        frequencies = variant_info.get('frequency', {})
        for population, freq in frequencies.items():
            print(f"• {population.replace('_', ' ').title()}: {freq:.2%}")
        
        print("\nTreatment Implications:")
        for implication in variant_info.get('treatment_implications', []):
            print(f"• {implication.get('treatment', '')}: {implication.get('effect', '')}")
            print(f"  Evidence Level: {implication.get('evidence_level', '').title()}")
        
        # Create output directory
        os.makedirs('demo_output/genetic_analysis', exist_ok=True)
        
        # Save analysis results to file
        with open('demo_output/genetic_analysis/analysis_results.json', 'w') as f:
            json.dump(analysis_result, f, indent=2)
        
        # Save variant info to file
        with open('demo_output/genetic_analysis/NOD2_R702W_info.json', 'w') as f:
            json.dump(variant_info, f, indent=2)
        
        print("\nAnalysis results saved to demo_output/genetic_analysis/analysis_results.json")
        print("Variant details saved to demo_output/genetic_analysis/NOD2_R702W_info.json")
        
        # Create visualizations for genetic analysis
        visualizer = TrialResultsVisualizer()
        genetic_viz = visualizer.visualize_genetic_analysis(analysis_result)
        
        # Save visualizations
        os.makedirs('demo_output/genetic_analysis/visualizations', exist_ok=True)
        for name, img_data in genetic_viz.items():
            import base64
            img_binary = base64.b64decode(img_data)
            
            with open(f'demo_output/genetic_analysis/visualizations/{name}.png', 'wb') as f:
                f.write(img_binary)
        
        print(f"\nVisualizations saved to demo_output/genetic_analysis/visualizations/")
        
    except Exception as e:
        logger.error(f"Error in genetic sequence analysis demo: {e}")
        print(f"\nError in genetic sequence analysis demo: {e}")


async def demo_adaptive_trial():
    """Demonstrate adaptive trial execution"""
    print("\n" + "="*80)
    print("ADAPTIVE CLINICAL TRIAL DEMO")
    print("="*80)
    
    # Initialize components
    await codex_integration.initialize()
    transformer = TrialDataTransformer()
    visualizer = TrialResultsVisualizer()
    
    try:
        print("\nTrial Protocol:")
        print("--------------")
        print(f"ID: {SAMPLE_TRIAL_PROTOCOL['trial_id']}")
        print(f"Title: {SAMPLE_TRIAL_PROTOCOL['title']}")
        print(f"Phase: {SAMPLE_TRIAL_PROTOCOL['phase']}")
        
        print("\nTreatment Arms:")
        for arm in SAMPLE_TRIAL_PROTOCOL['arms']:
            print(f"• {arm['name']}: {arm['treatment']['medication']} {arm['treatment']['dosage']}{arm['treatment']['unit']} {arm['treatment']['frequency']}")
        
        print("\nAdaptive Rules:")
        for rule in SAMPLE_TRIAL_PROTOCOL['adaptiveRules']:
            print(f"• {rule['action']} triggered by {rule['triggerCondition']}")
        
        print("\nGenerating patient cohort...")
        patient_cohort = transformer.csv_to_patient_profiles('demo_data/patients.csv' if not MOCK_MODE else 'mock_patients.csv')
        print(f"Generated cohort with {len(patient_cohort)} patients")
        
        print("\nTransforming patient data for trial...")
        trial_patients = []
        for patient in patient_cohort:
            genetic_format = transformer.transform_patient_for_genetic_engine(patient)
            trial_patients.append(genetic_format)
        
        print("\nRunning adaptive trial...")
        trial_results = await codex_integration.run_adaptive_trial(SAMPLE_TRIAL_PROTOCOL, trial_patients)
        
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
        
        # Create output directory
        os.makedirs('demo_output/trial', exist_ok=True)
        
        # Save trial results to file
        with open('demo_output/trial/trial_results.json', 'w') as f:
            json.dump(trial_results, f, indent=2)
        
        print("\nTrial results saved to demo_output/trial/trial_results.json")
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        visualizations = visualizer.create_trial_summary_dashboard(trial_results)
        
        # Save visualizations
        os.makedirs('demo_output/trial/visualizations', exist_ok=True)
        visualizer.save_visualizations(visualizations, 'demo_output/trial/visualizations')
        
        # Generate HTML report
        visualizer.generate_html_report(trial_results, 'demo_output/trial/trial_report.html')
        
        print("\nTrial report generated at demo_output/trial/trial_report.html")
        print("Individual visualizations saved in demo_output/trial/visualizations/")
        
    finally:
        # Shutdown
        await codex_integration.shutdown()


async def demo_self_healing():
    """Demonstrate self-healing capabilities"""
    print("\n" + "="*80)
    print("SELF-HEALING SYSTEM DEMO")
    print("="*80)
    
    # Initialize components
    await codex_integration.initialize()
    
    try:
        # Create output directory
        os.makedirs('demo_output/self_healing', exist_ok=True)
        
        print("\nDemonstrating self-healing capabilities")
        print("=====================================")
        
        # Step 1: Run a healthy trial as baseline
        print("\nStep 1: Running healthy trial as baseline...")
        healthy_results = SAMPLE_TRIAL_RESULTS
        
        # Save healthy results
        with open('demo_output/self_healing/healthy_results.json', 'w') as f:
            json.dump(healthy_results, f, indent=2)
        
        print(f"Healthy trial completed with {len(healthy_results['patient_outcomes'])} patient outcomes")
        
        # Step 2: Create a corrupted version of the results
        print("\nStep 2: Simulating failure conditions...")
        corrupted_results = healthy_results.copy()
        corrupted_results['status'] = 'error'
        corrupted_results['patient_outcomes'] = []  # Remove all outcomes
        corrupted_results['error'] = 'Simulation failure'
        
        # Save corrupted results
        with open('demo_output/self_healing/corrupted_results.json', 'w') as f:
            json.dump(corrupted_results, f, indent=2)
        
        # Step 3: Apply self-healing to the corrupted results
        print("\nStep 3: Applying self-healing...")
        healed_results = await codex_integration._apply_self_healing(
            corrupted_results, SAMPLE_TRIAL_PROTOCOL, [SAMPLE_PATIENT] * 5
        )
        
        # Save healed results
        with open('demo_output/self_healing/healed_results.json', 'w') as f:
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
        print("• demo_output/self_healing/healthy_results.json")
        print("• demo_output/self_healing/corrupted_results.json")
        print("• demo_output/self_healing/healed_results.json")
        
    finally:
        # Shutdown
        await codex_integration.shutdown()


async def demo_system_health():
    """Demonstrate system health monitoring"""
    print("\n" + "="*80)
    print("SYSTEM HEALTH MONITORING DEMO")
    print("="*80)
    
    # Initialize components
    await codex_integration.initialize()
    
    try:
        # Monitor system health
        print("\nMonitoring system health...")
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
        os.makedirs('demo_output/monitoring', exist_ok=True)
        
        # Save health report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f'demo_output/monitoring/health_report_{timestamp}.json'
        
        with open(report_path, 'w') as f:
            json.dump(health, f, indent=2)
        
        print(f"\nHealth report saved to '{report_path}'")
        
    finally:
        # Shutdown
        await codex_integration.shutdown()


async def run_full_demo():
    """Run all demo components"""
    # Create main output directory
    os.makedirs('demo_output', exist_ok=True)
    
    # Welcome message
    print("\n" + "="*80)
    print("Welcome to the Crohn's Disease Treatment System Demo")
    print("="*80)
    print("\nThis demo showcases the following capabilities:")
    print("1. Genetic sequence analysis for Crohn's disease")
    print("2. Treatment optimization for individual patients")
    print("3. Adaptive clinical trial execution")
    print("4. Self-healing system capabilities")
    print("5. System health monitoring")
    
    if MOCK_MODE:
        print("\nRunning in MOCK MODE - using simulated data and functionality")
    else:
        print("\nRunning with ACTUAL SYSTEM COMPONENTS")
    
    # Run all demos
    await demo_genetic_sequence_analysis()
    await demo_treatment_optimization()
    await demo_adaptive_trial()
    await demo_self_healing()
    await demo_system_health()
    
    # Summary
    print("\n" + "="*80)
    print("Demo Complete!")
    print("="*80)
    print("\nAll output files have been saved to the 'demo_output' directory.")
    print("\nKey files to examine:")
    print("• demo_output/genetic_analysis/analysis_results.json")
    print("• demo_output/genetic_analysis/visualizations/")
    print("• demo_output/treatment/treatment_plan.json")
    print("• demo_output/treatment/visualizations/")
    print("• demo_output/trial/trial_report.html")
    print("• demo_output/trial/visualizations/")
    print("• demo_output/self_healing/")
    
    print("\nThank you for exploring the Crohn's Disease Treatment System!")


def main():
    """Main entry point for the demo script"""
    parser = argparse.ArgumentParser(description='Crohn\'s Disease Treatment System Demo')
    parser.add_argument('--genetic-only', action='store_true', help='Run only the genetic sequence analysis demo')
    parser.add_argument('--treatment-only', action='store_true', help='Run only the treatment optimization demo')
    parser.add_argument('--trial-only', action='store_true', help='Run only the adaptive trial demo')
    parser.add_argument('--healing-only', action='store_true', help='Run only the self-healing demo')
    parser.add_argument('--health-only', action='store_true', help='Run only the system health demo')
    parser.add_argument('--output-dir', help='Output directory for demo files (default: demo_output)')
    
    args = parser.parse_args()
    
    # Set output directory if specified
    if args.output_dir:
        global demo_output_dir
        demo_output_dir = args.output_dir
    
    # Run the appropriate demo(s)
    if args.genetic_only:
        asyncio.run(demo_genetic_sequence_analysis())
    elif args.treatment_only:
        asyncio.run(demo_treatment_optimization())
    elif args.trial_only:
        asyncio.run(demo_adaptive_trial())
    elif args.healing_only:
        asyncio.run(demo_self_healing())
    elif args.health_only:
        asyncio.run(demo_system_health())
    else:
        asyncio.run(run_full_demo())


if __name__ == "__main__":
    main()