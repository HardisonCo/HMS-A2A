#!/usr/bin/env python3
"""
Update Agency Progress

This script updates the agency progress tracker by checking
the status of each agency's components.
"""

import os
import sys
import json
import argparse
from datetime import datetime

def check_agency_status(agency, base_dir):
    """
    Check the implementation status of an agency.
    
    Args:
        agency: Agency acronym
        base_dir: Base directory for agency interface
        
    Returns:
        Status dictionary
    """
    agency_lower = agency.lower()
    
    # Check if issue finder exists
    issue_finder = os.path.join(base_dir, "agency_issue_finder", "agencies", f"{agency_lower}_finder.py")
    has_issue_finder = os.path.exists(issue_finder)
    
    # Check if research connector exists
    research_connector = os.path.join(base_dir, "agencies", f"{agency_lower}_connector.py")
    has_research_connector = os.path.exists(research_connector)
    
    # Check if ASCII art exists
    ascii_art = os.path.join(base_dir, "templates", f"{agency_lower}_ascii.txt")
    has_ascii_art = os.path.exists(ascii_art)
    
    # Determine overall status
    status = "not_started"
    if has_issue_finder and has_research_connector and has_ascii_art:
        status = "completed"
    elif has_issue_finder or has_research_connector or has_ascii_art:
        status = "in_progress"
    
    # Calculate completion percentage
    completion = 0
    if has_issue_finder:
        completion += 34
    if has_research_connector:
        completion += 33
    if has_ascii_art:
        completion += 33
    
    return {
        "status": status,
        "completion": completion,
        "components": {
            "issue_finder": has_issue_finder,
            "research_connector": has_research_connector,
            "ascii_art": has_ascii_art
        }
    }

def update_progress_tracker(config_file, tracker_file, base_dir):
    """
    Update the progress tracker file.
    
    Args:
        config_file: Path to configuration file
        tracker_file: Path to tracker file
        base_dir: Base directory for agency interface
        
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(config_file):
        print(f"Error: Config file not found: {config_file}")
        return False
    
    # Create empty tracker if it doesn't exist
    if not os.path.exists(tracker_file):
        tracker_data = {
            "agencies": {},
            "last_updated": datetime.now().isoformat()
        }
    else:
        # Load existing tracker
        try:
            with open(tracker_file, 'r') as f:
                tracker_data = json.load(f)
        except Exception as e:
            print(f"Error loading tracker file: {e}")
            return False
    
    # Load agency data from config
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        return False
    
    # Update status for each agency
    for agency_data in config_data.get("agencies", []):
        agency = agency_data.get("acronym")
        if agency:
            status = check_agency_status(agency, base_dir)
            
            # Update tracker
            tracker_data["agencies"][agency] = status
    
    # Update timestamp
    tracker_data["last_updated"] = datetime.now().isoformat()
    
    # Save updated tracker
    try:
        with open(tracker_file, 'w') as f:
            json.dump(tracker_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving tracker file: {e}")
        return False

def main():
    """Main entry point function."""
    parser = argparse.ArgumentParser(description="Update Agency Progress Tracker")
    parser.add_argument("--config", default="config/agency_data.json",
                       help="Path to configuration file")
    parser.add_argument("--tracker", default="config/agency_progress.json",
                       help="Path to tracker file")
    parser.add_argument("--base-dir", default=os.path.dirname(os.path.abspath(__file__)),
                       help="Base directory for agency interface")
    
    args = parser.parse_args()
    
    # Check if config file is absolute path
    config_file = args.config
    if not os.path.isabs(config_file):
        config_file = os.path.join(args.base_dir, config_file)
    
    # Check if tracker file is absolute path
    tracker_file = args.tracker
    if not os.path.isabs(tracker_file):
        tracker_file = os.path.join(args.base_dir, tracker_file)
    
    # Update progress tracker
    success = update_progress_tracker(config_file, tracker_file, args.base_dir)
    
    if success:
        print(f"Progress tracker updated: {tracker_file}")
    else:
        print("Failed to update progress tracker.")
        sys.exit(1)

if __name__ == "__main__":
    main()