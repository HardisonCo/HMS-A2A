"""
Map generator service for avian influenza visualization.

This module provides services for generating geospatial visualizations
of avian influenza outbreaks, risk maps, and surveillance data.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
import json
import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
import matplotlib.cm as cm
import io
import base64

from ...models.base import GeoLocation, GeoRegion
from ...models.case import Case, VirusSubtype
from ...models.surveillance import SurveillanceSite

logger = logging.getLogger(__name__)


class MapGenerator:
    """
    Service for generating geospatial visualizations of avian influenza data.
    """
    
    def __init__(self, 
                boundary_file: Optional[str] = None,
                state_file: Optional[str] = None,
                county_file: Optional[str] = None):
        """
        Initialize the map generator service.
        
        Args:
            boundary_file: Path to GeoJSON file with country boundaries
            state_file: Path to GeoJSON file with state/province boundaries
            county_file: Path to GeoJSON file with county boundaries
        """
        self.boundary_file = boundary_file
        self.state_file = state_file
        self.county_file = county_file
        
        # Load boundary data if available
        self.country_boundaries = None
        self.state_boundaries = None
        self.county_boundaries = None
        
        self._load_boundary_data()
        
        # Define color schemes
        self.risk_colors = {
            'low': '#91cf60',            # green
            'moderate_low': '#ffffbf',   # yellow
            'moderate': '#fee08b',       # light orange
            'moderate_high': '#fc8d59',  # orange
            'high': '#d73027'            # red
        }
        
        # Default figure settings
        self.default_figsize = (12, 9)
        self.default_dpi = 100
    
    def _load_boundary_data(self) -> None:
        """Load boundary data from GeoJSON files if available."""
        try:
            if self.boundary_file and os.path.exists(self.boundary_file):
                self.country_boundaries = gpd.read_file(self.boundary_file)
                logger.info(f"Loaded country boundaries from {self.boundary_file}")
                
            if self.state_file and os.path.exists(self.state_file):
                self.state_boundaries = gpd.read_file(self.state_file)
                logger.info(f"Loaded state boundaries from {self.state_file}")
                
            if self.county_file and os.path.exists(self.county_file):
                self.county_boundaries = gpd.read_file(self.county_file)
                logger.info(f"Loaded county boundaries from {self.county_file}")
                
        except Exception as e:
            logger.error(f"Error loading boundary data: {str(e)}")
    
    def create_case_map(self, 
                      cases: List[Case],
                      regions: Optional[List[GeoRegion]] = None,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None,
                      title: Optional[str] = None,
                      show_legend: bool = True,
                      width: int = 1200,
                      height: int = 900,
                      region_level: str = 'county') -> Dict[str, Any]:
        """
        Create a map visualization of avian influenza cases.
        
        Args:
            cases: List of cases to visualize
            regions: Optional list of regions to include
            start_date: Optional start date for filtering cases (ISO format)
            end_date: Optional end date for filtering cases (ISO format)
            title: Optional title for the map
            show_legend: Whether to show the legend
            width: Width of the map in pixels
            height: Height of the map in pixels
            region_level: Level of regional boundaries to display (county, state, none)
            
        Returns:
            Dictionary with visualization data:
                - base64_image: Base64-encoded PNG image
                - case_count: Total number of cases displayed
                - date_range: Date range of displayed cases
                - center: Center coordinates of the map
                - metadata: Additional metadata
        """
        # Filter cases by date if needed
        filtered_cases = cases
        if start_date or end_date:
            filtered_cases = []
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None
            
            for case in cases:
                case_dt = datetime.fromisoformat(case.detection_date)
                if start_dt and case_dt < start_dt:
                    continue
                if end_dt and case_dt > end_dt:
                    continue
                filtered_cases.append(case)
        
        if not filtered_cases:
            logger.warning("No cases to display after filtering")
            return {
                "error": "No cases to display after applying filters",
                "case_count": 0
            }
        
        # Prepare data for plotting
        case_points = []
        case_colors = []
        case_sizes = []
        
        # Determine color based on virus subtype
        subtype_colors = {}
        for subtype in VirusSubtype:
            subtype_colors[subtype] = mcolors.TABLEAU_COLORS[list(mcolors.TABLEAU_COLORS.keys())[hash(subtype) % len(mcolors.TABLEAU_COLORS)]]
        
        # Default color for unknown subtype
        default_color = 'gray'
        
        # Process cases
        for case in filtered_cases:
            if not hasattr(case, 'location') or not case.location:
                continue
                
            lat = case.location.latitude
            lon = case.location.longitude
            case_points.append((lon, lat))
            
            # Determine color by subtype
            subtype = getattr(case, 'virus_subtype', None)
            color = subtype_colors.get(subtype, default_color) if subtype else default_color
            case_colors.append(color)
            
            # Determine size by impact (if available)
            impact = getattr(case, 'impact_score', None)
            size = 50 + (impact * 100 if impact is not None else 0)
            case_sizes.append(size)
        
        # Create figure
        figsize = (width / self.default_dpi, height / self.default_dpi)
        fig, ax = plt.subplots(figsize=figsize, dpi=self.default_dpi)
        
        # Plot appropriate boundaries
        boundary_gdf = None
        if region_level == 'county' and self.county_boundaries is not None:
            boundary_gdf = self.county_boundaries
        elif region_level == 'state' and self.state_boundaries is not None:
            boundary_gdf = self.state_boundaries
        elif self.country_boundaries is not None:
            boundary_gdf = self.country_boundaries
        
        if boundary_gdf is not None:
            boundary_gdf.plot(ax=ax, color='lightgray', edgecolor='darkgray', linewidth=0.5)
        
        # Add regions if provided
        if regions:
            # Convert regions to GeoDataFrame
            region_shapes = []
            region_ids = []
            
            for region in regions:
                if hasattr(region, 'boundary') and region.boundary:
                    # Regions with boundary polygons
                    try:
                        # Assuming boundary is a list of (lon, lat) tuples
                        poly = Polygon(region.boundary)
                        region_shapes.append(poly)
                        region_ids.append(region.id)
                    except Exception as e:
                        logger.error(f"Error processing region boundary: {str(e)}")
            
            if region_shapes:
                # Create GeoDataFrame for regions
                region_gdf = gpd.GeoDataFrame({
                    'id': region_ids,
                    'geometry': region_shapes
                })
                
                # Plot regions with light fill and border
                region_gdf.plot(ax=ax, color='lightblue', edgecolor='blue', alpha=0.3, linewidth=1)
        
        # Plot case points
        if case_points:
            x, y = zip(*case_points)
            ax.scatter(x, y, c=case_colors, s=case_sizes, alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # Set up legend
        if show_legend:
            legend_elements = []
            for subtype, color in subtype_colors.items():
                if any(getattr(c, 'virus_subtype', None) == subtype for c in filtered_cases):
                    legend_elements.append(Patch(facecolor=color, edgecolor='black', 
                                                label=f"{subtype.value if hasattr(subtype, 'value') else subtype}"))
            
            ax.legend(handles=legend_elements, loc='upper right', title="Virus Subtypes")
        
        # Set title
        if title:
            ax.set_title(title, fontsize=14)
        else:
            date_range_str = ""
            if start_date and end_date:
                date_range_str = f"({start_date.split('T')[0]} to {end_date.split('T')[0]})"
            elif start_date:
                date_range_str = f"(from {start_date.split('T')[0]})"
            elif end_date:
                date_range_str = f"(until {end_date.split('T')[0]})"
                
            ax.set_title(f"Avian Influenza Cases {date_range_str}", fontsize=14)
        
        # Configure axis appearance
        ax.set_xlabel("Longitude", fontsize=10)
        ax.set_ylabel("Latitude", fontsize=10)
        
        # Adjust extent to fit all points with padding
        if case_points:
            x, y = zip(*case_points)
            padding = 0.5  # degrees
            ax.set_xlim(min(x) - padding, max(x) + padding)
            ax.set_ylim(min(y) - padding, max(y) + padding)
        
        # Generate date range info
        date_range = {}
        if filtered_cases:
            detection_dates = [datetime.fromisoformat(c.detection_date) for c in filtered_cases 
                            if hasattr(c, 'detection_date')]
            if detection_dates:
                date_range = {
                    "min": min(detection_dates).isoformat(),
                    "max": max(detection_dates).isoformat()
                }
        
        # Convert plot to base64 image
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # Calculate map center
        center = None
        if case_points:
            x, y = zip(*case_points)
            center = {
                "longitude": sum(x) / len(x),
                "latitude": sum(y) / len(y)
            }
        
        return {
            "base64_image": img_base64,
            "case_count": len(filtered_cases),
            "date_range": date_range,
            "center": center,
            "metadata": {
                "region_level": region_level,
                "subtypes": list(set(getattr(c, 'virus_subtype', None) for c in filtered_cases if hasattr(c, 'virus_subtype')))
            }
        }
    
    def create_risk_map(self,
                      risk_data: Dict[str, Union[float, str]],
                      regions: List[GeoRegion],
                      region_mapping: Optional[Dict[str, str]] = None,
                      title: Optional[str] = None,
                      prediction_date: Optional[str] = None,
                      days_ahead: Optional[int] = None,
                      width: int = 1200,
                      height: int = 900,
                      show_legend: bool = True) -> Dict[str, Any]:
        """
        Create a risk map visualization based on predictive model outputs.
        
        Args:
            risk_data: Dictionary mapping region IDs to risk values or categories
            regions: List of regions with boundary information
            region_mapping: Optional mapping between region IDs and boundary IDs
            title: Optional title for the map
            prediction_date: Date of the prediction (ISO format)
            days_ahead: Number of days ahead in the prediction
            width: Width of the map in pixels
            height: Height of the map in pixels
            show_legend: Whether to show the legend
            
        Returns:
            Dictionary with visualization data:
                - base64_image: Base64-encoded PNG image
                - region_count: Number of regions displayed
                - center: Center coordinates of the map
                - metadata: Additional metadata
        """
        # Create figure
        figsize = (width / self.default_dpi, height / self.default_dpi)
        fig, ax = plt.subplots(figsize=figsize, dpi=self.default_dpi)
        
        # Prepare region data
        region_shapes = []
        region_ids = []
        region_risks = []
        
        for region in regions:
            if region.id not in risk_data:
                continue
                
            if not hasattr(region, 'boundary') or not region.boundary:
                logger.warning(f"Region {region.id} has no boundary information")
                continue
            
            try:
                # Assuming boundary is a list of (lon, lat) tuples
                poly = Polygon(region.boundary)
                region_shapes.append(poly)
                region_ids.append(region.id)
                
                # Get risk value or category
                risk_value = risk_data[region.id]
                region_risks.append(risk_value)
            except Exception as e:
                logger.error(f"Error processing region {region.id}: {str(e)}")
        
        if not region_shapes:
            logger.warning("No valid regions with risk data to display")
            return {
                "error": "No valid regions with risk data to display",
                "region_count": 0
            }
        
        # Create GeoDataFrame for regions
        region_gdf = gpd.GeoDataFrame({
            'id': region_ids,
            'risk': region_risks,
            'geometry': region_shapes
        })
        
        # Determine color scheme based on risk data type
        if all(isinstance(risk, str) for risk in region_risks):
            # Categorical risk levels
            cmap = {category: self.risk_colors.get(category, '#CCCCCC') 
                  for category in set(region_risks)}
            
            # Plot regions with categorical colors
            for category, color in cmap.items():
                category_regions = region_gdf[region_gdf['risk'] == category]
                if not category_regions.empty:
                    category_regions.plot(ax=ax, color=color, edgecolor='darkgray', 
                                        linewidth=0.5, label=category)
        else:
            # Numerical risk values
            # Convert any string values to float if possible
            for i, risk in enumerate(region_risks):
                if isinstance(risk, str):
                    try:
                        region_risks[i] = float(risk)
                    except ValueError:
                        region_risks[i] = 0
            
            # Update the GeoDataFrame
            region_gdf['risk'] = region_risks
            
            # Create a continuous colormap
            cmap = cm.get_cmap('RdYlGn_r')
            norm = mcolors.Normalize(vmin=0, vmax=1)
            
            # Plot regions with continuous color scale
            region_gdf.plot(ax=ax, column='risk', cmap=cmap, norm=norm, 
                          edgecolor='darkgray', linewidth=0.5, legend=show_legend)
            
            if show_legend:
                # Add colorbar
                sm = cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])
                cbar = fig.colorbar(sm, ax=ax)
                cbar.set_label('Risk Level')
        
        # Plot country boundaries for context if available
        if self.country_boundaries is not None:
            self.country_boundaries.boundary.plot(ax=ax, color='black', linewidth=0.8)
        
        # Set title
        if title:
            ax.set_title(title, fontsize=14)
        else:
            prediction_str = f"as of {prediction_date.split('T')[0]}" if prediction_date else ""
            days_str = f"for next {days_ahead} days" if days_ahead else ""
            ax.set_title(f"Avian Influenza Risk Map {prediction_str} {days_str}", fontsize=14)
        
        # Configure axis appearance
        ax.set_xlabel("Longitude", fontsize=10)
        ax.set_ylabel("Latitude", fontsize=10)
        
        # Add legend for categorical data if not already added
        if all(isinstance(risk, str) for risk in region_risks) and show_legend:
            legend_elements = []
            for category, color in cmap.items():
                legend_elements.append(Patch(facecolor=color, edgecolor='darkgray', 
                                            label=category.replace('_', ' ').title()))
            
            ax.legend(handles=legend_elements, loc='upper right', title="Risk Levels")
        
        # Convert plot to base64 image
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # Calculate map center from region centroids
        x = []
        y = []
        for region in regions:
            if hasattr(region, 'centroid') and region.centroid:
                x.append(region.centroid.longitude)
                y.append(region.centroid.latitude)
        
        center = None
        if x and y:
            center = {
                "longitude": sum(x) / len(x),
                "latitude": sum(y) / len(y)
            }
        
        return {
            "base64_image": img_base64,
            "region_count": len(region_shapes),
            "center": center,
            "metadata": {
                "prediction_date": prediction_date,
                "days_ahead": days_ahead,
                "risk_type": "categorical" if all(isinstance(risk, str) for risk in region_risks) else "numerical"
            }
        }
    
    def create_surveillance_map(self,
                              surveillance_sites: List[SurveillanceSite],
                              cases: Optional[List[Case]] = None,
                              regions: Optional[List[GeoRegion]] = None,
                              sampling_allocation: Optional[Dict[str, float]] = None,
                              title: Optional[str] = None,
                              width: int = 1200,
                              height: int = 900,
                              show_legend: bool = True) -> Dict[str, Any]:
        """
        Create a map visualization of surveillance sites and sampling allocation.
        
        Args:
            surveillance_sites: List of surveillance sites to visualize
            cases: Optional list of cases to include
            regions: Optional list of regions to include
            sampling_allocation: Optional dictionary mapping site IDs to allocation values
            title: Optional title for the map
            width: Width of the map in pixels
            height: Height of the map in pixels
            show_legend: Whether to show the legend
            
        Returns:
            Dictionary with visualization data:
                - base64_image: Base64-encoded PNG image
                - site_count: Number of surveillance sites displayed
                - case_count: Number of cases displayed (if applicable)
                - center: Center coordinates of the map
                - metadata: Additional metadata
        """
        # Create figure
        figsize = (width / self.default_dpi, height / self.default_dpi)
        fig, ax = plt.subplots(figsize=figsize, dpi=self.default_dpi)
        
        # Plot country or state boundaries for context
        if self.state_boundaries is not None:
            self.state_boundaries.plot(ax=ax, color='lightgray', edgecolor='darkgray', linewidth=0.5)
        elif self.country_boundaries is not None:
            self.country_boundaries.plot(ax=ax, color='lightgray', edgecolor='darkgray', linewidth=0.5)
        
        # Add regions if provided
        if regions:
            # Convert regions to GeoDataFrame
            region_shapes = []
            region_ids = []
            
            for region in regions:
                if hasattr(region, 'boundary') and region.boundary:
                    try:
                        poly = Polygon(region.boundary)
                        region_shapes.append(poly)
                        region_ids.append(region.id)
                    except Exception as e:
                        logger.error(f"Error processing region boundary: {str(e)}")
            
            if region_shapes:
                # Create GeoDataFrame for regions
                region_gdf = gpd.GeoDataFrame({
                    'id': region_ids,
                    'geometry': region_shapes
                })
                
                # Plot regions with light fill and border
                region_gdf.plot(ax=ax, color='lightblue', edgecolor='blue', alpha=0.3, linewidth=1)
        
        # Add cases if provided
        case_points = []
        if cases:
            for case in cases:
                if hasattr(case, 'location') and case.location:
                    case_points.append((case.location.longitude, case.location.latitude))
            
            if case_points:
                x, y = zip(*case_points)
                ax.scatter(x, y, c='red', s=50, alpha=0.7, edgecolor='black', 
                          linewidth=0.5, label='Cases')
        
        # Prepare surveillance site data
        site_points = []
        site_allocations = []
        site_types = []
        
        for site in surveillance_sites:
            if not hasattr(site, 'location') or not site.location:
                continue
                
            site_points.append((site.location.longitude, site.location.latitude))
            
            # Get allocation value if available
            allocation = sampling_allocation.get(site.id, 1.0) if sampling_allocation else 1.0
            site_allocations.append(allocation)
            
            # Get site type if available
            site_type = getattr(site, 'site_type', 'unknown')
            site_types.append(site_type)
        
        # Plot surveillance sites
        if site_points:
            x, y = zip(*site_points)
            
            # Normalize allocations for size scaling
            if site_allocations:
                max_alloc = max(site_allocations)
                min_alloc = min(site_allocations)
                norm_allocations = [(a - min_alloc) / (max_alloc - min_alloc) * 0.8 + 0.2 
                                  if max_alloc > min_alloc else 0.5 for a in site_allocations]
                
                # Scale marker sizes based on allocation
                # The formula maps allocations to sizes between 30 and 150
                sizes = [30 + a * 120 for a in norm_allocations]
            else:
                sizes = [80] * len(site_points)
            
            # Color by site type
            site_type_colors = {}
            for site_type in set(site_types):
                site_type_colors[site_type] = mcolors.TABLEAU_COLORS[list(mcolors.TABLEAU_COLORS.keys())[hash(site_type) % len(mcolors.TABLEAU_COLORS)]]
            
            colors = [site_type_colors.get(site_type, 'blue') for site_type in site_types]
            
            # Plot surveillance sites
            scatter = ax.scatter(x, y, c=colors, s=sizes, alpha=0.7, edgecolor='black', 
                               linewidth=0.5, marker='^')
        
        # Set up legend
        if show_legend:
            legend_elements = []
            
            # Add site types to legend
            for site_type, color in site_type_colors.items():
                legend_elements.append(Patch(facecolor=color, edgecolor='black', 
                                          label=f"{site_type.replace('_', ' ').title()}"))
            
            # Add cases to legend if included
            if case_points:
                legend_elements.append(Patch(facecolor='red', edgecolor='black', 
                                          label='Confirmed Cases'))
            
            # Add allocation scale if available
            if sampling_allocation:
                legend_elements.append(Patch(facecolor='white', edgecolor='black', alpha=0,
                                          label='Marker size = sampling allocation'))
            
            ax.legend(handles=legend_elements, loc='upper right', title="Map Elements")
        
        # Set title
        if title:
            ax.set_title(title, fontsize=14)
        else:
            ax.set_title("Avian Influenza Surveillance Network", fontsize=14)
        
        # Configure axis appearance
        ax.set_xlabel("Longitude", fontsize=10)
        ax.set_ylabel("Latitude", fontsize=10)
        
        # Adjust extent to fit all points with padding
        all_points = site_points + case_points
        if all_points:
            x, y = zip(*all_points)
            padding = 0.5  # degrees
            ax.set_xlim(min(x) - padding, max(x) + padding)
            ax.set_ylim(min(y) - padding, max(y) + padding)
        
        # Convert plot to base64 image
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # Calculate map center
        center = None
        if all_points:
            x, y = zip(*all_points)
            center = {
                "longitude": sum(x) / len(x),
                "latitude": sum(y) / len(y)
            }
        
        return {
            "base64_image": img_base64,
            "site_count": len(site_points),
            "case_count": len(case_points),
            "center": center,
            "metadata": {
                "site_types": list(set(site_types)),
                "has_allocation_data": sampling_allocation is not None
            }
        }
    
    def create_transmission_network_map(self,
                                      cases: List[Case],
                                      transmission_paths: List[Dict[str, Any]],
                                      regions: Optional[List[GeoRegion]] = None,
                                      title: Optional[str] = None,
                                      width: int = 1200,
                                      height: int = 900,
                                      show_legend: bool = True) -> Dict[str, Any]:
        """
        Create a map visualization of transmission networks between cases.
        
        Args:
            cases: List of cases to visualize
            transmission_paths: List of dictionaries with source, target, and probability
            regions: Optional list of regions to include
            title: Optional title for the map
            width: Width of the map in pixels
            height: Height of the map in pixels
            show_legend: Whether to show the legend
            
        Returns:
            Dictionary with visualization data:
                - base64_image: Base64-encoded PNG image
                - case_count: Number of cases displayed
                - path_count: Number of transmission paths displayed
                - center: Center coordinates of the map
                - metadata: Additional metadata
        """
        # Create figure
        figsize = (width / self.default_dpi, height / self.default_dpi)
        fig, ax = plt.subplots(figsize=figsize, dpi=self.default_dpi)
        
        # Plot country or state boundaries for context
        if self.state_boundaries is not None:
            self.state_boundaries.plot(ax=ax, color='lightgray', edgecolor='darkgray', linewidth=0.5)
        elif self.country_boundaries is not None:
            self.country_boundaries.plot(ax=ax, color='lightgray', edgecolor='darkgray', linewidth=0.5)
        
        # Add regions if provided
        if regions:
            # Convert regions to GeoDataFrame
            region_shapes = []
            region_ids = []
            
            for region in regions:
                if hasattr(region, 'boundary') and region.boundary:
                    try:
                        poly = Polygon(region.boundary)
                        region_shapes.append(poly)
                        region_ids.append(region.id)
                    except Exception as e:
                        logger.error(f"Error processing region boundary: {str(e)}")
            
            if region_shapes:
                # Create GeoDataFrame for regions
                region_gdf = gpd.GeoDataFrame({
                    'id': region_ids,
                    'geometry': region_shapes
                })
                
                # Plot regions with light fill and border
                region_gdf.plot(ax=ax, color='lightblue', edgecolor='blue', alpha=0.3, linewidth=1)
        
        # Create case lookup by ID
        case_lookup = {}
        for case in cases:
            if hasattr(case, 'id') and hasattr(case, 'location') and case.location:
                case_lookup[case.id] = case
        
        # Process transmission paths
        valid_paths = []
        for path in transmission_paths:
            source_id = path.get('source')
            target_id = path.get('target')
            prob = path.get('probability', path.get('risk', 0.5))
            
            if source_id in case_lookup and target_id in case_lookup:
                source_case = case_lookup[source_id]
                target_case = case_lookup[target_id]
                
                source_point = (source_case.location.longitude, source_case.location.latitude)
                target_point = (target_case.location.longitude, target_case.location.latitude)
                
                valid_paths.append({
                    'source': source_point,
                    'target': target_point,
                    'probability': prob
                })
        
        # Plot transmission paths
        for path in valid_paths:
            source = path['source']
            target = path['target']
            prob = path['probability']
            
            # Determine line width and alpha based on probability
            # Scale from 0.5-3 width and 0.2-0.8 alpha
            lw = 0.5 + 2.5 * prob
            alpha = 0.2 + 0.6 * prob
            
            # Draw line
            ax.plot([source[0], target[0]], [source[1], target[1]], 
                   c='red', lw=lw, alpha=alpha, zorder=1)
            
            # Add arrow to indicate direction
            mid_x = (source[0] + target[0]) / 2
            mid_y = (source[1] + target[1]) / 2
            dx = target[0] - source[0]
            dy = target[1] - source[1]
            
            # Normalize and scale for arrow
            length = np.sqrt(dx**2 + dy**2)
            if length > 0:
                dx = dx / length * 0.05  # Scale arrow length
                dy = dy / length * 0.05
                
                ax.arrow(mid_x - dx/2, mid_y - dy/2, dx, dy, 
                        head_width=0.02, head_length=0.03, 
                        fc='red', ec='red', alpha=alpha, zorder=2)
        
        # Plot case points
        case_points = []
        case_statuses = []
        for case in cases:
            if not hasattr(case, 'location') or not case.location:
                continue
                
            case_points.append((case.location.longitude, case.location.latitude))
            
            # Get case status if available
            status = getattr(case, 'status', 'confirmed')
            case_statuses.append(status)
        
        if case_points:
            x, y = zip(*case_points)
            
            # Define status colors
            status_colors = {
                'suspected': 'orange',
                'confirmed': 'red',
                'resolved': 'green',
                'negative': 'blue'
            }
            
            # Set default color for unknown status
            default_color = 'gray'
            
            # Get color for each case
            colors = [status_colors.get(status, default_color) for status in case_statuses]
            
            # Plot cases
            ax.scatter(x, y, c=colors, s=80, alpha=0.8, edgecolor='black', 
                      linewidth=0.5, zorder=3)
        
        # Set up legend
        if show_legend:
            legend_elements = []
            
            # Add case status to legend
            for status in set(case_statuses):
                color = status_colors.get(status, default_color)
                legend_elements.append(Patch(facecolor=color, edgecolor='black', 
                                          label=f"{status.title()} Case"))
            
            # Add transmission path to legend
            legend_elements.append(Patch(facecolor='red', edgecolor='red', alpha=0.6,
                                      label='Transmission Path'))
            
            ax.legend(handles=legend_elements, loc='upper right', title="Map Elements")
        
        # Set title
        if title:
            ax.set_title(title, fontsize=14)
        else:
            ax.set_title("Avian Influenza Transmission Network", fontsize=14)
        
        # Configure axis appearance
        ax.set_xlabel("Longitude", fontsize=10)
        ax.set_ylabel("Latitude", fontsize=10)
        
        # Adjust extent to fit all points with padding
        if case_points:
            x, y = zip(*case_points)
            padding = 0.5  # degrees
            ax.set_xlim(min(x) - padding, max(x) + padding)
            ax.set_ylim(min(y) - padding, max(y) + padding)
        
        # Convert plot to base64 image
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # Calculate map center
        center = None
        if case_points:
            x, y = zip(*case_points)
            center = {
                "longitude": sum(x) / len(x),
                "latitude": sum(y) / len(y)
            }
        
        return {
            "base64_image": img_base64,
            "case_count": len(case_points),
            "path_count": len(valid_paths),
            "center": center,
            "metadata": {
                "case_statuses": list(set(case_statuses))
            }
        }