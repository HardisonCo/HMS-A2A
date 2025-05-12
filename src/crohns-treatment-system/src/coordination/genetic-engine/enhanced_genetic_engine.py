"""
Enhanced Genetic Engine that utilizes abstraction and relationship insights.

This module extends the base genetic engine with capabilities to incorporate
insights from the abstraction and relationship analysis.
"""
import json
import logging
import re
import networkx as nx
from typing import Dict, List, Any, Optional, Callable

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import placeholder for the actual genetic engine
# In the real implementation, this would be imported from the Rust FFI module
class GeneticEngine:
    """Stub for the actual genetic engine, to be replaced by the Rust FFI implementation."""
    
    def optimize_treatment(self, patient_data, fitness_function=None, constraints=None):
        """
        Optimize treatment for a patient using the genetic algorithm.
        
        Args:
            patient_data: Patient data dictionary
            fitness_function: Optional custom fitness function
            constraints: Optional treatment constraints
            
        Returns:
            Optimized treatment plan
        """
        logger.info(f"[STUB] Optimizing treatment for patient {patient_data.get('patient_id')}")
        # This is a stub implementation - in production this would call the actual Rust genetic engine
        return {
            "treatment_plan": [
                {
                    "medication": "Upadacitinib",
                    "dosage": "15",
                    "unit": "mg",
                    "frequency": "daily",
                    "duration": 90
                }
            ],
            "fitness": 0.85
        }
    
    def calculate_fitness(self, treatment_plan, patient_data):
        """
        Calculate fitness score for a treatment plan.
        
        Args:
            treatment_plan: Treatment plan to evaluate
            patient_data: Patient data dictionary
            
        Returns:
            Fitness score between 0 and 1
        """
        # This is a stub implementation - in production this would call the actual fitness calculation
        return 0.8


