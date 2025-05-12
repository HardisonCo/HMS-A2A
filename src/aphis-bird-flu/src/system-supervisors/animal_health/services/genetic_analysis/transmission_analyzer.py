"""
Transmission pathway analysis for avian influenza outbreaks.

This module provides tools for analyzing genetic and epidemiological data
to infer transmission pathways between cases, identify sources, and
reconstruct outbreak events.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Set, Union
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import networkx as nx

from ...models.case import Case
from ...models.base import GeoLocation
from .sequence_analyzer import SequenceAnalyzer

logger = logging.getLogger(__name__)


class TransmissionAnalyzer:
    """
    Analyzer for reconstructing transmission pathways between avian influenza cases
    based on genetic, temporal, and geographical information.
    """
    
    def __init__(self, sequence_analyzer: Optional[SequenceAnalyzer] = None):
        """
        Initialize the transmission analyzer.
        
        Args:
            sequence_analyzer: Sequence analyzer for genetic comparisons
        """
        self.sequence_analyzer = sequence_analyzer or SequenceAnalyzer()
        
    def infer_transmission_network(self, 
                                 cases: List[Case], 
                                 genetic_threshold: float = 0.05,
                                 temporal_window: int = 30,  # days
                                 spatial_threshold: float = 100.0  # km
                                ) -> Dict[str, Any]:
        """
        Infer a transmission network from a set of cases.
        
        Args:
            cases: List of cases to analyze
            genetic_threshold: Maximum genetic distance for potential transmission
            temporal_window: Maximum time (in days) between potential transmission events
            spatial_threshold: Maximum distance (in km) between potential transmission events
            
        Returns:
            Dictionary describing the inferred transmission network
        """
        # Sort cases by detection date
        sorted_cases = sorted(cases, key=lambda c: datetime.fromisoformat(c.detection_date))
        
        if len(sorted_cases) < 2:
            return {"error": "Need at least 2 cases to infer transmission"}
        
        # Create graph for transmission network
        transmission_links = []
        
        # For each pair of cases, check if transmission is plausible
        for i, source_case in enumerate(sorted_cases[:-1]):
            source_date = datetime.fromisoformat(source_case.detection_date)
            
            for target_case in sorted_cases[i+1:]:
                target_date = datetime.fromisoformat(target_case.detection_date)
                
                # Check temporal relationship (target must be after source)
                days_difference = (target_date - source_date).days
                if not (0 < days_difference <= temporal_window):
                    continue
                
                # Check spatial relationship
                distance = self._calculate_distance(
                    source_case.location.latitude, 
                    source_case.location.longitude,
                    target_case.location.latitude,
                    target_case.location.longitude
                )
                
                if distance > spatial_threshold:
                    continue
                
                # Check genetic relationship if sequence data is available
                genetic_compatible = True
                if hasattr(source_case, 'sequence') and hasattr(target_case, 'sequence'):
                    genetic_distance = self.sequence_analyzer.calculate_genetic_distance(
                        source_case.sequence, target_case.sequence)
                    genetic_compatible = genetic_distance <= genetic_threshold
                
                # If all criteria are met, add a transmission link
                if genetic_compatible:
                    # Calculate likelihood based on various factors
                    temporal_factor = 1.0 - (days_difference / temporal_window)
                    spatial_factor = 1.0 - (distance / spatial_threshold)
                    
                    # Higher weight to genetic similarity if available
                    if hasattr(source_case, 'sequence') and hasattr(target_case, 'sequence'):
                        genetic_factor = 1.0 - (genetic_distance / genetic_threshold)
                        likelihood = (temporal_factor * 0.3 + 
                                     spatial_factor * 0.3 + 
                                     genetic_factor * 0.4)
                    else:
                        likelihood = (temporal_factor * 0.5 + 
                                     spatial_factor * 0.5)
                    
                    transmission_links.append({
                        "source": source_case.id,
                        "target": target_case.id,
                        "likelihood": likelihood,
                        "days_apart": days_difference,
                        "distance_km": distance,
                        "genetic_distance": genetic_distance if hasattr(source_case, 'sequence') else None
                    })
        
        # Create a graph structure for network analysis
        graph = self._create_transmission_graph(sorted_cases, transmission_links)
        
        # Calculate network metrics
        network_metrics = self._calculate_network_metrics(graph)
        
        # Identify clusters within the network
        clusters = self._identify_transmission_clusters(graph)
        
        # Identify likely index cases
        index_cases = self._identify_index_cases(graph, sorted_cases)
        
        # Identify super-spreaders
        superspreaders = self._identify_superspreaders(graph)
        
        return {
            "cases": len(sorted_cases),
            "links": transmission_links,
            "network_metrics": network_metrics,
            "clusters": clusters,
            "index_cases": index_cases,
            "superspreaders": superspreaders,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the distance between two geographic points in kilometers.
        
        Args:
            lat1: Latitude of first point
            lon1: Longitude of first point
            lat2: Latitude of second point
            lon2: Longitude of second point
            
        Returns:
            Distance in kilometers
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        return c * r
    
    def _create_transmission_graph(self, 
                                cases: List[Case], 
                                links: List[Dict[str, Any]]) -> nx.DiGraph:
        """
        Create a directed graph representing the transmission network.
        
        Args:
            cases: List of cases
            links: List of transmission links
            
        Returns:
            NetworkX DiGraph object
        """
        try:
            import networkx as nx
        except ImportError:
            # If NetworkX is not available, return a mock graph
            class MockGraph:
                def __init__(self):
                    self.nodes = {}
                    self.edges = []
                
                def add_node(self, node, **attrs):
                    self.nodes[node] = attrs
                
                def add_edge(self, u, v, **attrs):
                    self.edges.append((u, v, attrs))
                
                def in_degree(self, node):
                    return sum(1 for u, v, _ in self.edges if v == node)
                
                def out_degree(self, node):
                    return sum(1 for u, v, _ in self.edges if u == node)
                
                def nodes(self):
                    return list(self.nodes.keys())
                
                def edges(self):
                    return [(u, v) for u, v, _ in self.edges]
            
            graph = MockGraph()
            
            # Add nodes (cases)
            for case in cases:
                graph.add_node(case.id, detection_date=case.detection_date)
            
            # Add edges (transmission links)
            for link in links:
                graph.add_edge(
                    link["source"], 
                    link["target"], 
                    likelihood=link["likelihood"],
                    days_apart=link["days_apart"],
                    distance_km=link["distance_km"],
                    genetic_distance=link["genetic_distance"]
                )
            
            return graph
        
        # Create a directed graph
        graph = nx.DiGraph()
        
        # Add nodes (cases)
        for case in cases:
            graph.add_node(case.id, detection_date=case.detection_date)
        
        # Add edges (transmission links)
        for link in links:
            graph.add_edge(
                link["source"], 
                link["target"], 
                likelihood=link["likelihood"],
                days_apart=link["days_apart"],
                distance_km=link["distance_km"],
                genetic_distance=link["genetic_distance"]
            )
        
        return graph
    
    def _calculate_network_metrics(self, graph) -> Dict[str, Any]:
        """
        Calculate various metrics from the transmission network.
        
        Args:
            graph: NetworkX DiGraph object
            
        Returns:
            Dictionary with network metrics
        """
        try:
            import networkx as nx
            
            # Calculate network metrics
            metrics = {}
            
            # Basic metrics
            if isinstance(graph, nx.Graph):
                metrics["node_count"] = graph.number_of_nodes()
                metrics["edge_count"] = graph.number_of_edges()
                
                # Only calculate if graph has nodes
                if metrics["node_count"] > 0:
                    # Density
                    metrics["density"] = nx.density(graph)
                    
                    # Components
                    if isinstance(graph, nx.DiGraph):
                        components = list(nx.weakly_connected_components(graph))
                    else:
                        components = list(nx.connected_components(graph))
                    
                    metrics["component_count"] = len(components)
                    metrics["largest_component_size"] = len(max(components, key=len)) if components else 0
                    
                    # Centrality (only if graph has edges)
                    if metrics["edge_count"] > 0:
                        try:
                            # Degree centrality
                            in_degree_centrality = nx.in_degree_centrality(graph)
                            out_degree_centrality = nx.out_degree_centrality(graph)
                            
                            metrics["max_in_degree_centrality"] = max(in_degree_centrality.values()) if in_degree_centrality else 0
                            metrics["max_out_degree_centrality"] = max(out_degree_centrality.values()) if out_degree_centrality else 0
                            
                            # Betweenness centrality (takes longer to compute)
                            betweenness = nx.betweenness_centrality(graph)
                            metrics["max_betweenness_centrality"] = max(betweenness.values()) if betweenness else 0
                            
                            # Average path length (only for connected graphs)
                            largest_component = max(components, key=len) if components else []
                            if largest_component:
                                subgraph = graph.subgraph(largest_component)
                                try:
                                    if isinstance(graph, nx.DiGraph):
                                        metrics["average_path_length"] = nx.average_shortest_path_length(subgraph)
                                    else:
                                        metrics["average_path_length"] = nx.average_shortest_path_length(subgraph)
                                except:
                                    metrics["average_path_length"] = None
                        except:
                            # Handle potential errors in centrality calculations
                            metrics["centrality_calculation_error"] = True
            
            return metrics
            
        except ImportError:
            # If NetworkX is not available, return basic metrics
            return {
                "node_count": len(graph.nodes) if hasattr(graph, "nodes") else 0,
                "edge_count": len(graph.edges) if hasattr(graph, "edges") else 0,
                "note": "Limited metrics available without NetworkX"
            }
    
    def _identify_transmission_clusters(self, graph) -> List[Dict[str, Any]]:
        """
        Identify clusters within the transmission network.
        
        Args:
            graph: NetworkX DiGraph object
            
        Returns:
            List of cluster information dictionaries
        """
        try:
            import networkx as nx
            
            # Find connected components (clusters)
            if isinstance(graph, nx.DiGraph):
                components = list(nx.weakly_connected_components(graph))
            else:
                components = list(nx.connected_components(graph))
            
            clusters = []
            for i, component in enumerate(components):
                component_list = list(component)
                
                # Skip tiny components (single nodes)
                if len(component_list) < 2:
                    continue
                
                # Create subgraph for this component
                subgraph = graph.subgraph(component_list)
                
                # Calculate component metrics
                metrics = {
                    "size": len(component_list),
                    "edge_count": subgraph.number_of_edges(),
                    "density": nx.density(subgraph)
                }
                
                # Find central nodes
                try:
                    in_degree_centrality = nx.in_degree_centrality(subgraph)
                    most_central = max(in_degree_centrality.items(), key=lambda x: x[1]) if in_degree_centrality else (None, 0)
                    
                    betweenness = nx.betweenness_centrality(subgraph)
                    most_between = max(betweenness.items(), key=lambda x: x[1]) if betweenness else (None, 0)
                    
                    central_nodes = {
                        "highest_in_degree": most_central[0],
                        "highest_betweenness": most_between[0]
                    }
                except:
                    central_nodes = {"error": "Failed to calculate centrality"}
                
                clusters.append({
                    "id": f"cluster_{i+1}",
                    "cases": component_list,
                    "metrics": metrics,
                    "central_nodes": central_nodes
                })
            
            return clusters
            
        except ImportError:
            # If NetworkX is not available, return basic clusters
            return [{"id": "cluster_1", "cases": list(graph.nodes), "note": "Limited clustering without NetworkX"}]
    
    def _identify_index_cases(self, 
                           graph, 
                           cases: List[Case]) -> List[Dict[str, Any]]:
        """
        Identify potential index cases (sources of outbreaks).
        
        Args:
            graph: NetworkX DiGraph object
            cases: List of cases
            
        Returns:
            List of potential index cases with scores
        """
        # Create a mapping from case ID to case object
        case_map = {case.id: case for case in cases}
        
        # Identify cases with in-degree 0 (no incoming links)
        index_candidates = []
        
        for node in graph.nodes():
            in_deg = graph.in_degree(node) if hasattr(graph, "in_degree") else 0
            
            if in_deg == 0:
                out_deg = graph.out_degree(node) if hasattr(graph, "out_degree") else 0
                
                # Only consider as index if it has outgoing links
                if out_deg > 0:
                    case = case_map.get(node)
                    
                    # Calculate index score based on outbreak size
                    outbreak_size = out_deg
                    temporal_priority = 1.0  # Default
                    
                    # Adjust by temporal priority if date available
                    if case and hasattr(case, 'detection_date'):
                        case_date = datetime.fromisoformat(case.detection_date)
                        earliest_date = min(datetime.fromisoformat(c.detection_date) 
                                         for c in cases if hasattr(c, 'detection_date'))
                        days_from_earliest = (case_date - earliest_date).days
                        
                        # Earlier cases more likely to be index
                        temporal_priority = 1.0 - (days_from_earliest / 30.0) if days_from_earliest < 30 else 0.0
                        temporal_priority = max(0.1, temporal_priority)  # Ensure minimum score
                    
                    # Combine factors
                    index_score = (outbreak_size * 0.7 + temporal_priority * 0.3)
                    
                    index_candidates.append({
                        "case_id": node,
                        "outbreak_size": outbreak_size,
                        "index_score": index_score,
                        "detection_date": case.detection_date if case and hasattr(case, 'detection_date') else None
                    })
        
        # Sort by index score
        index_candidates.sort(key=lambda x: x["index_score"], reverse=True)
        
        return index_candidates
    
    def _identify_superspreaders(self, graph) -> List[Dict[str, Any]]:
        """
        Identify potential superspreaders in the transmission network.
        
        Args:
            graph: NetworkX DiGraph object
            
        Returns:
            List of potential superspreader cases with scores
        """
        superspreader_candidates = []
        
        for node in graph.nodes():
            out_deg = graph.out_degree(node) if hasattr(graph, "out_degree") else 0
            
            # Consider as superspreader if it has multiple outgoing links
            if out_deg > 1:
                # Calculate superspreader score based on outgoing links
                superspreader_score = out_deg
                
                # Also consider betweenness if available
                try:
                    import networkx as nx
                    if isinstance(graph, nx.Graph) and graph.number_of_edges() > 0:
                        betweenness = nx.betweenness_centrality(graph)
                        if node in betweenness:
                            # Incorporate betweenness into score
                            superspreader_score = out_deg * 0.7 + betweenness[node] * 30 * 0.3
                except:
                    # Continue without betweenness
                    pass
                
                superspreader_candidates.append({
                    "case_id": node,
                    "outgoing_links": out_deg,
                    "superspreader_score": superspreader_score
                })
        
        # Sort by superspreader score
        superspreader_candidates.sort(key=lambda x: x["superspreader_score"], reverse=True)
        
        return superspreader_candidates
    
    def assess_transmission_pattern(self, 
                                  network: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the overall transmission pattern from the network.
        
        Args:
            network: Transmission network from infer_transmission_network
            
        Returns:
            Dictionary with transmission pattern assessment
        """
        # Extract key network properties
        clusters = network.get("clusters", [])
        links = network.get("links", [])
        metrics = network.get("network_metrics", {})
        
        # Count the number of cases and links
        case_count = metrics.get("node_count", 0)
        link_count = metrics.get("edge_count", 0)
        cluster_count = len(clusters)
        
        # Calculate average links per case
        avg_links = link_count / case_count if case_count > 0 else 0
        
        # Determine pattern type
        pattern_type = "sporadic"  # Default
        
        if cluster_count == 1 and case_count > 5:
            # Single large cluster suggests a common source
            pattern_type = "common_source"
        elif cluster_count > 1 and any(c.get("metrics", {}).get("size", 0) > 3 for c in clusters):
            # Multiple medium/large clusters suggest separate introductions
            pattern_type = "multiple_introductions"
        elif avg_links > 1.2:
            # High connectivity suggests sustained transmission
            pattern_type = "sustained_transmission"
        
        # Assess geographic spread
        geographic_focus = "local"
        if len(links) > 0:
            distances = [link.get("distance_km", 0) for link in links]
            max_distance = max(distances) if distances else 0
            avg_distance = sum(distances) / len(distances) if distances else 0
            
            if max_distance > 300:
                geographic_focus = "widespread"
            elif max_distance > 100 or avg_distance > 50:
                geographic_focus = "regional"
        
        # Assess temporal pattern
        temporal_pattern = "unknown"
        if "max_temporal_distance" in network:
            max_days = network["max_temporal_distance"]
            if max_days < 14:
                temporal_pattern = "rapid"
            elif max_days < 30:
                temporal_pattern = "moderate"
            else:
                temporal_pattern = "extended"
        
        # Determine interventions needed based on pattern
        interventions = self._recommend_interventions(
            pattern_type, geographic_focus, temporal_pattern)
        
        return {
            "pattern_type": pattern_type,
            "geographic_focus": geographic_focus,
            "temporal_pattern": temporal_pattern,
            "transmission_intensity": self._assess_transmission_intensity(avg_links),
            "superspreading_evidence": len(network.get("superspreaders", [])) > 0,
            "intervention_recommendations": interventions,
            "assessment_timestamp": datetime.now().isoformat()
        }
    
    def _assess_transmission_intensity(self, avg_links: float) -> str:
        """
        Assess transmission intensity based on average links per case.
        
        Args:
            avg_links: Average number of transmission links per case
            
        Returns:
            Intensity level (low, moderate, high)
        """
        if avg_links < 0.5:
            return "low"
        elif avg_links < 1.0:
            return "moderate"
        else:
            return "high"
    
    def _recommend_interventions(self, 
                              pattern_type: str, 
                              geographic_focus: str,
                              temporal_pattern: str) -> Dict[str, Any]:
        """
        Recommend interventions based on the transmission pattern.
        
        Args:
            pattern_type: Type of transmission pattern
            geographic_focus: Geographic extent of spread
            temporal_pattern: Temporal pattern of spread
            
        Returns:
            Dictionary with recommended interventions
        """
        interventions = {
            "surveillance": [],
            "control": [],
            "priority_level": "standard"
        }
        
        # Base recommendations on pattern type
        if pattern_type == "common_source":
            interventions["surveillance"].append("Intensive source investigation")
            interventions["surveillance"].append("Environmental sampling")
            interventions["control"].append("Source-targeted control measures")
            interventions["priority_level"] = "high"
            
        elif pattern_type == "multiple_introductions":
            interventions["surveillance"].append("Wild bird surveillance")
            interventions["surveillance"].append("Import pathway monitoring")
            interventions["control"].append("Border biosecurity enhancement")
            interventions["priority_level"] = "high"
            
        elif pattern_type == "sustained_transmission":
            interventions["surveillance"].append("Contact tracing")
            interventions["surveillance"].append("Expanded ring surveillance")
            interventions["control"].append("Movement restrictions")
            interventions["control"].append("Enhanced farm biosecurity")
            interventions["priority_level"] = "very high"
            
        else:  # sporadic
            interventions["surveillance"].append("Routine surveillance")
            interventions["control"].append("Standard biosecurity measures")
            interventions["priority_level"] = "standard"
        
        # Adjust based on geographic focus
        if geographic_focus == "widespread":
            interventions["surveillance"].append("Multi-jurisdictional coordination")
            interventions["control"].append("Regional movement controls")
            # Increase priority level
            if interventions["priority_level"] == "standard":
                interventions["priority_level"] = "high"
            elif interventions["priority_level"] == "high":
                interventions["priority_level"] = "very high"
        
        # Adjust based on temporal pattern
        if temporal_pattern == "rapid":
            interventions["surveillance"].append("Daily reporting")
            interventions["control"].append("Urgent response measures")
            # Increase priority level
            if interventions["priority_level"] != "very high":
                interventions["priority_level"] = "very high"
        
        return interventions
    
    def predict_spread_trajectory(self, 
                               network: Dict[str, Any],
                               cases: List[Case],
                               days_ahead: int = 14) -> Dict[str, Any]:
        """
        Predict the spread trajectory based on the transmission network.
        
        Args:
            network: Transmission network from infer_transmission_network
            cases: List of cases
            days_ahead: Number of days to predict ahead
            
        Returns:
            Dictionary with spread predictions
        """
        # Extract key network properties
        links = network.get("links", [])
        metrics = network.get("network_metrics", {})
        
        # Calculate transmission rate
        case_count = metrics.get("node_count", 0)
        
        if case_count < 2:
            return {
                "error": "Insufficient cases for trajectory prediction",
                "days_ahead": days_ahead
            }
        
        # Create a case date mapping
        case_dates = {}
        for case in cases:
            if hasattr(case, 'detection_date'):
                case_dates[case.id] = datetime.fromisoformat(case.detection_date)
        
        # Calculate average time between linked cases
        if links:
            transmission_intervals = []
            for link in links:
                source_id = link.get("source")
                target_id = link.get("target")
                
                if source_id in case_dates and target_id in case_dates:
                    interval = (case_dates[target_id] - case_dates[source_id]).days
                    transmission_intervals.append(interval)
            
            avg_interval = sum(transmission_intervals) / len(transmission_intervals) if transmission_intervals else 7
        else:
            avg_interval = 7  # Default assumption
        
        # Calculate reproduction number (R) from network
        if case_count > 0:
            # Simple R calculation - average outgoing links per case
            total_outgoing_links = sum(1 for link in links)
            reproduction_number = total_outgoing_links / case_count
        else:
            reproduction_number = 1.0  # Default assumption
        
        # Sort cases by date
        dated_cases = [(case.id, case_dates[case.id]) for case in cases if case.id in case_dates]
        dated_cases.sort(key=lambda x: x[1])
        
        # Calculate recent trend
        recent_window = 14  # days
        now = datetime.now()
        recent_cutoff = now - timedelta(days=recent_window)
        
        recent_cases = [case for case in cases 
                      if hasattr(case, 'detection_date') and 
                      datetime.fromisoformat(case.detection_date) >= recent_cutoff]
        
        recent_count = len(recent_cases)
        growth_rate = 0.0
        
        if recent_count > 0 and len(dated_cases) > recent_count:
            # Calculate growth compared to previous period
            previous_cutoff = recent_cutoff - timedelta(days=recent_window)
            previous_cases = [case for case in cases 
                            if hasattr(case, 'detection_date') and 
                            previous_cutoff <= datetime.fromisoformat(case.detection_date) < recent_cutoff]
            
            previous_count = len(previous_cases)
            
            if previous_count > 0:
                growth_rate = (recent_count - previous_count) / previous_count
        
        # Predict future cases using simple exponential growth model
        projected_cases = []
        cumulative_projection = recent_count
        
        daily_rate = (1 + growth_rate) ** (1 / recent_window)
        
        for day in range(1, days_ahead + 1):
            # Project using combination of R and recent growth
            # More weight to recent growth for short-term, more weight to R for longer-term
            short_term_weight = max(0, 1 - (day / 14))
            
            # Daily projection for this day
            if reproduction_number > 0 and avg_interval > 0:
                r_projection = recent_count * (reproduction_number ** (day / avg_interval))
            else:
                r_projection = recent_count
                
            growth_projection = recent_count * (daily_rate ** day)
            
            # Combine projections
            day_projection = (growth_projection * short_term_weight + 
                             r_projection * (1 - short_term_weight))
            
            # Add uncertainty as we project further
            uncertainty = 0.1 * day  # 10% per day
            
            projected_date = now + timedelta(days=day)
            projected_cases.append({
                "day": day,
                "date": projected_date.date().isoformat(),
                "projected_new_cases": round(day_projection - cumulative_projection, 1),
                "cumulative_projected_cases": round(day_projection, 1),
                "uncertainty": uncertainty
            })
            
            cumulative_projection = day_projection
        
        # Generate projection summary
        total_new_cases = sum(day["projected_new_cases"] for day in projected_cases)
        
        return {
            "reproduction_number": reproduction_number,
            "growth_rate": growth_rate,
            "average_transmission_interval_days": avg_interval,
            "days_ahead": days_ahead,
            "total_projected_new_cases": round(total_new_cases, 1),
            "daily_projections": projected_cases,
            "confidence_level": "moderate",
            "projection_timestamp": datetime.now().isoformat()
        }
    
    def analyze_transmission_dynamics(self, 
                                    cases: List[Case],
                                    temporal_window: int = 30,
                                    spatial_threshold: float = 100.0) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of transmission dynamics.
        
        Args:
            cases: List of cases to analyze
            temporal_window: Maximum time window for transmission links
            spatial_threshold: Maximum distance for transmission links
            
        Returns:
            Dictionary with comprehensive analysis
        """
        # First infer the transmission network
        network = self.infer_transmission_network(
            cases, 
            temporal_window=temporal_window,
            spatial_threshold=spatial_threshold
        )
        
        # Assess the transmission pattern
        pattern = self.assess_transmission_pattern(network)
        
        # Predict future trajectory
        trajectory = self.predict_spread_trajectory(network, cases)
        
        # Combine all analyses
        return {
            "transmission_network": network,
            "pattern_assessment": pattern,
            "trajectory_prediction": trajectory,
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_version": "1.0"
        }