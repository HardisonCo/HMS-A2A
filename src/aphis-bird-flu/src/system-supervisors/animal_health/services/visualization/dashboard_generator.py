"""
Dashboard generator service for avian influenza visualization.

This module provides services for generating dashboard data,
including summary statistics, trends, and charts for visualizing
avian influenza surveillance and outbreak data.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import seaborn as sns
import io
import base64

from ...models.base import GeoRegion
from ...models.case import Case, VirusSubtype
from ...models.surveillance import SurveillanceSite, SurveillanceEvent

logger = logging.getLogger(__name__)


class DashboardGenerator:
    """
    Service for generating dashboard data and visualizations.
    """
    
    def __init__(self):
        """Initialize the dashboard generator service."""
        # Default figure settings
        self.default_figsize = (10, 6)
        self.default_dpi = 100
        
        # Set default seaborn style
        sns.set_style('whitegrid')
        
        # Default colors
        self.default_colors = sns.color_palette('tab10')
        
    def generate_summary_statistics(self,
                                  cases: List[Case],
                                  surveillance_events: Optional[List[SurveillanceEvent]] = None,
                                  days: int = 30) -> Dict[str, Any]:
        """
        Generate summary statistics for the dashboard.
        
        Args:
            cases: List of case data
            surveillance_events: Optional list of surveillance events
            days: Number of days to include in summary (default: 30)
            
        Returns:
            Dictionary with summary statistics
        """
        # Define time periods
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        last_24h = now - timedelta(days=1)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        last_90d = now - timedelta(days=90)
        
        # Initialize summary dict
        summary = {
            "timestamp": now.isoformat(),
            "cases": {
                "total": 0,
                "last_24h": 0,
                "last_7d": 0,
                "last_30d": 0,
                "last_90d": 0,
                "by_status": {},
                "by_subtype": {}
            },
            "surveillance": {
                "total_events": 0,
                "last_24h": 0,
                "last_7d": 0,
                "last_30d": 0,
                "positive_rate": 0,
                "by_site_type": {}
            },
            "trends": {
                "daily_cases": [],
                "daily_positivity": [],
                "case_growth_rate": None
            }
        }
        
        # Process cases
        if cases:
            # Count cases by time period
            for case in cases:
                if not hasattr(case, 'detection_date'):
                    continue
                
                detection_date = datetime.fromisoformat(case.detection_date)
                summary["cases"]["total"] += 1
                
                if detection_date >= last_24h:
                    summary["cases"]["last_24h"] += 1
                if detection_date >= last_7d:
                    summary["cases"]["last_7d"] += 1
                if detection_date >= last_30d:
                    summary["cases"]["last_30d"] += 1
                if detection_date >= last_90d:
                    summary["cases"]["last_90d"] += 1
                
                # Count by status
                status = getattr(case, 'status', 'confirmed')
                if status not in summary["cases"]["by_status"]:
                    summary["cases"]["by_status"][status] = 0
                summary["cases"]["by_status"][status] += 1
                
                # Count by subtype
                subtype = getattr(case, 'virus_subtype', 'unknown')
                subtype_str = subtype.value if hasattr(subtype, 'value') else str(subtype)
                if subtype_str not in summary["cases"]["by_subtype"]:
                    summary["cases"]["by_subtype"][subtype_str] = 0
                summary["cases"]["by_subtype"][subtype_str] += 1
            
            # Calculate daily case counts for trend data
            date_range = [today - timedelta(days=i) for i in range(days)]
            daily_counts = {d.date(): 0 for d in date_range}
            
            for case in cases:
                if not hasattr(case, 'detection_date'):
                    continue
                
                detection_date = datetime.fromisoformat(case.detection_date)
                detection_day = detection_date.date()
                
                if detection_day in daily_counts:
                    daily_counts[detection_day] += 1
            
            # Format for trend data (sorted by date)
            for day, count in sorted(daily_counts.items()):
                summary["trends"]["daily_cases"].append({
                    "date": day.isoformat(),
                    "count": count
                })
            
            # Calculate case growth rate (comparing last 7 days to previous 7 days)
            last_7d_count = sum(daily_counts[d.date()] for d in date_range[:7])
            prev_7d_count = sum(daily_counts[d.date()] for d in date_range[7:14])
            
            if prev_7d_count > 0:
                growth_rate = (last_7d_count - prev_7d_count) / prev_7d_count
                summary["trends"]["case_growth_rate"] = growth_rate
        
        # Process surveillance events
        if surveillance_events:
            # Count surveillance events
            total_events = 0
            positive_events = 0
            
            events_by_site_type = {}
            positives_by_site_type = {}
            
            last_24h_events = 0
            last_7d_events = 0
            last_30d_events = 0
            
            for event in surveillance_events:
                if not hasattr(event, 'event_date'):
                    continue
                    
                event_date = datetime.fromisoformat(event.event_date)
                total_events += 1
                
                # Count by time period
                if event_date >= last_24h:
                    last_24h_events += 1
                if event_date >= last_7d:
                    last_7d_events += 1
                if event_date >= last_30d:
                    last_30d_events += 1
                
                # Check if positive
                is_positive = getattr(event, 'is_positive', False)
                if is_positive:
                    positive_events += 1
                
                # Count by site type
                site_type = getattr(event, 'site_type', 'unknown')
                if site_type not in events_by_site_type:
                    events_by_site_type[site_type] = 0
                    positives_by_site_type[site_type] = 0
                
                events_by_site_type[site_type] += 1
                if is_positive:
                    positives_by_site_type[site_type] += 1
            
            # Update summary
            summary["surveillance"]["total_events"] = total_events
            summary["surveillance"]["last_24h"] = last_24h_events
            summary["surveillance"]["last_7d"] = last_7d_events
            summary["surveillance"]["last_30d"] = last_30d_events
            
            # Calculate positivity rate
            if total_events > 0:
                summary["surveillance"]["positive_rate"] = positive_events / total_events
            
            # Site type breakdown
            for site_type, count in events_by_site_type.items():
                positive_count = positives_by_site_type.get(site_type, 0)
                positivity_rate = positive_count / count if count > 0 else 0
                
                summary["surveillance"]["by_site_type"][site_type] = {
                    "events": count,
                    "positives": positive_count,
                    "positivity_rate": positivity_rate
                }
            
            # Calculate daily positivity rates for trend data
            date_range = [today - timedelta(days=i) for i in date_range]
            daily_events = {d.date(): 0 for d in date_range}
            daily_positives = {d.date(): 0 for d in date_range}
            
            for event in surveillance_events:
                if not hasattr(event, 'event_date'):
                    continue
                
                event_date = datetime.fromisoformat(event.event_date)
                event_day = event_date.date()
                
                if event_day in daily_events:
                    daily_events[event_day] += 1
                    if getattr(event, 'is_positive', False):
                        daily_positives[event_day] += 1
            
            # Format for trend data (sorted by date)
            for day in sorted(daily_events.keys()):
                events = daily_events[day]
                positives = daily_positives[day]
                positivity = positives / events if events > 0 else 0
                
                summary["trends"]["daily_positivity"].append({
                    "date": day.isoformat(),
                    "events": events,
                    "positives": positives,
                    "positivity_rate": positivity
                })
        
        return summary
    
    def create_case_trend_chart(self,
                              cases: List[Case],
                              days: int = 30,
                              title: Optional[str] = None,
                              include_subtypes: bool = True,
                              width: int = 800,
                              height: int = 500,
                              show_legend: bool = True) -> Dict[str, Any]:
        """
        Create a chart showing case trends over time.
        
        Args:
            cases: List of case data
            days: Number of days to include in chart
            title: Optional title for the chart
            include_subtypes: Whether to break down by virus subtype
            width: Width of the chart in pixels
            height: Height of the chart in pixels
            show_legend: Whether to show the legend
            
        Returns:
            Dictionary with chart data:
                - base64_image: Base64-encoded PNG image
                - total_cases: Total number of cases in the period
                - metadata: Additional chart metadata
        """
        # Define time period
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = today - timedelta(days=days)
        
        # Create date range
        date_range = [today - timedelta(days=i) for i in range(days)]
        date_range.reverse()  # Earliest first
        
        # Filter cases to time period
        filtered_cases = []
        for case in cases:
            if not hasattr(case, 'detection_date'):
                continue
                
            detection_date = datetime.fromisoformat(case.detection_date)
            if detection_date >= start_date:
                filtered_cases.append(case)
        
        if not filtered_cases:
            logger.warning(f"No cases in the last {days} days")
            return {
                "error": f"No cases in the last {days} days",
                "total_cases": 0
            }
        
        # Prepare figure
        figsize = (width / self.default_dpi, height / self.default_dpi)
        fig, ax = plt.subplots(figsize=figsize, dpi=self.default_dpi)
        
        # Count cases by date
        if include_subtypes:
            # Get unique subtypes
            subtypes = set()
            for case in filtered_cases:
                subtype = getattr(case, 'virus_subtype', 'unknown')
                subtype_str = subtype.value if hasattr(subtype, 'value') else str(subtype)
                subtypes.add(subtype_str)
            
            # Prepare counts by date and subtype
            subtype_counts = {}
            for subtype in subtypes:
                subtype_counts[subtype] = {d.date(): 0 for d in date_range}
            
            # Count cases
            for case in filtered_cases:
                detection_date = datetime.fromisoformat(case.detection_date)
                detection_day = detection_date.date()
                
                subtype = getattr(case, 'virus_subtype', 'unknown')
                subtype_str = subtype.value if hasattr(subtype, 'value') else str(subtype)
                
                if detection_day in subtype_counts[subtype_str]:
                    subtype_counts[subtype_str][detection_day] += 1
            
            # Plot stacked bar chart
            bottom = np.zeros(len(date_range))
            x = [d.date() for d in date_range]
            
            for i, (subtype, counts) in enumerate(subtype_counts.items()):
                y = [counts[d] for d in x]
                ax.bar(x, y, bottom=bottom, label=subtype, 
                      color=self.default_colors[i % len(self.default_colors)])
                bottom += np.array(y)
            
            total_cases = int(sum(bottom))
            
        else:
            # Simple case counts by date
            date_counts = {d.date(): 0 for d in date_range}
            
            for case in filtered_cases:
                detection_date = datetime.fromisoformat(case.detection_date)
                detection_day = detection_date.date()
                
                if detection_day in date_counts:
                    date_counts[detection_day] += 1
            
            # Plot bar chart
            x = [d for d in date_counts.keys()]
            y = [date_counts[d] for d in x]
            ax.bar(x, y, color='steelblue')
            
            total_cases = sum(y)
        
        # Add 7-day moving average line
        if len(date_range) >= 7:
            # Compute moving average for the dates we have
            if include_subtypes:
                # Sum across all subtypes for each date
                date_sums = {d: sum(subtype_counts[s][d] for s in subtypes) for d in x}
                y_vals = [date_sums[d] for d in x]
            else:
                y_vals = y
            
            # Calculate 7-day moving average
            ma_y = []
            for i in range(len(y_vals)):
                if i < 6:  # Not enough data for 7-day window
                    ma_y.append(np.nan)
                else:
                    ma_y.append(np.mean(y_vals[i-6:i+1]))
            
            # Plot moving average line
            ax.plot(x, ma_y, color='red', linestyle='-', linewidth=2, 
                   label='7-day Moving Average')
        
        # Configure axis
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Number of Cases', fontsize=12)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        if len(date_range) > 14:
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))  # Every Monday
        else:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Every day
            
        plt.xticks(rotation=45)
        
        # Set title
        if title:
            ax.set_title(title, fontsize=14)
        else:
            ax.set_title(f'Avian Influenza Cases - Last {days} Days', fontsize=14)
        
        # Add legend if needed
        if show_legend and (include_subtypes or len(date_range) >= 7):
            ax.legend(loc='upper left')
        
        # Ensure axis starts at zero
        ax.set_ylim(bottom=0)
        
        # Add grid
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Make layout tight
        fig.tight_layout()
        
        # Convert to base64 image
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # Calculate basic statistics
        last_7d = sum(y_vals[-7:]) if len(y_vals) >= 7 else sum(y_vals)
        last_14d = sum(y_vals[-14:]) if len(y_vals) >= 14 else sum(y_vals)
        
        growth_rate = None
        if len(y_vals) >= 14:
            week1 = sum(y_vals[-7:])
            week2 = sum(y_vals[-14:-7])
            if week2 > 0:
                growth_rate = (week1 - week2) / week2
        
        return {
            "base64_image": img_base64,
            "total_cases": total_cases,
            "metadata": {
                "period_days": days,
                "start_date": start_date.date().isoformat(),
                "end_date": today.date().isoformat(),
                "last_7d_cases": int(last_7d),
                "last_14d_cases": int(last_14d),
                "growth_rate": growth_rate,
                "includes_subtypes": include_subtypes
            }
        }
    
    def create_geographic_distribution_chart(self,
                                           cases: List[Case],
                                           regions: List[GeoRegion],
                                           days: int = 30,
                                           title: Optional[str] = None,
                                           top_n: int = 10,
                                           width: int = 800,
                                           height: int = 500) -> Dict[str, Any]:
        """
        Create a chart showing the geographic distribution of cases.
        
        Args:
            cases: List of case data
            regions: List of geographic regions
            days: Number of days to include
            title: Optional title for the chart
            top_n: Number of top regions to display
            width: Width of the chart in pixels
            height: Height of the chart in pixels
            
        Returns:
            Dictionary with chart data:
                - base64_image: Base64-encoded PNG image
                - total_regions: Total number of regions with cases
                - metadata: Additional chart metadata
        """
        # Define time period
        now = datetime.now()
        start_date = now - timedelta(days=days)
        
        # Filter cases to time period
        filtered_cases = []
        for case in cases:
            if not hasattr(case, 'detection_date'):
                continue
                
            detection_date = datetime.fromisoformat(case.detection_date)
            if detection_date >= start_date:
                filtered_cases.append(case)
        
        if not filtered_cases:
            logger.warning(f"No cases in the last {days} days")
            return {
                "error": f"No cases in the last {days} days",
                "total_regions": 0
            }
        
        # Count cases by region
        region_counts = {}
        for case in filtered_cases:
            if not hasattr(case, 'region_id'):
                continue
                
            region_id = case.region_id
            if region_id not in region_counts:
                region_counts[region_id] = 0
            region_counts[region_id] += 1
        
        if not region_counts:
            logger.warning("No region information available in cases")
            return {
                "error": "No region information available in cases",
                "total_regions": 0
            }
        
        # Create region name lookup
        region_names = {}
        for region in regions:
            if hasattr(region, 'id') and hasattr(region, 'name'):
                region_names[region.id] = region.name
        
        # Prepare data for chart
        region_data = []
        for region_id, count in region_counts.items():
            region_name = region_names.get(region_id, region_id)
            region_data.append((region_name, count))
        
        # Sort by count and take top N
        region_data.sort(key=lambda x: x[1], reverse=True)
        top_regions = region_data[:top_n]
        
        # Prepare figure
        figsize = (width / self.default_dpi, height / self.default_dpi)
        fig, ax = plt.subplots(figsize=figsize, dpi=self.default_dpi)
        
        # Extract data for plotting
        names = [r[0] for r in top_regions]
        counts = [r[1] for r in top_regions]
        
        # Plot horizontal bar chart
        ax.barh(names, counts, color='steelblue')
        
        # Add count labels
        for i, count in enumerate(counts):
            ax.text(count + (max(counts) * 0.01), i, str(count), 
                   va='center', color='black', fontweight='bold')
        
        # Configure axis
        ax.set_xlabel('Number of Cases', fontsize=12)
        ax.set_ylabel('Region', fontsize=12)
        
        # Invert y-axis to have highest count at top
        ax.invert_yaxis()
        
        # Set title
        if title:
            ax.set_title(title, fontsize=14)
        else:
            ax.set_title(f'Top {len(top_regions)} Regions by Case Count - Last {days} Days', fontsize=14)
        
        # Ensure x-axis starts at zero
        ax.set_xlim(left=0)
        
        # Add grid
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Make layout tight
        fig.tight_layout()
        
        # Convert to base64 image
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return {
            "base64_image": img_base64,
            "total_regions": len(region_counts),
            "metadata": {
                "period_days": days,
                "top_n": top_n,
                "displayed_regions": names,
                "total_cases": sum(counts),
                "top_region": names[0] if names else None,
                "top_region_count": counts[0] if counts else 0
            }
        }
    
    def create_subtype_distribution_chart(self,
                                       cases: List[Case],
                                       days: int = 30,
                                       title: Optional[str] = None,
                                       chart_type: str = 'pie',
                                       width: int = 800,
                                       height: int = 500) -> Dict[str, Any]:
        """
        Create a chart showing the distribution of virus subtypes.
        
        Args:
            cases: List of case data
            days: Number of days to include
            title: Optional title for the chart
            chart_type: Type of chart ('pie' or 'bar')
            width: Width of the chart in pixels
            height: Height of the chart in pixels
            
        Returns:
            Dictionary with chart data:
                - base64_image: Base64-encoded PNG image
                - subtype_counts: Dictionary of counts by subtype
                - metadata: Additional chart metadata
        """
        # Define time period
        now = datetime.now()
        start_date = now - timedelta(days=days)
        
        # Filter cases to time period
        filtered_cases = []
        for case in cases:
            if not hasattr(case, 'detection_date'):
                continue
                
            detection_date = datetime.fromisoformat(case.detection_date)
            if detection_date >= start_date:
                filtered_cases.append(case)
        
        if not filtered_cases:
            logger.warning(f"No cases in the last {days} days")
            return {
                "error": f"No cases in the last {days} days",
                "subtype_counts": {}
            }
        
        # Count cases by subtype
        subtype_counts = {}
        for case in filtered_cases:
            subtype = getattr(case, 'virus_subtype', 'unknown')
            subtype_str = subtype.value if hasattr(subtype, 'value') else str(subtype)
            
            if subtype_str not in subtype_counts:
                subtype_counts[subtype_str] = 0
            subtype_counts[subtype_str] += 1
        
        # Prepare figure
        figsize = (width / self.default_dpi, height / self.default_dpi)
        fig, ax = plt.subplots(figsize=figsize, dpi=self.default_dpi)
        
        # Extract data for plotting
        labels = list(subtype_counts.keys())
        counts = list(subtype_counts.values())
        
        # Create chart based on type
        if chart_type == 'pie':
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                counts, 
                labels=None,  # Will use legend instead
                autopct='%1.1f%%',
                startangle=90,
                colors=self.default_colors[:len(counts)]
            )
            
            # Enhance appearance
            plt.setp(autotexts, size=10, weight='bold')
            
            # Add legend with counts
            legend_labels = [f'{label} ({count})' for label, count in zip(labels, counts)]
            ax.legend(wedges, legend_labels, loc='best', bbox_to_anchor=(1, 0, 0.5, 1))
            
        else:  # 'bar'
            # Create bar chart
            bars = ax.bar(labels, counts, color=self.default_colors[:len(counts)])
            
            # Add count labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{height}', ha='center', va='bottom')
            
            # Configure axis
            ax.set_xlabel('Virus Subtype', fontsize=12)
            ax.set_ylabel('Number of Cases', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            
            # Add grid
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Ensure y-axis starts at zero
            ax.set_ylim(bottom=0)
        
        # Set title
        if title:
            ax.set_title(title, fontsize=14)
        else:
            ax.set_title(f'Virus Subtype Distribution - Last {days} Days', fontsize=14)
        
        # Make layout tight
        fig.tight_layout()
        
        # Convert to base64 image
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # Find dominant subtype
        dominant_subtype = max(subtype_counts.items(), key=lambda x: x[1]) if subtype_counts else (None, 0)
        
        return {
            "base64_image": img_base64,
            "subtype_counts": subtype_counts,
            "metadata": {
                "period_days": days,
                "chart_type": chart_type,
                "total_cases": sum(counts),
                "subtype_count": len(subtype_counts),
                "dominant_subtype": dominant_subtype[0],
                "dominant_subtype_count": dominant_subtype[1],
                "dominant_subtype_percentage": (dominant_subtype[1] / sum(counts)) * 100 if sum(counts) > 0 else 0
            }
        }
    
    def create_surveillance_effectiveness_chart(self,
                                             surveillance_events: List[SurveillanceEvent],
                                             days: int = 30,
                                             title: Optional[str] = None,
                                             by_site_type: bool = True,
                                             width: int = 800,
                                             height: int = 500) -> Dict[str, Any]:
        """
        Create a chart showing surveillance effectiveness over time.
        
        Args:
            surveillance_events: List of surveillance events
            days: Number of days to include
            title: Optional title for the chart
            by_site_type: Whether to break down by site type
            width: Width of the chart in pixels
            height: Height of the chart in pixels
            
        Returns:
            Dictionary with chart data:
                - base64_image: Base64-encoded PNG image
                - total_events: Total number of surveillance events
                - metadata: Additional chart metadata
        """
        # Define time period
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = today - timedelta(days=days)
        
        # Create date range
        date_range = [today - timedelta(days=i) for i in range(days)]
        date_range.reverse()  # Earliest first
        
        # Filter events to time period
        filtered_events = []
        for event in surveillance_events:
            if not hasattr(event, 'event_date'):
                continue
                
            event_date = datetime.fromisoformat(event.event_date)
            if event_date >= start_date:
                filtered_events.append(event)
        
        if not filtered_events:
            logger.warning(f"No surveillance events in the last {days} days")
            return {
                "error": f"No surveillance events in the last {days} days",
                "total_events": 0
            }
        
        # Prepare figure
        figsize = (width / self.default_dpi, height / self.default_dpi)
        fig, ax = plt.subplots(figsize=figsize, dpi=self.default_dpi)
        
        # Count events by date
        if by_site_type:
            # Get unique site types
            site_types = set()
            for event in filtered_events:
                site_type = getattr(event, 'site_type', 'unknown')
                site_types.add(site_type)
            
            # Prepare counts by date and site type
            site_type_counts = {}
            site_type_positives = {}
            
            for site_type in site_types:
                site_type_counts[site_type] = {d.date(): 0 for d in date_range}
                site_type_positives[site_type] = {d.date(): 0 for d in date_range}
            
            # Count events and positives
            for event in filtered_events:
                event_date = datetime.fromisoformat(event.event_date)
                event_day = event_date.date()
                
                site_type = getattr(event, 'site_type', 'unknown')
                is_positive = getattr(event, 'is_positive', False)
                
                if event_day in site_type_counts[site_type]:
                    site_type_counts[site_type][event_day] += 1
                    if is_positive:
                        site_type_positives[site_type][event_day] += 1
            
            # Create stacked bar chart for total events
            bottom = np.zeros(len(date_range))
            x = [d.date() for d in date_range]
            
            site_type_handles = []
            site_type_labels = []
            
            for i, site_type in enumerate(site_types):
                y = [site_type_counts[site_type][d] for d in x]
                handle = ax.bar(x, y, bottom=bottom, label=f"{site_type}",
                               color=self.default_colors[i % len(self.default_colors)],
                               alpha=0.7)
                bottom += np.array(y)
                
                site_type_handles.append(handle)
                site_type_labels.append(site_type)
            
            total_events = int(sum(bottom))
            
            # Add positivity rate line
            ax2 = ax.twinx()
            
            # Calculate overall positivity rate by date
            positivity_rates = []
            for i, d in enumerate(x):
                total_events_day = sum(site_type_counts[st][d] for st in site_types)
                total_positives_day = sum(site_type_positives[st][d] for st in site_types)
                
                if total_events_day > 0:
                    rate = total_positives_day / total_events_day
                else:
                    rate = 0
                
                positivity_rates.append(rate)
            
            # Plot positivity rate line
            line = ax2.plot(x, positivity_rates, color='red', marker='o', 
                         linestyle='-', linewidth=2, label='Positivity Rate')
            
            # Configure second y-axis
            ax2.set_ylabel('Positivity Rate', color='red', fontsize=12)
            ax2.tick_params(axis='y', colors='red')
            ax2.set_ylim(0, 1)  # 0-100%
            ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
            ax2.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
            
            # Add combined legend
            all_handles = site_type_handles + line
            all_labels = site_type_labels + ['Positivity Rate']
            ax.legend(all_handles, all_labels, loc='upper left')
            
        else:
            # Simple counts by date
            date_counts = {d.date(): 0 for d in date_range}
            date_positives = {d.date(): 0 for d in date_range}
            
            for event in filtered_events:
                event_date = datetime.fromisoformat(event.event_date)
                event_day = event_date.date()
                is_positive = getattr(event, 'is_positive', False)
                
                if event_day in date_counts:
                    date_counts[event_day] += 1
                    if is_positive:
                        date_positives[event_day] += 1
            
            # Plot bar chart for events
            x = list(date_counts.keys())
            y = [date_counts[d] for d in x]
            ax.bar(x, y, color='steelblue', alpha=0.7, label='Surveillance Events')
            
            total_events = sum(y)
            
            # Add positivity rate line
            ax2 = ax.twinx()
            
            # Calculate positivity rates
            positivity_rates = []
            for d in x:
                events = date_counts[d]
                positives = date_positives[d]
                
                if events > 0:
                    rate = positives / events
                else:
                    rate = 0
                
                positivity_rates.append(rate)
            
            # Plot positivity rate line
            ax2.plot(x, positivity_rates, color='red', marker='o', 
                   linestyle='-', linewidth=2, label='Positivity Rate')
            
            # Configure second y-axis
            ax2.set_ylabel('Positivity Rate', color='red', fontsize=12)
            ax2.tick_params(axis='y', colors='red')
            ax2.set_ylim(0, 1)  # 0-100%
            ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
            ax2.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
            
            # Add legend
            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines + lines2, labels + labels2, loc='upper left')
        
        # Configure primary axis
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Number of Surveillance Events', fontsize=12)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        if len(date_range) > 14:
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))  # Every Monday
        else:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Every day
            
        plt.xticks(rotation=45)
        
        # Ensure y-axis starts at zero
        ax.set_ylim(bottom=0)
        
        # Set title
        if title:
            ax.set_title(title, fontsize=14)
        else:
            ax.set_title(f'Surveillance Effectiveness - Last {days} Days', fontsize=14)
        
        # Add grid
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Make layout tight
        fig.tight_layout()
        
        # Convert to base64 image
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        # Calculate overall positivity rate
        total_positives = 0
        for event in filtered_events:
            if getattr(event, 'is_positive', False):
                total_positives += 1
                
        overall_positivity = total_positives / total_events if total_events > 0 else 0
        
        return {
            "base64_image": img_base64,
            "total_events": total_events,
            "metadata": {
                "period_days": days,
                "by_site_type": by_site_type,
                "total_positives": total_positives,
                "overall_positivity_rate": overall_positivity,
                "site_types": list(site_types) if by_site_type else None
            }
        }