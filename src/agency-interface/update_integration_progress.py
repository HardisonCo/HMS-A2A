#!/usr/bin/env python3
"""
Update and visualize the progress of the HMS-API to Crohn's Adaptive Trials Integration.
"""

import json
import argparse
import datetime
from pathlib import Path
import sys
from typing import Dict, List, Any, Optional

# Configuration
TRACKER_PATH = Path(__file__).parent / "integration_progress_tracker.json"
CHART_PATH = Path(__file__).parent / "integration_progress_chart.html"

def load_tracker() -> Dict[str, Any]:
    """Load the progress tracker JSON file."""
    try:
        with open(TRACKER_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Tracker file not found at {TRACKER_PATH}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in tracker file {TRACKER_PATH}")
        sys.exit(1)

def save_tracker(tracker: Dict[str, Any]) -> None:
    """Save the progress tracker JSON file."""
    with open(TRACKER_PATH, 'w') as f:
        json.dump(tracker, f, indent=2)

def update_task_progress(tracker: Dict[str, Any], task_id: str, progress: int, 
                          status: Optional[str] = None, notes: Optional[str] = None) -> Dict[str, Any]:
    """Update the progress of a specific task."""
    found = False
    
    # Validate status if provided
    valid_statuses = ["not_started", "in_progress", "completed", "blocked", "at_risk"]
    if status and status not in valid_statuses:
        print(f"Error: Invalid status '{status}'. Must be one of {valid_statuses}")
        sys.exit(1)
    
    # Validate progress
    if not 0 <= progress <= 100:
        print(f"Error: Progress must be between 0 and 100, got {progress}")
        sys.exit(1)
    
    # Find and update the task
    for phase in tracker["phases"]:
        for task in phase["tasks"]:
            if task["id"] == task_id:
                task["progress"] = progress
                
                if status:
                    task["status"] = status
                
                # If task is marked as completed, set progress to 100
                if status == "completed" and progress < 100:
                    task["progress"] = 100
                    print(f"Note: Task {task_id} marked as completed, progress automatically set to 100%")
                
                # Add notes if provided
                if notes:
                    if "notes" not in task:
                        task["notes"] = []
                    
                    task["notes"].append({
                        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "content": notes
                    })
                
                found = True
                print(f"Updated task {task_id}: Progress = {progress}%, Status = {task['status']}")
                break
        
        if found:
            break
    
    if not found:
        print(f"Error: Task with ID '{task_id}' not found")
        sys.exit(1)
    
    # Recalculate phase and overall progress
    tracker = calculate_progress(tracker)
    
    # Update the last updated timestamp
    tracker["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    return tracker

def calculate_progress(tracker: Dict[str, Any]) -> Dict[str, Any]:
    """Recalculate progress for all phases and overall progress."""
    overall_tasks = 0
    overall_progress = 0
    
    for phase in tracker["phases"]:
        phase_tasks = len(phase["tasks"])
        phase_progress = sum(task["progress"] for task in phase["tasks"])
        
        if phase_tasks > 0:
            phase["progress"] = round(phase_progress / phase_tasks)
        else:
            phase["progress"] = 0
        
        overall_tasks += phase_tasks
        overall_progress += phase_progress
        
        # Update in overall_progress section
        tracker["overall_progress"][phase["id"]] = phase["progress"]
    
    # Calculate overall progress
    if overall_tasks > 0:
        tracker["overall_progress"]["total"] = round(overall_progress / overall_tasks)
    else:
        tracker["overall_progress"]["total"] = 0
    
    return tracker

def update_risk(tracker: Dict[str, Any], risk_id: str, status: str, 
                notes: Optional[str] = None) -> Dict[str, Any]:
    """Update the status of a risk."""
    valid_statuses = ["monitoring", "mitigating", "resolved", "occurred"]
    if status not in valid_statuses:
        print(f"Error: Invalid risk status '{status}'. Must be one of {valid_statuses}")
        sys.exit(1)
    
    found = False
    for risk in tracker["risks"]:
        if risk["id"] == risk_id:
            risk["status"] = status
            
            if notes:
                if "notes" not in risk:
                    risk["notes"] = []
                
                risk["notes"].append({
                    "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "content": notes
                })
            
            found = True
            print(f"Updated risk {risk_id}: Status = {status}")
            break
    
    if not found:
        print(f"Error: Risk with ID '{risk_id}' not found")
        sys.exit(1)
    
    return tracker

def update_milestone(tracker: Dict[str, Any], milestone_id: str, status: str) -> Dict[str, Any]:
    """Update the status of a milestone."""
    valid_statuses = ["not_started", "in_progress", "completed", "at_risk", "delayed"]
    if status not in valid_statuses:
        print(f"Error: Invalid milestone status '{status}'. Must be one of {valid_statuses}")
        sys.exit(1)
    
    found = False
    for milestone in tracker["milestones"]:
        if milestone["id"] == milestone_id:
            milestone["status"] = status
            found = True
            print(f"Updated milestone {milestone_id}: Status = {status}")
            break
    
    if not found:
        print(f"Error: Milestone with ID '{milestone_id}' not found")
        sys.exit(1)
    
    return tracker

def generate_html_chart(tracker: Dict[str, Any]) -> None:
    """Generate an HTML chart visualizing the progress."""
    total_progress = tracker["overall_progress"]["total"]
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Integration Progress</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1, h2 {{
            color: #2c3e50;
        }}
        .progress-container {{
            margin-bottom: 20px;
        }}
        .progress-bar {{
            height: 25px;
            background-color: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 5px;
            position: relative;
        }}
        .progress-bar-inner {{
            height: 100%;
            background-color: #3498db;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
        .phase-title {{
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
        }}
        .phase-progress {{
            font-weight: bold;
        }}
        .tasks-container {{
            margin-left: 20px;
            margin-bottom: 20px;
        }}
        .task-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }}
        .task-info {{
            flex: 1;
        }}
        .task-status {{
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        .status-not_started {{
            background-color: #e0e0e0;
        }}
        .status-in_progress {{
            background-color: #3498db;
            color: white;
        }}
        .status-completed {{
            background-color: #2ecc71;
            color: white;
        }}
        .status-blocked {{
            background-color: #e74c3c;
            color: white;
        }}
        .status-at_risk {{
            background-color: #f39c12;
            color: white;
        }}
        .task-progress-bar {{
            flex: 0 0 120px;
            height: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
            overflow: hidden;
            margin-top: 5px;
        }}
        .task-progress-bar-inner {{
            height: 100%;
            background-color: #3498db;
        }}
        .task-progress-text {{
            font-size: 0.8em;
            text-align: right;
            margin-top: 2px;
        }}
        .risk-container {{
            margin-bottom: 20px;
        }}
        .risk-row {{
            display: flex;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
            margin-bottom: 8px;
        }}
        .risk-info {{
            flex: 1;
        }}
        .risk-status {{
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        .status-monitoring {{
            background-color: #3498db;
            color: white;
        }}
        .status-mitigating {{
            background-color: #f39c12;
            color: white;
        }}
        .status-resolved {{
            background-color: #2ecc71;
            color: white;
        }}
        .status-occurred {{
            background-color: #e74c3c;
            color: white;
        }}
        .milestone-container {{
            margin-bottom: 20px;
        }}
        .milestone-row {{
            display: flex;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
            margin-bottom: 8px;
        }}
        .milestone-info {{
            flex: 1;
        }}
        .milestone-status {{
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        .status-delayed {{
            background-color: #e74c3c;
            color: white;
        }}
        .last-updated {{
            margin-top: 30px;
            font-size: 0.8em;
            color: #7f8c8d;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>HMS-API to Crohn's Adaptive Trials Integration Progress</h1>
        
        <!-- Overall Progress -->
        <div class="progress-container">
            <h2>Overall Progress: {total_progress}%</h2>
            <div class="progress-bar">
                <div class="progress-bar-inner" style="width: {total_progress}%">{total_progress}%</div>
            </div>
        </div>
        
        <!-- Phases Progress -->
        <h2>Phases</h2>
"""
    
    # Add phases
    for phase in tracker["phases"]:
        phase_name = phase["name"]
        weeks = phase["weeks"]
        progress = phase["progress"]
        
        html += f"""
        <div class="progress-container">
            <div class="phase-title">
                <h3>{phase_name} (Weeks {weeks})</h3>
                <span class="phase-progress">{progress}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-bar-inner" style="width: {progress}%">{progress}%</div>
            </div>
            
            <div class="tasks-container">
"""
        
        # Add tasks
        for task in phase["tasks"]:
            task_id = task["id"]
            task_name = task["name"]
            status = task["status"]
            description = task["description"]
            progress = task["progress"]
            
            html += f"""
                <div class="task-row">
                    <div class="task-info">
                        <strong>{task_id}: {task_name}</strong>
                        <span class="task-status status-{status}">{status}</span>
                        <div>{description}</div>
                        <div class="task-progress-bar">
                            <div class="task-progress-bar-inner" style="width: {progress}%"></div>
                        </div>
                        <div class="task-progress-text">{progress}%</div>
                    </div>
                </div>
"""
        
        html += """
            </div>
        </div>
"""
    
    # Add risks
    html += """
        <h2>Risks</h2>
        <div class="risk-container">
"""
    
    for risk in tracker["risks"]:
        risk_name = risk["name"]
        status = risk["status"]
        probability = risk["probability"]
        impact = risk["impact"]
        mitigation = risk["mitigation"]
        
        html += f"""
            <div class="risk-row">
                <div class="risk-info">
                    <strong>{risk_name}</strong>
                    <span class="risk-status status-{status}">{status}</span>
                    <div>Probability: {probability}, Impact: {impact}</div>
                    <div>Mitigation: {mitigation}</div>
                </div>
            </div>
"""
    
    html += """
        </div>
        
        <h2>Milestones</h2>
        <div class="milestone-container">
"""
    
    # Add milestones
    for milestone in tracker["milestones"]:
        milestone_name = milestone["name"]
        status = milestone["status"]
        date = milestone["date"]
        
        html += f"""
            <div class="milestone-row">
                <div class="milestone-info">
                    <strong>{milestone_name}</strong>
                    <span class="milestone-status status-{status}">{status}</span>
                    <div>Target Date: {date}</div>
                </div>
            </div>
"""
    
    last_updated = tracker["last_updated"]
    
    html += f"""
        </div>
        
        <div class="last-updated">
            Last updated: {last_updated}
        </div>
    </div>
</body>
</html>
"""
    
    with open(CHART_PATH, 'w') as f:
        f.write(html)
    
    print(f"Progress chart generated at {CHART_PATH}")

def show_tasks(tracker: Dict[str, Any]) -> None:
    """Display all tasks with their IDs and current progress."""
    print("\nTask List:")
    print("-" * 80)
    print(f"{'ID':<8} {'Status':<12} {'Progress':<10} {'Name':<30} {'Phase'}")
    print("-" * 80)
    
    for phase in tracker["phases"]:
        for task in phase["tasks"]:
            print(f"{task['id']:<8} {task['status']:<12} {task['progress']:<10}% {task['name']:<30} {phase['name']}")
    
    print("-" * 80)

def show_risks(tracker: Dict[str, Any]) -> None:
    """Display all risks with their IDs and current status."""
    print("\nRisk List:")
    print("-" * 80)
    print(f"{'ID':<8} {'Status':<12} {'Probability':<12} {'Impact':<8} {'Name'}")
    print("-" * 80)
    
    for risk in tracker["risks"]:
        print(f"{risk['id']:<8} {risk['status']:<12} {risk['probability']:<12} {risk['impact']:<8} {risk['name']}")
    
    print("-" * 80)

def show_milestones(tracker: Dict[str, Any]) -> None:
    """Display all milestones with their IDs and current status."""
    print("\nMilestone List:")
    print("-" * 80)
    print(f"{'ID':<12} {'Status':<12} {'Date':<12} {'Name'}")
    print("-" * 80)
    
    for milestone in tracker["milestones"]:
        print(f"{milestone['id']:<12} {milestone['status']:<12} {milestone['date']:<12} {milestone['name']}")
    
    print("-" * 80)

def show_progress(tracker: Dict[str, Any]) -> None:
    """Display overall progress and progress by phase."""
    print("\nProgress Summary:")
    print("-" * 60)
    print(f"Overall Progress: {tracker['overall_progress']['total']}%")
    print("-" * 60)
    
    for phase in tracker["phases"]:
        print(f"{phase['name']} (Weeks {phase['weeks']}): {phase['progress']}%")
    
    print("-" * 60)
    print(f"Last Updated: {tracker['last_updated']}")

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Update and visualize integration progress")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Task update command
    task_parser = subparsers.add_parser("update-task", help="Update task progress")
    task_parser.add_argument("task_id", help="Task ID to update")
    task_parser.add_argument("progress", type=int, help="New progress value (0-100)")
    task_parser.add_argument("--status", help="New task status")
    task_parser.add_argument("--notes", help="Notes about the update")
    
    # Risk update command
    risk_parser = subparsers.add_parser("update-risk", help="Update risk status")
    risk_parser.add_argument("risk_id", help="Risk ID to update")
    risk_parser.add_argument("status", help="New risk status")
    risk_parser.add_argument("--notes", help="Notes about the update")
    
    # Milestone update command
    milestone_parser = subparsers.add_parser("update-milestone", help="Update milestone status")
    milestone_parser.add_argument("milestone_id", help="Milestone ID to update")
    milestone_parser.add_argument("status", help="New milestone status")
    
    # Show commands
    subparsers.add_parser("show-tasks", help="Show all tasks")
    subparsers.add_parser("show-risks", help="Show all risks")
    subparsers.add_parser("show-milestones", help="Show all milestones")
    subparsers.add_parser("show-progress", help="Show progress summary")
    
    # Chart command
    subparsers.add_parser("generate-chart", help="Generate HTML progress chart")
    
    args = parser.parse_args()
    
    # Load tracker data
    tracker = load_tracker()
    
    # Process commands
    if args.command == "update-task":
        tracker = update_task_progress(tracker, args.task_id, args.progress, args.status, args.notes)
        save_tracker(tracker)
        generate_html_chart(tracker)
    
    elif args.command == "update-risk":
        tracker = update_risk(tracker, args.risk_id, args.status, args.notes)
        save_tracker(tracker)
        generate_html_chart(tracker)
    
    elif args.command == "update-milestone":
        tracker = update_milestone(tracker, args.milestone_id, args.status)
        save_tracker(tracker)
        generate_html_chart(tracker)
    
    elif args.command == "show-tasks":
        show_tasks(tracker)
    
    elif args.command == "show-risks":
        show_risks(tracker)
    
    elif args.command == "show-milestones":
        show_milestones(tracker)
    
    elif args.command == "show-progress":
        show_progress(tracker)
    
    elif args.command == "generate-chart":
        generate_html_chart(tracker)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()