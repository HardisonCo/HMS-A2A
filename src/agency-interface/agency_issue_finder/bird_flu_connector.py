#!/usr/bin/env python3
"""
Bird Flu Research Connector

A specialized connector that interfaces with the APHIS bird flu implementation
and provides structured access to relevant research and implementation data.
This component is used by the Codex CLI when operating in bird flu response mode.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class BirdFluConnectorException(Exception):
    """Custom exception for bird flu connector errors."""
    pass

class BirdFluConnector:
    """
    Bird Flu Research Connector main class.
    Provides structured access to bird flu research and implementation data.
    """
    
    def __init__(self, base_path: str) -> None:
        """
        Initialize the bird flu connector.
        
        Args:
            base_path: Base path to the bird flu implementation files
        """
        self.base_path = base_path
        self.implementation_plan_path = os.path.join(base_path, "..", "..", "..", "..", "APHIS-BIRD-FLU-IMPLEMENTATION-PLAN.md")
        self.progress_tracking_path = os.path.join(base_path, "..", "..", "..", "..", "APHIS-PROGRESS-TRACKING.md")
        self.implementation_dir = os.path.join(base_path, "..", "..", "..", "..", "aphis-bird-flu")
        
        # Validate paths
        self._validate_paths()
        
        # Load implementation data
        self.implementation_plan = self._load_implementation_plan()
        self.progress_data = self._load_progress_data()
        self.component_data = self._scan_implementation_components()
    
    def _validate_paths(self) -> None:
        """Validate that all required paths exist."""
        if not os.path.exists(self.implementation_plan_path):
            raise BirdFluConnectorException(f"Implementation plan not found: {self.implementation_plan_path}")
        
        # Progress tracking is optional
        
        if not os.path.exists(self.implementation_dir):
            raise BirdFluConnectorException(f"Implementation directory not found: {self.implementation_dir}")
    
    def _load_implementation_plan(self) -> Dict[str, Any]:
        """
        Load and parse the implementation plan.
        
        Returns:
            Dictionary with implementation plan data
        """
        try:
            with open(self.implementation_plan_path, 'r') as f:
                content = f.read()
                
                # Extract sections using regex
                sections = {}
                
                # Extract executive summary
                executive_summary_match = re.search(r'## Executive Summary\s+(.*?)(?=##)', content, re.DOTALL)
                if executive_summary_match:
                    sections['executive_summary'] = executive_summary_match.group(1).strip()
                
                # Extract system overview
                system_overview_match = re.search(r'## 1\. System Overview\s+(.*?)(?=## 2\.)', content, re.DOTALL)
                if system_overview_match:
                    sections['system_overview'] = system_overview_match.group(1).strip()
                
                # Extract implementation phases
                phases_match = re.search(r'## 3\. Implementation Phases\s+(.*?)(?=## 4\.)', content, re.DOTALL)
                if phases_match:
                    phases_content = phases_match.group(1).strip()
                    
                    # Extract individual phases
                    phases = {}
                    phase_matches = re.finditer(r'### 3\.\d+\s+Phase \d+:.*?\s+(.*?)(?=###|$)', phases_content, re.DOTALL)
                    for i, phase_match in enumerate(phase_matches):
                        phases[f'phase_{i+1}'] = phase_match.group(1).strip()
                    
                    sections['implementation_phases'] = phases
                
                # Extract adaptive methodologies
                adaptive_match = re.search(r'## 5\. Adaptive Methodologies\s+(.*?)(?=## 6\.)', content, re.DOTALL)
                if adaptive_match:
                    sections['adaptive_methodologies'] = adaptive_match.group(1).strip()
                
                return {
                    'title': 'APHIS Bird Flu Tracking System Implementation Plan',
                    'last_updated': datetime.fromtimestamp(os.path.getmtime(self.implementation_plan_path)).isoformat(),
                    'sections': sections
                }
                
        except Exception as e:
            raise BirdFluConnectorException(f"Failed to load implementation plan: {e}")
    
    def _load_progress_data(self) -> Dict[str, Any]:
        """
        Load and parse the progress tracking data.
        
        Returns:
            Dictionary with progress tracking data
        """
        if not os.path.exists(self.progress_tracking_path):
            return {
                'title': 'APHIS Bird Flu Progress Tracking',
                'last_updated': None,
                'sections': {}
            }
        
        try:
            with open(self.progress_tracking_path, 'r') as f:
                content = f.read()
                
                # Extract sections using regex
                sections = {}
                
                # Extract overall progress
                overall_match = re.search(r'## Overall Progress\s+(.*?)(?=##)', content, re.DOTALL)
                if overall_match:
                    sections['overall_progress'] = overall_match.group(1).strip()
                
                # Extract phase status
                phase_status_match = re.search(r'## Phase Status\s+(.*?)(?=##)', content, re.DOTALL)
                if phase_status_match:
                    sections['phase_status'] = phase_status_match.group(1).strip()
                
                # Extract key accomplishments
                accomplishments_match = re.search(r'## Key Accomplishments\s+(.*?)(?=##)', content, re.DOTALL)
                if accomplishments_match:
                    sections['key_accomplishments'] = accomplishments_match.group(1).strip()
                
                # Extract next steps
                next_steps_match = re.search(r'## Next Steps\s+(.*?)(?=##|$)', content, re.DOTALL)
                if next_steps_match:
                    sections['next_steps'] = next_steps_match.group(1).strip()
                
                return {
                    'title': 'APHIS Bird Flu Progress Tracking',
                    'last_updated': datetime.fromtimestamp(os.path.getmtime(self.progress_tracking_path)).isoformat(),
                    'sections': sections
                }
                
        except Exception as e:
            raise BirdFluConnectorException(f"Failed to load progress data: {e}")
    
    def _scan_implementation_components(self) -> Dict[str, Any]:
        """
        Scan the implementation directory to identify components.
        
        Returns:
            Dictionary with component data
        """
        components = {}
        
        if not os.path.exists(self.implementation_dir):
            return components
        
        try:
            # Check for adaptive sampling component
            adaptive_sampling_dir = os.path.join(self.implementation_dir, "src", "system-supervisors", 
                                                "animal_health", "services", "adaptive_sampling")
            if os.path.exists(adaptive_sampling_dir):
                components['adaptive_sampling'] = {
                    'path': adaptive_sampling_dir,
                    'files': os.listdir(adaptive_sampling_dir),
                    'status': 'implemented'
                }
            
            # Check for outbreak detection component
            outbreak_detection_dir = os.path.join(self.implementation_dir, "src", "system-supervisors", 
                                                 "animal_health", "services", "outbreak_detection")
            if os.path.exists(outbreak_detection_dir):
                components['outbreak_detection'] = {
                    'path': outbreak_detection_dir,
                    'files': os.listdir(outbreak_detection_dir),
                    'status': 'implemented'
                }
            
            # Check for predictive modeling component
            predictive_modeling_dir = os.path.join(self.implementation_dir, "src", "system-supervisors", 
                                                  "animal_health", "services", "predictive_modeling")
            if os.path.exists(predictive_modeling_dir):
                components['predictive_modeling'] = {
                    'path': predictive_modeling_dir,
                    'files': os.listdir(predictive_modeling_dir),
                    'status': 'implemented'
                }
            
            # Check for notification component
            notification_dir = os.path.join(self.implementation_dir, "src", "system-supervisors", 
                                           "animal_health", "services", "notification")
            if os.path.exists(notification_dir):
                components['notification'] = {
                    'path': notification_dir,
                    'files': os.listdir(notification_dir),
                    'status': 'implemented'
                }
            
            # Check for configuration
            config_dir = os.path.join(self.implementation_dir, "config")
            if os.path.exists(config_dir):
                components['configuration'] = {
                    'path': config_dir,
                    'files': os.listdir(config_dir),
                    'status': 'implemented'
                }
            
            return components
            
        except Exception as e:
            raise BirdFluConnectorException(f"Failed to scan implementation components: {e}")
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get the implementation status of the bird flu system.
        
        Returns:
            Dictionary with implementation status data
        """
        # Extract tasks from implementation phases
        tasks = []
        
        if 'implementation_phases' in self.implementation_plan.get('sections', {}):
            for phase_key, phase_content in self.implementation_plan['sections']['implementation_phases'].items():
                # Extract tasks from the phase content
                task_matches = re.finditer(r'- \[([ x])\] (.*?)$', phase_content, re.MULTILINE)
                for task_match in task_matches:
                    completed = task_match.group(1) == 'x'
                    task_name = task_match.group(2).strip()
                    
                    tasks.append({
                        'name': task_name,
                        'completed': completed,
                        'phase': phase_key
                    })
        
        # Calculate completion percentage
        completed_tasks = sum(1 for task in tasks if task['completed'])
        completion_percentage = (completed_tasks / len(tasks)) * 100 if tasks else 0
        
        # Determine current phase
        current_phase = "Unknown"
        if tasks:
            phase_completion = {}
            for task in tasks:
                phase = task['phase']
                if phase not in phase_completion:
                    phase_completion[phase] = {'total': 0, 'completed': 0}
                
                phase_completion[phase]['total'] += 1
                if task['completed']:
                    phase_completion[phase]['completed'] += 1
            
            # The current phase is the first one that's not 100% complete
            for phase, stats in sorted(phase_completion.items()):
                percentage = (stats['completed'] / stats['total']) * 100
                if percentage < 100:
                    current_phase = phase
                    break
        
        # Get component implementation status
        implemented_components = sum(1 for component in self.component_data.values() 
                                    if component.get('status') == 'implemented')
        total_components = len(self.component_data) or 1
        component_percentage = (implemented_components / total_components) * 100
        
        return {
            'tasks': {
                'total': len(tasks),
                'completed': completed_tasks,
                'percentage': completion_percentage
            },
            'current_phase': current_phase,
            'components': {
                'total': total_components,
                'implemented': implemented_components,
                'percentage': component_percentage
            },
            'components_detail': self.component_data,
            'last_updated': self.implementation_plan.get('last_updated'),
            'next_steps': self.progress_data.get('sections', {}).get('next_steps', 'Not available')
        }
    
    def get_adaptive_sampling_status(self) -> Dict[str, Any]:
        """
        Get the status of the adaptive sampling component.
        
        Returns:
            Dictionary with adaptive sampling status
        """
        if 'adaptive_sampling' not in self.component_data:
            return {
                'status': 'not_implemented',
                'files': [],
                'methodology': 'Not available'
            }
        
        # Extract adaptive sampling methodology from implementation plan
        methodology = "Not available"
        if 'adaptive_methodologies' in self.implementation_plan.get('sections', {}):
            adaptive_content = self.implementation_plan['sections']['adaptive_methodologies']
            sampling_match = re.search(r'### 5\.1 Adaptive Sampling\s+(.*?)(?=###|$)', adaptive_content, re.DOTALL)
            if sampling_match:
                methodology = sampling_match.group(1).strip()
        
        return {
            'status': self.component_data['adaptive_sampling']['status'],
            'files': self.component_data['adaptive_sampling']['files'],
            'methodology': methodology
        }
    
    def get_outbreak_detection_status(self) -> Dict[str, Any]:
        """
        Get the status of the outbreak detection component.
        
        Returns:
            Dictionary with outbreak detection status
        """
        if 'outbreak_detection' not in self.component_data:
            return {
                'status': 'not_implemented',
                'files': [],
                'methodology': 'Not available'
            }
        
        # Extract outbreak detection methodology from implementation plan
        methodology = "Not available"
        if 'adaptive_methodologies' in self.implementation_plan.get('sections', {}):
            adaptive_content = self.implementation_plan['sections']['adaptive_methodologies']
            detection_match = re.search(r'### 5\.2 Outbreak Detection\s+(.*?)(?=###|$)', adaptive_content, re.DOTALL)
            if detection_match:
                methodology = detection_match.group(1).strip()
        
        return {
            'status': self.component_data['outbreak_detection']['status'],
            'files': self.component_data['outbreak_detection']['files'],
            'methodology': methodology
        }
    
    def get_next_steps_recommendations(self) -> List[str]:
        """
        Generate recommendations for next steps based on current status.
        
        Returns:
            List of recommended next steps
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Add recommendations based on component status
        if 'adaptive_sampling' not in self.component_data:
            recommendations.append("Implement adaptive sampling component based on clinical trial methodologies")
        
        if 'outbreak_detection' not in self.component_data:
            recommendations.append("Implement outbreak detection component with sequential testing algorithms")
        
        if 'predictive_modeling' not in self.component_data:
            recommendations.append("Implement predictive modeling component for outbreak forecasting")
        
        if 'notification' not in self.component_data:
            recommendations.append("Implement notification system for alerting stakeholders")
        
        # Add recommendations based on completion percentage
        completion_percentage = status['tasks']['percentage']
        if completion_percentage < 25:
            recommendations.append("Accelerate implementation of core data models and database schema")
            recommendations.append("Prioritize development environment setup and API framework")
        elif completion_percentage < 50:
            recommendations.append("Focus on laboratory results integration and case management system")
            recommendations.append("Begin development of basic visualization components")
        elif completion_percentage < 75:
            recommendations.append("Implement advanced outbreak detection algorithms and resource optimization")
            recommendations.append("Develop predictive modeling engine for outbreak progression")
        else:
            recommendations.append("Finalize system deployment and user acceptance testing")
            recommendations.append("Prepare training materials and conduct user workshops")
        
        # If we have progress data with next steps, add those as well
        if 'next_steps' in self.progress_data.get('sections', {}):
            next_steps = self.progress_data['sections']['next_steps']
            step_matches = re.finditer(r'^\d+\.\s+(.*?)$', next_steps, re.MULTILINE)
            for step_match in step_matches:
                recommendations.append(step_match.group(1).strip())
        
        return recommendations
    
    def get_codex_context(self) -> Dict[str, Any]:
        """
        Generate a context object for use with Codex CLI.
        
        Returns:
            Dictionary with context information for Codex
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_next_steps_recommendations()
        
        return {
            'agency': 'APHIS',
            'project': 'Bird Flu Tracking System',
            'implementation_status': status,
            'recommendations': recommendations,
            'adaptive_sampling': self.get_adaptive_sampling_status(),
            'outbreak_detection': self.get_outbreak_detection_status(),
            'last_updated': datetime.now().isoformat()
        }