class EnhancedGeneticEngine:
    """
    Enhanced genetic engine that utilizes abstraction and relationship insights.
    """
    
    def __init__(self, abstraction_analysis_results=None):
        """
        Initialize the enhanced genetic engine.
        
        Args:
            abstraction_analysis_results: Results from abstraction analysis
        """
        self.base_genetic_engine = GeneticEngine()  # Original genetic engine
        self.abstraction_results = abstraction_analysis_results
        self.relationship_graph = self._build_relationship_graph()
        logger.info(f"Initialized EnhancedGeneticEngine with {'with' if abstraction_analysis_results else 'without'} abstraction results")
    
    def _build_relationship_graph(self):
        """
        Build a graph representation of relationships.
        
        Returns:
            NetworkX DiGraph of relationships or None if no data available
        """
        if not self.abstraction_results:
            return None
            
        graph = nx.DiGraph()
        
        # Add nodes (abstractions)
        for i, abstraction in enumerate(self.abstraction_results.get("abstractions", [])):
            graph.add_node(i, name=abstraction["name"], description=abstraction["description"])
        
        # Add edges (relationships)
        for rel in self.abstraction_results.get("relationships", {}).get("details", []):
            graph.add_edge(
                rel["from"], 
                rel["to"], 
                label=rel["label"]
            )
        
        logger.info(f"Built relationship graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        return graph
    
    def optimize_treatment(self, patient_data, abstraction_guided=True):
        """
        Optimize treatment using genetic algorithm with abstraction guidance.
        
        Args:
            patient_data: Patient data dictionary
            abstraction_guided: Whether to use abstraction insights for optimization
            
        Returns:
            Optimized treatment plan
        """
        patient_id = patient_data.get('patient_id', 'unknown')
        logger.info(f"Optimizing treatment for patient {patient_id}, abstraction_guided={abstraction_guided}")
        
        if not abstraction_guided or not self.abstraction_results:
            # Fall back to base genetic engine if abstraction results not available
            logger.info(f"Using base genetic engine for patient {patient_id} (abstraction_guided={abstraction_guided})")
            return self.base_genetic_engine.optimize_treatment(patient_data)
        
        # Get relevant abstractions for this patient
        relevant_abstractions = self._get_relevant_abstractions(patient_data)
        logger.info(f"Found {len(relevant_abstractions)} relevant abstractions for patient {patient_id}")
        
        # Get treatment constraints from relationships
        treatment_constraints = self._derive_treatment_constraints(relevant_abstractions, patient_data)
        
        # Apply enhanced fitness function
        enhanced_fitness_fn = self._create_enhanced_fitness_function(relevant_abstractions)
        
        # Run optimized genetic algorithm
        logger.info(f"Running enhanced genetic optimization with {len(treatment_constraints)} constraints")
        return self.base_genetic_engine.optimize_treatment(
            patient_data,
            fitness_function=enhanced_fitness_fn,
            constraints=treatment_constraints
        )
    
    def _get_relevant_abstractions(self, patient_data):
        """
        Identify abstractions relevant to this patient.
        
        Args:
            patient_data: Patient data dictionary
            
        Returns:
            List of abstraction indices relevant to the patient
        """
        if not self.abstraction_results:
            return []
            
        relevant = []
        for i, abstraction in enumerate(self.abstraction_results.get("abstractions", [])):
            if self._matches_patient(abstraction, patient_data):
                relevant.append(i)
                
        return relevant
    
    def _matches_patient(self, abstraction, patient_data):
        """
        Check if abstraction matches patient characteristics.
        
        Args:
            abstraction: Abstraction dictionary
            patient_data: Patient data dictionary
            
        Returns:
            Boolean indicating whether the abstraction matches
        """
        # Check for biomarker matches
        if "biomarker" in abstraction["name"].lower() or "genetic" in abstraction["name"].lower():
            for marker in patient_data.get("biomarkers", {}).get("genetic_markers", []):
                if marker["gene"] in abstraction["description"]:
                    return True
        
        # Check for disease type matches
        if "crohn" in abstraction["name"].lower():
            crohns_type = patient_data.get("clinical_data", {}).get("crohns_type", "")
            if crohns_type and crohns_type.lower() in abstraction["description"].lower():
                return True
        
        # Check for treatment history matches
        if "treatment" in abstraction["name"].lower() or "medication" in abstraction["name"].lower():
            # Check if any medications mentioned in the abstraction match the patient's history
            medications = []
            if "medication_history" in patient_data:
                medications = [m.get("name", "") for m in patient_data.get("medication_history", [])]
            
            # Extract medication names from abstraction description
            for medication in ["Infliximab", "Adalimumab", "Ustekinumab", "Vedolizumab", "Upadacitinib"]:
                if medication.lower() in abstraction["description"].lower() and medication in medications:
                    return True
                    
        return False
    
    def _derive_treatment_constraints(self, relevant_abstractions, patient_data):
        """
        Derive treatment constraints from relationship analysis.
        
        Args:
            relevant_abstractions: List of relevant abstraction indices
            patient_data: Patient data dictionary
            
        Returns:
            List of treatment constraints
        """
        constraints = []
        
        if not self.relationship_graph:
            return constraints
            
        # Find contraindication relationships
        for abs_id in relevant_abstractions:
            for _, target, data in self.relationship_graph.out_edges(abs_id, data=True):
                if any(term in data.get("label", "").lower() for term in ["contraindication", "adverse", "avoid"]):
                    # Add medication contraindication constraint
                    target_abstraction = self.abstraction_results["abstractions"][target]
                    medication = self._extract_medication_from_abstraction(target_abstraction)
                    if medication:
                        constraints.append({
                            "type": "exclude_medication",
                            "medication": medication
                        })
                        logger.info(f"Added contraindication constraint for {medication}")
        
        # Add biomarker-specific constraints
        biomarkers = self._get_patient_biomarkers(patient_data)
        for biomarker in biomarkers:
            constraints.extend(self._get_biomarker_constraints(biomarker, relevant_abstractions))
        
        return constraints
    
    def _get_patient_biomarkers(self, patient_data):
        """
        Extract biomarkers from patient data.
        
        Args:
            patient_data: Patient data dictionary
            
        Returns:
            List of biomarkers
        """
        biomarkers = []
        for marker in patient_data.get("biomarkers", {}).get("genetic_markers", []):
            biomarkers.append(f"{marker['gene']}:{marker['variant']}:{marker['zygosity']}")
        return biomarkers
    
    def _get_biomarker_constraints(self, biomarker, relevant_abstractions):
        """
        Get constraints specific to a biomarker.
        
        Args:
            biomarker: Biomarker string
            relevant_abstractions: List of relevant abstraction indices
            
        Returns:
            List of constraints for the biomarker
        """
        constraints = []
        
        if not self.relationship_graph:
            return constraints
            
        # Extract gene from biomarker string
        gene = biomarker.split(":")[0] if ":" in biomarker else biomarker
        
        # Find biomarker-related abstractions
        biomarker_abstractions = []
        for i, abstraction in enumerate(self.abstraction_results.get("abstractions", [])):
            if gene in abstraction["description"] and i in relevant_abstractions:
                biomarker_abstractions.append(i)
        
        # Check for contraindications
        for abs_id in biomarker_abstractions:
            for _, target, data in self.relationship_graph.out_edges(abs_id, data=True):
                if "contraindication" in data.get("label", "").lower():
                    medication = self._extract_medication_from_abstraction(
                        self.abstraction_results["abstractions"][target]
                    )
                    if medication:
                        constraints.append({
                            "type": "exclude_medication",
                            "medication": medication,
                            "reason": f"Contraindicated for {gene}"
                        })
        
        return constraints
    
    def _extract_medication_from_abstraction(self, abstraction):
        """
        Extract medication name from abstraction.
        
        Args:
            abstraction: Abstraction dictionary
            
        Returns:
            Extracted medication name or None
        """
        # Check for common Crohn's medications in the description
        medications = ["Infliximab", "Adalimumab", "Ustekinumab", "Vedolizumab", "Upadacitinib", 
                      "Tofacitinib", "Risankizumab", "Certolizumab", "Golimumab", "Prednisone"]
        
        for med in medications:
            if med.lower() in abstraction["description"].lower():
                return med
                
        # Use regex as fallback
        match = re.search(r'medication[s]?:?\s*([A-Za-z0-9]+)', abstraction["description"], re.IGNORECASE)
        if match:
            return match.group(1)
            
        return None
    
    def _create_enhanced_fitness_function(self, relevant_abstractions):
        """
        Create enhanced fitness function using abstraction insights.
        
        Args:
            relevant_abstractions: List of relevant abstraction indices
            
        Returns:
            Enhanced fitness function
        """
        def enhanced_fitness(treatment_plan, patient_data):
            # Base fitness from original genetic engine
            base_fitness = self.base_genetic_engine.calculate_fitness(treatment_plan, patient_data)
            
            # Enhanced fitness based on abstractions
            abstraction_bonus = 0.0
            
            if not self.relationship_graph:
                return base_fitness
                
            # Check for positive relationship patterns
            for abs_id in relevant_abstractions:
                for _, target, data in self.relationship_graph.out_edges(abs_id, data=True):
                    if any(term in data.get("label", "").lower() for term in ["improves", "enhances", "boosts", "effective"]):
                        target_abstraction = self.abstraction_results["abstractions"][target]
                        if self._treatment_matches_abstraction(treatment_plan, target_abstraction):
                            abstraction_bonus += 0.1
                            logger.debug(f"Added fitness bonus for matching abstraction {target_abstraction['name']}")
                    
            adjusted_fitness = base_fitness * (1.0 + abstraction_bonus)
            logger.debug(f"Enhanced fitness: {base_fitness} → {adjusted_fitness} (bonus: {abstraction_bonus})")
            return adjusted_fitness
            
        return enhanced_fitness
    
    def _treatment_matches_abstraction(self, treatment_plan, abstraction):
        """
        Check if treatment plan matches an abstraction.
        
        Args:
            treatment_plan: Treatment plan dictionary
            abstraction: Abstraction dictionary
            
        Returns:
            Boolean indicating whether the treatment matches
        """
        # Search for medication names in the abstraction
        medications = ["Infliximab", "Adalimumab", "Ustekinumab", "Vedolizumab", "Upadacitinib", 
                      "Tofacitinib", "Risankizumab", "Certolizumab", "Golimumab", "Prednisone"]
        
        for treatment in treatment_plan:
            treatment_med = treatment.get("medication", "").lower()
            
            # Check if this medication is mentioned in the abstraction
            if treatment_med in abstraction["description"].lower():
                return True
                
            # Check if medication is mentioned by brand names
            if treatment_med == "infliximab" and any(term in abstraction["description"].lower() for term in ["remicade", "inflectra", "renflexis"]):
                return True
            elif treatment_med == "adalimumab" and any(term in abstraction["description"].lower() for term in ["humira", "amjevita"]):
                return True
            elif treatment_med == "ustekinumab" and "stelara" in abstraction["description"].lower():
                return True
            elif treatment_med == "vedolizumab" and "entyvio" in abstraction["description"].lower():
                return True
                
        return False