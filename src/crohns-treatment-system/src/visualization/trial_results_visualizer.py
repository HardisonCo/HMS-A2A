#!/usr/bin/env python3
"""
Trial Results Visualizer for Crohn's Disease Treatment System

This module provides visualization capabilities for the adaptive clinical trial
results, including treatment effectiveness, patient outcomes, biomarker correlations,
and adaptive trial decisions.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Union, Tuple, TextIO
from datetime import datetime
import io
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('hms.visualization.trial-results-visualizer')

class TrialResultsVisualizer:
    """
    Visualizes results from adaptive clinical trials for Crohn's disease,
    providing insights into treatment effectiveness, biomarker correlations,
    and adaptive trial decisions.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the visualizer with optional configuration.
        
        Args:
            config: Configuration options for the visualizer
        """
        self.config = config or {}
        self.figsize = self.config.get('figsize', (10, 6))
        self.dpi = self.config.get('dpi', 100)
        self.style = self.config.get('style', 'seaborn-whitegrid')
        self.palette = self.config.get('palette', 'Set2')
        self.theme = self.config.get('theme', 'light')
        
        # Set up matplotlib style
        plt.style.use(self.style)
        sns.set_palette(self.palette)
        
        # Set theme colors
        if self.theme == 'dark':
            plt.rcParams['figure.facecolor'] = '#2E3440'
            plt.rcParams['axes.facecolor'] = '#3B4252'
            plt.rcParams['text.color'] = '#ECEFF4'
            plt.rcParams['axes.labelcolor'] = '#E5E9F0'
            plt.rcParams['xtick.color'] = '#E5E9F0'
            plt.rcParams['ytick.color'] = '#E5E9F0'
            plt.rcParams['axes.edgecolor'] = '#4C566A'
            plt.rcParams['grid.color'] = '#4C566A'
        else:
            # Default light theme
            plt.rcParams['figure.facecolor'] = 'white'
            plt.rcParams['axes.facecolor'] = 'white'
        
        logger.info("Trial results visualizer initialized")
    
    def create_trial_summary_dashboard(self, trial_results: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a comprehensive dashboard of visualizations for trial results.
        
        Args:
            trial_results: The trial results dictionary
            
        Returns:
            Dictionary mapping visualization names to base64-encoded PNG images
        """
        logger.info(f"Creating dashboard for trial {trial_results.get('trial_id', 'unknown')}")
        
        # Prepare data
        trial_id = trial_results.get('trial_id', 'unknown')
        outcomes = trial_results.get('patient_outcomes', [])
        adaptations = trial_results.get('adaptations', [])
        
        if not outcomes:
            logger.warning("No patient outcomes found in trial results")
            return {"error": "No patient outcomes found in trial results"}
        
        # Convert outcomes to DataFrame
        df = pd.DataFrame(outcomes)
        
        # Create visualizations
        visualizations = {}
        
        try:
            # Response by treatment arm
            visualizations['response_by_arm'] = self.visualize_response_by_arm(df)
            
            # Response distribution
            visualizations['response_distribution'] = self.visualize_response_distribution(df)
            
            # Adverse events
            if 'adverse_events' in df.columns:
                visualizations['adverse_events'] = self.visualize_adverse_events(df)
            
            # Biomarker correlation if available
            if 'biomarkers' in df.columns or any(col.startswith('biomarker_') for col in df.columns):
                visualizations['biomarker_correlation'] = self.visualize_biomarker_correlation(df)
            
            # Adaptation timeline
            if adaptations:
                visualizations['adaptation_timeline'] = self.visualize_adaptation_timeline(adaptations)
            
            # Trial summary
            visualizations['trial_summary'] = self.visualize_trial_summary(trial_results)
            
            logger.info(f"Created {len(visualizations)} visualizations for dashboard")
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
            return {"error": f"Error creating visualizations: {e}"}
    
    def visualize_response_by_arm(self, df: pd.DataFrame) -> str:
        """
        Visualize patient response by treatment arm.
        
        Args:
            df: DataFrame with patient outcomes
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=self.figsize, dpi=self.dpi)
        
        # Check if we have the necessary columns
        if 'arm' not in df.columns or 'response' not in df.columns:
            plt.text(0.5, 0.5, "Missing required columns 'arm' or 'response'", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        # Calculate mean response and standard error by arm
        arm_stats = df.groupby('arm')['response'].agg(['mean', 'sem', 'count']).reset_index()
        
        # Create bar plot
        ax = sns.barplot(x='arm', y='mean', data=arm_stats, palette=self.palette)
        
        # Add error bars
        for i, row in arm_stats.iterrows():
            ax.errorbar(i, row['mean'], yerr=row['sem'], fmt='none', color='black', capsize=5)
        
        # Add count labels
        for i, row in arm_stats.iterrows():
            ax.text(i, row['mean'] + row['sem'] + 0.02, f"n={int(row['count'])}", 
                   ha='center', va='bottom', fontsize=10)
        
        # Add mean value labels
        for i, row in arm_stats.iterrows():
            ax.text(i, row['mean'] / 2, f"{row['mean']:.2f}", 
                   ha='center', va='center', fontsize=10, color='white', fontweight='bold')
        
        # Set labels and title
        plt.xlabel('Treatment Arm')
        plt.ylabel('Mean Response')
        plt.title('Patient Response by Treatment Arm')
        plt.ylim(0, 1.1)  # Assuming response is normalized to 0-1
        
        # Return the figure as base64-encoded PNG
        return self._figure_to_base64()
    
    def visualize_response_distribution(self, df: pd.DataFrame) -> str:
        """
        Visualize distribution of patient responses.
        
        Args:
            df: DataFrame with patient outcomes
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=self.figsize, dpi=self.dpi)
        
        # Check if we have the necessary columns
        if 'response' not in df.columns:
            plt.text(0.5, 0.5, "Missing required column 'response'", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        # Create histogram with KDE
        ax = sns.histplot(df['response'], kde=True, bins=15)
        
        # Add vertical line for mean
        mean_response = df['response'].mean()
        plt.axvline(mean_response, color='red', linestyle='dashed', linewidth=1)
        plt.text(mean_response, plt.gca().get_ylim()[1]*0.9, 
                f' Mean: {mean_response:.2f}', color='red')
        
        # Set labels and title
        plt.xlabel('Response Value')
        plt.ylabel('Count')
        plt.title('Distribution of Patient Responses')
        
        # Return the figure as base64-encoded PNG
        return self._figure_to_base64()
    
    def visualize_adverse_events(self, df: pd.DataFrame) -> str:
        """
        Visualize adverse events by treatment arm.
        
        Args:
            df: DataFrame with patient outcomes
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=self.figsize, dpi=self.dpi)
        
        # Check if we have the necessary columns
        if 'adverse_events' not in df.columns or 'arm' not in df.columns:
            plt.text(0.5, 0.5, "Missing required columns 'adverse_events' or 'arm'", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        # Extract and count adverse events
        all_events = []
        for events in df['adverse_events']:
            if isinstance(events, list) and events:
                all_events.extend(events)
        
        if not all_events:
            plt.text(0.5, 0.5, "No adverse events reported", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        # Count events
        event_counts = pd.Series(all_events).value_counts()
        
        # Create bar plot
        ax = sns.barplot(x=event_counts.index, y=event_counts.values, palette=self.palette)
        
        # Add count labels
        for i, count in enumerate(event_counts.values):
            ax.text(i, count + 0.1, str(count), ha='center', va='bottom', fontsize=10)
        
        # Set labels and title
        plt.xlabel('Adverse Event')
        plt.ylabel('Count')
        plt.title('Frequency of Adverse Events')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Return the figure as base64-encoded PNG
        return self._figure_to_base64()
    
    def visualize_biomarker_correlation(self, df: pd.DataFrame) -> str:
        """
        Visualize correlation between biomarkers and response.
        
        Args:
            df: DataFrame with patient outcomes and biomarkers
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=self.figsize, dpi=self.dpi)
        
        # Check if we have biomarker columns and response
        biomarker_cols = [col for col in df.columns if col.startswith('biomarker_')]
        
        if not biomarker_cols and 'biomarkers' not in df.columns:
            plt.text(0.5, 0.5, "No biomarker data found", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        if 'response' not in df.columns:
            plt.text(0.5, 0.5, "Missing required column 'response'", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        # If we have a 'biomarkers' column but no biomarker_* columns, extract them
        if not biomarker_cols and 'biomarkers' in df.columns:
            # This assumes biomarkers is a dict-like object with numeric values
            try:
                biomarker_df = pd.DataFrame(df['biomarkers'].tolist())
                # Prefix columns with 'biomarker_'
                biomarker_df = biomarker_df.add_prefix('biomarker_')
                # Join with original df
                df = pd.concat([df, biomarker_df], axis=1)
                biomarker_cols = [col for col in df.columns if col.startswith('biomarker_')]
            except Exception as e:
                logger.error(f"Error extracting biomarkers: {e}")
                plt.text(0.5, 0.5, "Error extracting biomarker data", 
                        ha='center', va='center', fontsize=12)
                return self._figure_to_base64()
        
        # Ensure biomarker columns contain numeric data
        for col in biomarker_cols:
            if not pd.api.types.is_numeric_dtype(df[col]):
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate correlations with response
        correlations = []
        for col in biomarker_cols:
            corr = df[['response', col]].corr().iloc[0, 1]
            if not pd.isna(corr):  # Skip NaN correlations
                correlations.append({
                    'biomarker': col.replace('biomarker_', ''),
                    'correlation': corr
                })
        
        if not correlations:
            plt.text(0.5, 0.5, "No valid correlations found", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        # Convert to DataFrame and sort
        corr_df = pd.DataFrame(correlations)
        corr_df = corr_df.sort_values('correlation', ascending=False)
        
        # Create bar plot
        colors = ['green' if x > 0 else 'red' for x in corr_df['correlation']]
        ax = sns.barplot(x='biomarker', y='correlation', data=corr_df, palette=colors)
        
        # Add correlation values
        for i, row in corr_df.reset_index().iterrows():
            va = 'bottom' if row['correlation'] >= 0 else 'top'
            ax.text(i, row['correlation'] + (0.02 if row['correlation'] >= 0 else -0.02), 
                   f"{row['correlation']:.2f}", ha='center', va=va, fontsize=9)
        
        # Set labels and title
        plt.xlabel('Biomarker')
        plt.ylabel('Correlation with Response')
        plt.title('Biomarker Correlation with Treatment Response')
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Return the figure as base64-encoded PNG
        return self._figure_to_base64()
    
    def visualize_adaptation_timeline(self, adaptations: List[Dict[str, Any]]) -> str:
        """
        Visualize timeline of adaptive trial decisions.
        
        Args:
            adaptations: List of adaptation decisions
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=self.figsize, dpi=self.dpi)
        
        if not adaptations:
            plt.text(0.5, 0.5, "No adaptation data found", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        # Process adaptations to ensure they have timestamps
        adaptation_data = []
        for i, adaptation in enumerate(adaptations):
            # Use timestamp if available, otherwise use the index as x position
            timestamp = adaptation.get('timestamp')
            if timestamp:
                try:
                    # Convert to datetime if it's a string
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except Exception:
                    timestamp = i
            else:
                timestamp = i
            
            adaptation_data.append({
                'timestamp': timestamp,
                'type': adaptation.get('type', 'unknown'),
                'details': str(adaptation.get('parameters', ''))
            })
        
        # Sort by timestamp if they're datetimes
        if all(isinstance(d['timestamp'], datetime) for d in adaptation_data):
            adaptation_data.sort(key=lambda x: x['timestamp'])
            # Convert to days since first adaptation for plotting
            first_date = adaptation_data[0]['timestamp']
            for data in adaptation_data:
                data['days'] = (data['timestamp'] - first_date).days
            x_values = [d['days'] for d in adaptation_data]
            x_label = 'Days Since First Adaptation'
        else:
            # Use indices for non-datetime timestamps
            x_values = list(range(len(adaptation_data)))
            x_label = 'Adaptation Index'
        
        # Get adaptation types
        adaptation_types = [d['type'] for d in adaptation_data]
        
        # Create timeline plot
        plt.figure(figsize=(10, 6))
        
        # Plot points
        for i, (x, adaptation_type) in enumerate(zip(x_values, adaptation_types)):
            plt.scatter(x, 0, s=100, 
                       color=plt.cm.tab10(hash(adaptation_type) % 10), 
                       zorder=2)
            plt.text(x, 0.1, adaptation_type, ha='center', rotation=45, fontsize=10)
            plt.text(x, -0.1, adaptation_data[i]['details'], ha='center', rotation=-45, fontsize=8)
        
        # Connect points with line
        plt.plot(x_values, [0] * len(x_values), 'k-', alpha=0.3, zorder=1)
        
        # Set up the plot
        plt.yticks([])  # Hide y-axis
        plt.xlabel(x_label)
        plt.title('Timeline of Adaptive Trial Decisions')
        plt.tight_layout()
        
        # Return the figure as base64-encoded PNG
        return self._figure_to_base64()
    
    def visualize_trial_summary(self, trial_results: Dict[str, Any]) -> str:
        """
        Create a summary visualization of trial results.
        
        Args:
            trial_results: Trial results dictionary
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=self.figsize, dpi=self.dpi)
        
        # Extract key information
        trial_id = trial_results.get('trial_id', 'Unknown')
        status = trial_results.get('status', 'Unknown')
        outcomes = trial_results.get('patient_outcomes', [])
        adaptations = trial_results.get('adaptations', [])
        
        # Create a table with summary information
        data = [
            ['Trial ID', trial_id],
            ['Status', status],
            ['Total Patients', len(outcomes)],
            ['Adaptations', len(adaptations)],
        ]
        
        # Add mean response if available
        if outcomes and all('response' in o for o in outcomes):
            mean_response = sum(o['response'] for o in outcomes) / len(outcomes)
            data.append(['Mean Response', f"{mean_response:.2f}"])
        
        # Add adverse event count if available
        adverse_events_count = 0
        for outcome in outcomes:
            events = outcome.get('adverse_events', [])
            if isinstance(events, list):
                adverse_events_count += len(events)
        data.append(['Adverse Events', adverse_events_count])
        
        # Create table
        table = plt.table(
            cellText=data,
            colWidths=[0.3, 0.5],
            loc='center',
            cellLoc='center',
        )
        
        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 1.5)
        
        # Hide axes
        plt.axis('off')
        
        # Set title
        plt.title('Trial Summary', fontsize=16, pad=20)
        
        # Return the figure as base64-encoded PNG
        return self._figure_to_base64()
    
    def visualize_patient_specific_results(self, patient_data: Dict[str, Any], 
                                          treatment_plan: Dict[str, Any]) -> Dict[str, str]:
        """
        Create visualizations for patient-specific results and treatment plans.
        
        Args:
            patient_data: Patient profile data
            treatment_plan: Optimized treatment plan
            
        Returns:
            Dictionary mapping visualization names to base64-encoded PNG images
        """
        logger.info(f"Creating visualizations for patient {patient_data.get('patient_id', 'unknown')}")
        
        visualizations = {}
        
        try:
            # Treatment plan summary
            visualizations['treatment_plan'] = self.visualize_treatment_plan(treatment_plan)
            
            # Biomarker influence
            visualizations['biomarker_influence'] = self.visualize_biomarker_influence(
                patient_data, treatment_plan
            )
            
            # Confidence breakdown
            if 'confidence_scores' in treatment_plan:
                visualizations['confidence_breakdown'] = self.visualize_confidence_breakdown(
                    treatment_plan['confidence_scores']
                )
            
            # Treatment comparison
            if 'alternatives' in treatment_plan:
                visualizations['treatment_comparison'] = self.visualize_treatment_comparison(
                    treatment_plan['alternatives']
                )
            
            logger.info(f"Created {len(visualizations)} patient-specific visualizations")
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating patient-specific visualizations: {e}")
            return {"error": f"Error creating visualizations: {e}"}
    
    def visualize_treatment_plan(self, treatment_plan: Dict[str, Any]) -> str:
        """
        Visualize the treatment plan for a patient.
        
        Args:
            treatment_plan: Optimized treatment plan
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=self.figsize, dpi=self.dpi)
        
        medications = treatment_plan.get('treatment_plan', [])
        if not medications:
            plt.text(0.5, 0.5, "No medications in treatment plan", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        # Create a table with medication details
        rows = []
        for med in medications:
            dosage = f"{med.get('dosage', '')} {med.get('unit', '')}"
            frequency = med.get('frequency', '')
            duration = f"{med.get('duration', '')} days"
            rows.append([med.get('medication', ''), dosage, frequency, duration])
        
        # Add header row
        rows.insert(0, ['Medication', 'Dosage', 'Frequency', 'Duration'])
        
        # Create table
        table = plt.table(
            cellText=rows,
            colWidths=[0.3, 0.2, 0.2, 0.2],
            loc='center',
            cellLoc='center',
        )
        
        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 1.5)
        
        # Style header row
        for i in range(len(rows[0])):
            cell = table[(0, i)]
            cell.set_fontsize(12)
            cell.set_text_props(fontweight='bold')
            cell.set_facecolor('#e6e6e6')
        
        # Hide axes
        plt.axis('off')
        
        # Set title
        fitness = treatment_plan.get('fitness', 0)
        plt.title(f'Optimized Treatment Plan (Fitness: {fitness:.2f})', fontsize=14, pad=20)
        
        # Return the figure as base64-encoded PNG
        return self._figure_to_base64()
    
    def visualize_biomarker_influence(self, patient_data: Dict[str, Any], 
                                     treatment_plan: Dict[str, Any]) -> str:
        """
        Visualize the influence of biomarkers on treatment selection.
        
        Args:
            patient_data: Patient profile data
            treatment_plan: Optimized treatment plan
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=self.figsize, dpi=self.dpi)
        
        # Try to extract biomarker influences
        influences = treatment_plan.get('biomarker_influences', {})
        
        if not influences:
            # If no explicit influences, check for biomarker_weights
            influences = treatment_plan.get('biomarker_weights', {})
        
        if not influences:
            # If still no influences, try to extract from patient data
            biomarkers = patient_data.get('biomarkers', {})
            genetic_markers = biomarkers.get('genetic_markers', [])
            
            # Create dummy influences based on genetic markers
            if genetic_markers:
                influences = {}
                for marker in genetic_markers:
                    gene = marker.get('gene', '')
                    variant = marker.get('variant', '')
                    if gene and variant == 'variant':
                        influences[gene] = 0.5  # Dummy value
        
        if not influences:
            plt.text(0.5, 0.5, "No biomarker influence data available", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        # Convert to DataFrame for plotting
        influence_data = []
        for biomarker, value in influences.items():
            influence_data.append({
                'biomarker': biomarker,
                'influence': value
            })
        
        if not influence_data:
            plt.text(0.5, 0.5, "No valid biomarker influence data", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        df = pd.DataFrame(influence_data)
        
        # Sort by influence value
        df = df.sort_values('influence', ascending=False)
        
        # Create horizontal bar chart
        ax = sns.barplot(x='influence', y='biomarker', data=df, palette=self.palette)
        
        # Add value labels
        for i, row in df.reset_index().iterrows():
            ax.text(row['influence'] + 0.02, i, f"{row['influence']:.2f}", 
                   va='center', fontsize=10)
        
        # Set labels and title
        plt.xlabel('Influence Score')
        plt.ylabel('Biomarker')
        plt.title('Biomarker Influence on Treatment Selection')
        plt.xlim(0, df['influence'].max() * 1.2)  # Add some padding for labels
        
        # Return the figure as base64-encoded PNG
        return self._figure_to_base64()
    
    def visualize_confidence_breakdown(self, confidence_scores: Dict[str, float]) -> str:
        """
        Visualize the breakdown of confidence scores for a treatment plan.
        
        Args:
            confidence_scores: Confidence score dictionary
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=self.figsize, dpi=self.dpi)
        
        if not confidence_scores:
            plt.text(0.5, 0.5, "No confidence score data available", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        # Remove overall score for component breakdown
        component_scores = {k: v for k, v in confidence_scores.items() if k != 'overall'}
        
        if not component_scores:
            plt.text(0.5, 0.5, "No confidence component data available", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        # Convert to DataFrame for plotting
        score_data = []
        for component, score in component_scores.items():
            score_data.append({
                'component': component.capitalize(),
                'score': score
            })
        
        df = pd.DataFrame(score_data)
        
        # Sort by score value
        df = df.sort_values('score', ascending=False)
        
        # Create bar chart
        ax = sns.barplot(x='component', y='score', data=df, palette=self.palette)
        
        # Add value labels
        for i, row in df.reset_index().iterrows():
            ax.text(i, row['score'] + 0.02, f"{row['score']:.2f}", 
                   ha='center', va='bottom', fontsize=10)
        
        # Set labels and title
        plt.xlabel('Confidence Component')
        plt.ylabel('Score')
        overall = confidence_scores.get('overall', 0)
        plt.title(f'Treatment Plan Confidence Breakdown (Overall: {overall:.2f})')
        plt.ylim(0, 1.1)  # Assuming scores are normalized to 0-1
        
        # Add horizontal line for overall confidence
        plt.axhline(y=overall, color='red', linestyle='dashed', linewidth=1, alpha=0.7)
        
        # Return the figure as base64-encoded PNG
        return self._figure_to_base64()
    
    def visualize_treatment_comparison(self, alternatives: List[Dict[str, Any]]) -> str:
        """
        Visualize comparison of alternative treatment plans.
        
        Args:
            alternatives: List of alternative treatment plans
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=self.figsize, dpi=self.dpi)
        
        if not alternatives:
            plt.text(0.5, 0.5, "No alternative treatment data available", 
                    ha='center', va='center', fontsize=12)
            return self._figure_to_base64()
        
        # Extract fitness scores and descriptions
        comparison_data = []
        for alt in alternatives:
            description = []
            for med in alt.get('treatment_plan', []):
                med_name = med.get('medication', '')
                dosage = med.get('dosage', '')
                unit = med.get('unit', '')
                description.append(f"{med_name} {dosage}{unit}")
            
            comparison_data.append({
                'description': ", ".join(description) or "Unknown",
                'fitness': alt.get('fitness', 0)
            })
        
        # Create a column for the primary treatment (should be first)
        comparison_data[0]['type'] = 'Primary'
        for i in range(1, len(comparison_data)):
            comparison_data[i]['type'] = 'Alternative'
        
        # Convert to DataFrame
        df = pd.DataFrame(comparison_data)
        
        # Sort by fitness
        df = df.sort_values('fitness', ascending=False)
        
        # Create bar chart with hue for primary vs alternatives
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x='description', y='fitness', hue='type', data=df, 
                        palette={'Primary': 'green', 'Alternative': 'blue'})
        
        # Add value labels
        for i, row in df.reset_index().iterrows():
            ax.text(i, row['fitness'] + 0.02, f"{row['fitness']:.2f}", 
                   ha='center', va='bottom', fontsize=10)
        
        # Set labels and title
        plt.xlabel('Treatment Description')
        plt.ylabel('Fitness Score')
        plt.title('Comparison of Alternative Treatment Plans')
        plt.ylim(0, 1.1)  # Assuming fitness is normalized to 0-1
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='')
        plt.tight_layout()
        
        # Return the figure as base64-encoded PNG
        return self._figure_to_base64()
    
    def _figure_to_base64(self) -> str:
        """
        Convert the current matplotlib figure to a base64-encoded PNG.
        
        Returns:
            Base64-encoded PNG image
        """
        # Save the figure to a PNG in memory
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        
        # Encode the PNG as base64
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        return img_str
    
    def save_visualizations(self, visualizations: Dict[str, str], output_dir: str) -> None:
        """
        Save visualizations to files.
        
        Args:
            visualizations: Dictionary mapping visualization names to base64-encoded images
            output_dir: Directory to save the files
        """
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save each visualization
        for name, img_data in visualizations.items():
            file_path = os.path.join(output_dir, f"{name}.png")
            
            # Decode base64 to binary
            img_binary = base64.b64decode(img_data)
            
            # Write to file
            with open(file_path, 'wb') as f:
                f.write(img_binary)
            
            logger.info(f"Saved visualization '{name}' to {file_path}")
    
    def generate_html_report(self, trial_results: Dict[str, Any], 
                            output_file: str) -> None:
        """
        Generate an HTML report with all visualizations.
        
        Args:
            trial_results: Trial results dictionary
            output_file: Path to output HTML file
        """
        logger.info(f"Generating HTML report for trial {trial_results.get('trial_id', 'unknown')}")
        
        # Generate visualizations
        visualizations = self.create_trial_summary_dashboard(trial_results)
        
        if "error" in visualizations:
            logger.error(f"Error generating visualizations: {visualizations['error']}")
            return
        
        # Create HTML content
        html = self._create_html_report(trial_results, visualizations)
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(html)
        
        logger.info(f"HTML report saved to {output_file}")
    
    def _create_html_report(self, trial_results: Dict[str, Any], 
                           visualizations: Dict[str, str]) -> str:
        """
        Create the HTML content for the report.
        
        Args:
            trial_results: Trial results dictionary
            visualizations: Dictionary mapping visualization names to base64-encoded images
            
        Returns:
            HTML content as string
        """
        trial_id = trial_results.get('trial_id', 'unknown')
        status = trial_results.get('status', 'unknown')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create HTML header and style
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Trial Results: {trial_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f9f9f9;
            color: #333;
        }}
        .header {{
            background-color: #4b6cb7;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .section {{
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .visualization {{
            text-align: center;
            margin: 20px 0;
        }}
        h1, h2, h3 {{
            color: #4b6cb7;
        }}
        .status {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
        }}
        .status-completed {{
            background-color: #4CAF50;
            color: white;
        }}
        .status-error, .status-failed {{
            background-color: #f44336;
            color: white;
        }}
        .status-in-progress {{
            background-color: #2196F3;
            color: white;
        }}
        .metadata {{
            color: #666;
            font-style: italic;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Adaptive Clinical Trial Results</h1>
        <p>Trial ID: {trial_id}</p>
        <p>Status: <span class="status status-{status.lower()}">{status}</span></p>
        <p class="metadata">Generated on {timestamp}</p>
    </div>
"""
        
        # Add summary section
        html += f"""
    <div class="section">
        <h2>Trial Summary</h2>
"""
        
        if 'trial_summary' in visualizations:
            html += f"""
        <div class="visualization">
            <img src="data:image/png;base64,{visualizations['trial_summary']}" alt="Trial Summary">
        </div>
"""
        
        # Add patient outcomes table
        outcomes = trial_results.get('patient_outcomes', [])
        if outcomes:
            html += f"""
        <h3>Patient Outcomes</h3>
        <table>
            <tr>
                <th>Patient ID</th>
                <th>Treatment Arm</th>
                <th>Response</th>
                <th>Adverse Events</th>
            </tr>
"""
            
            for outcome in outcomes:
                patient_id = outcome.get('patient_id', 'Unknown')
                arm = outcome.get('arm', 'Unknown')
                response = outcome.get('response', 0)
                events = outcome.get('adverse_events', [])
                events_str = ", ".join(events) if events else "None"
                
                html += f"""
            <tr>
                <td>{patient_id}</td>
                <td>{arm}</td>
                <td>{response:.2f}</td>
                <td>{events_str}</td>
            </tr>
"""
            
            html += """
        </table>
"""
        
        html += """
    </div>
"""
        
        # Add response analysis section
        html += """
    <div class="section">
        <h2>Response Analysis</h2>
"""
        
        if 'response_by_arm' in visualizations:
            html += f"""
        <div class="visualization">
            <h3>Response by Treatment Arm</h3>
            <img src="data:image/png;base64,{visualizations['response_by_arm']}" alt="Response by Treatment Arm">
        </div>
"""
        
        if 'response_distribution' in visualizations:
            html += f"""
        <div class="visualization">
            <h3>Response Distribution</h3>
            <img src="data:image/png;base64,{visualizations['response_distribution']}" alt="Response Distribution">
        </div>
"""
        
        html += """
    </div>
"""
        
        # Add biomarker analysis section
        if 'biomarker_correlation' in visualizations:
            html += f"""
    <div class="section">
        <h2>Biomarker Analysis</h2>
        <div class="visualization">
            <h3>Biomarker Correlation with Response</h3>
            <img src="data:image/png;base64,{visualizations['biomarker_correlation']}" alt="Biomarker Correlation">
        </div>
    </div>
"""
        
        # Add adaptation analysis section
        if 'adaptation_timeline' in visualizations:
            html += f"""
    <div class="section">
        <h2>Adaptation Analysis</h2>
        <div class="visualization">
            <h3>Adaptation Timeline</h3>
            <img src="data:image/png;base64,{visualizations['adaptation_timeline']}" alt="Adaptation Timeline">
        </div>
"""
            
            # Add adaptations table
            adaptations = trial_results.get('adaptations', [])
            if adaptations:
                html += f"""
        <h3>Adaptation Details</h3>
        <table>
            <tr>
                <th>Type</th>
                <th>Trigger</th>
                <th>Parameters</th>
            </tr>
"""
                
                for adaptation in adaptations:
                    adaptation_type = adaptation.get('type', 'Unknown')
                    trigger = adaptation.get('triggerCondition', 'Unknown')
                    parameters = str(adaptation.get('parameters', {}))
                    
                    html += f"""
            <tr>
                <td>{adaptation_type}</td>
                <td>{trigger}</td>
                <td>{parameters}</td>
            </tr>
"""
                
                html += """
        </table>
"""
            
            html += """
    </div>
"""
        
        # Add adverse events section
        if 'adverse_events' in visualizations:
            html += f"""
    <div class="section">
        <h2>Safety Analysis</h2>
        <div class="visualization">
            <h3>Adverse Events</h3>
            <img src="data:image/png;base64,{visualizations['adverse_events']}" alt="Adverse Events">
        </div>
    </div>
"""
        
        # Add footer
        html += """
    <div class="section">
        <p class="metadata">Generated by Crohn's Disease Treatment System</p>
    </div>
</body>
</html>
"""
        
        return html

# Simple test function
def main():
    """Test the trial results visualizer"""
    # Create a visualizer
    visualizer = TrialResultsVisualizer()
    
    # Example trial results (would normally come from the adaptive trial engine)
    trial_results = {
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
    
    # Generate visualizations
    visualizations = visualizer.create_trial_summary_dashboard(trial_results)
    
    # Save visualizations to files
    os.makedirs("test_output", exist_ok=True)
    visualizer.save_visualizations(visualizations, "test_output")
    
    # Generate HTML report
    visualizer.generate_html_report(trial_results, "test_output/trial_report.html")
    
    print("Visualizations and report generated in 'test_output' directory")

if __name__ == "__main__":
    main()