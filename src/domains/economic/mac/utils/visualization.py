"""
Visualization utilities for the MAC architecture.

This module provides functions for visualizing MAC collaborations,
including collaboration graphs, task timelines, and state views.
"""

import logging
from typing import Dict, Any, List, Optional

def visualize_collaboration(
    tasks: Dict[str, Any], 
    domains: List[str], 
    format_type: str = "text",
    output_file: Optional[str] = None
) -> str:
    """
    Generate a visualization of MAC collaboration.
    
    Args:
        tasks: Dictionary of tasks from the environment
        domains: List of domains involved in collaboration
        format_type: Output format ("text", "mermaid", "json")
        output_file: Optional file to write visualization
        
    Returns:
        Visualization string
    """
    if format_type == "text":
        return _generate_text_visualization(tasks, domains, output_file)
    elif format_type == "mermaid":
        return _generate_mermaid_visualization(tasks, domains, output_file)
    elif format_type == "json":
        return _generate_json_visualization(tasks, domains, output_file)
    else:
        logging.warning(f"Unsupported visualization format: {format_type}")
        return _generate_text_visualization(tasks, domains, output_file)

def _generate_text_visualization(
    tasks: Dict[str, Any], 
    domains: List[str],
    output_file: Optional[str] = None
) -> str:
    """
    Generate a text-based visualization.
    
    Args:
        tasks: Dictionary of tasks
        domains: List of domains
        output_file: Optional output file
        
    Returns:
        Text visualization
    """
    lines = []
    lines.append("MAC Collaboration Visualization")
    lines.append("=" * 40)
    lines.append("")
    
    # Display domains
    lines.append("Domains:")
    for domain in domains:
        lines.append(f"- {domain}")
    lines.append("")
    
    # Display tasks
    lines.append("Tasks:")
    for task_id, task_data in tasks.items():
        lines.append(f"Task: {task_id}")
        lines.append(f"  Description: {task_data.get('data', {}).get('description', 'N/A')}")
        lines.append(f"  Status: {task_data.get('status', 'unknown')}")
        
        # Display subtasks
        if "subtasks" in task_data and task_data["subtasks"]:
            lines.append("  Subtasks:")
            for subtask_id in task_data["subtasks"]:
                subtask = tasks.get(subtask_id)
                if subtask:
                    lines.append(f"    - {subtask_id}: {subtask.get('data', {}).get('description', 'N/A')}")
                    lines.append(f"      Status: {subtask.get('status', 'unknown')}")
                    lines.append(f"      Domain: {subtask.get('domain', 'unknown')}")
        
        lines.append("")
    
    # Display task flow
    lines.append("Task Flow:")
    for task_id, task_data in tasks.items():
        if "history" in task_data:
            lines.append(f"Task: {task_id}")
            for entry in task_data["history"]:
                lines.append(f"  {entry.get('timestamp', 'unknown')}: {entry.get('status', 'unknown')}")
            lines.append("")
    
    # Join all lines
    result = "\n".join(lines)
    
    # Write to file if requested
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(result)
        except Exception as e:
            logging.error(f"Error writing visualization to {output_file}: {str(e)}")
    
    return result

def _generate_mermaid_visualization(
    tasks: Dict[str, Any], 
    domains: List[str],
    output_file: Optional[str] = None
) -> str:
    """
    Generate a Mermaid-format visualization.
    
    Args:
        tasks: Dictionary of tasks
        domains: List of domains
        output_file: Optional output file
        
    Returns:
        Mermaid visualization
    """
    lines = []
    lines.append("```mermaid")
    lines.append("graph TD")
    
    # Add supervisor
    lines.append("  Supervisor[Supervisor Agent]")
    
    # Add domains
    for domain in domains:
        lines.append(f"  {domain}[{domain} Domain]")
        lines.append(f"  Supervisor -- Delegates --> {domain}")
    
    # Add tasks
    for task_id, task_data in tasks.items():
        # Skip subtasks as they'll be handled with parent tasks
        if task_data.get('data', {}).get('parent_id'):
            continue
            
        # Add main task
        safe_id = task_id.replace("-", "_")
        lines.append(f"  {safe_id}[{task_data.get('data', {}).get('description', 'Task')}]")
        lines.append(f"  Supervisor -- Decomposes --> {safe_id}")
        
        # Add subtasks
        if "subtasks" in task_data and task_data["subtasks"]:
            for subtask_id in task_data["subtasks"]:
                subtask = tasks.get(subtask_id)
                if subtask:
                    safe_subtask_id = subtask_id.replace("-", "_")
                    subtask_domain = subtask.get('domain', 'unknown')
                    lines.append(f"  {safe_subtask_id}[{subtask.get('data', {}).get('description', 'Subtask')}]")
                    lines.append(f"  {safe_id} -- Creates --> {safe_subtask_id}")
                    
                    # Link to domain
                    if subtask_domain in domains:
                        lines.append(f"  {subtask_domain} -- Executes --> {safe_subtask_id}")
    
    lines.append("```")
    
    # Join all lines
    result = "\n".join(lines)
    
    # Write to file if requested
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(result)
        except Exception as e:
            logging.error(f"Error writing visualization to {output_file}: {str(e)}")
    
    return result

def _generate_json_visualization(
    tasks: Dict[str, Any], 
    domains: List[str],
    output_file: Optional[str] = None
) -> str:
    """
    Generate a JSON-format visualization.
    
    Args:
        tasks: Dictionary of tasks
        domains: List of domains
        output_file: Optional output file
        
    Returns:
        JSON visualization
    """
    import json
    
    # Create visualization structure
    visualization = {
        "domains": domains,
        "tasks": tasks,
        "flow": _extract_task_flow(tasks)
    }
    
    # Convert to JSON
    result = json.dumps(visualization, indent=2)
    
    # Write to file if requested
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(result)
        except Exception as e:
            logging.error(f"Error writing visualization to {output_file}: {str(e)}")
    
    return result

def _extract_task_flow(tasks: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract task flow information for visualization.
    
    Args:
        tasks: Dictionary of tasks
        
    Returns:
        Task flow dictionary
    """
    flow = {}
    
    # Extract flow for each task
    for task_id, task_data in tasks.items():
        if "history" in task_data:
            flow[task_id] = []
            for entry in task_data["history"]:
                flow[task_id].append({
                    "timestamp": entry.get("timestamp", 0),
                    "status": entry.get("status", "unknown"),
                    "details": {k: v for k, v in entry.items() if k not in ["timestamp", "status"]}
                })
    
    return flow