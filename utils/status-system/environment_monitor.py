#!/usr/bin/env python3
"""
HMS Environment Monitor
This script monitors environment health and resource usage for HMS components.
"""

import argparse
import json
import os
import sys
import datetime
import platform
import psutil
import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Constants
ENVIRONMENTS_DIR = Path("data/environments")
STATUS_DIR = Path("data/status")

class EnvironmentMonitor:
    """Main environment monitor class"""
    
    def __init__(self):
        """Initialize the environment monitor"""
        self.ensure_directories()
        
    def ensure_directories(self) -> None:
        """Ensure required directories exist"""
        ENVIRONMENTS_DIR.mkdir(parents=True, exist_ok=True)
        STATUS_DIR.mkdir(parents=True, exist_ok=True)
    
    def check_environment(self, component: str) -> Dict[str, Any]:
        """Check environment for a component"""
        # Get basic system information
        system_info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "platform_release": platform.release(),
            "processor": platform.processor(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        }
        
        # Get resource usage
        resources = {
            "cpu_count": psutil.cpu_count(),
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_usage_percent": psutil.virtual_memory().percent,
            "disk_total": shutil.disk_usage("/").total,
            "disk_free": shutil.disk_usage("/").free,
            "disk_usage_percent": shutil.disk_usage("/").used / shutil.disk_usage("/").total * 100
        }
        
        # Get component-specific information
        component_info = self.get_component_info(component)
        
        # Combine all information
        env_data = {
            "component": component,
            "timestamp": datetime.datetime.now().isoformat(),
            "system": system_info,
            "resources": resources,
            "component_info": component_info
        }
        
        # Determine environment health
        env_data["health"] = self.determine_health(env_data)
        
        # Save environment data
        self.save_environment_data(component, env_data)
        
        return env_data
    
    def get_component_info(self, component: str) -> Dict[str, Any]:
        """Get component-specific information"""
        # Check component status
        status_file = os.path.join(STATUS_DIR, f"{component}.json")
        component_info = {
            "found": os.path.exists(status_file),
            "status": "UNKNOWN",
            "start_found": False,
            "version": "unknown",
            "environment": "unknown",
            "last_start": None
        }
        
        if component_info["found"]:
            with open(status_file, 'r') as f:
                status_data = json.load(f)
                component_info["status"] = status_data.get("status", "UNKNOWN")
        
        # Check component start information
        start_file = os.path.join(STATUS_DIR, f"{component}-start.json")
        if os.path.exists(start_file):
            with open(start_file, 'r') as f:
                start_data = json.load(f)
                component_info["start_found"] = True
                component_info["version"] = start_data.get("version", "unknown")
                component_info["environment"] = start_data.get("environment", "unknown")
                component_info["last_start"] = start_data.get("timestamp")
        
        return component_info
    
    def determine_health(self, env_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine environment health based on collected data"""
        health = {
            "status": "HEALTHY",
            "issues": []
        }
        
        # Check system resources
        resources = env_data.get("resources", {})
        
        # CPU usage check
        cpu_usage = resources.get("cpu_usage", 0)
        if cpu_usage > 90:
            health["status"] = "UNHEALTHY"
            health["issues"].append(f"High CPU usage: {cpu_usage}%")
        elif cpu_usage > 75:
            health["status"] = "DEGRADED"
            health["issues"].append(f"Elevated CPU usage: {cpu_usage}%")
        
        # Memory usage check
        memory_usage = resources.get("memory_usage_percent", 0)
        if memory_usage > 90:
            health["status"] = "UNHEALTHY"
            health["issues"].append(f"High memory usage: {memory_usage}%")
        elif memory_usage > 80:
            if health["status"] != "UNHEALTHY":
                health["status"] = "DEGRADED"
            health["issues"].append(f"Elevated memory usage: {memory_usage}%")
        
        # Disk usage check
        disk_usage = resources.get("disk_usage_percent", 0)
        if disk_usage > 95:
            health["status"] = "UNHEALTHY"
            health["issues"].append(f"Critical disk usage: {disk_usage}%")
        elif disk_usage > 85:
            if health["status"] != "UNHEALTHY":
                health["status"] = "DEGRADED"
            health["issues"].append(f"High disk usage: {disk_usage}%")
        
        # Component status check
        component_info = env_data.get("component_info", {})
        if component_info.get("status") == "UNHEALTHY":
            health["status"] = "UNHEALTHY"
            health["issues"].append("Component status is UNHEALTHY")
        elif component_info.get("status") == "DEGRADED":
            if health["status"] != "UNHEALTHY":
                health["status"] = "DEGRADED"
            health["issues"].append("Component status is DEGRADED")
        
        return health
    
    def save_environment_data(self, component: str, env_data: Dict[str, Any]) -> None:
        """Save environment data to file"""
        # Create environment file path
        file_path = os.path.join(ENVIRONMENTS_DIR, f"{component}.json")
        
        # Save data
        with open(file_path, 'w') as f:
            json.dump(env_data, f, indent=2)
            
        print(f"Environment data saved to: {file_path}")
    
    def get_environment(self, component: str) -> Dict[str, Any]:
        """Get environment data for a component"""
        file_path = os.path.join(ENVIRONMENTS_DIR, f"{component}.json")
        
        if not os.path.exists(file_path):
            return {
                "component": component,
                "status": "UNKNOWN",
                "message": "No environment data available"
            }
            
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def list_environments(self) -> List[str]:
        """List all environments with data"""
        if not os.path.exists(ENVIRONMENTS_DIR):
            return []
            
        return [
            os.path.splitext(f)[0] for f in os.listdir(ENVIRONMENTS_DIR)
            if f.endswith('.json')
        ]
    
    def get_all_environments(self) -> Dict[str, Dict[str, Any]]:
        """Get all environment data"""
        environments = self.list_environments()
        env_data = {}
        
        for env in environments:
            env_data[env] = self.get_environment(env)
            
        return env_data


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="HMS Environment Monitor")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")
    
    # check command
    check_parser = subparsers.add_parser("check", help="Check environment")
    check_parser.add_argument("component", help="Component name")
    
    # get command
    get_parser = subparsers.add_parser("get", help="Get environment data")
    get_parser.add_argument("component", help="Component name")
    
    # list command
    subparsers.add_parser("list", help="List all environments")
    
    # all command
    subparsers.add_parser("all", help="Get all environment data")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create monitor
    monitor = EnvironmentMonitor()
    
    # Execute command
    if args.command == "check":
        env_data = monitor.check_environment(args.component)
        print(json.dumps(env_data, indent=2))
    elif args.command == "get":
        env_data = monitor.get_environment(args.component)
        print(json.dumps(env_data, indent=2))
    elif args.command == "list":
        environments = monitor.list_environments()
        for env in environments:
            print(env)
    elif args.command == "all":
        env_data = monitor.get_all_environments()
        print(json.dumps(env_data, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()