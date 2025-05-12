"""
Enhanced Adaptive Trial Framework with abstraction and relationship analysis integration.

This module extends the base adaptive trial framework with capabilities to incorporate
insights from abstraction and relationship analysis.
"""
import json
import logging
import re
import copy
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Placeholder for the actual adaptive trial framework
class AdaptiveTrialFramework:
    """Stub for the actual adaptive trial framework."""
    
    def design_trial(self, protocol_template, patient_population):
        """
        Design an adaptive trial based on a protocol template and patient population.
        
        Args:
            protocol_template: Template for trial protocol
            patient_population: Target patient population
            
        Returns:
            Complete trial protocol
        """
        logger.info(f"[STUB] Designing trial with {len(patient_population)} patients")
        # This is a stub implementation
        return protocol_template
    
    def analyze_interim_results(self, trial_data, patient_outcomes):
        """
        Analyze interim trial results.
        
        Args:
            trial_data: Current trial data
            patient_outcomes: Current patient outcomes
            
        Returns:
            Analysis results and recommendations
        """
        logger.info(f"[STUB] Analyzing interim results for {len(patient_outcomes)} patients")
        # This is a stub implementation
        return {
            "trial_id": trial_data.get("trial_id", "unknown"),
            "analysis_time": datetime.now().isoformat(),
            "total_patients": len(patient_outcomes),
            "recommendations": []
        }


