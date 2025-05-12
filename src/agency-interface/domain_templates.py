#!/usr/bin/env python3
"""
Domain Templates for Agency Generation

This module provides templates for additional agency domains beyond the
ones included in the original agency_generator.py.
"""

# Additional domain templates for agency generation
ADDITIONAL_DOMAIN_TEMPLATES = {
    "intelligence": {
        "DEFAULT_DOMAINS": {
            "intelligence_collection": ["signals_intelligence", "human_intelligence", "open_source_intelligence"],
            "intelligence_analysis": ["threat_assessment", "strategic_analysis", "tactical_analysis"],
            "counterintelligence": ["counterespionage", "counterterrorism", "counterproliferation"],
            "cybersecurity": ["threat_detection", "vulnerability_assessment", "incident_response"],
            "intelligence_policy": ["oversight", "compliance", "legal_framework"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "intelligence_collection": {
                "description": "Collection of intelligence information",
                "sub_domains": ["signals_intelligence", "human_intelligence", "open_source_intelligence"]
            },
            "intelligence_analysis": {
                "description": "Analysis of intelligence information",
                "sub_domains": ["threat_assessment", "strategic_analysis", "tactical_analysis"]
            },
            "counterintelligence": {
                "description": "Protection against foreign intelligence threats",
                "sub_domains": ["counterespionage", "counterterrorism", "counterproliferation"]
            },
            "cybersecurity": {
                "description": "Protection of computer systems and networks",
                "sub_domains": ["threat_detection", "vulnerability_assessment", "incident_response"]
            },
            "intelligence_policy": {
                "description": "Policies governing intelligence activities",
                "sub_domains": ["oversight", "compliance", "legal_framework"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "executive_order_12333": {
                "name": "Executive Order 12333",
                "description": "Framework for intelligence activities",
                "components": ["collection", "analysis", "dissemination"]
            },
            "fisa": {
                "name": "Foreign Intelligence Surveillance Act",
                "description": "Framework for foreign intelligence surveillance",
                "components": ["electronic_surveillance", "physical_searches", "business_records"]
            },
            "intelligence_authorization": {
                "name": "Intelligence Authorization Act",
                "description": "Annual authorization for intelligence activities",
                "components": ["funding", "authorities", "reporting"]
            },
            "cybersecurity_framework": {
                "name": "Cybersecurity Framework",
                "description": "Framework for managing cybersecurity risk",
                "components": ["identify", "protect", "detect", "respond", "recover"]
            },
            "intelligence_sharing": {
                "name": "Intelligence Community Sharing Framework",
                "description": "Framework for sharing intelligence",
                "components": ["need_to_know", "handling_requirements", "dissemination"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["intelligence_collection", "intelligence_analysis", "cybersecurity"]
    },
    "financial_regulation": {
        "DEFAULT_DOMAINS": {
            "banking_regulation": ["bank_supervision", "capital_requirements", "stress_testing"],
            "securities_regulation": ["disclosure", "insider_trading", "market_manipulation"],
            "consumer_protection": ["fair_lending", "disclosure_requirements", "unfair_practices"],
            "financial_stability": ["systemic_risk", "macroprudential_policy", "crisis_response"],
            "enforcement": ["investigations", "enforcement_actions", "penalties"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "banking_regulation": {
                "description": "Regulation of banks and depository institutions",
                "sub_domains": ["bank_supervision", "capital_requirements", "stress_testing"]
            },
            "securities_regulation": {
                "description": "Regulation of securities markets",
                "sub_domains": ["disclosure", "insider_trading", "market_manipulation"]
            },
            "consumer_protection": {
                "description": "Protection of consumers in financial markets",
                "sub_domains": ["fair_lending", "disclosure_requirements", "unfair_practices"]
            },
            "financial_stability": {
                "description": "Maintaining stability of the financial system",
                "sub_domains": ["systemic_risk", "macroprudential_policy", "crisis_response"]
            },
            "enforcement": {
                "description": "Enforcement of financial regulations",
                "sub_domains": ["investigations", "enforcement_actions", "penalties"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "basel_iii": {
                "name": "Basel III",
                "description": "International framework for bank regulation",
                "components": ["capital_requirements", "leverage_ratio", "liquidity_requirements"]
            },
            "dodd_frank": {
                "name": "Dodd-Frank Act",
                "description": "Framework for financial regulation",
                "components": ["systemic_risk", "consumer_protection", "derivatives_regulation"]
            },
            "securities_laws": {
                "name": "Securities Laws",
                "description": "Framework for securities regulation",
                "components": ["registration", "disclosure", "antifraud"]
            },
            "supervisory_framework": {
                "name": "Supervisory Framework",
                "description": "Framework for bank supervision",
                "components": ["examinations", "reporting", "enforcement"]
            },
            "consumer_financial_protection": {
                "name": "Consumer Financial Protection Framework",
                "description": "Framework for consumer protection",
                "components": ["disclosure", "fair_lending", "unfair_practices"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["banking_regulation", "securities_regulation", "financial_stability"]
    },
    "cultural": {
        "DEFAULT_DOMAINS": {
            "arts": ["visual_arts", "performing_arts", "literary_arts"],
            "humanities": ["history", "philosophy", "literature"],
            "cultural_heritage": ["museums", "historical_sites", "archives"],
            "education": ["arts_education", "humanities_education", "public_programs"],
            "research": ["artistic_research", "historical_research", "cultural_research"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "arts": {
                "description": "Support for arts and artists",
                "sub_domains": ["visual_arts", "performing_arts", "literary_arts"]
            },
            "humanities": {
                "description": "Support for humanities disciplines",
                "sub_domains": ["history", "philosophy", "literature"]
            },
            "cultural_heritage": {
                "description": "Preservation of cultural heritage",
                "sub_domains": ["museums", "historical_sites", "archives"]
            },
            "education": {
                "description": "Education in arts and humanities",
                "sub_domains": ["arts_education", "humanities_education", "public_programs"]
            },
            "research": {
                "description": "Research in arts and humanities",
                "sub_domains": ["artistic_research", "historical_research", "cultural_research"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "grants_program": {
                "name": "Grants Program",
                "description": "Framework for grants to support arts and humanities",
                "components": ["project_grants", "fellowship_grants", "challenge_grants"]
            },
            "preservation_program": {
                "name": "Preservation Program",
                "description": "Framework for preservation of cultural heritage",
                "components": ["conservation", "digitization", "access"]
            },
            "education_program": {
                "name": "Education Program",
                "description": "Framework for education in arts and humanities",
                "components": ["curriculum_development", "teacher_training", "public_programs"]
            },
            "research_program": {
                "name": "Research Program",
                "description": "Framework for research in arts and humanities",
                "components": ["scholarly_research", "archival_research", "digital_humanities"]
            },
            "public_engagement": {
                "name": "Public Engagement Program",
                "description": "Framework for public engagement with arts and humanities",
                "components": ["exhibitions", "public_programs", "digital_engagement"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["arts", "humanities", "cultural_heritage"]
    },
    "international_development": {
        "DEFAULT_DOMAINS": {
            "humanitarian_assistance": ["disaster_response", "refugee_assistance", "food_assistance"],
            "economic_development": ["trade_capacity", "agricultural_development", "private_sector"],
            "democracy_governance": ["elections", "civil_society", "anticorruption"],
            "health": ["maternal_health", "infectious_diseases", "health_systems"],
            "education": ["basic_education", "higher_education", "workforce_development"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "humanitarian_assistance": {
                "description": "Emergency assistance in crisis situations",
                "sub_domains": ["disaster_response", "refugee_assistance", "food_assistance"]
            },
            "economic_development": {
                "description": "Support for economic growth and development",
                "sub_domains": ["trade_capacity", "agricultural_development", "private_sector"]
            },
            "democracy_governance": {
                "description": "Support for democratic institutions and governance",
                "sub_domains": ["elections", "civil_society", "anticorruption"]
            },
            "health": {
                "description": "Support for health systems and services",
                "sub_domains": ["maternal_health", "infectious_diseases", "health_systems"]
            },
            "education": {
                "description": "Support for education systems and services",
                "sub_domains": ["basic_education", "higher_education", "workforce_development"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "foreign_assistance_act": {
                "name": "Foreign Assistance Act",
                "description": "Framework for foreign assistance",
                "components": ["development_assistance", "economic_support", "humanitarian_assistance"]
            },
            "democracy_initiative": {
                "name": "Democracy Initiative",
                "description": "Framework for democracy and governance assistance",
                "components": ["elections", "civil_society", "rule_of_law"]
            },
            "health_initiative": {
                "name": "Global Health Initiative",
                "description": "Framework for health assistance",
                "components": ["maternal_health", "child_health", "infectious_diseases"]
            },
            "education_strategy": {
                "name": "Education Strategy",
                "description": "Framework for education assistance",
                "components": ["basic_education", "higher_education", "workforce_development"]
            },
            "food_security_initiative": {
                "name": "Food Security Initiative",
                "description": "Framework for food security assistance",
                "components": ["agricultural_development", "nutrition", "resilience"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["humanitarian_assistance", "economic_development", "health"]
    },
    "regulatory": {
        "DEFAULT_DOMAINS": {
            "rulemaking": ["proposed_rules", "final_rules", "regulatory_analysis"],
            "enforcement": ["investigations", "compliance_monitoring", "enforcement_actions"],
            "standards": ["technical_standards", "safety_standards", "performance_standards"],
            "licensing": ["licensing_review", "permit_issuance", "compliance_verification"],
            "policy": ["regulatory_policy", "guidance_development", "regulatory_reform"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "rulemaking": {
                "description": "Development of regulations and rules",
                "sub_domains": ["proposed_rules", "final_rules", "regulatory_analysis"]
            },
            "enforcement": {
                "description": "Enforcement of regulations",
                "sub_domains": ["investigations", "compliance_monitoring", "enforcement_actions"]
            },
            "standards": {
                "description": "Development and maintenance of standards",
                "sub_domains": ["technical_standards", "safety_standards", "performance_standards"]
            },
            "licensing": {
                "description": "Licensing and permitting activities",
                "sub_domains": ["licensing_review", "permit_issuance", "compliance_verification"]
            },
            "policy": {
                "description": "Development of regulatory policy",
                "sub_domains": ["regulatory_policy", "guidance_development", "regulatory_reform"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "administrative_procedure_act": {
                "name": "Administrative Procedure Act",
                "description": "Framework for regulatory procedures",
                "components": ["rulemaking", "adjudication", "judicial_review"]
            },
            "regulatory_flexibility_act": {
                "name": "Regulatory Flexibility Act",
                "description": "Framework for considering small entity impacts",
                "components": ["initial_analysis", "final_analysis", "periodic_review"]
            },
            "paperwork_reduction_act": {
                "name": "Paperwork Reduction Act",
                "description": "Framework for information collection",
                "components": ["information_collection", "burden_estimation", "omb_review"]
            },
            "executive_order_12866": {
                "name": "Executive Order 12866",
                "description": "Framework for regulatory planning and review",
                "components": ["principles", "oira_review", "cost_benefit_analysis"]
            },
            "unfunded_mandates_reform_act": {
                "name": "Unfunded Mandates Reform Act",
                "description": "Framework for analyzing unfunded mandates",
                "components": ["mandate_identification", "cost_analysis", "alternatives"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["rulemaking", "enforcement", "standards"]
    },
    "infrastructure": {
        "DEFAULT_DOMAINS": {
            "public_buildings": ["federal_buildings", "courthouses", "border_facilities"],
            "acquisition": ["leasing", "purchasing", "construction"],
            "property_management": ["maintenance", "security", "energy_efficiency"],
            "technology": ["information_technology", "telecommunications", "cybersecurity"],
            "contracting": ["procurement_policy", "contract_management", "small_business"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "public_buildings": {
                "description": "Management of public buildings",
                "sub_domains": ["federal_buildings", "courthouses", "border_facilities"]
            },
            "acquisition": {
                "description": "Acquisition of property and facilities",
                "sub_domains": ["leasing", "purchasing", "construction"]
            },
            "property_management": {
                "description": "Management of federal property",
                "sub_domains": ["maintenance", "security", "energy_efficiency"]
            },
            "technology": {
                "description": "Management of information technology",
                "sub_domains": ["information_technology", "telecommunications", "cybersecurity"]
            },
            "contracting": {
                "description": "Management of federal contracting",
                "sub_domains": ["procurement_policy", "contract_management", "small_business"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "federal_property_act": {
                "name": "Federal Property and Administrative Services Act",
                "description": "Framework for property management",
                "components": ["acquisition", "use", "disposal"]
            },
            "federal_acquisition_regulation": {
                "name": "Federal Acquisition Regulation",
                "description": "Framework for procurement",
                "components": ["competition", "contract_types", "socioeconomic_programs"]
            },
            "public_buildings_act": {
                "name": "Public Buildings Act",
                "description": "Framework for public buildings",
                "components": ["construction", "alteration", "operation"]
            },
            "clinger_cohen_act": {
                "name": "Clinger-Cohen Act",
                "description": "Framework for information technology management",
                "components": ["capital_planning", "investment_control", "performance_measurement"]
            },
            "energy_policy_act": {
                "name": "Energy Policy Act",
                "description": "Framework for energy management",
                "components": ["energy_efficiency", "renewable_energy", "sustainable_buildings"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["public_buildings", "acquisition", "technology"]
    },
    "archives": {
        "DEFAULT_DOMAINS": {
            "records_management": ["federal_records", "presidential_records", "electronic_records"],
            "archival_programs": ["preservation", "processing", "description"],
            "access": ["research_services", "declassification", "digital_access"],
            "public_programs": ["exhibitions", "education", "outreach"],
            "policy": ["records_policy", "preservation_policy", "access_policy"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "records_management": {
                "description": "Management of federal records",
                "sub_domains": ["federal_records", "presidential_records", "electronic_records"]
            },
            "archival_programs": {
                "description": "Programs for archival preservation and access",
                "sub_domains": ["preservation", "processing", "description"]
            },
            "access": {
                "description": "Access to archival records",
                "sub_domains": ["research_services", "declassification", "digital_access"]
            },
            "public_programs": {
                "description": "Public programs and outreach",
                "sub_domains": ["exhibitions", "education", "outreach"]
            },
            "policy": {
                "description": "Policies for records and archives",
                "sub_domains": ["records_policy", "preservation_policy", "access_policy"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "records_act": {
                "name": "Federal Records Act",
                "description": "Framework for federal records management",
                "components": ["creation", "maintenance", "disposition"]
            },
            "presidential_records_act": {
                "name": "Presidential Records Act",
                "description": "Framework for presidential records",
                "components": ["ownership", "custody", "access"]
            },
            "freedom_of_information_act": {
                "name": "Freedom of Information Act",
                "description": "Framework for access to government information",
                "components": ["request_process", "exemptions", "appeals"]
            },
            "executive_order_13526": {
                "name": "Executive Order 13526",
                "description": "Framework for classified information",
                "components": ["classification", "declassification", "safeguarding"]
            },
            "electronic_records_archives": {
                "name": "Electronic Records Archives",
                "description": "Framework for electronic records",
                "components": ["preservation", "access", "search"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["records_management", "archival_programs", "access"]
    },
    "nuclear": {
        "DEFAULT_DOMAINS": {
            "reactor_safety": ["licensing", "inspection", "regulatory_oversight"],
            "materials_safety": ["radioactive_materials", "spent_fuel", "transportation"],
            "security": ["physical_security", "cybersecurity", "insider_threats"],
            "emergency_preparedness": ["emergency_plans", "incident_response", "coordination"],
            "regulatory_policy": ["rulemaking", "guidance", "standards"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "reactor_safety": {
                "description": "Safety of nuclear reactors",
                "sub_domains": ["licensing", "inspection", "regulatory_oversight"]
            },
            "materials_safety": {
                "description": "Safety of nuclear materials",
                "sub_domains": ["radioactive_materials", "spent_fuel", "transportation"]
            },
            "security": {
                "description": "Security of nuclear facilities and materials",
                "sub_domains": ["physical_security", "cybersecurity", "insider_threats"]
            },
            "emergency_preparedness": {
                "description": "Preparedness for nuclear emergencies",
                "sub_domains": ["emergency_plans", "incident_response", "coordination"]
            },
            "regulatory_policy": {
                "description": "Policies for nuclear regulation",
                "sub_domains": ["rulemaking", "guidance", "standards"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "atomic_energy_act": {
                "name": "Atomic Energy Act",
                "description": "Framework for nuclear regulation",
                "components": ["licensing", "inspection", "enforcement"]
            },
            "nuclear_waste_policy_act": {
                "name": "Nuclear Waste Policy Act",
                "description": "Framework for nuclear waste management",
                "components": ["storage", "disposal", "transportation"]
            },
            "price_anderson_act": {
                "name": "Price-Anderson Nuclear Industries Indemnity Act",
                "description": "Framework for nuclear liability",
                "components": ["indemnification", "insurance", "compensation"]
            },
            "radiation_protection_standards": {
                "name": "Radiation Protection Standards",
                "description": "Framework for radiation protection",
                "components": ["exposure_limits", "monitoring", "dosimetry"]
            },
            "nuclear_security_regulations": {
                "name": "Nuclear Security Regulations",
                "description": "Framework for nuclear security",
                "components": ["physical_security", "cybersecurity", "insider_threats"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["reactor_safety", "materials_safety", "security"]
    },
    "pensions": {
        "DEFAULT_DOMAINS": {
            "pension_insurance": ["single_employer", "multiemployer", "risk_management"],
            "pension_regulation": ["reporting", "disclosure", "fiduciary_standards"],
            "research": ["pension_research", "economic_analysis", "policy_analysis"],
            "operations": ["premium_collection", "benefit_payments", "asset_management"],
            "policy": ["pension_policy", "retirement_security", "legislative_analysis"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "pension_insurance": {
                "description": "Insurance of pension plans",
                "sub_domains": ["single_employer", "multiemployer", "risk_management"]
            },
            "pension_regulation": {
                "description": "Regulation of pension plans",
                "sub_domains": ["reporting", "disclosure", "fiduciary_standards"]
            },
            "research": {
                "description": "Research on pension and retirement issues",
                "sub_domains": ["pension_research", "economic_analysis", "policy_analysis"]
            },
            "operations": {
                "description": "Operations of pension insurance program",
                "sub_domains": ["premium_collection", "benefit_payments", "asset_management"]
            },
            "policy": {
                "description": "Policies for pensions and retirement security",
                "sub_domains": ["pension_policy", "retirement_security", "legislative_analysis"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "erisa": {
                "name": "Employee Retirement Income Security Act",
                "description": "Framework for private pension plans",
                "components": ["reporting", "disclosure", "fiduciary_standards"]
            },
            "mppaa": {
                "name": "Multiemployer Pension Plan Amendments Act",
                "description": "Framework for multiemployer pension plans",
                "components": ["withdrawal_liability", "insolvency", "reorganization"]
            },
            "ppa": {
                "name": "Pension Protection Act",
                "description": "Framework for pension funding",
                "components": ["funding_rules", "benefit_restrictions", "reporting"]
            },
            "singleemployer_insurance": {
                "name": "Single-Employer Insurance Program",
                "description": "Framework for single-employer pension insurance",
                "components": ["premiums", "guarantees", "terminations"]
            },
            "multiemployer_insurance": {
                "name": "Multiemployer Insurance Program",
                "description": "Framework for multiemployer pension insurance",
                "components": ["premiums", "guarantees", "partitions"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["pension_insurance", "pension_regulation", "policy"]
    }
}

# Function to integrate additional domain templates with existing templates
def integrate_domain_templates(existing_templates, additional_templates):
    """
    Integrate additional domain templates with existing templates.
    
    Args:
        existing_templates: Existing domain templates dictionary
        additional_templates: Additional domain templates dictionary
        
    Returns:
        Updated domain templates dictionary
    """
    result = existing_templates.copy()
    
    for domain, templates in additional_templates.items():
        result[domain] = templates
    
    return result