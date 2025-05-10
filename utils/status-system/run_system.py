#!/usr/bin/env python3
"""
HMS Status System Runner
This script integrates all status system components to provide a unified interface.
"""

import argparse
import json
import os
import sys
import time
import datetime
import subprocess
import signal
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Import other scripts
import repository_analyzer
import status_tracker
import environment_monitor
import docs_integrator

# Constants
REPOS_DIR = Path("SYSTEM-COMPONENTS")
DATA_DIR = Path("data")
SUMMARIES_DIR = Path("data/summaries")
LOGS_DIR = Path("logs")

class StatusSystem:
    """Main status system class"""
    
    def __init__(self):
        """Initialize the status system"""
        self.ensure_directories()
        self.running = False
        self.monitor_interval = 300  # 5 minutes
        
        # Initialize components
        self.repo_analyzer = repository_analyzer.RepositoryAnalyzer()
        self.status_tracker = status_tracker.StatusTracker()
        self.env_monitor = environment_monitor.EnvironmentMonitor()
        self.docs_integrator = docs_integrator.DocsIntegrator()
        
    def ensure_directories(self) -> None:
        """Ensure required directories exist"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    def quick_update(self) -> Dict[str, Any]:
        """Perform a quick update of system status"""
        print("Performing quick status system update...")
        
        # Get list of components
        components = self.repo_analyzer.list_repositories()
        
        # Check and update environment for each component
        env_results = {}
        for component in components:
            try:
                env_data = self.env_monitor.check_environment(component)
                env_results[component] = env_data.get("health", {}).get("status", "UNKNOWN")
            except Exception as e:
                print(f"Error checking environment for {component}: {str(e)}")
                env_results[component] = "ERROR"
        
        # Generate and save summary
        summary = {
            "timestamp": datetime.datetime.now().isoformat(),
            "components": {
                component: {
                    "environment": env_results.get(component, "UNKNOWN"),
                    "status": "UNKNOWN"  # Will be updated in next step
                } for component in components
            }
        }
        
        # Get current status for each component
        for component in components:
            status_data = self.status_tracker.get_status(component)
            summary["components"][component]["status"] = status_data.get("status", "UNKNOWN")
            
        # Save summary
        self.save_summary(summary, "quick_update")
        
        return summary
    
    def full_update(self) -> Dict[str, Any]:
        """Perform a full update of system status"""
        print("Performing full status system update...")
        
        # Get list of components
        components = self.repo_analyzer.list_repositories()
        
        # Analyze each repository
        repo_results = {}
        for component in components:
            try:
                analysis = self.repo_analyzer.analyze_repository(component)
                repo_results[component] = analysis.get("overall_status", "UNKNOWN")
            except Exception as e:
                print(f"Error analyzing repository {component}: {str(e)}")
                repo_results[component] = "ERROR"
        
        # Check environment for each component
        env_results = {}
        for component in components:
            try:
                env_data = self.env_monitor.check_environment(component)
                env_results[component] = env_data.get("health", {}).get("status", "UNKNOWN")
            except Exception as e:
                print(f"Error checking environment for {component}: {str(e)}")
                env_results[component] = "ERROR"
        
        # Update component status based on analysis and environment
        status_results = {}
        for component in components:
            repo_status = repo_results.get(component, "UNKNOWN")
            env_status = env_results.get(component, "UNKNOWN")
            
            # Determine overall status
            if repo_status == "UNHEALTHY" or env_status == "UNHEALTHY":
                overall_status = "UNHEALTHY"
            elif repo_status == "DEGRADED" or env_status == "DEGRADED":
                overall_status = "DEGRADED"
            elif repo_status == "UNKNOWN" or env_status == "UNKNOWN":
                overall_status = "UNKNOWN"
            else:
                overall_status = "HEALTHY"
            
            # Update component status
            message = f"Repository: {repo_status}, Environment: {env_status}"
            try:
                status_data = self.status_tracker.set_status(component, overall_status, message)
                status_results[component] = overall_status
            except Exception as e:
                print(f"Error updating status for {component}: {str(e)}")
                status_results[component] = "ERROR"
        
        # Update documentation
        doc_results = {}
        for component in components:
            try:
                result = self.docs_integrator.update_component_docs(component)
                doc_results[component] = result.get("status", "ERROR")
            except Exception as e:
                print(f"Error updating documentation for {component}: {str(e)}")
                doc_results[component] = "ERROR"
        
        # Generate and save summary
        summary = {
            "timestamp": datetime.datetime.now().isoformat(),
            "components": {
                component: {
                    "repository": repo_results.get(component, "UNKNOWN"),
                    "environment": env_results.get(component, "UNKNOWN"),
                    "status": status_results.get(component, "UNKNOWN"),
                    "documentation": doc_results.get(component, "ERROR")
                } for component in components
            }
        }
        
        # Save summary
        self.save_summary(summary, "full_update")
        
        # Generate system-wide summary
        self.generate_system_summary(summary)
        
        return summary
    
    def monitor(self) -> None:
        """Start continuous monitoring"""
        print("Starting continuous monitoring...")
        
        self.running = True
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        
        # Initial full update
        self.full_update()
        
        # Monitoring loop
        try:
            while self.running:
                print(f"Next update in {self.monitor_interval} seconds...")
                time.sleep(self.monitor_interval)
                
                # Perform quick update
                self.quick_update()
                
                # Full update every hour (12 quick updates)
                if datetime.datetime.now().minute < 5:
                    self.full_update()
        except KeyboardInterrupt:
            print("Monitoring stopped by user")
        finally:
            self.running = False
            print("Monitoring stopped")
    
    def handle_signal(self, sig, frame):
        """Handle termination signals"""
        print(f"Received signal {sig}, stopping monitoring...")
        self.running = False
    
    def save_summary(self, summary: Dict[str, Any], name: str) -> None:
        """Save summary to file"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(SUMMARIES_DIR, f"{name}_{timestamp}.json")
        
        with open(file_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
        # Also save as latest
        latest_path = os.path.join(SUMMARIES_DIR, f"{name}_latest.json")
        with open(latest_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"Summary saved to: {file_path}")
    
    def generate_system_summary(self, data: Dict[str, Any]) -> None:
        """Generate system-wide summary"""
        components = data.get("components", {})
        
        # Count status types
        counts = {
            "HEALTHY": 0,
            "DEGRADED": 0,
            "UNHEALTHY": 0,
            "UNKNOWN": 0,
            "ERROR": 0,
            "total": len(components)
        }
        
        for component, info in components.items():
            status = info.get("status", "UNKNOWN")
            counts[status] = counts.get(status, 0) + 1
        
        # Generate markdown summary
        markdown = f"""# HMS System Status

Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Health

| Status | Count | Percentage |
|--------|-------|------------|
| HEALTHY | {counts["HEALTHY"]} | {counts["HEALTHY"] / counts["total"] * 100:.1f}% |
| DEGRADED | {counts["DEGRADED"]} | {counts["DEGRADED"] / counts["total"] * 100:.1f}% |
| UNHEALTHY | {counts["UNHEALTHY"]} | {counts["UNHEALTHY"] / counts["total"] * 100:.1f}% |
| UNKNOWN | {counts["UNKNOWN"]} | {counts["UNKNOWN"] / counts["total"] * 100:.1f}% |
| ERROR | {counts.get("ERROR", 0)} | {counts.get("ERROR", 0) / counts["total"] * 100:.1f}% |

## Component Status

| Component | Status | Repository | Environment |
|-----------|--------|------------|-------------|
"""
        
        # Add each component
        for component, info in sorted(components.items()):
            status = info.get("status", "UNKNOWN")
            repo_status = info.get("repository", "UNKNOWN")
            env_status = info.get("environment", "UNKNOWN")
            
            markdown += f"| {component} | **{status}** | {repo_status} | {env_status} |\n"
        
        markdown += "\n\n*This status summary is automatically generated by the HMS Status System.*\n"
        
        # Save markdown summary
        file_path = os.path.join(SUMMARIES_DIR, "system_status.md")
        with open(file_path, 'w') as f:
            f.write(markdown)
            
        print(f"System summary saved to: {file_path}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="HMS Status System Runner")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")
    
    # quick-update command
    subparsers.add_parser("quick-update", help="Perform a quick update of system status")
    
    # full-update command
    subparsers.add_parser("full-update", help="Perform a full update of system status")
    
    # monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Start continuous monitoring")
    monitor_parser.add_argument("--interval", type=int, default=300, help="Monitoring interval in seconds (default: 300)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create system
    system = StatusSystem()
    
    # Execute command
    if args.command == "quick-update":
        system.quick_update()
    elif args.command == "full-update":
        system.full_update()
    elif args.command == "monitor":
        system.monitor_interval = args.interval
        system.monitor()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()