class EnhancedAdaptiveTrialFramework:
    """
    Enhanced adaptive trial framework that utilizes abstraction and relationship insights.
    """
    
    def __init__(self, abstraction_analysis_results=None):
        """
        Initialize the enhanced adaptive trial framework.
        
        Args:
            abstraction_analysis_results: Results from abstraction analysis
        """
        self.base_trial_framework = AdaptiveTrialFramework()  # Original framework
        self.abstraction_results = abstraction_analysis_results
        self.biomarker_clusters = self._identify_biomarker_clusters()
        logger.info(f"Initialized EnhancedAdaptiveTrialFramework with {'with' if abstraction_analysis_results else 'without'} abstraction results")
    
    def _identify_biomarker_clusters(self):
        """
        Identify biomarker clusters from abstractions.
        
        Returns:
            Dictionary of biomarker clusters
        """
        if not self.abstraction_results:
            return {}
            
        clusters = {}
        for i, abstraction in enumerate(self.abstraction_results.get("abstractions", [])):
            if "biomarker" in abstraction["name"].lower() or "genetic" in abstraction["name"].lower():
                # Extract biomarkers mentioned in the abstraction
                biomarkers = self._extract_biomarkers_from_abstraction(abstraction)
                if biomarkers:
                    clusters[i] = {
                        "name": abstraction["name"],
                        "biomarkers": biomarkers
                    }
                    
        logger.info(f"Identified {len(clusters)} biomarker clusters")
        return clusters
    
    def _extract_biomarkers_from_abstraction(self, abstraction):
        """
        Extract biomarker names from abstraction.
        
        Args:
            abstraction: Abstraction dictionary
            
        Returns:
            List of extracted biomarkers
        """
        # Common Crohn's disease biomarkers
        known_biomarkers = ["NOD2", "IL23R", "ATG16L1", "IRGM", "LRRK2", "TNF", "IL10", "JAK2", "STAT3"]
        
        biomarkers = []
        # Find known biomarkers in the description
        for biomarker in known_biomarkers:
            if biomarker in abstraction["description"]:
                biomarkers.append(biomarker)
        
        # Use regex to find additional biomarker-like patterns
        if not biomarkers:
            matches = re.findall(r'([A-Z0-9]{2,}[0-9]?)', abstraction["description"])
            for match in matches:
                # Exclude common non-biomarker acronyms
                if match not in ["API", "GUI", "HTTP", "JSON", "REST", "XML", "CDAI", "SES"]:
                    biomarkers.append(match)
        
        return list(set(biomarkers))
    
    def design_trial(self, protocol_template, patient_population, abstraction_guided=True):
        """
        Design an adaptive trial using abstraction insights.
        
        Args:
            protocol_template: Base protocol template
            patient_population: Target patient population
            abstraction_guided: Whether to use abstraction insights
            
        Returns:
            Adaptive trial protocol
        """
        logger.info(f"Designing trial for {len(patient_population)} patients, abstraction_guided={abstraction_guided}")
        
        if not abstraction_guided or not self.abstraction_results:
            # Fall back to base framework if abstraction results not available
            logger.info("Using base adaptive trial framework (abstraction_guided=False)")
            return self.base_trial_framework.design_trial(protocol_template, patient_population)
        
        # Enhanced protocol with abstraction-guided components
        enhanced_protocol = copy.deepcopy(protocol_template)
        
        # Add biomarker stratification based on abstractions
        enhanced_protocol["arms"] = self._enhance_trial_arms(enhanced_protocol.get("arms", []))
        
        # Add relationship-guided adaptive rules
        enhanced_protocol["adaptiveRules"] = self._enhance_adaptive_rules(
            enhanced_protocol.get("adaptiveRules", [])
        )
        
        logger.info(f"Enhanced protocol: {len(enhanced_protocol['arms'])} arms, {len(enhanced_protocol['adaptiveRules'])} adaptive rules")
        return enhanced_protocol
    
    def _enhance_trial_arms(self, arms):
        """
        Enhance trial arms with biomarker stratification based on abstractions.
        
        Args:
            arms: List of trial arms
            
        Returns:
            Enhanced trial arms
        """
        enhanced_arms = []
        
        for arm in arms:
            enhanced_arm = copy.deepcopy(arm)
            
            # Add biomarker stratification based on clusters
            if "biomarkerStratification" not in enhanced_arm:
                enhanced_arm["biomarkerStratification"] = []
                
            # Find relevant biomarker clusters for this arm's treatment
            for cluster_id, cluster in self.biomarker_clusters.items():
                # Check if this medication works better for this biomarker cluster
                if self._is_effective_for_cluster(arm["treatment"]["medication"], cluster_id):
                    # Add all biomarkers from this cluster to stratification
                    for biomarker in cluster["biomarkers"]:
                        if not any(b["biomarker"] == biomarker for b in enhanced_arm["biomarkerStratification"]):
                            enhanced_arm["biomarkerStratification"].append({
                                "biomarker": biomarker,
                                "criteria": "variant"
                            })
                            logger.info(f"Added biomarker {biomarker} stratification to arm {arm['armId']}")
            
            enhanced_arms.append(enhanced_arm)
            
        return enhanced_arms
    
    def _is_effective_for_cluster(self, medication, cluster_id):
        """
        Check if medication is known to be effective for a biomarker cluster.
        
        Args:
            medication: Medication name
            cluster_id: Biomarker cluster ID
            
        Returns:
            Boolean indicating effectiveness
        """
        if not self.abstraction_results or not self.abstraction_results.get("relationships"):
            return False
            
        # Look for positive relationships in the graph
        for rel in self.abstraction_results["relationships"].get("details", []):
            # Check if this is a positive relationship between medication and biomarker cluster
            if rel["from"] == cluster_id:
                target_abstraction = self.abstraction_results["abstractions"][rel["to"]]
                # Check if the target abstraction mentions this medication
                if medication.lower() in target_abstraction["description"].lower():
                    # Check if the relationship is positive
                    if any(term in rel["label"].lower() for term in ["response", "effective", "improves"]):
                        logger.info(f"Found effectiveness relationship between cluster {cluster_id} and {medication}")
                        return True
        
        return False
    
    def _enhance_adaptive_rules(self, rules):
        """
        Enhance adaptive rules based on abstraction relationships.
        
        Args:
            rules: List of adaptive rules
            
        Returns:
            Enhanced adaptive rules
        """
        enhanced_rules = copy.deepcopy(rules)
        
        # Add new rules based on relationships if we have abstraction results
        if self.abstraction_results and self.abstraction_results.get("relationships"):
            # Check summary for insights
            summary = self.abstraction_results["relationships"].get("summary", "")
            
            # Add interim analysis rule if not already present
            if not any(r["action"] == "response_adaptive_randomization" for r in enhanced_rules):
                enhanced_rules.append({
                    "triggerCondition": "interim_analysis_1",
                    "action": "response_adaptive_randomization",
                    "parameters": {
                        "min_allocation": 0.1
                    }
                })
                logger.info("Added response_adaptive_randomization rule")
            
            # Add biomarker-based arm dropping rule if biomarker response mentioned
            if "biomarker" in summary.lower() and "response" in summary.lower():
                if not any(r["action"] == "biomarker_based_arm_dropping" for r in enhanced_rules):
                    enhanced_rules.append({
                        "triggerCondition": "interim_analysis_2",
                        "action": "biomarker_based_arm_dropping",
                        "parameters": {
                            "min_response_rate": 0.2,
                            "confidence_level": 0.9
                        }
                    })
                    logger.info("Added biomarker_based_arm_dropping rule")
                    
            # Add sample size re-estimation rule if treatment effect mentioned
            if "treatment" in summary.lower() and "effect" in summary.lower():
                if not any(r["action"] == "sample_size_reestimation" for r in enhanced_rules):
                    enhanced_rules.append({
                        "triggerCondition": "interim_analysis_1",
                        "action": "sample_size_reestimation",
                        "parameters": {
                            "target_power": 0.9
                        }
                    })
                    logger.info("Added sample_size_reestimation rule")
        
        return enhanced_rules
    
    def analyze_interim_results(self, trial_data, patient_outcomes, abstraction_guided=True):
        """
        Analyze interim trial results using abstraction insights.
        
        Args:
            trial_data: Current trial data
            patient_outcomes: Current patient outcomes
            abstraction_guided: Whether to use abstraction insights
            
        Returns:
            Analysis results and recommended adaptations
        """
        logger.info(f"Analyzing interim results for {len(patient_outcomes)} patients, abstraction_guided={abstraction_guided}")
        
        if not abstraction_guided or not self.abstraction_results:
            # Fall back to base framework if abstraction results not available
            logger.info("Using base analysis framework (abstraction_guided=False)")
            return self.base_trial_framework.analyze_interim_results(trial_data, patient_outcomes)
        
        # Get base analysis
        base_analysis = self.base_trial_framework.analyze_interim_results(trial_data, patient_outcomes)
        
        # Enhance with abstraction-guided insights
        enhanced_analysis = copy.deepcopy(base_analysis)
        
        # Add biomarker response patterns from abstractions
        enhanced_analysis["biomarker_patterns"] = self._identify_biomarker_patterns(patient_outcomes)
        
        # Add relationship-guided recommendations
        enhanced_analysis["recommendations"] = enhanced_analysis.get("recommendations", [])
        relationship_recommendations = self._generate_relationship_based_recommendations(trial_data, patient_outcomes)
        enhanced_analysis["recommendations"].extend(relationship_recommendations)
        
        logger.info(f"Generated {len(enhanced_analysis['biomarker_patterns'])} biomarker patterns and {len(relationship_recommendations)} recommendations")
        return enhanced_analysis
    
    def _identify_biomarker_patterns(self, patient_outcomes):
        """
        Identify patterns of biomarker response from outcomes.
        
        Args:
            patient_outcomes: List of patient outcome dictionaries
            
        Returns:
            List of biomarker response patterns
        """
        patterns = []
        
        # Skip if no abstractions
        if not self.abstraction_results:
            return patterns
            
        # Group patients by biomarker profile
        biomarker_groups = {}
        for patient in patient_outcomes:
            profile_key = self._create_biomarker_profile_key(patient)
            if profile_key not in biomarker_groups:
                biomarker_groups[profile_key] = []
            biomarker_groups[profile_key].append(patient)
        
        # Analyze response rates for each biomarker cluster
        for cluster_id, cluster in self.biomarker_clusters.items():
            cluster_patterns = {
                "cluster_id": cluster_id, 
                "cluster_name": cluster["name"], 
                "response_by_arm": {}
            }
            
            # Get all unique arm IDs
            arm_ids = set(p.get("arm_id") for p in patient_outcomes if p.get("arm_id"))
            
            for arm_id in arm_ids:
                # Calculate response rate for this biomarker cluster in this arm
                arm_patients = [p for p in patient_outcomes if p.get("arm_id") == arm_id]
                cluster_patients = [p for p in arm_patients if self._matches_cluster(p, cluster)]
                
                if cluster_patients:
                    responders = sum(1 for p in cluster_patients if p.get("is_responder", False))
                    response_rate = responders / len(cluster_patients)
                    
                    # Calculate overall arm response rate for comparison
                    overall_responders = sum(1 for p in arm_patients if p.get("is_responder", False))
                    overall_rate = overall_responders / len(arm_patients) if arm_patients else 0
                    
                    cluster_patterns["response_by_arm"][arm_id] = {
                        "patients": len(cluster_patients),
                        "response_rate": response_rate,
                        "overall_rate": overall_rate,
                        "significance": self._calculate_significance(response_rate, overall_rate)
                    }
            
            # Only add patterns if we have response data
            if cluster_patterns["response_by_arm"]:
                patterns.append(cluster_patterns)
            
        return patterns
    
    def _create_biomarker_profile_key(self, patient):
        """
        Create a string key representing a patient's biomarker profile.
        
        Args:
            patient: Patient data dictionary
            
        Returns:
            String key for the biomarker profile
        """
        markers = []
        for m in patient.get("biomarkers", {}).get("genetic_markers", []):
            if all(k in m for k in ["gene", "variant", "zygosity"]):
                markers.append(f"{m['gene']}:{m['variant']}:{m['zygosity']}")
        
        return "|".join(sorted(markers)) if markers else "no_biomarkers"
    
    def _matches_cluster(self, patient, cluster):
        """
        Check if a patient matches a biomarker cluster.
        
        Args:
            patient: Patient data dictionary
            cluster: Biomarker cluster dictionary
            
        Returns:
            Boolean indicating whether the patient matches the cluster
        """
        patient_markers = []
        for m in patient.get("biomarkers", {}).get("genetic_markers", []):
            if "gene" in m:
                patient_markers.append(m["gene"])
        
        return any(marker in patient_markers for marker in cluster["biomarkers"])
    
    def _calculate_significance(self, cluster_rate, overall_rate):
        """
        Calculate statistical significance of difference in response rates.
        
        Args:
            cluster_rate: Response rate in the cluster
            overall_rate: Overall response rate
            
        Returns:
            Significance level (high, medium, low)
        """
        # Simplified implementation - real version would use proper statistical test
        diff = abs(cluster_rate - overall_rate)
        if diff > 0.2:
            return "high"
        elif diff > 0.1:
            return "medium"
        return "low"
    
    def _generate_relationship_based_recommendations(self, trial_data, patient_outcomes):
        """
        Generate recommendations based on relationship analysis.
        
        Args:
            trial_data: Trial data dictionary
            patient_outcomes: List of patient outcome dictionaries
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not self.abstraction_results or not self.abstraction_results.get("relationships"):
            return recommendations
        
        # Look for biomarker-treatment relationships with strong effects
        for rel in self.abstraction_results["relationships"].get("details", []):
            from_abstraction = self.abstraction_results["abstractions"][rel["from"]]
            to_abstraction = self.abstraction_results["abstractions"][rel["to"]]
            
            # If relationship suggests treatment efficacy
            if any(term in rel["label"].lower() for term in ["improves", "effective", "response"]):
                # Extract biomarker and treatment information
                biomarker = self._extract_primary_biomarker(from_abstraction)
                treatment = self._extract_primary_treatment(to_abstraction)
                
                if biomarker and treatment:
                    # Check outcomes to see if this is supported by data
                    if self._is_supported_by_outcomes(biomarker, treatment, patient_outcomes):
                        recommendations.append({
                            "type": "biomarker_treatment_match",
                            "biomarker": biomarker,
                            "treatment": treatment,
                            "confidence": "high",
                            "action": "increase_allocation",
                            "justification": f"Patients with {biomarker} show higher response to {treatment}"
                        })
                        logger.info(f"Added recommendation for {biomarker} and {treatment}")
        
        return recommendations
    
    def _extract_primary_biomarker(self, abstraction):
        """
        Extract primary biomarker from abstraction.
        
        Args:
            abstraction: Abstraction dictionary
            
        Returns:
            Extracted biomarker or None
        """
        # Common Crohn's disease biomarkers
        known_biomarkers = ["NOD2", "IL23R", "ATG16L1", "IRGM", "LRRK2", "TNF", "IL10", "JAK2", "STAT3"]
        
        # Check for known biomarkers in the description
        for biomarker in known_biomarkers:
            if biomarker in abstraction["description"]:
                return biomarker
                
        # Use regex as fallback
        match = re.search(r'(NOD2|IL23R|ATG16L1|IRGM|LRRK2|[A-Z0-9]{2,}[0-9]?)', abstraction["description"])
        return match.group(1) if match else None
    
    def _extract_primary_treatment(self, abstraction):
        """
        Extract primary treatment from abstraction.
        
        Args:
            abstraction: Abstraction dictionary
            
        Returns:
            Extracted treatment name or None
        """
        # Common Crohn's disease treatments
        treatments = ["Upadacitinib", "Adalimumab", "Infliximab", "Vedolizumab", "Ustekinumab", 
                     "Tofacitinib", "Risankizumab", "Certolizumab", "Golimumab", "Prednisone"]
        
        for treatment in treatments:
            if treatment.lower() in abstraction["description"].lower():
                return treatment
                
        # Check for brand names
        brand_names = {
            "Humira": "Adalimumab",
            "Remicade": "Infliximab",
            "Entyvio": "Vedolizumab",
            "Stelara": "Ustekinumab",
            "Xeljanz": "Tofacitinib",
            "Skyrizi": "Risankizumab",
            "Cimzia": "Certolizumab",
            "Simponi": "Golimumab"
        }
        
        for brand, generic in brand_names.items():
            if brand.lower() in abstraction["description"].lower():
                return generic
                
        return None
    
    def _is_supported_by_outcomes(self, biomarker, treatment, patient_outcomes):
        """
        Check if biomarker-treatment relationship is supported by outcomes.
        
        Args:
            biomarker: Biomarker name
            treatment: Treatment name
            patient_outcomes: List of patient outcome dictionaries
            
        Returns:
            Boolean indicating whether the relationship is supported
        """
        # Group patients by biomarker status and treatment
        biomarker_positive_treated = []
        biomarker_negative_treated = []
        
        for patient in patient_outcomes:
            # Check if patient has this biomarker
            has_biomarker = False
            for m in patient.get("biomarkers", {}).get("genetic_markers", []):
                if m.get("gene") == biomarker and m.get("variant") == "variant":
                    has_biomarker = True
                    break
            
            # Check if patient received this treatment
            got_treatment = False
            if patient.get("treatment", {}).get("medication") == treatment:
                got_treatment = True
            
            if got_treatment:
                if has_biomarker:
                    biomarker_positive_treated.append(patient)
                else:
                    biomarker_negative_treated.append(patient)
        
        # Calculate response rates
        if biomarker_positive_treated and biomarker_negative_treated:
            positive_response_rate = sum(1 for p in biomarker_positive_treated if p.get("is_responder", False)) / len(biomarker_positive_treated)
            negative_response_rate = sum(1 for p in biomarker_negative_treated if p.get("is_responder", False)) / len(biomarker_negative_treated)
            
            # Check if there's a significant difference
            return positive_response_rate > negative_response_rate * 1.3  # 30% better response
        
        return False