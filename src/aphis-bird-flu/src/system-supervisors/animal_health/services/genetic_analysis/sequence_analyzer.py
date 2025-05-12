"""
Genetic sequence analysis for avian influenza viral genomes.

This module provides tools for analyzing avian influenza genetic sequences,
identifying mutations, tracking lineages, and assessing genetic relationships
between viral isolates.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Set, Union
import json
import re
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class SequenceAnalyzer:
    """
    Analyzer for avian influenza genetic sequences to track mutations,
    identify lineages, and assess evolutionary patterns.
    """
    
    def __init__(self, 
                reference_sequences: Optional[Dict[str, str]] = None,
                mutation_database: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Initialize the sequence analyzer with reference sequences and mutation database.
        
        Args:
            reference_sequences: Dictionary mapping virus subtypes to reference genome sequences
            mutation_database: Dictionary mapping known mutations to metadata
        """
        self.reference_sequences = reference_sequences or {}
        self.mutation_database = mutation_database or {}
        
        # Initialize default references if none provided
        if not self.reference_sequences:
            # Just placeholders for demonstration - would be actual sequences in production
            self.reference_sequences = {
                "H5N1": "PLACEHOLDER_H5N1_REFERENCE_SEQUENCE",
                "H7N9": "PLACEHOLDER_H7N9_REFERENCE_SEQUENCE",
                "H9N2": "PLACEHOLDER_H9N2_REFERENCE_SEQUENCE"
            }
    
    def identify_mutations(self, 
                         sequence: str, 
                         subtype: str,
                         gene: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Identify mutations in a sequence compared to the reference.
        
        Args:
            sequence: The genetic sequence to analyze
            subtype: Virus subtype (e.g., "H5N1")
            gene: Specific gene to analyze (e.g., "HA", "NA")
            
        Returns:
            List of identified mutations with positions and metadata
        """
        if subtype not in self.reference_sequences:
            raise ValueError(f"No reference sequence available for subtype {subtype}")
        
        reference = self.reference_sequences[subtype]
        
        # In a real implementation, this would use proper sequence alignment
        # and mutation detection algorithms. This is a simplified example.
        mutations = []
        
        # Simulate mutation detection with random positions for demonstration
        # In production, this would be real sequence analysis
        import random
        mutation_count = random.randint(3, 10)
        
        for _ in range(mutation_count):
            position = random.randint(1, len(reference) - 1 if len(reference) > 1 else 1)
            ref_base = reference[position - 1] if position <= len(reference) else "N"
            alt_base = random.choice(["A", "C", "G", "T"])
            
            # Skip if no actual mutation
            if ref_base == alt_base:
                continue
                
            mutation = {
                "position": position,
                "reference": ref_base,
                "alternate": alt_base,
                "mutation": f"{ref_base}{position}{alt_base}",
                "gene": gene or "unknown",
                "significance": self._get_mutation_significance(f"{ref_base}{position}{alt_base}", subtype)
            }
            
            mutations.append(mutation)
        
        return mutations
    
    def _get_mutation_significance(self, 
                                 mutation: str, 
                                 subtype: str) -> Dict[str, Any]:
        """
        Get significance of a known mutation from the database.
        
        Args:
            mutation: Mutation identifier (e.g., "A123T")
            subtype: Virus subtype
            
        Returns:
            Dictionary with significance information
        """
        # Check if mutation is in database
        if mutation in self.mutation_database:
            data = self.mutation_database[mutation]
            # Filter by subtype if needed
            if subtype in data.get("subtypes", [subtype]):
                return {
                    "phenotype": data.get("phenotype", "unknown"),
                    "drug_resistance": data.get("drug_resistance", False),
                    "transmission": data.get("transmission_impact", "unknown"),
                    "severity": data.get("severity_impact", "unknown"),
                    "first_detected": data.get("first_detected", "unknown"),
                    "literature_refs": data.get("literature_refs", [])
                }
        
        # Default significance for unknown mutations
        return {
            "phenotype": "unknown",
            "drug_resistance": False,
            "transmission": "unknown",
            "severity": "unknown",
            "first_detected": "unknown",
            "literature_refs": []
        }
    
    def assess_lineage(self, 
                     mutations: List[Dict[str, Any]], 
                     subtype: str) -> Dict[str, Any]:
        """
        Determine the lineage of a virus based on its mutations.
        
        Args:
            mutations: List of mutations identified in the sequence
            subtype: Virus subtype
            
        Returns:
            Dictionary with lineage information
        """
        # In a real implementation, this would use phylogenetic analysis
        # Here we provide a simplified example based on mutation patterns
        
        # Extract mutation strings for pattern matching
        mutation_strings = [m["mutation"] for m in mutations]
        
        # Simplified lineage determination
        lineage = "unknown"
        confidence = 0.0
        related_lineages = []
        
        # Simulate lineage identification based on mutations
        # In production, this would use proper phylogenetic algorithms
        if subtype == "H5N1":
            if any(m.startswith("A") for m in mutation_strings) and any(m.startswith("G") for m in mutation_strings):
                lineage = "clade_2.3.4.4b"
                confidence = 0.85
                related_lineages = ["clade_2.3.4.4a", "clade_2.3.4.4c"]
            elif any(m.startswith("T") for m in mutation_strings):
                lineage = "clade_2.3.2.1"
                confidence = 0.78
                related_lineages = ["clade_2.3.2.1a", "clade_2.3.2.1c"]
            else:
                lineage = "clade_2.2"
                confidence = 0.65
                related_lineages = ["clade_2.2.1", "clade_2.2.2"]
        
        elif subtype == "H7N9":
            if any(m.startswith("C") for m in mutation_strings):
                lineage = "yangtze_river_delta"
                confidence = 0.82
                related_lineages = ["pearl_river_delta"]
            else:
                lineage = "pearl_river_delta"
                confidence = 0.75
                related_lineages = ["yangtze_river_delta"]
        
        elif subtype == "H9N2":
            if any(m.startswith("G") for m in mutation_strings):
                lineage = "G1_lineage"
                confidence = 0.88
                related_lineages = ["Y280_lineage"]
            else:
                lineage = "Y280_lineage"
                confidence = 0.76
                related_lineages = ["G1_lineage", "korean_lineage"]
                
        # Add geographic distribution for this lineage
        geographic_distribution = self._get_lineage_geographic_distribution(lineage, subtype)
        
        # Add temporal information
        temporal_data = self._get_lineage_temporal_data(lineage, subtype)
        
        return {
            "lineage": lineage,
            "confidence": confidence,
            "related_lineages": related_lineages,
            "defining_mutations": self._get_lineage_defining_mutations(lineage, subtype),
            "geographic_distribution": geographic_distribution,
            "first_detected": temporal_data.get("first_detected", "unknown"),
            "recent_expansion": temporal_data.get("recent_expansion", False),
            "trend": temporal_data.get("trend", "stable")
        }
    
    def _get_lineage_defining_mutations(self, 
                                      lineage: str, 
                                      subtype: str) -> List[str]:
        """
        Get the mutations that define a specific lineage.
        
        Args:
            lineage: Virus lineage
            subtype: Virus subtype
            
        Returns:
            List of defining mutations
        """
        # In a real implementation, this would look up actual defining mutations
        # from a database. Here we provide example mutations.
        
        if subtype == "H5N1":
            if lineage == "clade_2.3.4.4b":
                return ["T96I", "G54R", "T140K", "N220K", "N94H"]
            elif lineage == "clade_2.3.2.1":
                return ["R189K", "S120D", "I151T", "Y252N"]
            elif lineage == "clade_2.2":
                return ["L73P", "I83A", "N244H"]
        
        elif subtype == "H7N9":
            if lineage == "yangtze_river_delta":
                return ["V100A", "A135T", "L217Q"]
            elif lineage == "pearl_river_delta":
                return ["I38T", "K22R", "G186V"]
        
        elif subtype == "H9N2":
            if lineage == "G1_lineage":
                return ["Q226L", "H183N", "A131T"]
            elif lineage == "Y280_lineage":
                return ["T131N", "V216I", "E179D"]
        
        return ["unknown"]
    
    def _get_lineage_geographic_distribution(self, 
                                          lineage: str, 
                                          subtype: str) -> Dict[str, float]:
        """
        Get the geographic distribution of a lineage.
        
        Args:
            lineage: Virus lineage
            subtype: Virus subtype
            
        Returns:
            Dictionary mapping regions to prevalence scores
        """
        # In a real implementation, this would retrieve actual distribution data
        # Here we provide example distributions for demonstration purposes
        
        if subtype == "H5N1":
            if lineage == "clade_2.3.4.4b":
                return {
                    "Eastern_Asia": 0.85,
                    "Southeast_Asia": 0.65,
                    "Europe": 0.45,
                    "North_America": 0.35,
                    "Africa": 0.20
                }
            elif lineage == "clade_2.3.2.1":
                return {
                    "Eastern_Asia": 0.75,
                    "Southeast_Asia": 0.80,
                    "South_Asia": 0.60,
                    "Middle_East": 0.40
                }
        
        elif subtype == "H7N9":
            if lineage == "yangtze_river_delta":
                return {
                    "Eastern_China": 0.90,
                    "Taiwan": 0.40,
                    "Hong_Kong": 0.35
                }
            elif lineage == "pearl_river_delta":
                return {
                    "Southern_China": 0.85,
                    "Hong_Kong": 0.70,
                    "Vietnam": 0.30
                }
        
        # Default empty distribution
        return {"unknown": 0.0}
    
    def _get_lineage_temporal_data(self, 
                                lineage: str, 
                                subtype: str) -> Dict[str, Any]:
        """
        Get temporal data about a lineage, such as when it was first detected
        and recent trends.
        
        Args:
            lineage: Virus lineage
            subtype: Virus subtype
            
        Returns:
            Dictionary with temporal information
        """
        # In a real implementation, this would retrieve actual temporal data
        # Here we provide example data for demonstration purposes
        
        if subtype == "H5N1":
            if lineage == "clade_2.3.4.4b":
                return {
                    "first_detected": "2020-03-15",
                    "recent_expansion": True,
                    "trend": "increasing",
                    "seasonality": "winter_peak"
                }
            elif lineage == "clade_2.3.2.1":
                return {
                    "first_detected": "2011-11-27",
                    "recent_expansion": False,
                    "trend": "stable",
                    "seasonality": "year_round"
                }
        
        elif subtype == "H7N9":
            if lineage == "yangtze_river_delta":
                return {
                    "first_detected": "2013-03-31",
                    "recent_expansion": False,
                    "trend": "decreasing",
                    "seasonality": "winter_spring"
                }
        
        # Default temporal data
        return {
            "first_detected": "unknown",
            "recent_expansion": False,
            "trend": "unknown",
            "seasonality": "unknown"
        }
    
    def calculate_genetic_distance(self, 
                                 sequence1: str, 
                                 sequence2: str) -> float:
        """
        Calculate genetic distance between two sequences.
        
        Args:
            sequence1: First genetic sequence
            sequence2: Second genetic sequence
            
        Returns:
            Numeric distance value (higher = more distant)
        """
        # In a real implementation, this would use proper genetic distance algorithms
        # such as Jukes-Cantor, Kimura, or more sophisticated methods
        
        # Simple hamming distance (requires equal length sequences)
        min_length = min(len(sequence1), len(sequence2))
        differences = sum(c1 != c2 for c1, c2 in zip(sequence1[:min_length], sequence2[:min_length]))
        
        # Normalize by sequence length
        distance = differences / min_length if min_length > 0 else 1.0
        
        return distance
    
    def build_phylogenetic_tree(self, 
                              sequences: Dict[str, str], 
                              method: str = "upgma") -> Dict[str, Any]:
        """
        Build a phylogenetic tree from a set of sequences.
        
        Args:
            sequences: Dictionary mapping sequence identifiers to sequences
            method: Phylogenetic tree construction method (upgma, nj, ml)
            
        Returns:
            Dictionary representing a phylogenetic tree
        """
        # In a real implementation, this would use proper phylogenetic algorithms
        # Here we create a simple mock tree structure for demonstration
        
        # Create distance matrix
        sequence_ids = list(sequences.keys())
        n_sequences = len(sequence_ids)
        
        if n_sequences < 2:
            return {"error": "Need at least 2 sequences to build a tree"}
            
        # Build a mock tree - in production this would be a real phylogenetic tree
        # using algorithms like UPGMA, Neighbor-Joining, or Maximum Likelihood
        
        # Create a simple tree structure
        tree = {
            "method": method,
            "root": {
                "id": "root",
                "children": []
            },
            "branch_lengths": {},
            "topology": "mock_topology_for_demonstration",
            "sequence_count": n_sequences
        }
        
        # Simulate a tree structure
        previous_node = "root"
        for i, seq_id in enumerate(sequence_ids):
            if i == 0:
                # First sequence as direct child of root
                tree["root"]["children"].append(seq_id)
                tree["branch_lengths"][f"root_{seq_id}"] = 0.01
            else:
                # Branch from either root or a previous node
                if i % 3 == 0:  # Occasionally branch from root
                    tree["root"]["children"].append(seq_id)
                    tree["branch_lengths"][f"root_{seq_id}"] = 0.01 * i
                else:  # Branch from the previous node
                    tree["branch_lengths"][f"{previous_node}_{seq_id}"] = 0.005 * i
                
            previous_node = seq_id
        
        return tree
    
    def predict_antigenic_properties(self, 
                                   mutations: List[Dict[str, Any]], 
                                   subtype: str) -> Dict[str, Any]:
        """
        Predict antigenic properties based on identified mutations.
        
        Args:
            mutations: List of mutations
            subtype: Virus subtype
            
        Returns:
            Dictionary with predicted antigenic properties
        """
        # In a real implementation, this would use machine learning models
        # trained on antigenic data. Here we provide a simplified example.
        
        # Count mutations by gene
        gene_mutation_counts = defaultdict(int)
        for mutation in mutations:
            gene = mutation.get("gene", "unknown")
            gene_mutation_counts[gene] += 1
        
        # Calculate an "antigenic drift score" based on mutations in key genes
        ha_mutations = gene_mutation_counts.get("HA", 0)
        na_mutations = gene_mutation_counts.get("NA", 0)
        
        # More weight to HA mutations which are generally more antigenically significant
        drift_score = (ha_mutations * a.5 + na_mutations * 0.3) / 10
        drift_score = min(max(drift_score, 0.0), 1.0)  # Clamp between 0 and 1
        
        # Predict antigenic cluster based on mutations
        antigenic_cluster = "unknown"
        if subtype == "H5N1":
            if drift_score > 0.7:
                antigenic_cluster = "clade_2.3.4.4b_HK2021"
            elif drift_score > 0.4:
                antigenic_cluster = "clade_2.3.4.4b_EU2020"
            else:
                antigenic_cluster = "clade_2.3.4.4b_original"
        elif subtype == "H7N9":
            if drift_score > 0.6:
                antigenic_cluster = "yangtze_2017"
            else:
                antigenic_cluster = "yangtze_2013"
        
        # Check for specific key mutations associated with antigenic change
        key_antigenic_mutation_found = False
        key_mutations = {
            "H5N1": ["T140K", "N220K", "R189K"],
            "H7N9": ["L217Q", "I38T"],
            "H9N2": ["Q226L"]
        }
        
        for mutation in mutations:
            if mutation["mutation"] in key_mutations.get(subtype, []):
                key_antigenic_mutation_found = True
                break
        
        # Predict vaccine effectiveness
        vaccine_match = 1.0 - drift_score
        
        return {
            "drift_score": drift_score,
            "antigenic_cluster": antigenic_cluster,
            "has_key_antigenic_mutation": key_antigenic_mutation_found,
            "vaccine_match": vaccine_match,
            "vaccine_effectiveness_prediction": self._predict_vaccine_effectiveness(vaccine_match),
            "cross_reactivity": self._predict_cross_reactivity(drift_score, subtype)
        }
    
    def _predict_vaccine_effectiveness(self, match_score: float) -> Dict[str, float]:
        """
        Predict vaccine effectiveness based on match score.
        
        Args:
            match_score: Antigenic match score (0-1)
            
        Returns:
            Dictionary with effectiveness predictions
        """
        # In production this would use a more sophisticated model
        # This is a simplified linear model for demonstration
        effectiveness = {}
        
        effectiveness["overall"] = match_score * 0.9  # Max effectiveness of 90%
        
        # Age group variations
        effectiveness["children"] = effectiveness["overall"] * 1.1  # Children often have better responses
        effectiveness["adults"] = effectiveness["overall"] 
        effectiveness["elderly"] = effectiveness["overall"] * 0.8  # Elderly often have reduced responses
        
        # Clamp values between 0 and 1
        for key in effectiveness:
            effectiveness[key] = min(max(effectiveness[key], 0.0), 1.0)
        
        return effectiveness
    
    def _predict_cross_reactivity(self, 
                                drift_score: float, 
                                subtype: str) -> Dict[str, float]:
        """
        Predict cross-reactivity with other virus strains.
        
        Args:
            drift_score: Antigenic drift score
            subtype: Virus subtype
            
        Returns:
            Dictionary mapping other subtypes to cross-reactivity scores
        """
        # Base cross-reactivity inversely proportional to drift
        base_reactivity = 1.0 - drift_score
        
        cross_reactivity = {}
        
        # Different subtypes have different cross-reactivity patterns
        if subtype == "H5N1":
            cross_reactivity = {
                "H5N1_clade_2.3.4.4a": base_reactivity * 0.9,
                "H5N1_clade_2.3.4.4c": base_reactivity * 0.8,
                "H5N1_clade_2.3.2.1": base_reactivity * 0.6,
                "H5N1_clade_2.2": base_reactivity * 0.5,
                "H5N6": base_reactivity * 0.4,
                "H5N8": base_reactivity * 0.4
            }
        elif subtype == "H7N9":
            cross_reactivity = {
                "H7N9_2013": base_reactivity * 0.9,
                "H7N9_2017": base_reactivity * 0.8,
                "H7N7": base_reactivity * 0.3,
                "H7N3": base_reactivity * 0.3
            }
        elif subtype == "H9N2":
            cross_reactivity = {
                "H9N2_G1": base_reactivity * 0.9,
                "H9N2_Y280": base_reactivity * 0.8,
                "H9N2_Korean": base_reactivity * 0.7
            }
        
        # Clamp values between 0 and 1
        for key in cross_reactivity:
            cross_reactivity[key] = min(max(cross_reactivity[key], 0.0), 1.0)
        
        return cross_reactivity
    
    def assess_zoonotic_potential(self, 
                               mutations: List[Dict[str, Any]],
                               subtype: str) -> Dict[str, Any]:
        """
        Assess the zoonotic potential of a virus based on its mutations.
        
        Args:
            mutations: List of identified mutations
            subtype: Virus subtype
            
        Returns:
            Dictionary with zoonotic risk assessment
        """
        # This would use a sophisticated model in production
        # Here we provide a simple rule-based assessment for demonstration
        
        # Known mammalian adaptation markers
        mammalian_markers = {
            "H5N1": ["E627K", "D701N", "T271A", "Q226L"],
            "H7N9": ["Q226L", "G186V", "T160A"],
            "H9N2": ["Q226L", "I155T", "H183N"]
        }
        
        # Check for presence of mammalian adaptation markers
        found_markers = []
        for mutation in mutations:
            if mutation["mutation"] in mammalian_markers.get(subtype, []):
                found_markers.append(mutation["mutation"])
        
        # Calculate mammalian adaptation score
        adaptation_score = len(found_markers) / len(mammalian_markers.get(subtype, [1])) if mammalian_markers.get(subtype) else 0
        
        # Categorize risk level
        risk_level = "low"
        if adaptation_score > 0.7:
            risk_level = "high"
        elif adaptation_score > 0.3:
            risk_level = "moderate"
        
        # Assess transmission risk in different hosts
        transmission_risk = {
            "avian": 0.9,  # Always high in birds
            "swine": 0.2 + adaptation_score * 0.6,
            "human": 0.1 + adaptation_score * 0.6,
            "other_mammals": 0.1 + adaptation_score * 0.4
        }
        
        return {
            "zoonotic_risk_level": risk_level,
            "mammalian_adaptation_score": adaptation_score,
            "mammalian_adaptation_markers": found_markers,
            "transmission_risk": transmission_risk,
            "surveillance_recommendation": self._get_surveillance_recommendation(risk_level),
            "history": self._get_zoonotic_history(subtype)
        }
    
    def _get_surveillance_recommendation(self, risk_level: str) -> Dict[str, Any]:
        """
        Get surveillance recommendations based on zoonotic risk level.
        
        Args:
            risk_level: Assessed risk level (low, moderate, high)
            
        Returns:
            Dictionary with surveillance recommendations
        """
        if risk_level == "high":
            return {
                "priority": "high",
                "sampling_frequency": "weekly",
                "geographic_focus": "widespread",
                "mammalian_surveillance": "enhanced",
                "sentinel_species": ["poultry", "wild_birds", "swine", "cats"]
            }
        elif risk_level == "moderate":
            return {
                "priority": "moderate",
                "sampling_frequency": "biweekly",
                "geographic_focus": "targeted",
                "mammalian_surveillance": "routine",
                "sentinel_species": ["poultry", "wild_birds", "swine"]
            }
        else:  # low
            return {
                "priority": "standard",
                "sampling_frequency": "monthly",
                "geographic_focus": "routine",
                "mammalian_surveillance": "minimal",
                "sentinel_species": ["poultry", "wild_birds"]
            }
    
    def _get_zoonotic_history(self, subtype: str) -> Dict[str, Any]:
        """
        Get historical zoonotic events for the subtype.
        
        Args:
            subtype: Virus subtype
            
        Returns:
            Dictionary with zoonotic history
        """
        # In production this would retrieve data from a database
        # Here we provide example historical data
        
        history = {
            "H5N1": {
                "first_human_case": "1997-05-21",
                "total_human_cases": 863,
                "total_human_deaths": 455,
                "case_fatality_rate": 0.53,
                "major_outbreaks": [
                    {"year": 1997, "location": "Hong Kong", "cases": 18},
                    {"year": 2004, "location": "Vietnam", "cases": 29},
                    {"year": 2006, "location": "Indonesia", "cases": 55},
                    {"year": 2009, "location": "Egypt", "cases": 39},
                    {"year": 2015, "location": "Egypt", "cases": 136}
                ],
                "sustained_human_transmission": False
            },
            "H7N9": {
                "first_human_case": "2013-02-19",
                "total_human_cases": 1568,
                "total_human_deaths": 616,
                "case_fatality_rate": 0.39,
                "major_outbreaks": [
                    {"year": 2013, "location": "Eastern China", "cases": 135},
                    {"year": 2014, "location": "Eastern China", "cases": 320},
                    {"year": 2017, "location": "China", "cases": 766}
                ],
                "sustained_human_transmission": False
            },
            "H9N2": {
                "first_human_case": "1998-08-09",
                "total_human_cases": 91,
                "total_human_deaths": 1,
                "case_fatality_rate": 0.01,
                "major_outbreaks": [
                    {"year": 2015, "location": "China", "cases": 18},
                    {"year": 2020, "location": "China", "cases": 24}
                ],
                "sustained_human_transmission": False
            }
        }
        
        return history.get(subtype, {
            "first_human_case": "unknown",
            "total_human_cases": 0,
            "case_fatality_rate": 0,
            "major_outbreaks": [],
            "sustained_human_transmission": False
        })
    
    def analyze_sequence(self, 
                       sequence: str, 
                       subtype: str,
                       gene: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a viral sequence.
        
        Args:
            sequence: The genetic sequence to analyze
            subtype: Virus subtype
            gene: Specific gene (optional)
            
        Returns:
            Dictionary with comprehensive sequence analysis
        """
        # Identify mutations
        mutations = self.identify_mutations(sequence, subtype, gene)
        
        # Determine lineage
        lineage_info = self.assess_lineage(mutations, subtype)
        
        # Predict antigenic properties
        antigenic_properties = self.predict_antigenic_properties(mutations, subtype)
        
        # Assess zoonotic potential
        zoonotic_potential = self.assess_zoonotic_potential(mutations, subtype)
        
        # Combine all analyses
        return {
            "sequence_length": len(sequence),
            "subtype": subtype,
            "gene": gene,
            "mutations": mutations,
            "lineage": lineage_info,
            "antigenic_properties": antigenic_properties,
            "zoonotic_potential": zoonotic_potential,
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_version": "1.0"
        }
    
    def compare_sequences(self, 
                        sequences: Dict[str, str], 
                        subtype: str) -> Dict[str, Any]:
        """
        Perform comparative analysis of multiple sequences.
        
        Args:
            sequences: Dictionary mapping sequence identifiers to sequences
            subtype: Virus subtype
            
        Returns:
            Dictionary with comparative analysis
        """
        if len(sequences) < 2:
            return {"error": "Need at least 2 sequences for comparison"}
        
        # Calculate pairwise distances
        sequence_ids = list(sequences.keys())
        distances = {}
        
        for i, id1 in enumerate(sequence_ids):
            for j, id2 in enumerate(sequence_ids):
                if i < j:  # Only calculate each pair once
                    distance = self.calculate_genetic_distance(sequences[id1], sequences[id2])
                    distances[f"{id1}_{id2}"] = distance
        
        # Find most and least similar pairs
        if distances:
            most_similar = min(distances.items(), key=lambda x: x[1])
            least_similar = max(distances.items(), key=lambda x: x[1])
        else:
            most_similar = ("none_none", 0)
            least_similar = ("none_none", 0)
        
        # Build phylogenetic tree
        tree = self.build_phylogenetic_tree(sequences)
        
        # Identify unique mutations per sequence
        unique_mutations = {}
        all_mutations = {}
        
        for seq_id, sequence in sequences.items():
            mutations = self.identify_mutations(sequence, subtype)
            all_mutations[seq_id] = mutations
            
            # Extract mutation strings for easy comparison
            mutation_strings = [m["mutation"] for m in mutations]
            unique_mutations[seq_id] = []
            
            # Check if mutation is unique to this sequence
            for mutation in mutation_strings:
                is_unique = True
                for other_id, other_sequence in sequences.items():
                    if other_id != seq_id:
                        other_mutations = [m["mutation"] for m in all_mutations.get(
                            other_id, self.identify_mutations(other_sequence, subtype))]
                        if mutation in other_mutations:
                            is_unique = False
                            break
                
                if is_unique:
                    unique_mutations[seq_id].append(mutation)
        
        # Identify shared mutations (present in all sequences)
        first_id = sequence_ids[0]
        first_mutations = [m["mutation"] for m in all_mutations.get(
            first_id, self.identify_mutations(sequences[first_id], subtype))]
        
        shared_mutations = []
        for mutation in first_mutations:
            is_shared = True
            for seq_id in sequence_ids[1:]:
                other_mutations = [m["mutation"] for m in all_mutations.get(
                    seq_id, self.identify_mutations(sequences[seq_id], subtype))]
                if mutation not in other_mutations:
                    is_shared = False
                    break
            
            if is_shared:
                shared_mutations.append(mutation)
        
        return {
            "sequence_count": len(sequences),
            "average_length": sum(len(seq) for seq in sequences.values()) / len(sequences),
            "pairwise_distances": distances,
            "most_similar_pair": {
                "ids": most_similar[0].split("_"),
                "distance": most_similar[1]
            },
            "least_similar_pair": {
                "ids": least_similar[0].split("_"),
                "distance": least_similar[1]
            },
            "phylogenetic_tree": tree,
            "unique_mutations": unique_mutations,
            "shared_mutations": shared_mutations,
            "analysis_timestamp": datetime.now().isoformat()
        }