def main():
    """Main entry point for the bird flu connector."""
    parser = argparse.ArgumentParser(description="Bird Flu Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.abspath(__file__)),
                        help="Base path to the bird flu implementation files")
    parser.add_argument("--output", choices=["status", "sampling", "detection", "recommendations", "context"],
                        default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the bird flu connector
        connector = BirdFluConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "sampling":
            result = connector.get_adaptive_sampling_status()
        elif args.output == "detection":
            result = connector.get_outbreak_detection_status()
        elif args.output == "recommendations":
            result = connector.get_next_steps_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"Implementation Status Summary")
                print(f"----------------------------")
                print(f"Tasks: {result['tasks']['completed']}/{result['tasks']['total']} "
                      f"({result['tasks']['percentage']:.1f}% complete)")
                print(f"Current Phase: {result['current_phase']}")
                print(f"Components: {result['components']['implemented']}/{result['components']['total']} "
                      f"({result['components']['percentage']:.1f}% implemented)")
                print(f"Last Updated: {result['last_updated']}")
            
            elif args.output == "sampling" or args.output == "detection":
                component = "Adaptive Sampling" if args.output == "sampling" else "Outbreak Detection"
                print(f"{component} Status")
                print(f"{'-' * len(component + ' Status')}")
                print(f"Status: {result['status']}")
                print(f"Files: {', '.join(result['files']) if result['files'] else 'None'}")
                print(f"\nMethodology:\n{result['methodology']}")
            
            elif args.output == "recommendations":
                print(f"Next Steps Recommendations")
                print(f"-------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"Codex Context Summary for {result['agency']} {result['project']}")
                print(f"{'-' * len('Codex Context Summary for ' + result['agency'] + ' ' + result['project'])}")
                print(f"Implementation: {result['implementation_status']['tasks']['percentage']:.1f}% complete")
                print(f"Current Phase: {result['implementation_status']['current_phase']}")
                print(f"Components: {result['implementation_status']['components']['implemented']}/"
                      f"{result['implementation_status']['components']['total']} implemented")
                print(f"\nTop Recommendations:")
                for i, recommendation in enumerate(result['recommendations'][:3], 1):
                    print(f"{i}. {recommendation}")
    
    except BirdFluConnectorException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()