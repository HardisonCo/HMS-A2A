#!/usr/bin/env python3
"""
HMS Documentation Integrator
This script integrates status and health information into component documentation.
"""

import argparse
import json
import os
import sys
import datetime
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Constants
STATUS_DIR = Path("data/status")
ANALYSIS_DIR = Path("data/analysis")
ENVIRONMENTS_DIR = Path("data/environments")
ISSUES_DIR = Path("data/issues")
DOCS_DIR = Path("docs")
COMPONENTS_DIR = Path("SYSTEM-COMPONENTS")

class DocsIntegrator:
    """Main documentation integrator class"""
    
    def __init__(self):
        """Initialize the documentation integrator"""
        self.ensure_directories()
        
    def ensure_directories(self) -> None:
        """Ensure required directories exist"""
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    def update_component_docs(self, component: str) -> Dict[str, Any]:
        """Update documentation for a component with status and health information"""
        print(f"Updating documentation for {component}...")
        
        # Get component status and analysis
        status_data = self.get_component_status(component)
        analysis_data = self.get_component_analysis(component)
        environment_data = self.get_component_environment(component)
        issues = self.get_component_issues(component)
        
        # Determine component docs location
        component_docs = self.find_component_docs(component)
        if not component_docs:
            print(f"No documentation found for {component}")
            return {
                "component": component,
                "status": "ERROR",
                "message": "No documentation found"
            }
        
        # Generate status badge markdown
        status_badge = self.generate_status_badge(status_data)
        
        # Generate summary markdown
        summary_md = self.generate_status_summary(component, status_data, analysis_data, environment_data, issues)
        
        # Update each documentation file
        updated_files = []
        for doc_file in component_docs:
            updated = self.update_doc_file(doc_file, component, status_badge, summary_md)
            if updated:
                updated_files.append(doc_file)
        
        return {
            "component": component,
            "status": "SUCCESS" if updated_files else "ERROR",
            "message": f"Updated {len(updated_files)} documentation files" if updated_files else "No documentation files updated",
            "updated_files": updated_files
        }
    
    def get_component_status(self, component: str) -> Dict[str, Any]:
        """Get component status data"""
        status_file = os.path.join(STATUS_DIR, f"{component}.json")
        
        if not os.path.exists(status_file):
            return {
                "status": "UNKNOWN",
                "message": "No status information available",
                "last_update": None
            }
            
        with open(status_file, 'r') as f:
            return json.load(f)
    
    def get_component_analysis(self, component: str) -> Dict[str, Any]:
        """Get component analysis data"""
        analysis_file = os.path.join(ANALYSIS_DIR, f"{component}.json")
        
        if not os.path.exists(analysis_file):
            return {
                "overall_status": "UNKNOWN",
                "message": "No analysis information available",
                "timestamp": None
            }
            
        with open(analysis_file, 'r') as f:
            return json.load(f)
    
    def get_component_environment(self, component: str) -> Dict[str, Any]:
        """Get component environment data"""
        env_file = os.path.join(ENVIRONMENTS_DIR, f"{component}.json")
        
        if not os.path.exists(env_file):
            return {
                "health": {"status": "UNKNOWN"},
                "message": "No environment information available",
                "timestamp": None
            }
            
        with open(env_file, 'r') as f:
            return json.load(f)
    
    def get_component_issues(self, component: str) -> List[Dict[str, Any]]:
        """Get issues for a component"""
        if not os.path.exists(ISSUES_DIR):
            return []
            
        issues = []
        for issue_file in os.listdir(ISSUES_DIR):
            if issue_file.endswith('.json'):
                with open(os.path.join(ISSUES_DIR, issue_file), 'r') as f:
                    issue = json.load(f)
                    if issue.get('component') == component:
                        issues.append(issue)
                        
        return sorted(issues, key=lambda x: x.get('created', ''), reverse=True)
    
    def find_component_docs(self, component: str) -> List[str]:
        """Find documentation files for a component"""
        # Check component-specific docs directory
        component_docs_dir = os.path.join(COMPONENTS_DIR, component)
        docs = []
        
        # Look for README.md in component directory
        readme_path = os.path.join(component_docs_dir, "README.md")
        if os.path.exists(readme_path):
            docs.append(readme_path)
            
        # Look for docs in main docs directory
        component_docs_pattern = re.compile(f"{component}-.*\\.md", re.IGNORECASE)
        
        if os.path.exists(DOCS_DIR):
            for doc_file in os.listdir(DOCS_DIR):
                if doc_file.endswith('.md') and (doc_file.startswith(component) or component_docs_pattern.match(doc_file)):
                    docs.append(os.path.join(DOCS_DIR, doc_file))
        
        return docs
    
    def generate_status_badge(self, status_data: Dict[str, Any]) -> str:
        """Generate a markdown status badge"""
        status = status_data.get("status", "UNKNOWN")
        
        if status == "HEALTHY":
            color = "brightgreen"
        elif status == "DEGRADED":
            color = "yellow"
        elif status == "UNHEALTHY":
            color = "red"
        else:
            color = "lightgrey"
            
        return f"![Status: {status}](https://img.shields.io/badge/Status-{status}-{color})"
    
    def generate_status_summary(self, component: str, status_data: Dict[str, Any], 
                               analysis_data: Dict[str, Any], environment_data: Dict[str, Any],
                               issues: List[Dict[str, Any]]) -> str:
        """Generate a markdown summary of component status"""
        status = status_data.get("status", "UNKNOWN")
        last_update = status_data.get("last_update", "Unknown")
        message = status_data.get("message", "No status message available")
        
        analysis_status = analysis_data.get("overall_status", "UNKNOWN")
        analysis_time = analysis_data.get("timestamp", "Unknown")
        
        env_status = environment_data.get("health", {}).get("status", "UNKNOWN")
        env_time = environment_data.get("timestamp", "Unknown")
        
        open_issues = [issue for issue in issues if issue.get("status") == "open"]
        
        md = f"""
## Component Status Summary

Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

| Metric | Status | Last Updated |
|--------|--------|-------------|
| Runtime Status | **{status}** | {last_update} |
| Repository Analysis | **{analysis_status}** | {analysis_time} |
| Environment Health | **{env_status}** | {env_time} |
| Open Issues | **{len(open_issues)}** | {datetime.datetime.now().strftime('%Y-%m-%d')} |

### Status Message
{message}

"""
        
        # Add issues if there are any
        if open_issues:
            md += "### Open Issues\n\n"
            md += "| ID | Title | Severity | Created |\n"
            md += "|-------|-------|----------|--------|\n"
            
            for issue in open_issues[:5]:  # Limit to 5 issues
                issue_id = issue.get("id", "")[:8]  # Truncate ID for readability
                title = issue.get("title", "No title")
                severity = issue.get("severity", "medium")
                created = issue.get("created", "")
                if created:
                    try:
                        created_date = datetime.datetime.fromisoformat(created).strftime('%Y-%m-%d')
                    except ValueError:
                        created_date = created
                else:
                    created_date = "Unknown"
                    
                md += f"| {issue_id} | {title} | {severity} | {created_date} |\n"
                
            if len(open_issues) > 5:
                md += f"\n*And {len(open_issues) - 5} more issues...*\n"
        
        md += "\n*This status summary is automatically generated and updated by the HMS Status System.*\n"
        
        return md
    
    def update_doc_file(self, doc_path: str, component: str, status_badge: str, summary_md: str) -> bool:
        """Update a documentation file with status information"""
        if not os.path.exists(doc_path):
            return False
            
        with open(doc_path, 'r') as f:
            content = f.read()
        
        # Define markers for status section
        start_marker = "<!-- HMS-STATUS-START -->"
        end_marker = "<!-- HMS-STATUS-END -->"
        
        # Check if status section exists
        if start_marker in content and end_marker in content:
            # Replace existing status section
            pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
            new_content = pattern.sub(f"{start_marker}\n{status_badge}\n\n{summary_md}\n{end_marker}", content)
        else:
            # Find heading to insert after
            heading_match = re.search(r"^# .+$", content, re.MULTILINE)
            
            if heading_match:
                # Insert after first heading
                heading_end = heading_match.end()
                new_content = (
                    content[:heading_end] + 
                    f"\n\n{start_marker}\n{status_badge}\n\n{summary_md}\n{end_marker}\n\n" + 
                    content[heading_end:]
                )
            else:
                # Insert at beginning of file
                new_content = f"{start_marker}\n{status_badge}\n\n{summary_md}\n{end_marker}\n\n{content}"
        
        # Write updated content
        with open(doc_path, 'w') as f:
            f.write(new_content)
            
        print(f"Updated documentation file: {doc_path}")
        return True
    
    def update_all_components(self) -> Dict[str, Any]:
        """Update documentation for all components with status information"""
        # Get list of components with status
        components = self.list_components_with_status()
        
        results = {}
        for component in components:
            result = self.update_component_docs(component)
            results[component] = result
            
        return results
    
    def list_components_with_status(self) -> List[str]:
        """List all components that have status information"""
        if not os.path.exists(STATUS_DIR):
            return []
            
        return [
            os.path.splitext(f)[0] for f in os.listdir(STATUS_DIR)
            if f.endswith('.json') and not f.endswith('-start.json')
        ]


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="HMS Documentation Integrator")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")
    
    # update command
    update_parser = subparsers.add_parser("update", help="Update documentation for a component")
    update_parser.add_argument("component", help="Component name")
    
    # update-all command
    subparsers.add_parser("update-all", help="Update documentation for all components")
    
    # list command
    subparsers.add_parser("list", help="List all components with status information")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create integrator
    integrator = DocsIntegrator()
    
    # Execute command
    if args.command == "update":
        result = integrator.update_component_docs(args.component)
        print(json.dumps(result, indent=2))
    elif args.command == "update-all":
        results = integrator.update_all_components()
        print(json.dumps(results, indent=2))
    elif args.command == "list":
        components = integrator.list_components_with_status()
        for component in components:
            print(component)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()