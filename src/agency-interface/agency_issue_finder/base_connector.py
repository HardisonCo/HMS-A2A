#!/usr/bin/env python3
"""
Base Agency Research Connector

A base class for agency-specific research connectors that provides 
common functionality for accessing agency implementation data.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class AgencyResearchConnectorException(Exception):
    """Custom exception for agency research connector errors."""
    pass

class AgencyResearchConnector:
    """
    Base class for agency-specific research connectors.
    Provides common functionality for accessing agency implementation data.
    """
    
    def __init__(self, agency: str, base_path: str) -> None:
        """
        Initialize the agency research connector.
        
        Args:
            agency: Agency identifier (e.g., HHS, DOD)
            base_path: Base path to agency data
        """
        self.agency = agency
        self.base_path = base_path
        self.agency_dir = os.path.join(base_path, agency.lower())
        
        # Create agency directory if it doesn't exist
        os.makedirs(self.agency_dir, exist_ok=True)
        
        # Load agency data
        self.data = self._load_agency_data()
    
    def _load_agency_data(self) -> Dict[str, Any]:
        """
        Load agency data from files.
        
        Returns:
            Dictionary with agency data
        """
        data = {
            "agency": self.agency,
            "last_updated": datetime.now().isoformat(),
            "sections": {}
        }
        
        # Look for agency implementation plan
        impl_plan_path = os.path.join(self.base_path, f"{self.agency}-IMPLEMENTATION-PLAN.md")
        if os.path.exists(impl_plan_path):
            try:
                with open(impl_plan_path, 'r') as f:
                    data["implementation_plan"] = f.read()
            except Exception as e:
                raise AgencyResearchConnectorException(f"Failed to load implementation plan: {e}")
        
        # Look for alternative path format
        alt_impl_plan_path = os.path.join(self.base_path, f"{self.agency.title()}-IMPLEMENTATION-PLAN.md")
        if not "implementation_plan" in data and os.path.exists(alt_impl_plan_path):
            try:
                with open(alt_impl_plan_path, 'r') as f:
                    data["implementation_plan"] = f.read()
            except Exception as e:
                raise AgencyResearchConnectorException(f"Failed to load implementation plan (alt path): {e}")
        
        # Look for agency progress tracking
        progress_path = os.path.join(self.base_path, f"{self.agency}-PROGRESS-TRACKING.md")
        if os.path.exists(progress_path):
            try:
                with open(progress_path, 'r') as f:
                    data["progress_tracking"] = f.read()
            except Exception as e:
                raise AgencyResearchConnectorException(f"Failed to load progress tracking: {e}")
        
        # Look for alternative path format
        alt_progress_path = os.path.join(self.base_path, f"{self.agency.title()}-PROGRESS-TRACKING.md")
        if not "progress_tracking" in data and os.path.exists(alt_progress_path):
            try:
                with open(alt_progress_path, 'r') as f:
                    data["progress_tracking"] = f.read()
            except Exception as e:
                raise AgencyResearchConnectorException(f"Failed to load progress tracking (alt path): {e}")
        
        # Load any JSON configuration from the agency directory
        for filename in os.listdir(self.agency_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.agency_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        key = filename.replace('.json', '')
                        data[key] = json.load(f)
                except json.JSONDecodeError as e:
                    raise AgencyResearchConnectorException(f"Invalid JSON in {filename}: {e}")
                except Exception as e:
                    raise AgencyResearchConnectorException(f"Failed to load {filename}: {e}")
        
        return data
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get implementation status for the agency.
        
        Returns:
            Implementation status dictionary
        """
        # This method should be overridden by agency-specific implementations
        status = {
            "agency": self.agency,
            "last_updated": datetime.now().isoformat()
        }
        
        # Parse implementation plan if available
        if "implementation_plan" in self.data:
            # Extract phases and tasks
            plan_content = self.data["implementation_plan"]
            phases = {}
            
            # Extract phase sections (handles various formats)
            phase_patterns = [
                r'## Phase (\d+): (.*?)\n(.*?)(?=##|\Z)',  # Standard format
                r'### Phase (\d+)[:\.]? (.*?)\n(.*?)(?=###|\Z)',  # Alternative format
                r'#### (?:Phase )?(\d+)[:\.]? (.*?)\n(.*?)(?=####|\Z)'  # Another alternative
            ]
            
            for pattern in phase_patterns:
                phase_matches = re.finditer(pattern, plan_content, re.DOTALL)
                found_phases = False
                
                for match in phase_matches:
                    found_phases = True
                    phase_num = match.group(1)
                    phase_name = match.group(2).strip()
                    phase_content = match.group(3)
                    
                    # Extract tasks and their status
                    tasks = []
                    task_patterns = [
                        r'- \[([ x])\] (.*?)$',  # Standard GitHub format
                        r'- (DONE|TODO|IN PROGRESS): (.*?)$',  # Alternative format 
                        r'(\d+\.) (.*?) - (Complete|In Progress|Not Started)'  # Yet another format
                    ]
                    
                    for task_pattern in task_patterns:
                        task_matches = re.finditer(task_pattern, phase_content, re.MULTILINE)
                        found_tasks = False
                        
                        for task_match in task_matches:
                            found_tasks = True
                            if task_pattern == r'- \[([ x])\] (.*?)$':
                                completed = task_match.group(1) == 'x'
                                task_name = task_match.group(2).strip()
                            elif task_pattern == r'- (DONE|TODO|IN PROGRESS): (.*?)$':
                                status_text = task_match.group(1)
                                completed = status_text == 'DONE'
                                task_name = task_match.group(2).strip()
                            else:  # Third pattern
                                task_name = task_match.group(2).strip()
                                status_text = task_match.group(3)
                                completed = status_text == 'Complete'
                            
                            tasks.append({
                                "name": task_name,
                                "completed": completed
                            })
                        
                        if found_tasks:
                            break
                    
                    # Calculate phase completion percentage
                    completed_tasks = sum(1 for task in tasks if task["completed"])
                    percentage = (completed_tasks / len(tasks)) * 100 if tasks else 0
                    
                    phases[f"phase_{phase_num}"] = {
                        "name": phase_name,
                        "tasks": tasks,
                        "completed_tasks": completed_tasks,
                        "total_tasks": len(tasks),
                        "percentage": percentage
                    }
                
                if found_phases:
                    break
            
            status["implementation_phases"] = phases
            
            # Calculate overall completion
            all_tasks = [task for phase in phases.values() for task in phase["tasks"]]
            completed_all = sum(1 for task in all_tasks if task["completed"])
            overall_percentage = (completed_all / len(all_tasks)) * 100 if all_tasks else 0
            
            status["overall_completion"] = {
                "completed_tasks": completed_all,
                "total_tasks": len(all_tasks),
                "percentage": overall_percentage
            }
        
        # Parse progress tracking if available
        if "progress_tracking" in self.data:
            progress_content = self.data["progress_tracking"]
            
            # Extract overall progress section
            overall_match = re.search(r'## Overall Progress\s+(.*?)(?=##|\Z)', 
                                     progress_content, re.DOTALL)
            if overall_match:
                status["overall_progress"] = overall_match.group(1).strip()
            
            # Extract next steps section
            next_steps_match = re.search(r'## Next Steps\s+(.*?)(?=##|\Z)', 
                                        progress_content, re.DOTALL)
            if next_steps_match:
                # Extract individual steps
                next_steps_content = next_steps_match.group(1)
                next_steps = []
                
                # Try different list formats
                step_patterns = [
                    r'(\d+\.)\s+(.*?)$',  # Numbered list
                    r'- (.*?)$'  # Bullet list
                ]
                
                for pattern in step_patterns:
                    step_matches = re.finditer(pattern, next_steps_content, re.MULTILINE)
                    found_steps = False
                    
                    for step_match in step_matches:
                        found_steps = True
                        if pattern == r'(\d+\.)\s+(.*?)$':
                            step_text = step_match.group(2).strip()
                        else:
                            step_text = step_match.group(1).strip()
                        
                        next_steps.append(step_text)
                    
                    if found_steps:
                        break
                
                status["next_steps"] = next_steps
        
        return status
    
    def get_recommendations(self) -> List[str]:
        """
        Get recommendations for the agency.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Add recommendations based on implementation status
        if "implementation_phases" in status:
            phases = status["implementation_phases"]
            
            # Find the first incomplete phase
            current_phase = None
            for phase_key, phase in sorted(phases.items()):
                if phase["percentage"] < 100:
                    current_phase = phase
                    break
            
            if current_phase:
                # Add recommendations for incomplete tasks in the current phase
                for task in current_phase["tasks"]:
                    if not task["completed"]:
                        recommendations.append(f"Complete task: {task['name']}")
        
        # Add recommendations from next steps if available
        if "next_steps" in status and status["next_steps"]:
            recommendations.extend(status["next_steps"])
        
        # Add general recommendation if no specific ones were found
        if not recommendations:
            recommendations.append(f"Develop comprehensive implementation plan for {self.agency}")
        
        return recommendations
    
    def get_codex_context(self) -> Dict[str, Any]:
        """
        Generate Codex context for the agency.
        
        Returns:
            Codex context dictionary
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_recommendations()
        
        # Compile context
        context = {
            "agency": self.agency,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context
    
    def save_data(self, key: str, data: Any) -> bool:
        """
        Save data to the agency directory.
        
        Args:
            key: Data key
            data: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        if key == "implementation_plan" or key == "progress_tracking":
            # These are stored as markdown files
            file_path = os.path.join(self.base_path, f"{self.agency}-{key.upper().replace('_', '-')}.md")
        else:
            # Everything else is stored as JSON
            file_path = os.path.join(self.agency_dir, f"{key}.json")
        
        try:
            if key == "implementation_plan" or key == "progress_tracking":
                # Save as markdown
                with open(file_path, 'w') as f:
                    f.write(data)
            else:
                # Save as JSON
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            
            # Update internal data
            self.data[key] = data
            
            return True
        except Exception as e:
            raise AgencyResearchConnectorException(f"Failed to save {key}: {e}")


def main():
    """Main entry point function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agency Research Connector")
    parser.add_argument("agency", help="Agency acronym (e.g., HHS, DOD)")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to agency data")
    parser.add_argument("--output", choices=["status", "recommendations", "context"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the connector
        connector = AgencyResearchConnector(args.agency, args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"{args.agency} Implementation Status")
                print(f"{'-' * len(args.agency + ' Implementation Status')}")
                
                if "overall_completion" in result:
                    overall = result["overall_completion"]
                    print(f"Overall Completion: {overall['completed_tasks']}/{overall['total_tasks']} "
                          f"({overall['percentage']:.1f}%)")
                
                if "implementation_phases" in result:
                    print("\nPhases:")
                    for phase_key, phase in sorted(result["implementation_phases"].items()):
                        print(f"  {phase['name']}: {phase['completed_tasks']}/{phase['total_tasks']} "
                              f"({phase['percentage']:.1f}%)")
                
                if "next_steps" in result:
                    print("\nNext Steps:")
                    for i, step in enumerate(result["next_steps"], 1):
                        print(f"  {i}. {step}")
            
            elif args.output == "recommendations":
                print(f"{args.agency} Implementation Recommendations")
                print(f"{'-' * len(args.agency + ' Implementation Recommendations')}")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"{args.agency} Codex Context Summary")
                print(f"{'-' * len(args.agency + ' Codex Context Summary')}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"Overall Completion: {overall['percentage']:.1f}%")
                
                print(f"\nRecommendations:")
                for i, recommendation in enumerate(result["recommendations"][:5], 1):
                    print(f"{i}. {recommendation}")
    
    except AgencyResearchConnectorException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    import sys
    main()