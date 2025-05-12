"""
Genetic analysis services for avian influenza.

This package provides tools for analyzing viral genetic sequences,
identifying mutations, tracking lineages, assessing antigenic properties,
and inferring transmission pathways between cases.
"""

from .sequence_analyzer import SequenceAnalyzer
from .transmission_analyzer import TransmissionAnalyzer


class SequenceAnalyzerService:
    """
    Service that provides comprehensive genetic analysis capabilities.
    This service wraps SequenceAnalyzer and TransmissionAnalyzer for
    convenient use by API controllers.
    """

    def __init__(self):
        """Initialize the sequence analyzer service."""
        self.sequence_analyzer = SequenceAnalyzer()
        self.transmission_analyzer = TransmissionAnalyzer(self.sequence_analyzer)

    def analyze_sequence(self, sequence_data, subtype, gene=None):
        """
        Analyze a genetic sequence.

        Args:
            sequence_data: Raw genetic sequence data
            subtype: Virus subtype (e.g., H5N1)
            gene: Specific gene to analyze (e.g., HA, NA)

        Returns:
            Dictionary with comprehensive sequence analysis
        """
        return self.sequence_analyzer.analyze_sequence(sequence_data, subtype, gene)

    def identify_mutations(self, sequence, subtype, gene=None):
        """
        Identify mutations in a sequence.

        Args:
            sequence: Genetic sequence
            subtype: Virus subtype
            gene: Specific gene

        Returns:
            List of identified mutations
        """
        return self.sequence_analyzer.identify_mutations(sequence, subtype, gene)

    def assess_lineage(self, mutations, subtype):
        """
        Determine virus lineage from mutations.

        Args:
            mutations: List of mutations
            subtype: Virus subtype

        Returns:
            Dictionary with lineage information
        """
        return self.sequence_analyzer.assess_lineage(mutations, subtype)

    def predict_antigenic_properties(self, mutations, subtype):
        """
        Predict antigenic properties from mutations.

        Args:
            mutations: List of mutations
            subtype: Virus subtype

        Returns:
            Dictionary with antigenic predictions
        """
        return self.sequence_analyzer.predict_antigenic_properties(mutations, subtype)

    def assess_zoonotic_potential(self, mutations, subtype):
        """
        Assess zoonotic potential from mutations.

        Args:
            mutations: List of mutations
            subtype: Virus subtype

        Returns:
            Dictionary with zoonotic risk assessment
        """
        return self.sequence_analyzer.assess_zoonotic_potential(mutations, subtype)

    def compare_sequences(self, sequences, subtype):
        """
        Compare multiple sequences.

        Args:
            sequences: Dictionary of sequence IDs to sequences
            subtype: Virus subtype

        Returns:
            Dictionary with comparison results
        """
        return self.sequence_analyzer.compare_sequences(sequences, subtype)

    def build_phylogenetic_tree(self, sequences, method="upgma"):
        """
        Build a phylogenetic tree from sequences.

        Args:
            sequences: Dictionary of sequence IDs to sequences
            method: Tree construction method

        Returns:
            Dictionary with tree information
        """
        return self.sequence_analyzer.build_phylogenetic_tree(sequences, method)

    def infer_transmission_network(self, cases, genetic_threshold=0.05,
                                 temporal_window=30, spatial_threshold=100.0):
        """
        Infer a transmission network from cases.

        Args:
            cases: List of cases
            genetic_threshold: Maximum genetic distance for links
            temporal_window: Maximum days between linked cases
            spatial_threshold: Maximum distance (km) between linked cases

        Returns:
            Dictionary with transmission network
        """
        return self.transmission_analyzer.infer_transmission_network(
            cases, genetic_threshold, temporal_window, spatial_threshold)

    def assess_transmission_pattern(self, network):
        """
        Assess transmission pattern from network.

        Args:
            network: Transmission network

        Returns:
            Dictionary with pattern assessment
        """
        return self.transmission_analyzer.assess_transmission_pattern(network)

    def predict_spread_trajectory(self, network, cases, days_ahead=14):
        """
        Predict future spread from current network.

        Args:
            network: Transmission network
            cases: List of cases
            days_ahead: Days to predict ahead

        Returns:
            Dictionary with trajectory prediction
        """
        return self.transmission_analyzer.predict_spread_trajectory(
            network, cases, days_ahead)

    def analyze_transmission_dynamics(self, cases, temporal_window=30,
                                   spatial_threshold=100.0):
        """
        Perform comprehensive transmission analysis.

        Args:
            cases: List of cases
            temporal_window: Maximum days between linked cases
            spatial_threshold: Maximum distance (km) between linked cases

        Returns:
            Dictionary with comprehensive analysis
        """
        return self.transmission_analyzer.analyze_transmission_dynamics(
            cases, temporal_window, spatial_threshold)


__all__ = [
    'SequenceAnalyzer',
    'TransmissionAnalyzer',
    'SequenceAnalyzerService'
]