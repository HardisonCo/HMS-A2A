#!/usr/bin/env python3
"""
AI Agency Generator

This script generates components for AI-focused agencies based on the
HMS-DEV agency integration plan. It creates connectors, issue finders,
and ASCII art for AI domain-specific agencies.
"""

import os
import sys
import json
import argparse
from string import Template
from datetime import datetime
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import base generator
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# AI domain specifications
AI_DOMAIN_TEMPLATES = {
    "healthcare": {
        "DEFAULT_DOMAINS": {
            "clinical_trials": ["trial_design", "participant_recruitment", "result_analysis"],
            "diagnostics": ["imaging_analysis", "biomarker_detection", "predictive_diagnostics"],
            "treatment_planning": ["personalized_medicine", "therapy_optimization", "outcome_prediction"],
            "drug_discovery": ["target_identification", "lead_optimization", "safety_assessment"],
            "regulatory_compliance": ["standards_adherence", "documentation_validation", "approval_process"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "clinical_trials": {
                "description": "AI-driven design and analysis of clinical trials",
                "sub_domains": ["trial_design", "participant_recruitment", "result_analysis"]
            },
            "diagnostics": {
                "description": "AI-powered diagnostic systems and tools",
                "sub_domains": ["imaging_analysis", "biomarker_detection", "predictive_diagnostics"]
            },
            "treatment_planning": {
                "description": "AI assistance for treatment planning and optimization",
                "sub_domains": ["personalized_medicine", "therapy_optimization", "outcome_prediction"]
            },
            "drug_discovery": {
                "description": "AI-enhanced drug discovery and development",
                "sub_domains": ["target_identification", "lead_optimization", "safety_assessment"]
            },
            "regulatory_compliance": {
                "description": "AI for regulatory compliance and documentation",
                "sub_domains": ["standards_adherence", "documentation_validation", "approval_process"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "fda_ai_guidance": {
                "name": "FDA Guidance on AI/ML in Medical Devices",
                "description": "Regulatory framework for AI-based medical devices",
                "components": ["validation", "monitoring", "updates"]
            },
            "hipaa_ai": {
                "name": "HIPAA AI Compliance Framework",
                "description": "Privacy and security for AI in healthcare",
                "components": ["data_protection", "access_control", "audit_trails"]
            },
            "ai_clinical_trials": {
                "name": "AI in Clinical Trials Framework",
                "description": "Guidelines for using AI in clinical trials",
                "components": ["protocol_design", "data_analysis", "reporting"]
            },
            "ai_diagnostics": {
                "name": "AI Diagnostic Systems Framework",
                "description": "Standards for AI-based diagnostic systems",
                "components": ["accuracy", "explainability", "clinical_validation"]
            },
            "ai_therapeutics": {
                "name": "AI Therapeutic Systems Framework",
                "description": "Guidelines for AI-based therapeutic systems",
                "components": ["efficacy", "safety", "monitoring"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["diagnostics", "treatment_planning", "regulatory_compliance"]
    },
    "agriculture": {
        "DEFAULT_DOMAINS": {
            "crop_protection": ["disease_detection", "pest_management", "treatment_optimization"],
            "yield_optimization": ["growth_prediction", "resource_allocation", "harvest_planning"],
            "animal_health": ["disease_surveillance", "welfare_monitoring", "nutrition_optimization"],
            "inspection_systems": ["quality_assessment", "contamination_detection", "compliance_verification"],
            "environmental_monitoring": ["soil_analysis", "water_quality", "climate_impact"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "crop_protection": {
                "description": "AI-driven crop disease and pest management",
                "sub_domains": ["disease_detection", "pest_management", "treatment_optimization"]
            },
            "yield_optimization": {
                "description": "AI-powered crop yield optimization",
                "sub_domains": ["growth_prediction", "resource_allocation", "harvest_planning"]
            },
            "animal_health": {
                "description": "AI-enhanced animal health monitoring",
                "sub_domains": ["disease_surveillance", "welfare_monitoring", "nutrition_optimization"]
            },
            "inspection_systems": {
                "description": "AI-based agricultural inspection systems",
                "sub_domains": ["quality_assessment", "contamination_detection", "compliance_verification"]
            },
            "environmental_monitoring": {
                "description": "AI for agricultural environmental monitoring",
                "sub_domains": ["soil_analysis", "water_quality", "climate_impact"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "usda_ai_guidelines": {
                "name": "USDA AI Guidelines",
                "description": "Guidelines for AI use in agriculture",
                "components": ["model_validation", "data_standards", "implementation"]
            },
            "aphis_ai_framework": {
                "name": "APHIS AI Framework",
                "description": "Framework for AI in animal and plant health",
                "components": ["surveillance", "detection", "response"]
            },
            "precision_agriculture": {
                "name": "Precision Agriculture Standards",
                "description": "Standards for AI in precision agriculture",
                "components": ["sensing", "analysis", "application"]
            },
            "food_safety_ai": {
                "name": "Food Safety AI Framework",
                "description": "Framework for AI in food safety",
                "components": ["hazard_detection", "traceability", "mitigation"]
            },
            "agricultural_data": {
                "name": "Agricultural Data Framework",
                "description": "Framework for agricultural data management",
                "components": ["collection", "privacy", "sharing"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["crop_protection", "animal_health", "inspection_systems"]
    },
    "safety": {
        "DEFAULT_DOMAINS": {
            "product_risk_assessment": ["hazard_identification", "exposure_analysis", "risk_characterization"],
            "defect_detection": ["automated_inspection", "anomaly_detection", "quality_control"],
            "consumer_behavior": ["usage_analysis", "misuse_prediction", "injury_prevention"],
            "recall_prediction": ["failure_analysis", "statistical_modeling", "early_warning"],
            "standards_compliance": ["regulation_analysis", "conformity_assessment", "documentation_validation"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "product_risk_assessment": {
                "description": "AI-driven product risk assessment",
                "sub_domains": ["hazard_identification", "exposure_analysis", "risk_characterization"]
            },
            "defect_detection": {
                "description": "AI-powered detection of product defects",
                "sub_domains": ["automated_inspection", "anomaly_detection", "quality_control"]
            },
            "consumer_behavior": {
                "description": "AI analysis of consumer product usage",
                "sub_domains": ["usage_analysis", "misuse_prediction", "injury_prevention"]
            },
            "recall_prediction": {
                "description": "AI for predicting and preventing product recalls",
                "sub_domains": ["failure_analysis", "statistical_modeling", "early_warning"]
            },
            "standards_compliance": {
                "description": "AI verification of product safety standards",
                "sub_domains": ["regulation_analysis", "conformity_assessment", "documentation_validation"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "cpsc_ai_guidelines": {
                "name": "CPSC AI Guidelines",
                "description": "Guidelines for AI in consumer product safety",
                "components": ["risk_assessment", "monitoring", "reporting"]
            },
            "product_safety_ai": {
                "name": "Product Safety AI Framework",
                "description": "Framework for AI in product safety",
                "components": ["design_safety", "manufacturing_quality", "post-market_surveillance"]
            },
            "recall_effectiveness": {
                "name": "Recall Effectiveness Framework",
                "description": "Framework for AI in recall effectiveness",
                "components": ["identification", "notification", "remedy"]
            },
            "safety_data_analysis": {
                "name": "Safety Data Analysis Framework",
                "description": "Framework for analyzing safety data with AI",
                "components": ["data_collection", "pattern_recognition", "casualty_assessment"]
            },
            "safety_standards": {
                "name": "Safety Standards AI Framework",
                "description": "Framework for AI in safety standards assessment",
                "components": ["requirements_extraction", "compliance_verification", "gap_analysis"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["product_risk_assessment", "defect_detection", "recall_prediction"]
    },
    "environment": {
        "DEFAULT_DOMAINS": {
            "environmental_assessment": ["impact_prediction", "risk_analysis", "compliance_verification"],
            "safety_monitoring": ["equipment_inspection", "operations_oversight", "incident_detection"],
            "emergency_response": ["spill_detection", "containment_planning", "damage_assessment"],
            "resource_management": ["energy_optimization", "waste_reduction", "efficiency_improvement"],
            "regulatory_compliance": ["documentation_validation", "permit_management", "reporting_automation"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "environmental_assessment": {
                "description": "AI-driven environmental impact assessment",
                "sub_domains": ["impact_prediction", "risk_analysis", "compliance_verification"]
            },
            "safety_monitoring": {
                "description": "AI-powered monitoring of safety systems",
                "sub_domains": ["equipment_inspection", "operations_oversight", "incident_detection"]
            },
            "emergency_response": {
                "description": "AI assistance for environmental emergencies",
                "sub_domains": ["spill_detection", "containment_planning", "damage_assessment"]
            },
            "resource_management": {
                "description": "AI optimization of resource utilization",
                "sub_domains": ["energy_optimization", "waste_reduction", "efficiency_improvement"]
            },
            "regulatory_compliance": {
                "description": "AI for regulatory compliance management",
                "sub_domains": ["documentation_validation", "permit_management", "reporting_automation"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "bsee_ai_guidelines": {
                "name": "BSEE AI Guidelines",
                "description": "Guidelines for AI in offshore energy safety",
                "components": ["risk_assessment", "monitoring", "emergency_response"]
            },
            "environmental_impact": {
                "name": "Environmental Impact AI Framework",
                "description": "Framework for AI in environmental impact assessment",
                "components": ["baseline_assessment", "impact_prediction", "mitigation_planning"]
            },
            "safety_systems": {
                "name": "Safety Systems AI Framework",
                "description": "Framework for AI in safety system monitoring",
                "components": ["real-time_monitoring", "anomaly_detection", "predictive_maintenance"]
            },
            "emergency_management": {
                "name": "Emergency Management AI Framework",
                "description": "Framework for AI in emergency management",
                "components": ["detection", "response_planning", "recovery"]
            },
            "compliance_management": {
                "name": "Compliance Management AI Framework",
                "description": "Framework for AI in compliance management",
                "components": ["requirements_tracking", "documentation", "reporting"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["environmental_assessment", "safety_monitoring", "emergency_response"]
    },
    "finance": {
        "DEFAULT_DOMAINS": {
            "risk_assessment": ["fraud_detection", "credit_scoring", "market_analysis"],
            "market_monitoring": ["trend_analysis", "volatility_prediction", "anomaly_detection"],
            "mortgage_analysis": ["application_processing", "risk_modeling", "default_prediction"],
            "policy_impact": ["economic_modeling", "scenario_analysis", "outcome_prediction"],
            "regulatory_compliance": ["documentation_validation", "reporting_automation", "audit_support"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "risk_assessment": {
                "description": "AI-driven financial risk assessment",
                "sub_domains": ["fraud_detection", "credit_scoring", "market_analysis"]
            },
            "market_monitoring": {
                "description": "AI-powered monitoring of financial markets",
                "sub_domains": ["trend_analysis", "volatility_prediction", "anomaly_detection"]
            },
            "mortgage_analysis": {
                "description": "AI analysis of mortgage applications and risks",
                "sub_domains": ["application_processing", "risk_modeling", "default_prediction"]
            },
            "policy_impact": {
                "description": "AI modeling of policy impacts on housing finance",
                "sub_domains": ["economic_modeling", "scenario_analysis", "outcome_prediction"]
            },
            "regulatory_compliance": {
                "description": "AI for financial regulatory compliance",
                "sub_domains": ["documentation_validation", "reporting_automation", "audit_support"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "fhfa_ai_guidelines": {
                "name": "FHFA AI Guidelines",
                "description": "Guidelines for AI in housing finance",
                "components": ["fairness", "transparency", "accountability"]
            },
            "financial_risk": {
                "name": "Financial Risk AI Framework",
                "description": "Framework for AI in financial risk management",
                "components": ["risk_identification", "risk_assessment", "risk_mitigation"]
            },
            "market_stability": {
                "name": "Market Stability AI Framework",
                "description": "Framework for AI in market stability monitoring",
                "components": ["early_warning", "stress_testing", "intervention_analysis"]
            },
            "housing_policy": {
                "name": "Housing Policy AI Framework",
                "description": "Framework for AI in housing policy analysis",
                "components": ["economic_modeling", "demographic_analysis", "impact_assessment"]
            },
            "mortgage_analytics": {
                "name": "Mortgage Analytics AI Framework",
                "description": "Framework for AI in mortgage analytics",
                "components": ["origination", "servicing", "secondary_market"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["risk_assessment", "mortgage_analysis", "policy_impact"]
    },
    "nutrition": {
        "DEFAULT_DOMAINS": {
            "nutrition_analysis": ["dietary_assessment", "nutrient_profiling", "meal_planning"],
            "policy_modeling": ["program_impact", "intervention_analysis", "outcome_prediction"],
            "population_monitoring": ["consumption_patterns", "nutritional_status", "health_outcomes"],
            "education_outreach": ["personalized_guidance", "material_optimization", "engagement_analysis"],
            "data_integration": ["survey_analysis", "research_synthesis", "knowledge_management"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "nutrition_analysis": {
                "description": "AI-driven nutrition analysis and planning",
                "sub_domains": ["dietary_assessment", "nutrient_profiling", "meal_planning"]
            },
            "policy_modeling": {
                "description": "AI modeling of nutrition policy impacts",
                "sub_domains": ["program_impact", "intervention_analysis", "outcome_prediction"]
            },
            "population_monitoring": {
                "description": "AI analysis of population nutrition patterns",
                "sub_domains": ["consumption_patterns", "nutritional_status", "health_outcomes"]
            },
            "education_outreach": {
                "description": "AI-enhanced nutrition education",
                "sub_domains": ["personalized_guidance", "material_optimization", "engagement_analysis"]
            },
            "data_integration": {
                "description": "AI integration of nutrition data sources",
                "sub_domains": ["survey_analysis", "research_synthesis", "knowledge_management"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "cnpp_ai_guidelines": {
                "name": "CNPP AI Guidelines",
                "description": "Guidelines for AI in nutrition policy",
                "components": ["data_standards", "modeling", "evaluation"]
            },
            "dietary_guidelines": {
                "name": "Dietary Guidelines AI Framework",
                "description": "Framework for AI in dietary guidelines development",
                "components": ["evidence_synthesis", "recommendation_formulation", "impact_assessment"]
            },
            "nutrition_monitoring": {
                "name": "Nutrition Monitoring AI Framework",
                "description": "Framework for AI in nutrition monitoring",
                "components": ["survey_design", "data_collection", "analysis"]
            },
            "program_evaluation": {
                "name": "Nutrition Program Evaluation Framework",
                "description": "Framework for AI in nutrition program evaluation",
                "components": ["design", "implementation", "outcomes"]
            },
            "consumer_education": {
                "name": "Nutrition Education AI Framework",
                "description": "Framework for AI in nutrition education",
                "components": ["personalization", "delivery", "assessment"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["nutrition_analysis", "policy_modeling", "population_monitoring"]
    },
    "food": {
        "DEFAULT_DOMAINS": {
            "risk_assessment": ["hazard_identification", "contamination_detection", "outbreak_prediction"],
            "quality_control": ["ingredient_analysis", "process_monitoring", "product_inspection"],
            "supply_chain": ["traceability", "authenticity_verification", "temperature_monitoring"],
            "regulatory_compliance": ["standards_verification", "documentation_validation", "labeling_compliance"],
            "research_integration": ["data_mining", "safety_modeling", "method_validation"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "risk_assessment": {
                "description": "AI-driven food safety risk assessment",
                "sub_domains": ["hazard_identification", "contamination_detection", "outbreak_prediction"]
            },
            "quality_control": {
                "description": "AI-powered food quality monitoring",
                "sub_domains": ["ingredient_analysis", "process_monitoring", "product_inspection"]
            },
            "supply_chain": {
                "description": "AI for food supply chain monitoring",
                "sub_domains": ["traceability", "authenticity_verification", "temperature_monitoring"]
            },
            "regulatory_compliance": {
                "description": "AI verification of food safety regulations",
                "sub_domains": ["standards_verification", "documentation_validation", "labeling_compliance"]
            },
            "research_integration": {
                "description": "AI integration of food safety research",
                "sub_domains": ["data_mining", "safety_modeling", "method_validation"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "cfsan_ai_guidelines": {
                "name": "CFSAN AI Guidelines",
                "description": "Guidelines for AI in food safety",
                "components": ["validation", "verification", "monitoring"]
            },
            "food_safety_modernization": {
                "name": "Food Safety Modernization Act AI Framework",
                "description": "Framework for AI in FSMA compliance",
                "components": ["preventive_controls", "produce_safety", "foreign_supplier_verification"]
            },
            "haccp_ai": {
                "name": "HACCP AI Framework",
                "description": "Framework for AI in hazard analysis",
                "components": ["hazard_analysis", "critical_control_points", "verification"]
            },
            "traceability_framework": {
                "name": "Food Traceability AI Framework",
                "description": "Framework for AI in food traceability",
                "components": ["tracking", "tracing", "recordkeeping"]
            },
            "testing_methods": {
                "name": "Food Testing Methods AI Framework",
                "description": "Framework for AI in food testing",
                "components": ["sampling", "analysis", "interpretation"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["risk_assessment", "quality_control", "regulatory_compliance"]
    },
    "transportation": {
        "DEFAULT_DOMAINS": {
            "crash_prevention": ["risk_analysis", "driver_behavior", "vehicle_systems"],
            "safety_regulations": ["compliance_monitoring", "standards_development", "effectiveness_assessment"],
            "incident_investigation": ["data_collection", "causal_analysis", "recommendation_formulation"],
            "vehicle_safety": ["design_analysis", "testing_simulation", "performance_monitoring"],
            "traffic_safety": ["pattern_analysis", "intervention_planning", "impact_assessment"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "crash_prevention": {
                "description": "AI-driven traffic crash prevention",
                "sub_domains": ["risk_analysis", "driver_behavior", "vehicle_systems"]
            },
            "safety_regulations": {
                "description": "AI for transportation safety regulations",
                "sub_domains": ["compliance_monitoring", "standards_development", "effectiveness_assessment"]
            },
            "incident_investigation": {
                "description": "AI-assisted transportation incident investigation",
                "sub_domains": ["data_collection", "causal_analysis", "recommendation_formulation"]
            },
            "vehicle_safety": {
                "description": "AI analysis of vehicle safety systems",
                "sub_domains": ["design_analysis", "testing_simulation", "performance_monitoring"]
            },
            "traffic_safety": {
                "description": "AI for traffic safety management",
                "sub_domains": ["pattern_analysis", "intervention_planning", "impact_assessment"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "nhtsa_ai_guidelines": {
                "name": "NHTSA AI Guidelines",
                "description": "Guidelines for AI in vehicle safety",
                "components": ["design", "testing", "monitoring"]
            },
            "crash_investigation": {
                "name": "Crash Investigation AI Framework",
                "description": "Framework for AI in crash investigation",
                "components": ["data_collection", "analysis", "reconstruction"]
            },
            "safety_standards": {
                "name": "Vehicle Safety Standards AI Framework",
                "description": "Framework for AI in safety standards development",
                "components": ["testing", "performance_metrics", "compliance"]
            },
            "traffic_analysis": {
                "name": "Traffic Analysis AI Framework",
                "description": "Framework for AI in traffic safety analysis",
                "components": ["pattern_recognition", "risk_assessment", "countermeasure_evaluation"]
            },
            "driver_assistance": {
                "name": "Driver Assistance Systems AI Framework",
                "description": "Framework for AI in driver assistance",
                "components": ["sensor_fusion", "decision_making", "human_factors"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["crash_prevention", "vehicle_safety", "incident_investigation"]
    },
    "drugs": {
        "DEFAULT_DOMAINS": {
            "drug_review": ["efficacy_assessment", "safety_evaluation", "benefit_risk_analysis"],
            "clinical_trials": ["protocol_optimization", "data_analysis", "outcome_prediction"],
            "pharmacovigilance": ["adverse_event_detection", "signal_analysis", "risk_management"],
            "manufacturing_quality": ["process_monitoring", "defect_detection", "compliance_verification"],
            "regulatory_science": ["methods_development", "standards_formulation", "decision_support"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "drug_review": {
                "description": "AI-driven drug application review",
                "sub_domains": ["efficacy_assessment", "safety_evaluation", "benefit_risk_analysis"]
            },
            "clinical_trials": {
                "description": "AI for clinical trial optimization",
                "sub_domains": ["protocol_optimization", "data_analysis", "outcome_prediction"]
            },
            "pharmacovigilance": {
                "description": "AI-enhanced monitoring of drug safety",
                "sub_domains": ["adverse_event_detection", "signal_analysis", "risk_management"]
            },
            "manufacturing_quality": {
                "description": "AI for pharmaceutical manufacturing quality",
                "sub_domains": ["process_monitoring", "defect_detection", "compliance_verification"]
            },
            "regulatory_science": {
                "description": "AI applications in regulatory science",
                "sub_domains": ["methods_development", "standards_formulation", "decision_support"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "cder_ai_guidelines": {
                "name": "CDER AI Guidelines",
                "description": "Guidelines for AI in drug evaluation",
                "components": ["model_validation", "performance_monitoring", "documentation"]
            },
            "drug_development": {
                "name": "Drug Development AI Framework",
                "description": "Framework for AI in drug development",
                "components": ["discovery", "preclinical", "clinical"]
            },
            "drug_safety": {
                "name": "Drug Safety AI Framework",
                "description": "Framework for AI in drug safety monitoring",
                "components": ["signal_detection", "causality_assessment", "risk_management"]
            },
            "manufacturing_oversight": {
                "name": "Manufacturing Oversight AI Framework",
                "description": "Framework for AI in manufacturing oversight",
                "components": ["process_analytics", "quality_control", "compliance"]
            },
            "clinical_research": {
                "name": "Clinical Research AI Framework",
                "description": "Framework for AI in clinical research",
                "components": ["protocol_design", "patient_selection", "data_analysis"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["drug_review", "pharmacovigilance", "regulatory_science"]
    },
    "biologics": {
        "DEFAULT_DOMAINS": {
            "product_review": ["efficacy_assessment", "safety_evaluation", "quality_analysis"],
            "manufacturing_oversight": ["process_monitoring", "deviation_detection", "quality_control"],
            "clinical_assessment": ["trial_design", "data_analysis", "benefit_risk_assessment"],
            "post_market_surveillance": ["adverse_event_detection", "signal_analysis", "risk_management"],
            "research_advancement": ["method_development", "knowledge_integration", "innovation_assessment"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "product_review": {
                "description": "AI-driven biologics application review",
                "sub_domains": ["efficacy_assessment", "safety_evaluation", "quality_analysis"]
            },
            "manufacturing_oversight": {
                "description": "AI for biologics manufacturing oversight",
                "sub_domains": ["process_monitoring", "deviation_detection", "quality_control"]
            },
            "clinical_assessment": {
                "description": "AI-enhanced clinical assessment",
                "sub_domains": ["trial_design", "data_analysis", "benefit_risk_assessment"]
            },
            "post_market_surveillance": {
                "description": "AI for post-market surveillance",
                "sub_domains": ["adverse_event_detection", "signal_analysis", "risk_management"]
            },
            "research_advancement": {
                "description": "AI applications in biologics research",
                "sub_domains": ["method_development", "knowledge_integration", "innovation_assessment"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "cber_ai_guidelines": {
                "name": "CBER AI Guidelines",
                "description": "Guidelines for AI in biologics evaluation",
                "components": ["validation", "verification", "monitoring"]
            },
            "biologics_development": {
                "name": "Biologics Development AI Framework",
                "description": "Framework for AI in biologics development",
                "components": ["design", "manufacturing", "testing"]
            },
            "biologics_safety": {
                "name": "Biologics Safety AI Framework",
                "description": "Framework for AI in biologics safety",
                "components": ["risk_assessment", "quality_control", "surveillance"]
            },
            "regenerative_medicine": {
                "name": "Regenerative Medicine AI Framework",
                "description": "Framework for AI in regenerative medicine",
                "components": ["cell_characterization", "product_quality", "patient_outcomes"]
            },
            "biologics_research": {
                "name": "Biologics Research AI Framework",
                "description": "Framework for AI in biologics research",
                "components": ["data_analysis", "model_development", "knowledge_discovery"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["product_review", "manufacturing_oversight", "post_market_surveillance"]
    },
    "complementary_health": {
        "DEFAULT_DOMAINS": {
            "research_integration": ["data_synthesis", "evidence_analysis", "knowledge_management"],
            "clinical_application": ["practice_guidelines", "treatment_optimization", "outcome_prediction"],
            "product_assessment": ["quality_evaluation", "safety_monitoring", "efficacy_analysis"],
            "insurance_validation": ["claim_verification", "fraud_detection", "policy_compliance"],
            "knowledge_dissemination": ["information_accuracy", "content_personalization", "engagement_optimization"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "research_integration": {
                "description": "AI integration of complementary health research",
                "sub_domains": ["data_synthesis", "evidence_analysis", "knowledge_management"]
            },
            "clinical_application": {
                "description": "AI for complementary health practices",
                "sub_domains": ["practice_guidelines", "treatment_optimization", "outcome_prediction"]
            },
            "product_assessment": {
                "description": "AI assessment of complementary health products",
                "sub_domains": ["quality_evaluation", "safety_monitoring", "efficacy_analysis"]
            },
            "insurance_validation": {
                "description": "AI for insurance claims validation",
                "sub_domains": ["claim_verification", "fraud_detection", "policy_compliance"]
            },
            "knowledge_dissemination": {
                "description": "AI for health information dissemination",
                "sub_domains": ["information_accuracy", "content_personalization", "engagement_optimization"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "nccih_ai_guidelines": {
                "name": "NCCIH AI Guidelines",
                "description": "Guidelines for AI in complementary health",
                "components": ["research", "practice", "dissemination"]
            },
            "evidence_integration": {
                "name": "Evidence Integration AI Framework",
                "description": "Framework for AI in evidence integration",
                "components": ["data_extraction", "synthesis", "evaluation"]
            },
            "practice_translation": {
                "name": "Practice Translation AI Framework",
                "description": "Framework for AI in practice translation",
                "components": ["guideline_development", "implementation", "evaluation"]
            },
            "product_safety": {
                "name": "Product Safety AI Framework",
                "description": "Framework for AI in product safety",
                "components": ["quality_assessment", "adverse_event_detection", "risk_management"]
            },
            "health_information": {
                "name": "Health Information AI Framework",
                "description": "Framework for AI in health information",
                "components": ["accuracy", "accessibility", "engagement"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["research_integration", "insurance_validation", "product_assessment"]
    }
}

# Issue finder template for AI-focused agencies
AI_ISSUE_FINDER_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
${AGENCY} Issue Finder

A specialized issue finder for the ${AGENCY_NAME} (${AGENCY})
that identifies ${DOMAIN}-related issues in AI applications.
\"\"\"

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from agency_issue_finder.issue_finder import AgencyIssueFinder, AgencyIssueFinderException

class ${AGENCY}IssueFinder(AgencyIssueFinder):
    \"\"\"
    ${AGENCY}-specific issue finder implementation.
    Identifies AI-driven ${DOMAIN} issues and prepares research context.
    \"\"\"
    
    def __init__(self, config_dir: str, data_dir: str) -> None:
        \"\"\"
        Initialize the ${AGENCY} issue finder.
        
        Args:
            config_dir: Directory containing configuration files
            data_dir: Directory containing agency data
        \"\"\"
        super().__init__("${AGENCY}", config_dir, data_dir)
        self.${DOMAIN_VAR}_domains = self._load_${DOMAIN_VAR}_domains()
    
    def _load_${DOMAIN_VAR}_domains(self) -> Dict[str, List[str]]:
        \"\"\"Load ${DOMAIN} domain information.\"\"\"
        domains_file = os.path.join(self.data_dir, "${AGENCY_LOWER}", "${DOMAIN_VAR}_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise AgencyIssueFinderException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return ${DEFAULT_DOMAINS}
    
    def find_issues(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        \"\"\"
        Find current issues for ${AGENCY}.
        
        Args:
            topic: Optional topic to filter issues
            
        Returns:
            List of issues found
        \"\"\"
        # Start with empty issues list
        self.issues = []
        
        # If a specific topic is provided, find relevant issues
        if topic:
            # Check if topic matches any ${DOMAIN} domain
            for domain, subdomains in self.${DOMAIN_VAR}_domains.items():
                if topic.lower() in domain.lower() or topic.lower() in [s.lower() for s in subdomains]:
                    self.issues.extend(self._get_domain_issues(domain))
        
        # If no topic is specified or no issues found for topic, return all high-priority issues
        if not self.issues:
            for domain in self.${DOMAIN_VAR}_domains:
                self.issues.extend(self._get_domain_issues(domain, high_priority_only=True))
        
        # If still no issues found, add a default issue
        if not self.issues:
            self.issues.append({
                "id": "${AGENCY}-GEN-001",
                "title": "AI-Driven ${DOMAIN_TITLE} System Integration",
                "status": "pending",
                "priority": "high",
                "description": "Integration of AI capabilities into ${DOMAIN} systems and workflows.",
                "affected_areas": ["All ${DOMAIN} domains"],
                "detection_date": datetime.now().strftime("%Y-%m-%d"),
                "resources": [
                    {"type": "implementation_plan", "path": "${AGENCY}-IMPLEMENTATION-PLAN.md"},
                    {"type": "codebase", "path": "SYSTEM-COMPONENTS/HMS-${AGENCY}/"}
                ]
            })
        
        return self.issues
    
    def _get_domain_issues(self, domain: str, high_priority_only: bool = False) -> List[Dict[str, Any]]:
        \"\"\"
        Get issues for a specific ${DOMAIN} domain.
        
        Args:
            domain: ${DOMAIN_TITLE} domain
            high_priority_only: Only return high priority issues
            
        Returns:
            List of domain issues
        \"\"\"
        issues = []
        
        # Add AI-specific issue for domain
        issues.append({
            "id": f"${AGENCY}-{domain[:2].upper()}-001",
            "title": f"AI-Powered {domain.title()} Implementation",
            "status": "pending",
            "priority": "high" if domain in ${HIGH_PRIORITY_DOMAINS} else "medium",
            "description": f"Implementation of AI capabilities for {domain} in the ${DOMAIN} context.",
            "affected_areas": [subdomain.replace('_', ' ').title() for subdomain in self.${DOMAIN_VAR}_domains.get(domain, [])],
            "detection_date": datetime.now().strftime("%Y-%m-%d"),
            "resources": [
                {"type": "implementation_plan", "path": "${AGENCY}-IMPLEMENTATION-PLAN.md"},
                {"type": "codebase", "path": f"SYSTEM-COMPONENTS/HMS-${AGENCY}/"}
            ]
        })
        
        # Add model validation issue for high-priority domains
        if domain in ${HIGH_PRIORITY_DOMAINS}:
            issues.append({
                "id": f"${AGENCY}-{domain[:2].upper()}-002",
                "title": f"AI Model Validation for {domain.title()}",
                "status": "pending",
                "priority": "high",
                "description": f"Validation framework for AI models used in {domain} applications.",
                "affected_areas": ["Model Validation", "Regulatory Compliance", "Quality Assurance"],
                "detection_date": datetime.now().strftime("%Y-%m-%d"),
                "resources": [
                    {"type": "implementation_plan", "path": "${AGENCY}-IMPLEMENTATION-PLAN.md"},
                    {"type": "guidance", "path": "${AGENCY}-AI-VALIDATION-GUIDE.md"}
                ]
            })
        
        # Filter by priority if requested
        if high_priority_only:
            issues = [issue for issue in issues if issue["priority"] == "high"]
        
        return issues
    
    def prepare_context(self, issue_id: Optional[str] = None) -> Dict[str, Any]:
        \"\"\"
        Prepare context for Codex CLI based on ${AGENCY} issues.
        
        Args:
            issue_id: Optional issue ID to focus on
            
        Returns:
            Context dictionary for Codex CLI
        \"\"\"
        # Find the specified issue
        issue = None
        if issue_id and self.issues:
            issue = next((i for i in self.issues if i["id"] == issue_id), None)
        
        # If no specific issue is selected, use the highest priority issue
        if not issue and self.issues:
            issue = sorted(self.issues, key=lambda x: 0 if x["priority"] == "high" else 
                                                     1 if x["priority"] == "medium" else 2)[0]
        
        # If no issues are found, return empty context
        if not issue:
            return {
                "agency": "${AGENCY}",
                "issue": None,
                "resources": [],
                "codex_args": "--agency=${AGENCY_LOWER}"
            }
        
        # Prepare agency-specific context
        context = {
            "agency": "${AGENCY}",
            "issue": issue,
            "resources": issue.get("resources", []),
            "domains": self.${DOMAIN_VAR}_domains,
            "codex_args": f"--agency=${AGENCY_LOWER} --issue-id={issue['id']}"
        }
        
        # Add additional arguments for high priority issues
        if issue.get("priority") == "high":
            context["codex_args"] += " --priority=high"
        
        # Add domain-specific arguments if applicable
        for domain in self.${DOMAIN_VAR}_domains:
            domain_code = domain[:2].upper()
            if f"${AGENCY}-{domain_code}-" in issue["id"]:
                context["codex_args"] += f" --domain={domain}"
                break
        
        # Add AI-specific context
        context["ai_capabilities"] = {
            "machine_learning": ["supervised", "unsupervised", "reinforcement"],
            "natural_language_processing": ["entity_recognition", "sentiment_analysis", "text_generation"],
            "computer_vision": ["image_classification", "object_detection", "segmentation"],
            "predictive_analytics": ["forecasting", "anomaly_detection", "risk_assessment"]
        }
        
        return context


def main():
    \"\"\"Main entry point for the ${AGENCY} issue finder.\"\"\"
    import argparse
    
    parser = argparse.ArgumentParser(description="${AGENCY} AI Issue Finder")
    parser.add_argument("--topic", help="Topic to filter issues")
    parser.add_argument("--config-dir", default=os.path.expanduser("~/.codex/agency-config"),
                       help="Directory containing configuration files")
    parser.add_argument("--data-dir", default=os.path.expanduser("~/.codex/agency-data"),
                       help="Directory containing agency data")
    parser.add_argument("--issue-id", help="Specific issue ID to prepare context for")
    parser.add_argument("--output-format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the ${AGENCY} issue finder
        finder = ${AGENCY}IssueFinder(args.config_dir, args.data_dir)
        
        # Find issues
        issues = finder.find_issues(args.topic)
        
        # Prepare context
        context = finder.prepare_context(args.issue_id)
        
        if args.output_format == "json":
            print(json.dumps(context, indent=2))
        else:
            print(f"Agency: {context['agency']} (AI-Powered ${DOMAIN_TITLE})")
            
            if context.get("issue"):
                print(f"Issue ID: {context['issue']['id']}")
                print(f"Title: {context['issue']['title']}")
                print(f"Status: {context['issue']['status']}")
                print(f"Priority: {context['issue']['priority']}")
                print(f"Resources: {len(context['resources'])}")
                print(f"Codex Args: {context['codex_args']}")
            else:
                print("No issues found.")
    
    except AgencyIssueFinderException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
"""

# Research connector template for AI-focused agencies
AI_RESEARCH_CONNECTOR_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
${AGENCY} Research Connector

A specialized connector for the ${AGENCY_NAME} (${AGENCY})
that provides access to AI-driven ${DOMAIN} research and implementation data.
\"\"\"

import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from agency_issue_finder.base_connector import AgencyResearchConnector

class ${AGENCY}Exception(Exception):
    \"\"\"Custom exception for ${AGENCY} connector errors.\"\"\"
    pass

class ${AGENCY}ResearchConnector(AgencyResearchConnector):
    \"\"\"
    ${AGENCY}-specific research connector implementation.
    Provides access to AI-driven ${DOMAIN} research and implementation data.
    \"\"\"
    
    def __init__(self, base_path: str) -> None:
        \"\"\"
        Initialize the ${AGENCY} research connector.
        
        Args:
            base_path: Base path to ${AGENCY} data
        \"\"\"
        super().__init__("${AGENCY}", base_path)
        self.${DOMAIN_VAR}_domains = self._load_${DOMAIN_VAR}_domains()
        self.${DOMAIN_VAR}_frameworks = self._load_${DOMAIN_VAR}_frameworks()
        self.ai_capabilities = self._load_ai_capabilities()
    
    def _load_${DOMAIN_VAR}_domains(self) -> Dict[str, Any]:
        \"\"\"Load ${DOMAIN} domain information.\"\"\"
        domains_file = os.path.join(self.agency_dir, "${DOMAIN_VAR}_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise ${AGENCY}Exception(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return ${DEFAULT_DOMAINS_FULL}
    
    def _load_${DOMAIN_VAR}_frameworks(self) -> Dict[str, Any]:
        \"\"\"Load ${AGENCY} regulatory frameworks.\"\"\"
        frameworks_file = os.path.join(self.agency_dir, "${DOMAIN_VAR}_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise ${AGENCY}Exception(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return ${DEFAULT_FRAMEWORKS}
    
    def _load_ai_capabilities(self) -> Dict[str, Any]:
        \"\"\"Load AI capabilities information.\"\"\"
        capabilities_file = os.path.join(self.agency_dir, "ai_capabilities.json")
        
        if os.path.exists(capabilities_file):
            try:
                with open(capabilities_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise ${AGENCY}Exception(f"Invalid JSON in capabilities file: {e}")
        
        # Return default capabilities if file not found
        return {
            "machine_learning": {
                "description": "Machine learning models and techniques",
                "types": ["supervised", "unsupervised", "reinforcement", "deep_learning"]
            },
            "natural_language_processing": {
                "description": "Processing and understanding of text",
                "types": ["entity_recognition", "sentiment_analysis", "text_generation", "summarization"]
            },
            "computer_vision": {
                "description": "Analysis and understanding of images and video",
                "types": ["image_classification", "object_detection", "segmentation", "feature_extraction"]
            },
            "predictive_analytics": {
                "description": "Predictive modeling and forecasting",
                "types": ["forecasting", "anomaly_detection", "risk_assessment", "recommendation"]
            },
            "decision_support": {
                "description": "AI-assisted decision making",
                "types": ["expert_systems", "recommendation_engines", "risk_analysis", "optimization"]
            }
        }
    
    def get_implementation_status(self) -> Dict[str, Any]:
        \"\"\"
        Get implementation status for ${AGENCY}.
        
        Returns:
            Implementation status dictionary
        \"\"\"
        # Get base implementation status
        status = super().get_implementation_status()
        
        # Add ${AGENCY}-specific status information
        status["domains"] = list(self.${DOMAIN_VAR}_domains.keys())
        status["frameworks"] = list(self.${DOMAIN_VAR}_frameworks.keys())
        status["ai_capabilities"] = list(self.ai_capabilities.keys())
        
        # Add AI-specific implementation metrics
        status["ai_metrics"] = {
            "models_deployed": 5,
            "accuracy_benchmark": 87.4,
            "validation_coverage": 92.3,
            "regulatory_compliance": 96.8
        }
        
        return status
    
    def get_ai_recommendations(self) -> List[str]:
        \"\"\"
        Get AI-specific recommendations for ${DOMAIN}.
        
        Returns:
            List of AI recommendations
        \"\"\"
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate domain-specific AI recommendations
        for domain, info in self.${DOMAIN_VAR}_domains.items():
            recommendations.append(f"Enhance AI capabilities for {domain} with focus on {', '.join(info['sub_domains'])}")
        
        # Generate framework-specific AI recommendations
        for framework, info in self.${DOMAIN_VAR}_frameworks.items():
            recommendations.append(f"Ensure AI compliance with {info['name']} regulations")
        
        # Generate capability-specific recommendations
        for capability, info in self.ai_capabilities.items():
            recommendations.append(f"Leverage {capability.replace('_', ' ')} for {info['description'].lower()}")
        
        # Generate recommendations based on implementation status
        if "implementation_phases" in status:
            phases = status["implementation_phases"]
            
            # Find the first incomplete phase
            current_phase = None
            for phase_key, phase in sorted(phases.items()):
                if phase["percentage"] < 100:
                    current_phase = phase
                    break
            
            if current_phase:
                # Add recommendations for incomplete tasks in the current phase
                for task in current_phase["tasks"]:
                    if not task["completed"]:
                        recommendations.append(f"Complete AI task: {task['name']}")
        
        # Add model validation recommendations
        recommendations.append("Implement comprehensive validation framework for AI models")
        recommendations.append("Establish continuous monitoring for deployed AI systems")
        recommendations.append("Create explainability documentation for critical AI components")
        
        return recommendations
    
    def get_codex_context(self) -> Dict[str, Any]:
        \"\"\"
        Generate Codex context for ${AGENCY}.
        
        Returns:
            Codex context dictionary
        \"\"\"
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_ai_recommendations()
        
        # Compile context
        context = {
            "agency": "${AGENCY}",
            "full_name": "${AGENCY_NAME}",
            "domains": self.${DOMAIN_VAR}_domains,
            "regulatory_frameworks": self.${DOMAIN_VAR}_frameworks,
            "ai_capabilities": self.ai_capabilities,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        # Add AI-specific integration details
        context["ai_integration"] = {
            "data_sources": [
                {"name": "HMS Core Database", "access_method": "API", "data_types": ["structured", "time_series"]},
                {"name": "${DOMAIN_TITLE} Knowledge Graph", "access_method": "SPARQL", "data_types": ["semantic"]},
                {"name": "Regulatory Documents", "access_method": "Document API", "data_types": ["text", "pdf"]}
            ],
            "model_deployment": {
                "environments": ["development", "testing", "production"],
                "containerization": "Docker",
                "orchestration": "Kubernetes",
                "monitoring": "Prometheus"
            },
            "validation_framework": {
                "methods": ["cross_validation", "holdout_testing", "adversarial_testing"],
                "metrics": ["accuracy", "precision", "recall", "f1_score", "auc"],
                "documentation": ["model_cards", "validation_reports", "audit_logs"]
            }
        }
        
        return context


def main():
    \"\"\"Main entry point function.\"\"\"
    import argparse
    
    parser = argparse.ArgumentParser(description="${AGENCY} AI Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to ${AGENCY} data")
    parser.add_argument("--output", choices=["status", "recommendations", "context"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the ${AGENCY} connector
        connector = ${AGENCY}ResearchConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_ai_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"${AGENCY} AI Implementation Status")
                print(f"-------------------------")
                
                if "overall_completion" in result:
                    overall = result["overall_completion"]
                    print(f"Overall Completion: {overall['completed_tasks']}/{overall['total_tasks']} "
                          f"({overall['percentage']:.1f}%)")
                
                if "implementation_phases" in result:
                    print("\\nPhases:")
                    for phase_key, phase in sorted(result["implementation_phases"].items()):
                        print(f"  {phase['name']}: {phase['completed_tasks']}/{phase['total_tasks']} "
                              f"({phase['percentage']:.1f}%)")
                
                print(f"\\nDomains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['frameworks'])}")
                print(f"AI Capabilities: {', '.join(result['ai_capabilities'])}")
                
                if "ai_metrics" in result:
                    print("\\nAI Metrics:")
                    for metric, value in result["ai_metrics"].items():
                        print(f"  {metric.replace('_', ' ').title()}: {value}")
            
            elif args.output == "recommendations":
                print(f"${AGENCY} AI Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"${AGENCY} AI Codex Context Summary")
                print(f"-------------------------")
                print(f"Domains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['regulatory_frameworks'].keys())}")
                print(f"AI Capabilities: {', '.join(result['ai_capabilities'].keys())}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\\nOverall Completion: {overall['percentage']:.1f}%")
                
                print(f"\\nTop AI Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")
    
    except ${AGENCY}Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
"""

# ASCII art template for AI agencies
AI_ASCII_ART_TEMPLATE = """ █████████████████████████████████████████████████████████
 █                                                       █
 █   ${ASCII_LINE1}                    █
 █   ${ASCII_LINE2}                    █
 █   ${ASCII_LINE3}                    █
 █   ${ASCII_LINE4}                    █
 █   ${ASCII_LINE5}                    █
 █                                                       █
 █         AI-Powered ${AGENCY_FULL_NAME}         █
 █                                                       █
 █████████████████████████████████████████████████████████"""

# Map of domain names to domain types
DOMAIN_TYPE_MAP = {
    "Animal and Plant Health Inspection Service": "agriculture",
    "Bureau of Safety and Environmental Enforcement": "environment",
    "Center for Biologics Evaluation and Research": "biologics",
    "Center for Drug Evaluation and Research": "drugs",
    "Center for Food Safety and Applied Nutrition": "food",
    "Center for Nutrition Policy and Promotion": "nutrition",
    "Consumer Product Safety Commission": "safety",
    "Crohn's Disease Prevention": "healthcare",
    "Commission on Security and Cooperation in Europe": "security",
    "Department of Education": "education",
    "Federal Housing Finance Agency": "finance",
    "Health Resources and Services Administration": "healthcare",
    "Homeland Security Information Network": "security",
    "National Association for the Advancement of Colored People": "healthcare",
    "National Center for Complementary and Integrative Health": "complementary_health",
    "National Highway Traffic Safety Administration": "transportation",
    "National Institute of Diabetes and Digestive and Kidney Diseases": "healthcare",
    "National School Lunch Program": "nutrition",
    "National Transportation Safety Board": "transportation",
    "Office of the Assistant Secretary for Health": "healthcare",
    "Office of National Drug Control Policy": "healthcare",
    "Population Health Management": "healthcare",
    "Specialty Provider Utility Health Care": "healthcare",
    "Talent Management": "personnel",
    "U.S. Interagency Council on Homelessness": "housing",
    "U.S. International Trade Commission": "commerce",
    "U.S. Trade and Development Agency": "commerce"
}

class AIAgencyGenerator:
    """
    Generator for AI agency-specific components.
    """
    
    def __init__(self, base_dir: str, templates_dir: str) -> None:
        """
        Initialize the AI agency generator.
        
        Args:
            base_dir: Base directory for agency interface
            templates_dir: Directory for ASCII art templates
        """
        self.base_dir = base_dir
        self.templates_dir = templates_dir
        
        # Ensure directories exist
        self._ensure_dirs()
    
    def _ensure_dirs(self) -> None:
        """Ensure required directories exist."""
        directories = [
            os.path.join(self.base_dir, "agency_issue_finder", "agencies"),
            os.path.join(self.base_dir, "agencies"),
            self.templates_dir,
            os.path.join(self.base_dir, "config", "ai_agencies")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def generate_agency(self, agency_acronym: str, agency_name: str, domain: str = None) -> bool:
        """
        Generate components for a specific AI agency.

        Args:
            agency_acronym: Agency acronym
            agency_name: Full agency name
            domain: Domain type (if None, determined from agency name)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get domain from agency name if not provided
            if not domain and agency_name in DOMAIN_TYPE_MAP:
                domain = DOMAIN_TYPE_MAP[agency_name]
            elif not domain:
                # Default to healthcare if domain can't be determined
                domain = "healthcare"
            
            # Create agency data
            agency_data = {
                "acronym": agency_acronym,
                "name": agency_name,
                "domain": domain,
                "ai_enabled": True
            }
            
            # Generate components
            print(f"Generating ASCII art for {agency_acronym}...")
            self._generate_ascii_art(agency_acronym, agency_name)
            
            print(f"Generating issue finder for {agency_acronym}...")
            self._generate_issue_finder(agency_acronym, agency_name, domain)
            
            print(f"Generating research connector for {agency_acronym}...")
            self._generate_research_connector(agency_acronym, agency_name, domain)
            
            print(f"Generating configuration for {agency_acronym}...")
            self._generate_config(agency_acronym, agency_data)
            
            print(f"Successfully generated components for {agency_acronym}.")
            return True
            
        except Exception as e:
            print(f"Error generating components for {agency_acronym}: {e}")
            return False
    
    def _generate_ascii_char(self, char: str) -> str:
        """
        Generate ASCII art for a single character.
        
        Args:
            char: Character to generate ASCII art for
            
        Returns:
            ASCII art for the character
        """
        char = char.upper()
        if char == 'A':
            return " █████  "
        elif char == 'B':
            return "██████  "
        elif char == 'C':
            return " █████  "
        elif char == 'D':
            return "██████  "
        elif char == 'E':
            return "███████ "
        elif char == 'F':
            return "███████ "
        elif char == 'G':
            return " █████  "
        elif char == 'H':
            return "██   ██ "
        elif char == 'I':
            return "███████ "
        elif char == 'J':
            return "     ██ "
        elif char == 'K':
            return "██  ███ "
        elif char == 'L':
            return "██      "
        elif char == 'M':
            return "██   ██ "
        elif char == 'N':
            return "███  ██ "
        elif char == 'O':
            return " █████  "
        elif char == 'P':
            return "██████  "
        elif char == 'Q':
            return " █████  "
        elif char == 'R':
            return "██████  "
        elif char == 'S':
            return " █████  "
        elif char == 'T':
            return "███████ "
        elif char == 'U':
            return "██   ██ "
        elif char == 'V':
            return "██   ██ "
        elif char == 'W':
            return "██   ██ "
        elif char == 'X':
            return "██   ██ "
        elif char == 'Y':
            return "██   ██ "
        elif char == 'Z':
            return "███████ "
        else:
            return "        "
    
    def _generate_ascii_art(self, agency: str, name: str) -> bool:
        """
        Generate ASCII art for an agency.
        
        Args:
            agency: Agency acronym
            name: Agency name
            
        Returns:
            True if successful, False otherwise
        """
        # Define ASCII art characters for agency acronym
        ascii_chars = {}
        for i, char in enumerate(agency):
            if char.isalpha():
                ascii_chars[f"ASCII_LINE{i+1}"] = self._generate_ascii_char(char)
            else:
                ascii_chars[f"ASCII_LINE{i+1}"] = " " * 10
        
        # Fill any remaining lines with spaces
        for i in range(len(agency) + 1, 6):
            ascii_chars[f"ASCII_LINE{i}"] = " " * 10
        
        # Create template substitution dictionary
        substitutions = {
            "AGENCY_FULL_NAME": name,
            **ascii_chars
        }
        
        # Generate ASCII art from template
        template = Template(AI_ASCII_ART_TEMPLATE)
        ascii_art = template.substitute(**substitutions)
        
        # Write ASCII art to file
        ascii_art_file = os.path.join(self.templates_dir, f"{agency.lower()}_ascii.txt")
        try:
            with open(ascii_art_file, 'w') as f:
                f.write(ascii_art)
            return True
        except Exception as e:
            print(f"Error writing ASCII art file: {e}")
            return False
    
    def _generate_issue_finder(self, agency: str, name: str, domain: str) -> bool:
        """
        Generate issue finder for an AI agency.
        
        Args:
            agency: Agency acronym
            name: Agency name
            domain: Agency domain
            
        Returns:
            True if successful, False otherwise
        """
        # Get domain templates
        domain_templates = AI_DOMAIN_TEMPLATES.get(domain, AI_DOMAIN_TEMPLATES["healthcare"])
        
        # Create template substitution dictionary
        substitutions = {
            "AGENCY": agency,
            "AGENCY_NAME": name,
            "AGENCY_LOWER": agency.lower(),
            "DOMAIN": domain,
            "DOMAIN_VAR": domain,
            "DOMAIN_TITLE": domain.title(),
            "DEFAULT_DOMAINS": json.dumps(domain_templates["DEFAULT_DOMAINS"], indent=8),
            "HIGH_PRIORITY_DOMAINS": json.dumps(domain_templates["HIGH_PRIORITY_DOMAINS"], indent=8)
        }
        
        # Generate issue finder from template
        template = Template(AI_ISSUE_FINDER_TEMPLATE)
        issue_finder = template.substitute(**substitutions)
        
        # Write issue finder to file
        issue_finder_file = os.path.join(self.base_dir, "agency_issue_finder", "agencies", f"{agency.lower()}_finder.py")
        try:
            with open(issue_finder_file, 'w') as f:
                f.write(issue_finder)
            return True
        except Exception as e:
            print(f"Error writing issue finder file: {e}")
            return False
    
    def _generate_research_connector(self, agency: str, name: str, domain: str) -> bool:
        """
        Generate research connector for an AI agency.
        
        Args:
            agency: Agency acronym
            name: Agency name
            domain: Agency domain
            
        Returns:
            True if successful, False otherwise
        """
        # Get domain templates
        domain_templates = AI_DOMAIN_TEMPLATES.get(domain, AI_DOMAIN_TEMPLATES["healthcare"])
        
        # Create template substitution dictionary
        substitutions = {
            "AGENCY": agency,
            "AGENCY_NAME": name,
            "AGENCY_LOWER": agency.lower(),
            "DOMAIN": domain,
            "DOMAIN_VAR": domain,
            "DOMAIN_TITLE": domain.title(),
            "DEFAULT_DOMAINS_FULL": json.dumps(domain_templates["DEFAULT_DOMAINS_FULL"], indent=8),
            "DEFAULT_FRAMEWORKS": json.dumps(domain_templates["DEFAULT_FRAMEWORKS"], indent=8)
        }
        
        # Generate research connector from template
        template = Template(AI_RESEARCH_CONNECTOR_TEMPLATE)
        research_connector = template.substitute(**substitutions)
        
        # Write research connector to file
        connector_file = os.path.join(self.base_dir, "agencies", f"{agency.lower()}_connector.py")
        try:
            with open(connector_file, 'w') as f:
                f.write(research_connector)
            return True
        except Exception as e:
            print(f"Error writing research connector file: {e}")
            return False
    
    def _generate_config(self, agency: str, agency_data: dict) -> bool:
        """
        Generate configuration file for an AI agency.
        
        Args:
            agency: Agency acronym
            agency_data: Agency data
            
        Returns:
            True if successful, False otherwise
        """
        config_file = os.path.join(self.base_dir, "config", "ai_agencies", f"{agency.lower()}.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(agency_data, indent=2, fp=f)
            return True
        except Exception as e:
            print(f"Error writing configuration file: {e}")
            return False
    
    def update_config(self, agencies: List[dict]) -> bool:
        """
        Update main configuration file with AI agencies.
        
        Args:
            agencies: List of agency data
            
        Returns:
            True if successful, False otherwise
        """
        config_file = os.path.join(self.base_dir, "config", "agency_data.json")
        
        # Load existing configuration
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {"agencies": [], "topics": {}}
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
        
        # Add or update agencies
        existing_agencies = {a["acronym"]: i for i, a in enumerate(config["agencies"])}
        
        for agency in agencies:
            if agency["acronym"] in existing_agencies:
                # Update existing agency
                config["agencies"][existing_agencies[agency["acronym"]]] = agency
            else:
                # Add new agency
                config["agencies"].append(agency)
        
        # Write updated configuration
        try:
            with open(config_file, 'w') as f:
                json.dump(config, indent=2, fp=f)
            return True
        except Exception as e:
            print(f"Error writing configuration: {e}")
            return False
    
    def generate_all_agencies(self, agency_list: List[dict]) -> dict:
        """
        Generate components for all AI agencies in the list.
        
        Args:
            agency_list: List of agency data (acronym, name, domain)
            
        Returns:
            Dictionary with status for each agency
        """
        results = {}
        all_agencies = []
        
        for agency_data in agency_list:
            agency = agency_data.get("acronym")
            name = agency_data.get("name")
            domain = agency_data.get("domain")
            
            if agency and name:
                print(f"Generating components for {agency}...")
                results[agency] = self.generate_agency(agency, name, domain)
                
                if results[agency]:
                    # Add to the list of agencies to update in the main config
                    agency_data["ai_enabled"] = True
                    all_agencies.append(agency_data)
        
        # Update main configuration
        if all_agencies:
            self.update_config(all_agencies)
        
        return results


def parse_agency_spec(spec: str) -> dict:
    """
    Parse agency specification string.
    
    Args:
        spec: Agency specification string in format "acronym (name) - description: domain"
        
    Returns:
        Dictionary with agency information
    """
    agency_data = {"acronym": "", "name": "", "domain": "", "description": ""}
    
    # Extract acronym and name
    if " (" in spec and ")" in spec:
        acronym_part = spec.split(" (")[0].strip()
        name_part = spec.split(" (")[1].split(")")[0].strip()
        agency_data["acronym"] = acronym_part
        agency_data["name"] = name_part
    else:
        agency_data["acronym"] = spec.split(" – ")[0].strip()
        agency_data["name"] = spec.split(" – ")[0].strip()
    
    # Extract description and domain
    if " – " in spec:
        description_part = spec.split(" – ")[1].strip()
        
        # Extract description
        agency_data["description"] = description_part
        
        # Try to determine domain from description
        domain_keywords = {
            "health": "healthcare",
            "medic": "healthcare",
            "drug": "drugs",
            "biologic": "biologics",
            "food": "food",
            "nutrition": "nutrition",
            "agricult": "agriculture",
            "environment": "environment",
            "safety": "safety",
            "consumer product": "safety",
            "housing": "finance",
            "financ": "finance",
            "educat": "education",
            "transport": "transportation",
            "highway": "transportation"
        }
        
        for keyword, domain in domain_keywords.items():
            if keyword.lower() in description_part.lower():
                agency_data["domain"] = domain
                break
        
        # If domain not determined, check agency name
        if not agency_data["domain"] and agency_data["name"] in DOMAIN_TYPE_MAP:
            agency_data["domain"] = DOMAIN_TYPE_MAP[agency_data["name"]]
        
        # Default to healthcare if domain can't be determined
        if not agency_data["domain"]:
            agency_data["domain"] = "healthcare"
    
    return agency_data


def main():
    """Main entry point function."""
    parser = argparse.ArgumentParser(description="AI Agency Generator for Codex CLI")
    parser.add_argument("--agency", help="Agency acronym to generate components for")
    parser.add_argument("--name", help="Agency name (required with --agency)")
    parser.add_argument("--domain", help="Agency domain (will be determined from name if not provided)")
    parser.add_argument("--file", help="File containing agency specifications, one per line")
    parser.add_argument("--base-dir", default=os.path.dirname(os.path.abspath(__file__)),
                       help="Base directory for agency interface")
    parser.add_argument("--templates-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                             "templates"),
                       help="Directory for ASCII art templates")

    args = parser.parse_args()

    generator = AIAgencyGenerator(args.base_dir, args.templates_dir)

    if args.agency and args.name:
        # Generate components for a specific agency
        success = generator.generate_agency(args.agency, args.name, args.domain)
        print(f"Generation {'succeeded' if success else 'failed'} for {args.agency}.")
        
        # Update configuration
        if success:
            generator.update_config([{"acronym": args.agency, "name": args.name, "domain": args.domain or "", "ai_enabled": True}])
    elif args.file:
        # Parse agency specifications from file
        if not os.path.exists(args.file):
            print(f"Error: File {args.file} does not exist.")
            sys.exit(1)
        
        agencies = []
        with open(args.file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    agency_data = parse_agency_spec(line)
                    if agency_data["acronym"] and agency_data["name"]:
                        agencies.append(agency_data)
        
        if agencies:
            # Generate components for all agencies
            results = generator.generate_all_agencies(agencies)
            
            successes = sum(1 for success in results.values() if success)
            failures = sum(1 for success in results.values() if not success)
            
            print(f"Generation completed: {successes} succeeded, {failures} failed.")
            
            if failures > 0:
                print("Failed agencies:")
                for agency, success in results.items():
                    if not success:
                        print(f"  - {agency}")
        else:
            print("No valid agency specifications found in the file.")
    else:
        print("Error: Either --agency and --name or --file must be specified.")
        sys.exit(1)


if __name__ == "__main__":
    main()