#!/usr/bin/env python3
"""
HMS Status Tracker
This script tracks the status of components and provides a centralized location
for storing and retrieving status information.
"""

import argparse
import json
import os
import sys
import datetime
import uuid
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Constants
STATUS_DIR = Path("data/status")
ISSUES_DIR = Path("data/issues")
TEST_RESULTS_DIR = Path("data/test-results")
WORK_TICKETS_DIR = Path("data/work-tickets")

class StatusTracker:
    """Main status tracker class"""
    
    def __init__(self):
        """Initialize the status tracker"""
        self.ensure_directories()
        
    def ensure_directories(self) -> None:
        """Ensure required directories exist"""
        STATUS_DIR.mkdir(parents=True, exist_ok=True)
        ISSUES_DIR.mkdir(parents=True, exist_ok=True)
        TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        WORK_TICKETS_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_status(self, component: str) -> Dict[str, Any]:
        """Get the status of a component"""
        status_file = os.path.join(STATUS_DIR, f"{component}.json")
        
        if not os.path.exists(status_file):
            return {
                "component": component,
                "status": "UNKNOWN",
                "last_update": None,
                "message": "No status information available"
            }
            
        with open(status_file, 'r') as f:
            return json.load(f)
    
    def set_status(self, component: str, status: str, message: str) -> Dict[str, Any]:
        """Set the status of a component"""
        timestamp = datetime.datetime.now().isoformat()
        
        status_data = {
            "component": component,
            "status": status,
            "message": message,
            "last_update": timestamp,
            "history": []
        }
        
        # Get existing data if available
        status_file = os.path.join(STATUS_DIR, f"{component}.json")
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                existing_data = json.load(f)
                
            # Add current status to history
            if "status" in existing_data and "last_update" in existing_data:
                history_entry = {
                    "status": existing_data["status"],
                    "message": existing_data.get("message", ""),
                    "timestamp": existing_data["last_update"]
                }
                
                # Get existing history and add new entry
                history = existing_data.get("history", [])
                history.append(history_entry)
                
                # Keep only last 10 entries
                if len(history) > 10:
                    history = history[-10:]
                    
                status_data["history"] = history
        
        # Save status
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
            
        return status_data
    
    def record_test(self, component: str, success: bool, results: Dict[str, Any]) -> Dict[str, Any]:
        """Record test results for a component"""
        timestamp = datetime.datetime.now().isoformat()
        
        test_data = {
            "component": component,
            "success": success,
            "timestamp": timestamp,
            **results
        }
        
        # Save test results
        test_file = os.path.join(TEST_RESULTS_DIR, f"{component}.json")
        with open(test_file, 'w') as f:
            json.dump(test_data, f, indent=2)
            
        # Update component status
        status = "HEALTHY" if success else "UNHEALTHY"
        message = f"Tests {'passed' if success else 'failed'}: {results.get('passed', 0)} passed, {results.get('failed', 0)} failed"
        self.set_status(component, status, message)
            
        return test_data
    
    def record_issue(self, component: str, title: str, description: str = "", severity: str = "medium") -> Dict[str, Any]:
        """Record an issue for a component"""
        timestamp = datetime.datetime.now().isoformat()
        issue_id = str(uuid.uuid4())
        
        issue_data = {
            "id": issue_id,
            "component": component,
            "title": title,
            "description": description,
            "severity": severity,
            "status": "open",
            "created": timestamp,
            "updated": timestamp
        }
        
        # Save issue
        issue_file = os.path.join(ISSUES_DIR, f"{issue_id}.json")
        with open(issue_file, 'w') as f:
            json.dump(issue_data, f, indent=2)
            
        # Update component status based on severity
        if severity == "critical":
            status = "UNHEALTHY"
        elif severity in ["high", "medium"]:
            status = "DEGRADED"
        else:
            status = "HEALTHY"
            
        message = f"Issue reported: {title} (Severity: {severity})"
        self.set_status(component, status, message)
            
        return issue_data
    
    def record_start(self, component: str, success: bool, env: str, version: str) -> Dict[str, Any]:
        """Record component start"""
        timestamp = datetime.datetime.now().isoformat()
        
        start_data = {
            "component": component,
            "success": success,
            "environment": env,
            "version": version,
            "timestamp": timestamp
        }
        
        # Save start data
        start_file = os.path.join(STATUS_DIR, f"{component}-start.json")
        with open(start_file, 'w') as f:
            json.dump(start_data, f, indent=2)
            
        # Update component status
        status = "HEALTHY" if success else "UNHEALTHY"
        message = f"Component {'started successfully' if success else 'failed to start'} in {env} environment with version {version}"
        self.set_status(component, status, message)
            
        return start_data
    
    def list_components(self) -> List[str]:
        """List all components with status information"""
        if not os.path.exists(STATUS_DIR):
            return []
            
        return [
            os.path.splitext(f)[0] for f in os.listdir(STATUS_DIR)
            if f.endswith('.json') and not f.endswith('-start.json')
        ]
    
    def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all components"""
        components = self.list_components()
        statuses = {}
        
        for component in components:
            statuses[component] = self.get_status(component)
            
        return statuses
    
    def get_issues(self, component: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all issues, optionally filtered by component"""
        if not os.path.exists(ISSUES_DIR):
            return []
            
        issues = []
        for f in os.listdir(ISSUES_DIR):
            if f.endswith('.json'):
                with open(os.path.join(ISSUES_DIR, f), 'r') as issue_file:
                    issue = json.load(issue_file)
                    if component is None or issue.get('component') == component:
                        issues.append(issue)
                        
        return sorted(issues, key=lambda x: x.get('created', ''), reverse=True)
    
    def create_work_ticket(self, issue_id: str, assigned_to: str, priority: str = "medium") -> Dict[str, Any]:
        """Create a work ticket from an issue"""
        # Get issue data
        issue_file = os.path.join(ISSUES_DIR, f"{issue_id}.json")
        if not os.path.exists(issue_file):
            raise ValueError(f"Issue {issue_id} not found")
            
        with open(issue_file, 'r') as f:
            issue = json.load(f)
            
        # Create ticket
        timestamp = datetime.datetime.now().isoformat()
        ticket_id = str(uuid.uuid4())
        
        ticket_data = {
            "id": ticket_id,
            "issue_id": issue_id,
            "component": issue.get("component"),
            "title": issue.get("title"),
            "description": issue.get("description", ""),
            "assigned_to": assigned_to,
            "priority": priority,
            "status": "open",
            "created": timestamp,
            "updated": timestamp
        }
        
        # Save ticket
        ticket_file = os.path.join(WORK_TICKETS_DIR, f"{ticket_id}.json")
        with open(ticket_file, 'w') as f:
            json.dump(ticket_data, f, indent=2)
            
        # Update issue status
        issue["status"] = "assigned"
        issue["updated"] = timestamp
        issue["ticket_id"] = ticket_id
        
        with open(issue_file, 'w') as f:
            json.dump(issue, f, indent=2)
            
        return ticket_data


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="HMS Status Tracker")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")
    
    # get command
    get_parser = subparsers.add_parser("get", help="Get component status")
    get_parser.add_argument("component", help="Component name")
    
    # set command
    set_parser = subparsers.add_parser("set", help="Set component status")
    set_parser.add_argument("component", help="Component name")
    set_parser.add_argument("status", choices=["HEALTHY", "DEGRADED", "UNHEALTHY", "UNKNOWN"], help="Status")
    set_parser.add_argument("message", help="Status message")
    
    # test command
    test_parser = subparsers.add_parser("test", help="Record test results")
    test_parser.add_argument("component", help="Component name")
    test_parser.add_argument("--success", action="store_true", help="Test succeeded")
    test_parser.add_argument("--failure", action="store_true", help="Test failed")
    test_parser.add_argument("--results", type=str, help="Test results in JSON format")
    
    # issue command
    issue_parser = subparsers.add_parser("issue", help="Record an issue")
    issue_parser.add_argument("component", help="Component name")
    issue_parser.add_argument("--title", required=True, help="Issue title")
    issue_parser.add_argument("--description", help="Issue description")
    issue_parser.add_argument("--severity", choices=["critical", "high", "medium", "low"], default="medium", help="Issue severity")
    
    # start command
    start_parser = subparsers.add_parser("start", help="Record component start")
    start_parser.add_argument("component", help="Component name")
    start_parser.add_argument("--success", action="store_true", help="Start succeeded")
    start_parser.add_argument("--failure", action="store_true", help="Start failed")
    start_parser.add_argument("--env", required=True, help="Environment (dev, test, prod)")
    start_parser.add_argument("--version", required=True, help="Component version")
    
    # list command
    subparsers.add_parser("list", help="List all components")
    
    # all command
    subparsers.add_parser("all", help="Get status of all components")
    
    # issues command
    issues_parser = subparsers.add_parser("issues", help="Get issues")
    issues_parser.add_argument("--component", help="Filter by component")
    
    # ticket command
    ticket_parser = subparsers.add_parser("ticket", help="Create work ticket from issue")
    ticket_parser.add_argument("issue_id", help="Issue ID")
    ticket_parser.add_argument("--assigned-to", required=True, help="Assignee")
    ticket_parser.add_argument("--priority", choices=["high", "medium", "low"], default="medium", help="Ticket priority")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create tracker
    tracker = StatusTracker()
    
    # Execute command
    if args.command == "get":
        status = tracker.get_status(args.component)
        print(json.dumps(status, indent=2))
    elif args.command == "set":
        status = tracker.set_status(args.component, args.status, args.message)
        print(json.dumps(status, indent=2))
    elif args.command == "test":
        if not (args.success or args.failure):
            print("Error: Must specify --success or --failure")
            sys.exit(1)
            
        results = {}
        if args.results:
            results = json.loads(args.results)
            
        test_data = tracker.record_test(args.component, args.success, results)
        print(json.dumps(test_data, indent=2))
    elif args.command == "issue":
        issue = tracker.record_issue(args.component, args.title, args.description or "", args.severity)
        print(json.dumps(issue, indent=2))
    elif args.command == "start":
        if not (args.success or args.failure):
            print("Error: Must specify --success or --failure")
            sys.exit(1)
            
        start_data = tracker.record_start(args.component, args.success, args.env, args.version)
        print(json.dumps(start_data, indent=2))
    elif args.command == "list":
        components = tracker.list_components()
        for component in components:
            print(component)
    elif args.command == "all":
        statuses = tracker.get_all_statuses()
        print(json.dumps(statuses, indent=2))
    elif args.command == "issues":
        issues = tracker.get_issues(args.component)
        print(json.dumps(issues, indent=2))
    elif args.command == "ticket":
        try:
            ticket = tracker.create_work_ticket(args.issue_id, args.assigned_to, args.priority)
            print(json.dumps(ticket, indent=2))
        except ValueError as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()